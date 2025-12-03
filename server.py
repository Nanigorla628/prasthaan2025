import pandas as pd
import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS # Required to handle cross-origin requests from HTML

app = Flask(__name__)
# Enable CORS to allow your HTML file (which runs locally) to post data to the Flask server
CORS(app) 

# Define the file name for the Excel output
EXCEL_FILE = 'registration_data.xlsx'

def append_to_excel(new_data_dict):
    """
    Appends a new record (dictionary) to the Excel file. 
    It creates the file and header if it doesn't exist.
    """
    # Convert the single dictionary into a DataFrame with one row
    new_df = pd.DataFrame([new_data_dict])
    
    # Check if the Excel file already exists
    if os.path.exists(EXCEL_FILE):
        try:
            # Read the existing data
            existing_df = pd.read_excel(EXCEL_FILE)
            
            # Append the new data
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            
            # Save the combined DataFrame back to the Excel file
            updated_df.to_excel(EXCEL_FILE, index=False)
            print(f"Data appended successfully to {EXCEL_FILE}")
            return True
        except Exception as e:
            print(f"Error reading/writing Excel file: {e}")
            return False
    else:
        # File does not exist, so create it with the new data
        try:
            new_df.to_excel(EXCEL_FILE, index=False)
            print(f"Created new Excel file: {EXCEL_FILE} and saved data.")
            return True
        except Exception as e:
            print(f"Error creating Excel file: {e}")
            return False

@app.route('/save-data', methods=['POST'])
def save_data():
    """
    API endpoint to receive registration data via POST request.
    """
    if request.method == 'POST':
        try:
            # Get the JSON data sent from the JavaScript fetch request
            data = request.json
            
            # NOTE: For security, you should HASH the 'password' before saving it to the Excel file.
            # E.g., data['password'] = hash_function(data['password'])
            
            success = append_to_excel(data)
            
            if success:
                return jsonify({"message": "Registration data saved successfully"}), 200
            else:
                return jsonify({"error": "Failed to save data to Excel"}), 500
                
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON data received"}), 400
        except Exception as e:
            return jsonify({"error": f"Internal server error: {e}"}), 500

if __name__ == '__main__':
    # Run the server on the specified port (8000) that the HTML/JS is calling
    print(f"Starting Flask server on http://localhost:8000")
    print(f"Excel data will be saved to: {EXCEL_FILE}")
    app.run(port=8000, debug=True)