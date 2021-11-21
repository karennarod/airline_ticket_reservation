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
					   port = 8889,
					   user = 'root',
					   password = 'root',
					   db = 'ticket_booking', # insert database name here 
					   charset = 'utf8mb4',
					   cursorclass = pymysql.cursors.DictCursor)
	
#PUBLIC VIEW
@app.route('/')
def public_search(): 
    return render_template("public_search.html")

@app.route('/public_view', methods = ["GET", "POST"])
def public_view(): 
    #today = str(date.today())
    #print(today)

    query = "SELECT * FROM flight WHERE departure_date >= '11-20-2021'"
    
    queries = []
    departure_date = request.form.get('departure_date')
    arrival_date = request.form.get('arrival_date')
    #departure_city = request.form.get('departure_city')
    #arrival_city = request.form.get('arrival_city')
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
    if queries:
        query += " AND " + " AND ".join(queries)
    print(query) 


    #execute queries from database
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    
    cursor.close()
    return render_template('public_view.html', data=data)

