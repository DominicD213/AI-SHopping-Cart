from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import json
import os

load_dotenv()

app = Flask("__name__")
app.secret_key = os.getenv('SECRET_KEY')

# =========== Database connection ================

app.config["MYSQL_HOST"] = os.getenv('MYSQL_HOST')
app.config["MYSQL_USER"] = os.getenv('MYSQL_USER')
app.config["MYSQL_PASSWORD"] = os.getenv('MYSQL_PASSWORD')
app.config["MYSQL_DB"] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

# =================================================

@app.route("/")
def home():
    with open('products.json') as f:
        items = json.load(f)
        if 'username' in session:
            return render_template('html/home.html', username=session['username'],items = items)
        else:
            return render_template('html/home.html', items = items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        pwd = request.form['password_hash']
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT username, password_hash from User where username = '{username}'")
        user = cur.fetchone()
        cur.close()

        if user and pwd == user[1]:
            session['username'] = user[0]
            return redirect(url_for('home'))
        else:
            return render_template('html/login.html', error='invalid username or password')
    return render_template('html/login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(f"insert into User (username, password_hash) VALUES ('{username}', '{pwd}')")
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))
    
    render_template('html/register.html')

    return render_template('html/register.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)

