from flask import Flask, session, render_template, redirect, url_for, request, flash, Blueprint
import sqlite3
import random
import string
from jinja2 import StrictUndefined
import mysql.connector

app = Flask('app')
app.secret_key = "CHANGE ME"
app.jinja_env.undefined = StrictUndefined



###########################################################################################################################

@app.route('/', methods=['GET', 'POST'])
def login():
 session.clear()
  


 if request.method == "GET":
    return render_template("login.html")

 if request.method == "POST":
    uname = (request.form["username"])
    password = (request.form["password"])
    cursor.execute("SELECT username, password, email, type, uID FROM user WHERE username = %s and password = %s", (uname,password))
    data = cursor.fetchone()
    
  
 if data != None :
    session['username'] = uname
    session['email'] = data['email']
    session['type'] = data['type']
    session['uID'] = data['uID']
    return redirect(url_for("home"))
 else:
    flash("Incorrect username or password")
    return render_template("login.html")

#############################################################################################################################################################################################



@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['username']
        password = request.form['password']
        email = request.form['email']
       

        if not userName or not password or not email:
            flash('Please fill out all the fields!')
            return render_template('signup.html')   
        else:
            
            cursor.execute('SELECT * FROM user WHERE email = %s OR userName = %s', (email, userName,))
            account = cursor.fetchone()
            if account:
                if userName in account :
                  flash('Username already in use')
                  return render_template('signup.html')
                else:
                  flash("Account already in use")
                  return render_template('signup.html')
            else:
                cursor.execute('INSERT INTO user  (username, password, email, type) VALUES (%s, %s, %s, %s)', (userName, password, email, 'applicant'))
                mydatabase.commit()
                flash("You have successfully registered! Please login now")
                return render_template('login.html')
    elif request.method == 'POST':
        flash("Please fill out all the fields!")
    return render_template('signup.html')


#if __name__ == "__main__":
#  app.run(debug=True)






app.run(host='0.0.0.0', port=8080)