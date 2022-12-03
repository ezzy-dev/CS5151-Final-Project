import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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

from models import Households

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

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
   global name
   if request.method == 'POST':
      name = request.form.get('name') 

   households = Households.query.all()     

   if name:
       return render_template('dashboard.html', name = name, households = households)
   elif "dashboard" in request.url:
       print("test")
       return render_template('dashboard.html', name = name, households = households)
   else:
       return redirect(url_for('login'))


if __name__ == '__main__':
   app.run()