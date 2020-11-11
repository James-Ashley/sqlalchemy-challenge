import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc, inspect

from flask import Flask, jsonify

import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

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
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    precip_value = {date:prcp for date, prcp in results}


    return jsonify(precip_value)

@app.route("/api/v1.0/stations")
def stats():
    session = Session(engine)

    results = session.query(Station.station).all()

    session.close()

    stats_list = list(np.ravel(results))

    return jsonify(stats_list)
    
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    latest_date_dt = dt.date(2017, 8, 23)
    
    year_ago = latest_date_dt - dt.timedelta(days=365)
    
    active = session.query(Measurement.station, func.count(Measurement.station)).\
                  group_by(Measurement.station).\
                  order_by(func.count(Measurement.station).desc()).all()

    top = active[0][0]

    tobs = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
                  filter(Measurement.date >= year_ago).\
                  filter(Measurement.station == top).all()
    
    session.close()

    return jsonify(tobs)

@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)

    weather = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    return jsonify(weather)

@app.route('/api/v1.0/<start>/<end>')
def startend(start, end):
    session = Session(engine)

    weather2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    return jsonify(weather2)

if __name__ == '__main__':
    app.run(debug=True)