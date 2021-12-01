#get to the correct directory
#source venv/bin/activate
#export FLASK_APP=main.py
#flask run

from flask import Flask, render_template, request, redirect, session
import pymysql
from datetime import date
import time
 

app = Flask(__name__) #initialize app from flask 
wsgi_app = app.wsgi_app


#configure MYSQL/connects to database
conn = pymysql.connect(host = '127.0.0.1',
					   #port = 8889,              #I REMOVED THIS because I added what the prof had at the bottom of this file and that somehow solved my 3 hour problem
					   user = 'root',
					   #password = 'root',
                       password = '',
					   db = 'ticket_booking', # insert database name here 
					   charset = 'utf8mb4',
					   cursorclass = pymysql.cursors.DictCursor)
	
#PUBLIC VIEW
@app.route('/')
def public_search(): 
    session.clear()
    session['display_destinations'] = 3
    return render_template("public_search.html")

@app.route('/public_view', methods = ["GET", "POST"])
def public_view(): 

    query = "SELECT * FROM available_tickets WHERE departure_date >= '2021-11-11'" #FIX
    
    queries = []
    departure_date = request.form.get('departure_date')
    arrival_date = request.form.get('arrival_date')
    departure_city = request.form.get('departure_city')
    arrival_city = request.form.get('arrival_city')
    departure_airport = request.form.get('departure_airport')
    arrival_airport = request.form.get('arrival_airport')

    if departure_airport != '':
        queries.append("departure_airport = '%s'" % departure_airport)
    if arrival_airport != '':
        queries.append("arrival_airport = '%s'" % arrival_airport)
    if departure_date != '':
        queries.append("departure_date = '%s'" % departure_date) 
    if arrival_date != '':
        queries.append("arrival_date = '%s'" % arrival_date) 
    if departure_city != '':
        queries.append("departure_city = '%s'" % departure_city)
    if arrival_city != '':
        queries.append("arrival_city = '%s'" % arrival_city)
    if queries:
        query += " AND " + " AND ".join(queries)

    #execute queries from database
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    
    cursor.close()
    return render_template('public_view.html', data=data)


#
# BEGIN CUSTOMER LOGIN
#

def isCustomer():
    """
    verifies if there is a customer with the current session's email
    should be used to check whether the user is trying to inappropriately access a customer method
    :return data: tuple of query result, can use "if VerifyCustomer():" to check whether or not it's empty.
    EXAMPLE USE IN CUSTHOME() FUNCTION
    """
    
    verify = "SELECT * FROM customer WHERE email = %s"
    try:
        cursor = conn.cursor()
        cursor.execute(verify, session['email'])
        data = cursor.fetchone()
        cursor.close()
        return len(data) > 0
    except:
        return False
    return False

@app.route('/customer_login', methods = ["GET", "POST"])
def cust_login():
    return render_template('customer_login.html')

@app.route('/customer_logged_in', methods = ["GET", "POST"])
def cust_logged():
    cursor = conn.cursor()
    if request.form.get('action') == 'login':
        email = request.form.get('email')
        password = request.form.get('password')
        cursor.execute("SELECT * FROM customer WHERE email = %s", email)
        existing_cust = cursor.fetchone()
        if existing_cust:
            cursor.execute("SELECT * FROM customer WHERE email = %s AND pw = md5(%s)", (email, password))
            existing_cust = cursor.fetchall()
            if existing_cust:
                cursor.close()
                session['email'] = email
                return render_template('customer_logged_in.html')
        cursor.close()
        error = "No existing customer for that combination of info. Please try again or register."
        return render_template('customer_login.html', error = error)

    else:
        email = request.form.get('email')
        name = request.form.get('name')
        building_num = int(request.form.get('building_num'))
        street = request.form.get('street')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = int(request.form.get('phone'))
        pp_num = int(request.form.get('pp_num'))
        pp_exp = request.form.get('pp_exp')
        pp_country = request.form.get('pp_country')
        dob = request.form.get('dob')
        pw = request.form.get('pw')
        print(email, name, building_num, street, city, state, phone, pp_num, pp_exp, pp_country, dob, pw)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customer WHERE email = %s", email)
        existing_cust = cursor.fetchone()
        if existing_cust:
            #error
            error = "There is already a customer with that email. Try a different email."
            cursor.close()
            return render_template('customer_login.html', error = error)
        cursor.execute("SELECT md5(%s)", pw)
        pw = list(cursor.fetchone().values())[0]
        cursor.execute("INSERT INTO customer VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
         (email, name, building_num, street, city, state, phone, pp_num, pp_exp, pp_country, dob, pw))
        cursor.close()
        return render_template('customer_logged_in.html')


