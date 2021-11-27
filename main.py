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
					   port = 8889,              #I REMOVED THIS because I added what the prof had at the bottom of this file and that somehow solved my 3 hour problem
					   user = 'root',
					   password = 'root',
                       #password = '',
					   db = 'ticket_booking', # insert database name here 
					   charset = 'utf8mb4',
					   cursorclass = pymysql.cursors.DictCursor)
	
#PUBLIC VIEW
@app.route('/')
def public_search(): 
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
    if request.form.get('action') == 'login':
        username = request.form.get('username')
        password = request.form.get('password')
        cursor.execute("SELECT * FROM airline_staff WHERE username = %s", username)
        existing_staff = cursor.fetchone()
        if existing_staff:
            #print("EMAIL AND PASSWORD: ", username, password)
            cursor.execute("SELECT * FROM airline_staff WHERE username = %s AND password = md5(%s)", (username, password))
            existing_staff = cursor.fetchone()
            if existing_staff:
                cursor.close()
                session['username'] = username
                return render_template('airline_logged_in.html')
        error = "No existing staff for that combination of info. Please try again or register."
        return render_template('airline_login.html', error = error)
    else:
        username = request.form.get('username')
        airline = request.form.get('airline')
        password = request.form.get('pw')
        fn = request.form.get('first_name')
        ln = request.form.get('last_name')
        dob = request.form.get('dob')
        cursor.execute("SELECT * FROM airline_staff WHERE username = %s", username)
        existing_staff = cursor.fetchone()
        if existing_staff:
            cursor.close()
            error = "There is already a staff member with that username. Try using a different username."
            return render_template('airline_login.html', error = error)
        cursor.execute("SELECT md5(%s)", password)
        password = list(cursor.fetchone().values())[0]

        cursor = conn.cursor()
        cursor.execute("INSERT INTO airline_staff VALUES (%s, %s, %s, %s, %s, %s)", (username, airline, password, fn, ln, dob))
        cursor.close()
        print(cursor)
        return render_template('airline_logged_in.html')


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