from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# Database connection configuration
db_config = {
    'host': 'cloudways-server.mysql.database.azure.com',
    'user': 'lxpfgntzwv',
    'password': 'Blueberry@2001',  # Replace with your actual password
    'database': 'cloudways-database',  # Replace with your actual database name
    'ssl_disabled': False  # SSL is required
}

# Function to store feedback in the database
def store_feedback(name, email, phone, address, city, country):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Feedback_Form (Name, Email, PhoneNumber, HouseAddress, City, Country) VALUES (%s, %s, %s, %s, %s, %s)",
        (name, email, phone, address, city, country)
    )
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def index():
    return render_template('feedback_form.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    city = request.form['city']
    country = request.form['country']
    store_feedback(name, email, phone, address, city, country)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)