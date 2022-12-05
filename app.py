import os
import pandas as pd
import plotly
import plotly.express as px
import json
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
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

    sales_graph, region_graph, commodity_graph = get_graphs()

    if name:
        return render_template('dashboard.html', name = name, 
        sales_graph = sales_graph,
        region_graph = region_graph, 
        commodity_graph = commodity_graph)
    else:
        return redirect(url_for('login'))

def get_graphs():
    sales = sales_graph()
    region = region_graph()
    commodity = commodity_graph()

    return sales, region, commodity

def sales_graph():
    sales_region = session.query(func.count(Transactions.SPEND), Transactions.YEAR, Transactions.STORE_R).\
        filter(Transactions.YEAR < 2021).\
        group_by(Transactions.YEAR, Transactions.STORE_R)

    sales_df = pd.read_sql(sales_region.statement.compile(engine), session.bind)
    
    sales_fig = px.bar(sales_df, x='YEAR', y='count_1', 
    color='STORE_R', barmode='group',
    labels = {
        "YEAR": "Year",
        "count_1": "Total Sales"
    })
    sales_fig.update_layout(title_text="Sales per Year", title_x=0.5)
    sales_graphJSON = json.dumps(sales_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return sales_graphJSON

def region_graph():
    households_region = session.query(func.count(Households.HSHD_NUM), Transactions.STORE_R).\
        join(Transactions, Transactions.HSHD_NUM == Households.HSHD_NUM).\
        group_by(Transactions.STORE_R)

    region_df = pd.read_sql(households_region.statement.compile(engine), session.bind)
    
    region_fig = px.bar(region_df, x='STORE_R', y='count_1',
    labels = {
        "STORE_R": "Store Region",
        "count_1": "Number of stores"
    })
    region_fig.update_traces(marker_color="#007bff")
    region_fig.update_layout(title_text="Stores per Division", title_x=0.5)
    region_graphJSON = json.dumps(region_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return region_graphJSON

def commodity_graph():
    households_commodity = session.query(func.count(Products.COMMODITY), Products.COMMODITY).\
        join(Transactions, Transactions.PRODUCT_NUM == Products.PRODUCT_NUM).\
        group_by(Products.COMMODITY)

    commodity_df = pd.read_sql(households_commodity.statement.compile(engine), session.bind)
    commodity_df.loc[commodity_df['count_1'] < 10000, 'COMMODITY'] = "Other Commodities"
    
    commodity_fig = px.pie(commodity_df, values='count_1', names='COMMODITY', width=1000, height=800)
    commodity_fig.update_layout(title_text="Commodity Purchase (%of Total Sales)", title_x=0.5)
    commodity_graphJSON = json.dumps(commodity_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return commodity_graphJSON

if __name__ == '__main__':
   app.run()
