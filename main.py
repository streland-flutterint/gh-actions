# Import required modules
from flask import Flask, request, jsonify, render_template
import sqlite3
from contextlib import closing
import pandas as pd
import logging

# Initialize Flask app and configure logging
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Database setup
DATABASE = 'example.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with closing(get_db_connection()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_first_request
def initialize():
    init_db()

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data', methods=['GET', 'POST'])
def data_operations():
    if request.method == 'POST':
        # Example POST operation: Add new data
        data = request.json
        try:
            with closing(get_db_connection()) as db:
                db.execute('INSERT INTO data (name, value) VALUES (?, ?)', (data['name'], data['value']))
                db.commit()
            return jsonify({"success": True, "message": "Data added successfully"}), 201
        except Exception as e:
            logging.error(f"Error adding data: {e}")
            return jsonify({"success": False, "message": "Error adding data"}), 500
    else:
        # Example GET operation: Fetch data and return as JSON
        with closing(get_db_connection()) as db:
            data = db.execute('SELECT * FROM data').fetchall()
            data_list = [dict(row) for row in data]
        return jsonify(data_list)

@app.route('/analyze', methods=['GET'])
def analyze_data():
    with closing(get_db_connection()) as db:
        data = pd.read_sql_query('SELECT * FROM data', db)
        # Example data manipulation with Pandas
        analysis_result = data['value'].describe()
    return jsonify(analysis_result.to_dict())

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Page not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
