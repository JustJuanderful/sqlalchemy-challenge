from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask
from flask import Flask, jsonify
app = Flask(__name__)

# Flask routes
@app.route("/")
# Home page
def welcome():
    '''List all available api routes.'''
    return (
        f"Surfs-up Brah! Let's get pitted!<br/>"
        f"Check out these routes:<br/>"
        f"/api/v1.0/precipitation<br/>JSON representation of precipitation dictionary.<br/>"
        f"/api/v1.0/stations<br/>JSON list of stations from the dataset.<br/>"
        f"/api/v1.0/tobs<br/>JSON list of temperature observations (TOBS) of the most active station for the last year of data.<br/>"
        f"/api/v1.0/temp/start/end<br/>JSON list of the minimum temperature, the average temperature, and the max temperature for all dates between the start and end dates.<br/>"
    )

# Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    '''JSON representation of precipitation dictionary.'''
    # Calculate the date 1 year ago from the last data point in the database
    last_data_point = session.query(Measurement.date,Measurement.prcp).order_by(Measurement.date.desc()).first()[0]
    year = str(dt.datetime.strptime(last_data_point,"%Y-%m-%d") - dt.timedelta(days=365))

    # Perform a query to retrieve the data and precipitation scores
    prcp_scores = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >=year, Measurement.date <=last_data_point).\
        order_by(Measurement.date).all()
    
    session.close()
    
    prcp_dict = {date: prcp for date, prcp in prcp_scores}
    return jsonify(prcp_dict)

# Stations
@app.route("/api/v1.0/stations")
def stations():
    '''Return a JSON list of stations from the dataset.'''
    results = session.query(Measurement.station).\
    	group_by(Measurement.station).all()

    session.close()

    #Convert list of tuples into normal list
    stations = list(np.ravel(results))
    return jsonify(stations)

# TOBS Route for Most Active Station
@app.route("/api/v1.0/tobs")
def most_tobs():
    '''Query the dates and temperature observations of the most active station for the last year of data.'''
    # Calculate the date 1 year ago from the last data point in the database
    last_data_point = session.query(Measurement.date,Measurement.prcp).order_by(Measurement.date.desc()).first()[0]
    year = str(dt.datetime.strptime(last_data_point,"%Y-%m-%d") - dt.timedelta(days=365))

    active_station = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >=year, Measurement.date <=last_data_point, Measurement.station == 'USC00519397').\
        order_by(Measurement.date).all()

    session.close()

    #Convert list of tuples into normal list
    most_tobs = list(np.ravel(active_station))
    return jsonify(most_tobs)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

# function usage example
print(calc_temps('2012-02-28', '2012-03-05'))

if __name__ == '__main__':
    app.run(debug=True)