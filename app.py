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
   
    <a href="/api/v1.0/2017-01-01">/api/v1.0/2017-01-01 </a> 
    <br>

    <a href="/api/v1.0/2017-01-10/2017-01-20">/api/v1.0/2017-01-10/2017-01-20 </a> 
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
    """Return a JSON list of All Stataions and their Names."""
    session = Session(engine)
    #Query for all stations
    all_stations =  session.query(Station.station, Station.name ).all()
    session.close()
    #Putting in a Dictionary
    station_dict = []
    for station, name in all_stations:
        st= {}
        st["station"] = station
        st["name"]= name
        station_dict.append(st)
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
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    trip= session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).group_by(Measurement.date).all()
    session.close()
    
    #Getting results from query into a list
    start_list = []
    for start_dates in trip:
        st={}
        st["Date"] = start_dates[0]
        st["Min Temp"] = start_dates[1]
        st["Avg Temp"]= start_dates[2]
        st["Max Temp"]= start_dates[3]
        start_list.append(st)
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    """Return a JSON list of calculations of calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date"""
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    
    session = Session(engine)
    
    #query for the whole trip duration and alculations for min, max, avg for the whole duration. 
    dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).group_by(Measurement.date).all()
    
    session.close()
    # Create a list to hold results
    dates_list = []
    for date in dates:
        l = {}
        l["Date"] = date[0]
        l["MIN Temp"] = date[1]
        l["Avg Temp"] = date[2]
        l["Max Temp"] = date[3]
        dates_list.append(l)

    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    
    return jsonify(dates_list)

if __name__ == '__main__':
    app.run(debug=True)