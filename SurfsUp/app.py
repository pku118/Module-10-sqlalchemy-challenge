# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import func, create_engine
from datetime import datetime, timedelta
from sqlalchemy.ext.automap import automap_base
from flask import Flask, jsonify
from sqlalchemy import create_engine, func, inspect, desc
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime, timedelta


# Create an app instance
app = Flask(__name__)

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################



#################################################
# Flask Routes
#################################################
# Define the homepage route
@app.route("/")
def landing_page():
    """Display available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return JSON with date as key and precipitation as value for the last year."""
    # Calculate the date one year ago
    last_year = datetime.now() - timedelta(days=365)
    
    # Query precipitation data for the last year
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()
    
    # Convert query results to dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_data)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return JSON data of all stations."""
    # Query all stations
    results = session.query(Station.station).all()
    
    # Convert query results to list
    stations_list = [station for station, in results]
    
    return jsonify(stations_list)

# Tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    """Return JSON data for the most active station (USC00519281) for the last year of data."""
    # Query the most active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count().desc()).first()[0]
    
    # Calculate the date one year ago
    last_year = datetime.now() - timedelta(days=365)
    
    # Query temperature observations for the most active station for the last year
    results = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == most_active_station).\
                filter(Measurement.date >= last_year).all()
    
    # Convert query results to list of dictionaries
    tobs_data = [{'Date': date, 'Temperature': tobs} for date, tobs in results]
    
    return jsonify(tobs_data)

# Start route
@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    """Return JSON data of min, max, and average temperatures from the start date to the end of the dataset."""
    # Query temperature statistics for dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    
    # Convert query results to dictionary
    temp_stats = {'Minimum Temperature': results[0][0],
                  'Average Temperature': results[0][1],
                  'Maximum Temperature': results[0][2]}
    
    return jsonify(temp_stats)

# Start/end route
@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end(start, end):
    """Return JSON data of min, max, and average temperatures from the start date to the end date."""
    # Query temperature statistics for dates between the start and end dates
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Convert query results to dictionary
    temp_stats = {'Minimum Temperature': results[0][0],
                  'Average Temperature': results[0][1],
                  'Maximum Temperature': results[0][2]}
    
    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)