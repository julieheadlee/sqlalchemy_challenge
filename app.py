import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine=engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #get last date
    precip = session.query(Measurement).order_by(Measurement.date.desc()).first()

    last_date = precip.date
    
    # Calculate the date 1 year ago from the last data point in the database
    date_obj = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_obj = date_obj.replace(year=date_obj.year-1)

    # Perform a query to retrieve the data and precipitation scores
    precip_scores = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_obj).all()  
    # Query all prcp values the query results to a dictionary using date as the key and prcp as the value.
    
    all_precip = []
    for row in precip_scores:
        precip_dict = {}
        precip_dict[row.date] = row.prcp
        all_precip.append(precip_dict)
    session.close()

    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data and precipitation scores
    stations = session.query(Station.station, Station.name)
        
    all_stations = []
    for row in stations:
        station_dict = {}
        station_dict[row.station] = row.name
        all_stations.append(station_dict)
    session.close()

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #get last date
    precip = session.query(Measurement).order_by(Measurement.date.desc()).first()
    last_date = precip.date
    
    # Calculate the date 1 year ago from the last data point in the database
    date_obj = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_obj = date_obj.replace(year=date_obj.year-1)

    # Perform a query to retrieve the data and precipitation scores
    tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= one_year_obj).\
        filter(Measurement.station == 'USC00519281').all()  
        
    all_tobs = []
    for row in tobs:
        tobs_dict = {}
        tobs_dict[row.date] = row.tobs
        all_tobs.append(tobs_dict)
    session.close()

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def startdate(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #temps = calc_temps(start, dt.date.today().strftime('%Y-%m-%d'))
    min_temp = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= dt.date.today().strftime('%Y-%m-%d')).all()   
    max_temp = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= dt.date.today().strftime('%Y-%m-%d')).all()   
    avg_temp = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= dt.date.today().strftime('%Y-%m-%d')).all()   
    
    # construct string
    return(f"Min temp: {min_temp}  Max temp: {max_temp}  Average temp: {avg_temp}")

@app.route("/api/v1.0/<start> <end>")
def startenddate(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #temps = calc_temps(start, dt.date.today().strftime('%Y-%m-%d'))
    min_temp = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()   
    max_temp = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()   
    avg_temp = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()   
    
    # construct string
    return(f"Min temp: {min_temp}  Max temp: {max_temp}  Average temp: {avg_temp}")

# def calc_temps(start_date, end_date):
#     """TMIN, TAVG, and TMAX for a list of dates.
    
#     Args:
#         start_date (string): A date string in the format %Y-%m-%d
#         end_date (string): A date string in the format %Y-%m-%d
        
#     Returns:
#         TMIN, TAVE, and TMAX
#     """
    
#     return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
#         filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

if __name__ == '__main__':
    app.run(debug=True)
