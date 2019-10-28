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
    <center>
    <h2>List of Available APIs</h2>
    </center>
    <br>
    <br>
    
    <a href="/api/v1.0/precipitation">/api/v1.0/precipitation </a> 
    
    <br>
    <br>
   <a href="/api/v1.0/stations">/api/v1.0/stations </a>
   
    <br>
    <br>
  
    <a href="/api/v1.0/tobs">/api/v1.0/tobs </a>
    <br>
    <br>
   
    <a href="/api/v1.0/2017-01-01">/api/v1.0/2017-01-01 </a> <h5>All dates greater than the start Date of the trip (date, minimum Temp, Avg Tempeerature, Maximum Temperature)</h5>
    <br>

    <a href="/api/v1.0/2017-01-10/2017-01-20">/api/v1.0/2017-01-10/2017-01-20 </a> <h5>Trip Duration (dates, minimum Temperature, Avg Temperature, Maximum Temperature)</h5>
    
    </html> """

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of Precepitation""" 
    session = Session(engine)
   
    # Query for Prcp and Dates
    prcp_query = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    # Convert list of tuples into normal list
    precipitation_dict = []
    for date, prcp in prcp_query:
        prcp_list = {}
        prcp_list['date']=date
        prcp_list['prcp']=prcp
        precipitation_dict.append(prcp_list)
    
    #Returning Json Dictionary
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations(): 
    session = Session(engine)
    #Query for all stations
    all_stations =  session.query(Measurement.station).group_by(Measurement.station).all()
    stations_list = list(np.ravel(all_stations))
    #Putting in a Dictionary
    station_dict = []
    for stations in stations_list:
        station= {}
        station["station"] = stations
        station_dict.append(station)
    #Returning a JSON list of stations from the dataset.
    return jsonify(station_dict)


@app.route("/api/v1.0/tobs")
def tobs(): 
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    session = Session(engine)
    #calculating tobs
    Twelve_mon = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    tobss = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= Twelve_mon).all()
    tobs_list = []
    for date, tobs in tobss:
        temp = {}
        temp["Date"]=date
        temp["temperature"]= tobs
        tobs_list.append(temp)
    #Return a JSON list of Temperature Observations (tobs) for the previous year.
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")  
def start(start=None):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""
    session = Session(engine)
    #query for the first day of trip and calculations for min, max, avg according to dates
    start= session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
   
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    return jsonify(start)

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