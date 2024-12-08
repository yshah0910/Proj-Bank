import os
from flask import Flask, request, jsonify
import oracledb
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

hostname = 'prophet.njit.edu'  
port = '1521'  
sid = 'course'  
username = os.getenv('ORACLE_DB_USERNAME')
password = os.getenv('ORACLE_DB_PASSWORD')

dsn = oracledb.makedsn(hostname, port, sid=sid)

connection = oracledb.connect(user=username, password=password, dsn=dsn)

@app.route('/api/tables', methods=['GET'])
def get_tables():
    cursor = connection.cursor()
    cursor.execute("SELECT table_name FROM all_tables WHERE owner = :owner", [username.upper()])
    tables = cursor.fetchall()
    cursor.close()
    return jsonify(tables)

@app.route('/api/columns/<table_name>', methods=['GET'])
def get_columns(table_name):
    cursor = connection.cursor()
    query = f"SELECT column_name FROM all_tab_columns WHERE table_name = :table_name"
    cursor.execute(query, {'table_name': table_name.upper()})
    columns = cursor.fetchall()
    cursor.close()
    return jsonify([col[0] for col in columns])

@app.route('/api/rows/<table_name>', methods=['GET'])
def get_rows(table_name):
    cursor = connection.cursor()
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    print("Rows fetched:", rows)  # Add this line to log the rows
    return jsonify(rows)

@app.route('/api/insert_row/<table_name>', methods=['POST'])
def insert_row(table_name):
    data = request.json
    cursor = connection.cursor()
    columns = ', '.join(data.keys())
    values = ', '.join([f":{key}" for key in data.keys()])
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
    cursor.execute(query, data)
    connection.commit()
    cursor.close()
    return jsonify({'status': 'success'}), 201

@app.route('/api/update_row/<table_name>/<row_id>', methods=['PUT'])
def update_row(table_name, row_id):
    data = request.json
    set_values = ', '.join([f"{key} = :{key}" for key in data.keys()])
    query = f"UPDATE {table_name} SET {set_values} WHERE id = :id"
    data['id'] = row_id
    cursor = connection.cursor()
    cursor.execute(query, data)
    connection.commit()
    cursor.close()
    return jsonify({'status': 'success'}), 200

@app.route('/api/delete_row/<table_name>/<row_id>', methods=['DELETE'])
def delete_row(table_name, row_id):
    query = f"DELETE FROM {table_name} WHERE id = :id"
    cursor = connection.cursor()
    cursor.execute(query, {'id': row_id})
    connection.commit()
    cursor.close()
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
