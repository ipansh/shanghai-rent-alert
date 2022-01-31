import os
from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://sqwmtyaiabsiff:7ecca47616bef71798632076ef45a52d3fba58691acbda0766f04bdd87d0155e@ec2-3-222-49-168.compute-1.amazonaws.com:5432/dcr89i9f2cnh2l'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'mysecretkey'

db = SQLAlchemy(app)

# Create our database model
class TestTable(db.Model):
    __tablename__ = "test_table"
    listing_id = db.Column(db.Integer, primary_key=True)
    added_time = db.Column(db.DateTime, unique=False)

    def __init__(self, listing_id, added_time):
        self.listing_id = listing_id
        self.ticker = added_time

    def __repr__(self):
        return '<Listing Id %r>' % self.listing_id

@app.route("/")
def home():

    db.create_all()

    return 'Hello!'

if __name__  == '__main__': 
    app.run(debug=True)