@app.route('/customer_view_flights', methods = ["GET", "POST"])
def cust_view_all(): 
    query = "SELECT * FROM available_tickets WHERE departure_date >= '2021-11-11'" 
    queries = []
    departure_date = request.form.get('departure_date')
    arrival_date = request.form.get('arrival_date')
    departure_city = request.form.get('departure_city')
    arrival_city = request.form.get('arrival_city')
    departure_airport = request.form.get('departure_airport')
    arrival_airport = request.form.get('arrival_airport')

    if departure_airport != '':
        queries.append("departure_airport = '%s'" % departure_airport)
    if arrival_airport != '':
        queries.append("arrival_airport = '%s'" % arrival_airport)
    if departure_date != '':
        queries.append("departure_date = '%s'" % departure_date) 
    if arrival_date != '':
        queries.append("arrival_date = '%s'" % arrival_date) 
    if departure_city != '':
        queries.append("departure_city = '%s'" % departure_city)
    if arrival_city != '':
        queries.append("arrival_city = '%s'" % arrival_city)
    if queries:
        query += " AND " + " AND ".join(queries)
    print(query) 

    #execute queries from database
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('customer_view_flights.html', data = data)

@app.route('/customer_my_flights', methods = ["GET", "POST"])
def cust_my_flights(): 
    if isCustomer(): 
        query = "SELECT * FROM purchase_info natural join ticket natural join available_tickets WHERE airline_name = airline_name " \
                    "AND purchase_info.customer_email = %s"
        cursor = conn.cursor()
        cursor.execute(query, session['email'])
        data = cursor.fetchall()
        cursor.close()
        return render_template('customer_my_flights.html', data=data)

#
# BEGIN AIRLINE STAFF LOGIN
#


@app.route('/airline_login', methods = ["GET", "POST"])
def airline_login():
    return render_template('airline_login.html')

