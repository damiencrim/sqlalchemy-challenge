# Import the dependencies.
import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify 


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references 
station = Base.classes.station
measurement = Base.classes.measurement
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# Create base route

@app.route("/")
def welcome():
    """ List all available api routes"""
    return(
        f"Available Routes for Hawaii Weather:<br/><br>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )



# #  Create route to query precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    """ Return Precipitation Totals"""
    prcp_data = session.query(measurement.date, measurement.prcp).all()

    session.close()
    
    prcp_list = []
    for date, prcp in prcp_data:
        prcp_dict={}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)
    
    
    # Jsonify Results  
    return jsonify(prcp_list)
    

# Create route to query stations
@app.route("/api/v1.0/stations") 
def stations():
    session = Session(engine)
    
    station_results = session.query(station.station, station.id).all()
    
    session.close()
    
    
    #Return a list of the Stations 
    station_totals = []
    for station, id in station_results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["id"] = id
        station_totals.append(station_dict)
    
    return jsonify (station_totals)


    
    
# Create route to query tobs
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    endstr = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    enddate = dt.datetime.strptime(endstr, '%Y-%m-%d')
    query = dt.date(enddate.year -1, enddate.month, enddate.day)
    sel = [measurement.date, measurement.tobs]
    query = session.query(*sel).filter(measurement.date >= query).all()
    
    session.close()
#  Query and return Observed Temp Data
    tobsall = []
    for date,tobs in query:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

#  Create route to query Start 
@app.route('/api/v1.0/<start>') 
def start(start):
    session = Session(engine)
    start_date = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    
    session.close()
    
    start_date = []
    for min, avg, max in start_date:
        start_date_dict = {}
        start_date_dict["Min"] = min
        start_date_dict["Average"] = avg
        start_date_dict["Max"] = max
        start_date.append(start_date_dict)
        
    return jsonify(start_date)
    
# Create route to query start/end
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    
    start_end_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()


    session.close()
#  Create and append list to store Observed Data
    start_end_results = []
    for min, avg, max in start_end_results:
        start_end_dict = {}
        start_end_dict["Min Temp"] = min
        start_end_dict["Avg Temp"] = avg
        start_end_dict["Max Temp"] = max
        
        start_end_results.append(start_end_dict)
        
        
        
        
        
if __name__ == "__main__":
    app.run(debug=True)

    
