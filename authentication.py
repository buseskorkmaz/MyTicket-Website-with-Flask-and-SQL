# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, url_for, request
from db_operations import *

app = Flask(__name__, static_url_path='', static_folder='static')

@app.route("/")
def hello():
    return 'Hello World!'

@app.route("/event",methods=['GET', 'POST'])
def event():
    event_id = request.args['event_id']
    event = get_event_from_db(event_id)
    if(event == 'Could not found'):
        return "Selected event is not available"
    else:
        #get event from db event_name, event_description, ticket_prices, place, location,time, total_basket 
        #event = ["event_name","image_link" ,"event_description", "ticket_prices", "place", "location","time", "total_basket"]
        print(event_id)
        print(event[1])
        if request.method == "POST":
            ticket_amount = request.form['ticket_amount']
            #sent data to basket
    return render_template('productpage.html',data=event)


@app.route("/myaccount",methods=['GET', 'POST'])
def myaccount():
    #event_name = request.args['event_name']
    #print(event_name)
    return "My Account Informations"


@app.route("/basket",methods=['GET', 'POST'])
def basket():
    #event_name = request.args['event_name']
    #print(event_name)
    return "My Basket Informations"


@app.route("/homepage",methods=['GET', 'POST'])
def homepage():
    error = None
    events = get_events_from_db()
    basket = 85
    if request.method == 'POST':
        event_id = request.form["event_id"] 
        return redirect(url_for("event",event_id=event_id))#encrypt it
    return render_template('tickets_for_events_with_dummy.html', error=error, data = events)

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        registered = check_auth_db(email,password)
        if(registered != 'Could not found'):
            return redirect(url_for('homepage'))
        else:
            error = "Check for credentials or register!"
      
    return render_template('signin.html', error=error)

# Route for handling the login page logic
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        try:
            email = request.form['email']
        except:
            return 'There is an error in email'
        try:
            password = request.form['password']
        except:
            return 'There is an error in password'
        
        try:
            repeatpasword = request.form['repeatpassword']
        except:
            return 'There is an error in password repeat'
        
        try:
             city = request.form['city']
        except:
            return 'There is an error in city'

        try:
            theaterFan = request.form.get('theater')
            if(theaterFan == "Yes"):
                theaterFan = True
            else:
                theaterFan = False
        except:
             return 'There is an error in theater'
         
        try:
            cinemaFan = request.form.get('cinema')
            if(cinemaFan == "Yes"):
                cinemaFan = True
            else:
                cinemaFan = False
        except:
             return 'There is an error in cinema'

        try:
            music = request.form.get("music")
            if music == "":
                music = None
        except:
             return 'There is an error in music'
        
        if(repeatpasword == password):
            success = register_to_db(email,password,city,theaterFan,cinemaFan,music)
            if(success):
                return redirect(url_for('login'))
            else:
                error = "Database error"
        else:
            error= "Passwords did not match"
    
    return render_template('register.html', error=error)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    