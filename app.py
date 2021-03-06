from flask import Flask, jsonify

import numpy as np
import pandas as pd

import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Set up DB connection
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# Set up flask
app = Flask(__name__)

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

@app.route("/")
def homepage():
    """List available routes on homepage"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        #f"/api/v1.0/&lt;start&gt;<br/>"
        #f"/api/v1.0/&lt;start&gt/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    format_str = "%Y-%m-%d"
    latest_date = dt.datetime.strptime(latest_date[0], format_str)
    year_ago = latest_date - dt.timedelta(days=365)
    
    precip = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago.strftime(format_str))

    df = pd.read_sql(precip.statement, engine).set_index("date")
    
    return jsonify(df.to_dict()['prcp'])

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station)
    df = pd.read_sql(stations.statement, engine)
    return(jsonify(df.to_dict(orient="records")))

@app.route("/api/v1.0/tobs")
def tobs():
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    format_str = "%Y-%m-%d"
    latest_date = dt.datetime.strptime(latest_date[0], format_str)
    year_ago = latest_date - dt.timedelta(days=365)

    tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= year_ago.strftime(format_str))

    df = pd.read_sql(tobs.statement, engine)

    return(jsonify(df.to_dict(orient="records")))

@app.route("/api/v1.0/<start>")
def from_date(start):
    """<start> should a date formatted as yyyy-mm-dd"""
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    format_str = "%Y-%m-%d"
    latest_date = dt.datetime.strptime(latest_date[0], format_str)

    tmax, tavg, tmin = calc_temps(start, latest_date)[0]

    temp_dict = {
        'tmax': tmax,
        'tavg': tavg,
        'tmin': tmin
    }

    return(jsonify(temp_dict))

@app.route("/api/v1.0/<start>/<end>")
def from_to_date(start, end):
    tmax, tavg, tmin = calc_temps(start, end)[0]

    temp_dict = {
        'tmax': tmax,
        'tavg': tavg,
        'tmin': tmin
    }

    return(jsonify(temp_dict))

if __name__ == '__main__':
    app.run(debug=True)

