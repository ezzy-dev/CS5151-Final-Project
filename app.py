import os
import csv
import time
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from werkzeug.utils import secure_filename

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

relative_path = os.path.dirname(__file__)

hfile_path = relative_path + '\\data\\400_households.csv'
pfile_path = relative_path + '\\data\\400_products.csv'
tfile_path = relative_path + '\\data\\400_transactions.csv'

app.config['UPLOAD_EXTENSIONS'] = ['.csv']
app.config['UPLOAD_FOLDER'] = relative_path + '\\uploads'

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

@app.route('/upload')
def upload():
    return render_template('upload.html', name = name)
	
@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        f = request.files['file']
        newFileName = fileNameAppend(secure_filename(f.filename))
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(newFileName)))
        tableString = readNewCSVData(app.config['UPLOAD_FOLDER'] + '\\' + secure_filename(newFileName))
    return render_template('uploaded.html', name = name, tableString = tableString)

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

def readNewCSVData(file_path):
    with open(file_path, 'r') as f:
        csv_reader = csv.reader(f)
        i = 0
        tableType = 0
        readSuccess = False #if header matches
        rows = []
        for line in csv_reader:

            #set table type by reading first header in first line
            if i == 0 and line[0].lower() == 'hshd_num': #households
                tableType = 1
                readSuccess = True
            elif i == 0 and line[0].lower() == 'basket_num': #transactions
                tableType = 2
                readSuccess = True
            elif i == 0 and line[0].lower() == 'product_num': #products
                tableType = 3
                readSuccess = True

            if readSuccess == True:
                if i > 0:
                    rows.append(line)
            i += 1

        if readSuccess == True and len(rows) > 0:
            returnMessage = writeNewCSVData(tableType, rows)
            tableString = ''
            if returnMessage == 1:
                tableString = 'Households'
            elif returnMessage == 2:
                tableString = 'Transactions'
            elif returnMessage == 3:
                tableString = 'Products'
            return('Updated table "'+tableString+'"')
        else:
            return('Error in reading CSV file, headers do not meet expectation')

def writeNewCSVData(tableType, rows):
    newRows = []

    if tableType == 1: #households
        for row in rows:
            print(row)
            newRow = Households(HSHD_NUM = row[0], L = boolFix(row[1]), AGE_RANGE = row[2], MARITAL = row[3], INCOME_RANGE = row[4], HOMEOWNER = row[5], HSHD_COMPOSITION = row[6], HH_SIZE = row[7], CHILDREN = row[8])
            newRows.append(newRow)
    elif tableType == 2: #transactions
        for row in rows:
            newRow = Transactions(BASKET_NUM = row[0], HSHD_NUM = row[1], PURCHASE = row[2], PRODUCT_NUM = row[3], SPEND = row[4], UNITS = row[5], STORE_R = row[6], WEEK_NUM = row[7], YEAR = row[8])
            newRows.append(newRow)
    elif tableType == 3: #products
        for row in rows:
            newRow = Products(PRODUCT_NUM = row[0], DEPARTMENT = row[1], COMMODITY = row[2], BRAND_TY = row[3], NATURAL_ORGANIC_FLAG = row[4])
            newRows.append(newRow)

    for newRow in newRows:
        session.add(newRow)

    session.commit()

    return tableType

def fileNameAppend(filename):
    name, ext = os.path.splitext(filename)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    return "{name}_{id}{ext}".format(name=name, id=timestr, ext=ext)

def boolFix(obj):
    if obj == 'TRUE' or '1':
        return True
    else:
        return False

if __name__ == '__main__':
   app.run()
