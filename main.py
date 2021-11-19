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
@app.route('/', methods = ["GET", "POST"])
def public_view(): 
    #today = str(date.today())
    #print(today)
    query = 'SELECT * FROM flight WHERE departure_date >= "11-19-2021"'
    
    queries = []
    departure_date = request.form.get('departure_date')
    print(departure_date)
    arrival_date = request.form.get('arrival_date')
    print(arrival_date)
    departure_city = request.form.get('departure_city')
    arrival_city = request.form.get('arrival_city')
    departure_airport = request.form.get('departure_airport')
    print(departure_airport)
    arrival_airport = request.form.get('arrival_airport')
    print(arrival_airport)

    #execute queries from database
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    print(data)
    cursor.close()
    return render_template('public_view.html', data=data)

