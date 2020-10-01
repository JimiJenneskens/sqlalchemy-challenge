from flask import Flask, json, jsonify
import datetime as dt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import inspect

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

app = Flask(__name__)

# List all routes that are available.
@app.route("/")
def welcome():
    session = Session(engine)
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date/"
    )

# Return the JSON representation of your dictionary
@app.route('/api/v1.0/precipitation/')
def precipitation():
    session = Session(engine)
    #find last date in database from Measurements 
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    #convert last date string to date
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")

    #calculate date one year after last date using timedelta datetime function
    first_date = last_date - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    last_year_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= first_date).all()

    return jsonify(last_year_data)

# Return a JSON-list of stations from the dataset.
@app.route('/api/v1.0/stations/')
def stations():
    session = Session(engine)
    stations = session.query(Station.station).all()
    
    return jsonify(stations)


# Return a JSON-list of Temperature Observations from the dataset.
@app.route('/api/v1.0/tobs/')
def tobs():
    session = Session(engine)
    stations = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    most_active_station = stations[0][0]
    station_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).all()
    station_data = list(np.ravel(station_data))

    return jsonify(station_data)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date
@app.route('/api/v1.0/<start_date>/')
def calc_temps_start(start_date):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date > start_date).all()
    temps = list(np.ravel(results))

    return jsonify(temps)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.
@app.route('/api/v1.0/<start_date>/<end_date>/')
def calc_temps_start_end(start_date, end_date):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == "__main__":
    app.run(debug=True)