@app.route('/airline_logged_in', methods = ["GET", "POST"])
def airline_logged():
    cursor = conn.cursor()
    if request.form.get('action') == 'login' or request.form.get('action') == 'register':
        if request.form.get('action') == 'login':
            username = request.form.get('username')
            password = request.form.get('password')
            cursor.execute("SELECT * FROM airline_staff WHERE username = %s", username)
            existing_staff = cursor.fetchone()
            if existing_staff:
                cursor.execute("SELECT * FROM airline_staff WHERE username = %s AND password = md5(%s)", (username, password))
                existing_staff = cursor.fetchone()
                if existing_staff:
                    cursor.close()
                    session['username'] = username
                    return render_template('airline_logged_in.html')
            error = "No existing staff for that combination of info. Please try again or register."
            return render_template('airline_login.html', error = error)


        elif request.form.get('action') == 'register':
            username = request.form.get('username')
            airline = request.form.get('airline')
            password = request.form.get('pw')
            fn = request.form.get('first_name')
            ln = request.form.get('last_name')
            dob = request.form.get('dob')
            cursor.execute("SELECT * FROM airline_staff WHERE username = %s", username)
            existing_staff = cursor.fetchall()
            if existing_staff:
                cursor.close()
                error = "There is already a staff member with that username. Try using a different username."
                return render_template('airline_login.html', error = error)
            cursor.execute("SELECT md5(%s)", password)
            password = list(cursor.fetchone().values())[0]

            cursor = conn.cursor()
            cursor.execute("INSERT INTO airline_staff VALUES (%s, %s, %s, %s, %s, %s)", (username, airline, password, fn, ln, dob))
            cursor.close()
            session['username'] = username
            return render_template('airline_logged_in.html')

    cursor.execute("SELECT username, airline_name FROM airline_staff WHERE username = %s", session['username'])
    logged_in = cursor.fetchone()
    if not logged_in:
        cursor.close()
        error = "Airline staff not logged in. Please login and try again."
        return render_template('airline_login.html', error = error)
    
    airline = logged_in['airline_name']
    cursor.execute("SELECT customer_email as email, flights_taken FROM (SELECT *, COUNT(UNIQUE ticket_id) as flights_taken FROM purchase_info NATURAL JOIN ticket WHERE airline_name = %s GROUP BY customer_email) as countflights ORDER BY flights_taken LIMIT 3", airline)
    data3 = cursor.fetchall()


    if request.form.get('action') == "register_plane":
        cursor.execute("SELECT username, airline_name FROM airline_staff WHERE username = %s", session['username'])
        logged_in = cursor.fetchone()
        if logged_in:
            airplane_id = request.form.get('airplane_id')
            num_seats = request.form.get('num_seats')
            airline = logged_in['airline_name']
            cursor.execute("SELECT * FROM airplane WHERE airline_name = %s AND airplane_id = %s", (airline, airplane_id))
            existing_plane = cursor.fetchone()
            if existing_plane:
                cursor.close()
                error = "There is already a plane with that ID and airline in the system. Please choose a new ID."
                return render_template('airline_logged_in.html', error = error)
            cursor.execute("INSERT INTO airplane VALUES (%s, %s, %s)", (airplane_id, airline, num_seats))
            cursor.close()
            error = "Sucessfully added a plane."
            return render_template('airline_logged_in.html', error = error)
        cursor.close()
        error = "Airline staff not logged in. Please login and try again."
        return render_template('airline_login.html', error = error)


    elif request.form.get('action') == "new_flight":
        cursor.execute("SELECT username, airline_name FROM airline_staff WHERE username = %s", session['username'])
        logged_in = cursor.fetchone()
        if logged_in:
            flight_num = request.form.get('flight_num')
            dep_date = request.form.get('departure_date')
            dep_time = request.form.get('departure_time')
            base_price = request.form.get('base_price')
            dep_airport = request.form.get('departure_airport')
            arr_airport = request.form.get('arrival_airport')
            arr_date = request.form.get('arrival_date')
            arr_time = request.form.get('arrival_time')
            airplane_id = request.form.get('airplane_id')
            airline = logged_in['airline_name']
            status = 'O'
            tickets_sold = 0
            cursor.execute("SELECT * FROM airplane WHERE airplane_id = %s AND airline_name = %s", (airplane_id, airline))
            ex_airplane = cursor.fetchall()
            if not ex_airplane:
                cursor.close()
                error = "There is no existing plane within your airline with that airplane ID. Please enter a valid airplane ID."
                return render_template('airline_logged_in.html', error = error)
            cursor.execute("SELECT * FROM airport WHERE airport_code = %s", dep_airport)
            ex_airport = cursor.fetchall()
            if not ex_airport:
                cursor.close()
                error = "There is no existing airport with that code for departure. Please enter a valid airport code."
                return render_template('airline_logged_in.html', error = error)
            cursor.execute("SELECT * FROM airport WHERE airport_code = %s", arr_airport)
            ex_airport = cursor.fetchall()
            if not ex_airport:
                cursor.close()
                error = "There is no existing airport with that code for arrival. Please enter a valid airport code."
                return render_template('airline_logged_in.html', error = error)
            cursor.execute("SELECT * FROM flight WHERE airline_name = %s AND departure_date = %s AND departure_time = %s", (airline, dep_date, dep_time))
            existing_flight = cursor.fetchone()
            if existing_flight:
                cursor.close()
                error = "There is already a flight with those details in the system. Please choose a new flight number, departure date, or departure time."
                return render_template('airline_logged_in.html', error = error)
            cursor.execute("INSERT INTO flight VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                (flight_num, dep_date, dep_time, airline, base_price, dep_airport, arr_airport, arr_date, arr_time, airplane_id, status, tickets_sold))
            cursor.close()
            error = "Sucessfully added a flight."
            return render_template('airline_logged_in.html', error = error)
        cursor.close()
        error = "Airline staff not logged in. Please login and try again."
        return render_template('airline_login.html', error = error)


    elif request.form.get("action") == "new_airport":
        cursor.execute("SELECT username, airline_name FROM airline_staff WHERE username = %s", session['username'])
        logged_in = cursor.fetchone()
        if logged_in:
            code = request.form.get('code')
            name = request.form.get('name')
            city = request.form.get('city')
            cursor.execute("SELECT * FROM airport WHERE airport_code = %s", code)
            existing_airport = cursor.fetchall()
            if existing_airport:
                cursor.close()
                error = "There is already an airport with that code. Please choose a new airport code."
                return render_template('airline_logged_in.html', error = error)
            if len(code) != 3:
                cursor.close()
                error = "Please choose an airport code that is exactly 3 characters long."
                return render_template('airline_logged_in.html', error = error)
            cursor.execute("INSERT INTO airport VALUES (%s, %s, %s)", (code, name, city))
            cursor.close()
            error = "Successfully added airport."
            return render_template('airline_logged_in.html', error = error)
        cursor.close()
        error = "Airline staff not logged in. Please login and try again."
        return render_template('airline_login.html', error = error)


    elif request.form.get("action") == "new_airport":
        cursor.execute("SELECT username, airline_name FROM airline_staff WHERE username = %s", session['username'])
        logged_in = cursor.fetchone()
        if logged_in:
            code = request.form.get('code')
            name = request.form.get('name')
            city = request.form.get('city')
            cursor.execute("SELECT * FROM airport WHERE airport_code = %s", code)
            existing_airport = cursor.fetchall()
            if existing_airport:
                cursor.close()
                error = "There is already an airport with that code. Please choose a new airport code."
                return render_template('airline_logged_in.html', error = error)
            if len(code) != 3:
                cursor.close()
                error = "Please choose an airport code that is exactly 3 characters long."
                return render_template('airline_logged_in.html', error = error)
            cursor.execute("INSERT INTO airport VALUES (%s, %s, %s)", (code, name, city))
            cursor.close()
            error = "Successfully added airport."
            return render_template('airline_logged_in.html', error = error)
        cursor.close()
        error = "Airline staff not logged in. Please login and try again."
        return render_template('airline_login.html', error = error)

    elif request.form.get("action") == "update_status":
        cursor.execute("SELECT username, airline_name FROM airline_staff WHERE username = %s", session['username'])
        logged_in = cursor.fetchone()
        if logged_in:
            flight_num = request.form.get('flight_num')
            dep_date = request.form.get('dep_date')
            dep_time = request.form.get('dep_time')
            airline = logged_in['airline_name']
            status = request.form.get('status')
            cursor.execute("SELECT * FROM flight WHERE flight_num = %s AND airline_name = %s AND departure_date = %s AND departure_time = %s", (flight_num, airline, dep_date, dep_time))
            existing_flight = cursor.fetchall()
            if existing_flight:
                cursor.execute("UPDATE flight SET flight_status = %s WHERE flight_num = %s AND airline_name = %s AND departure_date = %s AND departure_time = %s", (status, flight_num, airline, dep_date, dep_time))
                cursor.close()
                error = "Successfully updated flight status."
                return render_template('airline_logged_in.html', error = error)
            cursor.close()
            error = "No existing flight with those details. Unable to update."
            return render_template('airline_logged_in.html', error = error)
        cursor.close()
        error = "Airline staff not logged in. Please login and try again."
        return render_template('airline_login.html', error = error)

    elif request.form.get("action") == "see_ratings":
        cursor.execute("SELECT username, airline_name FROM airline_staff WHERE username = %s", session['username'])
        logged_in = cursor.fetchone()
        if logged_in:
            flight_num = request.form.get('flight_num')
            dep_date = request.form.get('dep_date')
            dep_time = request.form.get('dep_time')
            airline = logged_in['airline_name']
            if flight_num != 'See all flights':
                flight_num = int(flight_num)
                print(flight_num)
                print(dep_date)
                print(dep_time)
                cursor.execute("SELECT email, flight_num, departure_date, departure_time, rate, comment FROM rating WHERE flight_num = %s AND departure_date = %s AND departure_time = %s AND airline_name = %s",
                (flight_num, dep_date, dep_time, airline))
                data = cursor.fetchall()
                print(data)
                cursor.close()
                return render_template('airline_logged_in.html', data = data)
            cursor.execute("SELECT null as email, flight_num, departure_date, departure_time, AVG(rate) as rate, null as comment FROM rating WHERE airline_name = %s GROUP BY flight_num, departure_date, departure_time ORDER BY departure_date, departure_time", (airline))
            data = cursor.fetchall()
            cursor.close()
            return render_template('airline_logged_in.html', data = data)

    elif request.form.get("action") == 'see_opposite': #seems to be working but data set is small
        cursor.execute("SELECT username, airline_name FROM airline_staff WHERE username = %s", session['username'])
        logged_in = cursor.fetchone()
        if logged_in:
            airline = logged_in['airline_name']
            print(session.get('display_destinations'))
            if session['display_destinations'] == 3:
                session['display_destinations'] = 1
                cursor.execute("SELECT arrival_airport as airport_code, tickets_sold FROM ( SELECT *, SUM(tickets_booked) as tickets_sold FROM flight WHERE airline_name = %s AND departure_date > (SELECT DATE_SUB(CURDATE(), INTERVAL 1 YEAR)) GROUP BY airline_name, arrival_airport ORDER BY tickets_sold) AS finders LIMIT 3", airline)
                data2 = cursor.fetchall()
                cursor.close()
                return render_template('airline_logged_in.html', data2 = data2)
            session['display_destinations'] = 3
            cursor.execute("SELECT arrival_airport as airport_code, tickets_sold FROM (SELECT *, SUM(tickets_booked) as tickets_sold FROM flight WHERE airline_name = %s AND departure_date > (SELECT DATE_SUB(CURDATE(), INTERVAL 3 MONTH)) GROUP BY airline_name, arrival_airport ORDER BY tickets_sold) AS finders LIMIT 3", airline)
            data2 = cursor.fetchall()
            cursor.close()
            return render_template('airline_logged_in.html', data2 = data2)

    elif request.form.get("action") == "cust_flights":
        cursor.execute("SELECT username, airline_name FROM airline_staff WHERE username = %s", session['username'])
        logged_in = cursor.fetchone()
        if logged_in:
            airline = logged_in['airline_name']
            email = request.form.get('cust_email')
            cursor.execute("SELECT customer_email as email, flight_num, departure_date as dep_date, departure_time as dep_time FROM purchase_info NATURAL JOIN ticket WHERE airline_name = %s AND customer_email = %s", (airline, email))
            data4 = cursor.fetchall()
            return render_template('airline_logged_in.html', data4 = data4, data3 = data3)

    else:
        return render_template('public_search.html') # in case someone just tries to access this html page



@app.route('/airline_view_flights', methods = ["GET", "POST"])
def airline_view(): 
    query = "SELECT * FROM flight WHERE departure_date >= '2021-11-11'" #FIX
    
    queries = []
    departure_date = request.form.get('departure_date')
    arrival_date = request.form.get('arrival_date')
    departure_city = request.form.get('departure_city')
    arrival_city = request.form.get('arrival_city')
    departure_airport = request.form.get('departure_airport')
    arrival_airport = request.form.get('arrival_airport')

    if departure_airport != '':
        queries.append("departure_airport = '%s'" % departure_airport)
    if arrival_airport != '':
        queries.append("arrival_airport = '%s'" % arrival_airport)
    if departure_date != '':
        queries.append("departure_date = '%s'" % departure_date) 
    if arrival_date != '':
        queries.append("arrival_date = '%s'" % arrival_date) 
    if departure_city != '':
        queries.append("departure_city = '%s'" % departure_city)
    if arrival_city != '':
        queries.append("arrival_city = '%s'" % arrival_city)
    if queries:
        query += " AND " + " AND ".join(queries)
    print(query) 


    #execute queries from database
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('airline_view_flights.html', data=data)






app.secret_key = 'this is a key lol'
if __name__ == "__main__": #for some reason, these 2 lines of code solved my 3 hour issue, so you can remove it if it doesn't work for you and I will add it back for me
	app.run('127.0.0.1', 5000, debug = True)