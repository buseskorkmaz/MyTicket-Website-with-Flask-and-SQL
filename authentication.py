# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, url_for, request, make_response, jsonify
from db_operations import *
from flask import session
from functools import wraps
import jwt
from passlib.context import CryptContext
import datetime

pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
)

app = Flask(__name__, static_url_path='', static_folder='static')
app.config['SECRET_KEY'] = 'thisisthesecretkey'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        try:
            token = session['api_session_token']
        
        except:
            return redirect(url_for("login"))

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated

@app.route("/")
def hello():
    return 'Hello World!'

@app.route('/logout')
@token_required
def logout():
    session['api_session_token'] = ''
    return redirect(url_for("login"))

@app.route("/event",methods=['GET', 'POST'])
@token_required
def event():        
    event_id = request.args['event_id']
    event = get_event_from_db(event_id)
    data = jwt.decode(session['api_session_token'], app.config['SECRET_KEY'])
    email = data['user']
    basket = get_current_basket_amount(email)
    event.append(basket)
    if(event == 'Could not found'):
        return "Selected event is not available"
    else:
        #get event from db event_name, event_description, ticket_prices, place, location,time, total_basket 
        #event = ["event_name","image_link" ,"event_description", "ticket_prices", "place", "location","time", "total_basket"]
        #print(event_id)
        #print(event[1])
        if request.method == "POST":
            data = jwt.decode(session['api_session_token'], app.config['SECRET_KEY'])
            email = data['user']
            ticket_amount = request.form['ticket_amount']
            basket = get_current_basket_amount(email)
            event.append(basket)
            print(add_basket(event_id,ticket_amount,email))
    return render_template('productpage.html',data=event)


@app.route("/myaccount",methods=['GET', 'POST'])
@token_required
def myaccount():
    data = jwt.decode(session['api_session_token'], app.config['SECRET_KEY'])
    email = data['user']
    user_info = get_userinfo_from_db(email)
    error = None
    if(user_info != 'Could not found'):
        user_info = [get_current_basket_amount(email), email] + list(user_info)
        for i in range(len(user_info)):
            if user_info[i] == False:
                user_info[i] = 'No'
            elif user_info[i] == True:
                user_info[i] = 'Yes'
    else:
        error = 'Something goes wrong.'
    return render_template('myaccount.html', data=user_info, error=error)


@app.route("/basket",methods=['GET', 'POST'])
@token_required
def basket():
    try:
        basket_id = request.form['basket_id']
        print("basket_id is "+basket_id)
        print(delete_basket(basket_id))
    except:
        pass
    error = None
    data = jwt.decode(session['api_session_token'], app.config['SECRET_KEY'])
    email = data['user']
    baskets = get_basket_list_from_db(email)
    print(baskets)
    total= 0
    for i in range(len(baskets)):
        total+= baskets[i][3]
    return render_template('basketpage.html', data=[baskets,total])


@app.route("/homepage",methods=['GET', 'POST'])
@token_required
def homepage():
    error = None
    events = get_events_from_db()
    data = jwt.decode(session['api_session_token'], app.config['SECRET_KEY'])
    email = data['user']
    basket = get_current_basket_amount(email)
    events[0].append(basket)
    if request.method == 'POST':
        event_id = request.form["event_id"] 
        return redirect(url_for("event",event_id=event_id))#encrypt it
    return render_template('tickets_for_events_with_dummy.html', error=error, data = events)


@app.route("/login", methods=["GET", "POST"])
def login():

    payload = {"email": request.form.get('email'), "password": request.form.get('password')}
   
    #login to web service
    email = payload["email"]
    password = payload["password"]
    registered = check_auth_db(email,password)
    if(registered != 'Could not found'):
        token = jwt.encode({'user': email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, key=app.config['SECRET_KEY'])
        print(token)    
        # Put it in the session
        session['api_session_token'] = token
        return redirect(url_for('homepage'))
    error = 'Please enter correct credentials.'
    
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
            isadmin = False
            if( email == 'admin'):
                isadmin = True
            success = register_to_db(email,password,city,theaterFan,cinemaFan,music,isadmin)

            if(success==True):
                return redirect(url_for('login'))
            else:
                error = "Database error"
        else:
            error= "Passwords did not match"
    
    return render_template('register.html', error=error)

@app.route('/addevent', methods=['GET', 'POST'])
def addevent():
    title = request.form["title"]
    description = request.form["description"]
    date = request.form["date"]
    price = request.form["price"]
    place = request.form["place"]
    event_type = request.form["event_type"]
    if(add_event_to_db(title, description, date, price, place, event_type)):
        print('Success')
        return render_template('addevent.html')
    else:
        print('Error')
        return render_template('addevent.html')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0')
  