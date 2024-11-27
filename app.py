from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

config = {
    'host': 'cloudways-server.mysql.database.azure.com',
    'user': 'lxpfgntzwv',
    'password': 'Blueberry@2001',  # Replace with your actual password
    'database': 'cloudways-database',  # Replace with your actual database name
    'ssl_disabled': False  # SSL is required
}

@app.route('/')
def index():
    try:
        # try to establish a connection
        cnx = mysql.connector.connect(**config)

        # Check if the connection is successful
        if cnx.is_connected():
            print("Connection Successful")

            cursor = cnx.cursor()
            cursor.execute("SELECT * FROM Dimaircraft")  # Fetch all rows from the table
            users = cursor.fetchall()
            cursor.close()  # Close cursor
            cnx.close()  # Close the connection

            return render_template('index.html', aircrafts=users)
        else:
            return "Connection Failed", 500

    except mysql.connector.Error as e:
        return f"Error Connecting to MySQL Database: {e}", 500

    finally:
        if cnx and cnx.is_connected():
            cnx.close()
        
if __name__ == '__main__':
    app.run(debug=True)
