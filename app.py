import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

db = SQLAlchemy()
app = Flask(__name__)

DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=os.environ['DBUSER'],
    dbpass=os.environ['DBPASS'],
    dbhost=os.environ['DBHOST'],
    dbname=os.environ['DBNAME']
)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI

db = SQLAlchemy(app)
migrate = Migrate(app, db)
engine = db.create_engine(DATABASE_URI)
Session = sessionmaker(bind = engine)
session = Session()

from models import Households, Transactions, Products

@app.route('/')
def redirect_login():
    return redirect(url_for('login'))

@app.route('/login')
def login():
   return render_template('login.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/predictive_modeling')
def predictive_modeling():
    return render_template('predictive_modeling.html', name = name)


@app.route('/example_pull')
def example_pull():
    household_10 = session.query(Households, Transactions, Products).\
        join(Transactions, Transactions.HSHD_NUM == Households.HSHD_NUM).\
        join(Products, Products.PRODUCT_NUM == Transactions.PRODUCT_NUM).\
        filter(Households.HSHD_NUM == 10).all()

    return render_template('example_pull.html', name = name, households = household_10)  

@app.route('/search_input', methods=['GET', 'POST'])
def search_input():
    return render_template('search_input.html', name = name, hhs = hhs)

@app.route('/search_pull', methods=['GET', 'POST'])
def search_pull():
    selected_num = request.form['hh']

    household_search = session.query(Households, Transactions, Products).\
        join(Transactions, Transactions.HSHD_NUM == Households.HSHD_NUM).\
        join(Products, Products.PRODUCT_NUM == Transactions.PRODUCT_NUM).\
        filter(Households.HSHD_NUM == selected_num).all()

    return render_template('search_pull.html', name = name, households = household_search, hhs = hhs, selected_num = selected_num)  

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    global name
    global hhs
    hhst = session.query(Households.HSHD_NUM).order_by(Households.HSHD_NUM).all()
    i = 0
    hhs = [item[i] for item in hhst]

    if request.method == 'POST':
        name = request.form.get('name') 

    if name:
        return render_template('dashboard.html', name = name)
    elif "dashboard" in request.url:
        return render_template('dashboard.html', name = "user")
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
   app.run()
