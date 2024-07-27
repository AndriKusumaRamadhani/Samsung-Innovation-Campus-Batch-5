import json
import pandas as pd
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Initialize MongoDB client
client = MongoClient('mongodb+srv://JavaJunction:<password>@javajunction.mssuddt.mongodb.net/?retryWrites=true&w=majority&appName=JavaJunction')
db = client['java-database']
ldr_collection = db['sensor-colection2']    

# Initialize an empty DataFrame to store LDR data
columns = ["timestamp", "ldr1", "ldr2", "ldr3", "ldr4", "ldr5"]
ldr_df = pd.DataFrame(columns=columns)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 

@app.route("/")
def root_route():
    return "Hello world!"

@app.route("/ldr")
def get_ldr():
    # Fetch all documents from the MongoDB collection
    ldr_data = list(ldr_collection.find({}, {'_id': 0}))
    return jsonify(ldr_data)

@app.route("/submit-ldr", methods=["POST"])
def post_ldr():
    global ldr_df
    pesan = request.data.decode("utf8")
    ldr_values = json.loads(pesan)
    
    # Add the current timestamp to the data
    ldr_values["timestamp"] = datetime.now().isoformat()
    
    # Convert to DataFrame
    new_data = pd.DataFrame([ldr_values])
    
    # Append new data to the existing DataFrame
    ldr_df = pd.concat([ldr_df, new_data], ignore_index=True)
    
    # Insert new data into MongoDB
    ldr_collection.insert_one(ldr_values)
    
    print(ldr_values)
    return f"Received LDR values {ldr_values}"

@app.route("/submit", methods=["POST"])
def post_data():
    global ldr_df
    pesan = request.data.decode("utf8")
    pesan = json.loads(pesan)
    
    # Add the current timestamp to the data
    pesan["timestamp"] = datetime.now().isoformat()
    
    # Convert to DataFrame
    new_data = pd.DataFrame([pesan])
    
    # Append new data to the existing DataFrame
    ldr_df = pd.concat([ldr_df, new_data], ignore_index=True)
    
    # Insert new data into MongoDB
    ldr_collection.insert_one(pesan)
    
    print(pesan)
    return f"Received data {pesan}"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
