# 1. import Flask
import numpy as np

import sqlalchemy
import json
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify
import datetime as dt

#  Create an app, being sure to pass __name__
app = Flask(__name__)
# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)

Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# 3. Define what to do when a user hits the index route
@app.route("/")
def welcome():
    #using HTML for pretty layout
    """List all available api routes."""
    return"""<html>
    <h2>List of Available APIs</h2>
    
    <br>
    <br>
  
    <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a>
   
    <br>
    <br>
   <a href="/api/v1.0/stations">/api/v1.0/stations</a>
   
    <br>
    <br>
    <a href="/api/v1.0/tobs">/api/v1.0/tobs</a>
    <br>
    <br>
    <a href="/api/v1.0/2017-01-01">/api/v1.0/2017-01-01</a>
    <br>
    <br>
    <a href="/api/v1.0/2017-01-10/2017-01-20">/api/v1.0/2017-01-10/2017-01-20</a>
    </html> """

@app.route("/precipitation")
def precipitation():
    """Return a list of Precepitation""" 
    session = Session(engine)
    # Query for Prcp and Dates
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_date[0]
    Twelve_mon = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=366)
    pres = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > Twelve_mon).all()
    
    # Convert list of tuples into normal list
    precipitation_dict = dict(pres)
    #Returning Json Dict
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations(): 
    session = Session(engine)
    #Query for all stations
    all_stations =  session.query(Measurement.station).group_by(Measurement.station).all()
    stations_list = list(np.ravel(all_stations))
    #Returning a JSON list of stations from the dataset.
    return jsonify(stations_list)
@app.route("/api/v1.0/tobs")
def tobs(): 
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    session = Session(engine)
    #Query calculating the tobs
    Twelve_mon = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    tobss = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= Twelve_mon).all()
    tobs_list = list(tobss)
    #Return a JSON list of Temperature Observations (tobs) for the previous year.
    return jsonify(tobs_list)
@app.route("/api/v1.0/<start>")  
def start(start=None):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""
    session = Session(engine)
    #query for the first day of trip and calculations for min, max, avg according to dates
    start= session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    start_list=list(start)
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    return jsonify(start_list)
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    """Return a JSON list of calculations of calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date"""
    session = Session(engine)
    #query for the whole trip duration and alculations for min, max, avg for the whole duration. 
    dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    dates_list = list(dates)
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    return jsonify(dates_list)

if __name__ == '__main__':
    app.run(debug=True)