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

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# Define the homepage route
@app.route("/")
def homepage():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# Define the route for precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data."""
    # Calculate the date one year ago from the last date in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - timedelta(days=365)

    # Query precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
              filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

# Define the route for stations data
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    # Query stations
    results = session.query(Station.station).all()

    # Convert the query results to a list
    station_list = [station for station, in results]

    return jsonify(station_list)

# Define the route for temperature observations data
@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations for the previous year."""
    # Find the most active station
    most_active_station = session.query(Measurement.station).\
                          group_by(Measurement.station).\
                          order_by(desc(func.count(Measurement.station))).first()[0]

    # Calculate the date one year ago from the last date in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - timedelta(days=365)

    # Query temperature observations for the previous year
    results = session.query(Measurement.date, Measurement.tobs).\
              filter(Measurement.station == most_active_station).\
              filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a list of dictionaries
    tobs_data = [{"Date": date, "Temperature": tobs} for date, tobs in results]

    return jsonify(tobs_data)

# Define the route for temperature statistics based on start date
@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    """Return the minimum, average, and maximum temperatures for a specified start date."""
    # Query temperature statistics
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).all()

    # Convert the query results to a dictionary
    temp_stats = {"Minimum Temperature": results[0][0],
                  "Average Temperature": results[0][1],
                  "Maximum Temperature": results[0][2]}

    return jsonify(temp_stats)

# Define the route for temperature statistics based on start and end date
@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end(start, end):
    """Return the minimum, average, and maximum temperatures for a specified start and end date."""
    # Query temperature statistics
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).\
              filter(Measurement.date <= end).all()

    # Convert the query results to a dictionary
    temp_stats = {"Minimum Temperature": results[0][0],
                  "Average Temperature": results[0][1],
                  "Maximum Temperature": results[0][2]}

    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)