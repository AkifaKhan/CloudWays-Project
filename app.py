from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

# Database connection configuration
config = {
    'host': 'cloudways-server.mysql.database.azure.com',
    'user': 'lxpfgntzwv',
    'password': 'Blueberry@2001',
    'database': 'cloudways-database',
    'ssl_ca': r'Downloads\DigiCertGlobalRootG2.crt',  # Replace with your SSL certificate path
    'ssl_disabled': False
}

@app.route('/')
def index():
    return "Welcome to the Flask app connected to MySQL!"

@app.route('/feedback', methods=['GET'])
def get_feedback():
    # Create a connection to the database
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)  # Use dictionary cursor to get results as a dictionary
        
        # Query to fetch data from Feedback_Form table
        cursor.execute("SELECT * FROM Feedback_Form")
        feedback = cursor.fetchall()  # Fetch all rows
        
        cursor.close()
        conn.close()

        # Return the data as JSON response
        return jsonify(feedback)
    
    except mysql.connector.Error as err:
        return f"Error: {err}"

if __name__ == "__main__":
    app.run(debug=True)
