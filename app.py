from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS
import mysql.connector
import os

ssl_certificate_url = 'https://github.com/AkifaKhan/CloudWays-Project/blob/main/certs/DigiCertGlobalRootCA.crt.pem'
base_dir = os.path.abspath(os.path.dirname(__file__))
ssl_certificate_path = os.path.join(base_dir, 'certs', 'DigiCertGlobalRootCA.crt.pem')

app = Flask(__name__)
CORS(app)

# MySQL connection config
config = {
    'host': 'cloudways-server.mysql.database.azure.com',
    'user': 'lxpfgntzwv',
    'password': 'Blueberry@2001',
    'port': 3306,
    'database': 'cloudways-database',
    'ssl_ca': ssl_certificate_path,  # Path to downloaded certificate
    'ssl_disabled': False
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/book_flight', methods=['GET', 'POST'])
def book_flight():
    departure_cities = []
    arrival_cities = []
    try:
        # Fetch unique departure and arrival cities from the database
        cnx = mysql.connector.connect(**config)
        if cnx.is_connected():
            with cnx.cursor(buffered=True) as cursor:
                cursor.execute("SELECT DISTINCT departure_city FROM flights")
                departure_cities = [row[0] for row in cursor.fetchall()]
            
            with cnx.cursor(buffered=True) as cursor:
                cursor.execute("SELECT DISTINCT arrival_city FROM flights")
                arrival_cities = [row[0] for row in cursor.fetchall()]
            
            cnx.close()
    except mysql.connector.Error as err:
        return f"Error fetching cities: {err}", 500

    if request.method == 'POST':
        # Retrieve form data
        first_name = request.form['passenger_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        departure_city = request.form['departure_city']
        arrival_city = request.form['arrival_city']
        departure_date = request.form['departure_date']
        seats_booked = int(request.form['seats_booked'])

        try:
            # Connect to the database
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor(buffered=True, dictionary=True)

            # Query to find the flight based on the form inputs
            query_flight = """
            SELECT * FROM flights
            WHERE departure_city = %s AND arrival_city = %s AND departure_date = %s
            """
            cursor.execute(query_flight, (departure_city, arrival_city, departure_date))
            flight = cursor.fetchone()

            # Case 1: No flight found
            if not flight:
                return render_template(
                    'book_flight.html',
                    no_flight_found=True,
                    departure_cities=departure_cities,
                    arrival_cities=arrival_cities,
                    departure_city=departure_city,
                    arrival_city=arrival_city,
                    departure_date=departure_date
                )

            # Case 2: Flight found, check seats
            total_price = seats_booked * flight['price']
            new_seats_available = flight['seats_available'] - seats_booked

            if new_seats_available < 0:
                return render_template(
                    'book_flight.html',
                    not_enough_seats=True,
                    departure_cities=departure_cities,
                    arrival_cities=arrival_cities,
                    departure_city=departure_city,
                    arrival_city=arrival_city,
                    departure_date=departure_date
                )

            # Insert booking and update seats
            query_booking = """
            INSERT INTO bookings (flight_id, passenger_name, last_name, email, phone, seats_booked, total_price)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values_booking = (
                flight['flight_id'], first_name, last_name, email, phone, seats_booked, total_price
            )
            cursor.execute(query_booking, values_booking)

            query_update_seats = """
            UPDATE flights
            SET seats_available = %s
            WHERE flight_id = %s
            """
            cursor.execute(query_update_seats, (new_seats_available, flight['flight_id']))

            cnx.commit()
            cursor.close()
            cnx.close()
            flight['departure_time'] = str(flight['departure_time'])
            flight['arrival_time'] = str(flight['arrival_time'])


            print("Flight details:", flight)
            print("Seats booked:", seats_booked)
            print("Total price:", total_price)

            # Pass booking and flight details back to the template
            return render_template(
                'book_flight.html',
                success=True,
                flight=flight,
                seats_booked=seats_booked,
                total_price=total_price,
                departure_cities=departure_cities,
                arrival_cities=arrival_cities
            )
        

        except mysql.connector.Error as err:
            return f"Error: {err}", 500

    # For GET requests
    departure_city = request.args.get('departure_city')
    arrival_city = request.args.get('arrival_city')
    departure_date = request.args.get('departure_date')

    return render_template(
        'book_flight.html',
        departure_cities=departure_cities,
        arrival_cities=arrival_cities,
        departure_city=departure_city,
        arrival_city=arrival_city,
        departure_date=departure_date
    )

@app.route('/available_flights')
def available_flights():
    try:
        # Connect to the database to fetch available flights
        cnx = mysql.connector.connect(**config)
        if cnx.is_connected():
            with cnx.cursor(buffered=True, dictionary=True) as cursor:
                # Fetch available flights (those with seats available)
                query = """
                SELECT flight_id, departure_city, arrival_city, departure_date, departure_time, arrival_time, seats_available, price
                FROM flights
                WHERE seats_available > 0
                """
                cursor.execute(query)
                available_flights = cursor.fetchall()  # Fetch all available flights
                print(f"Available Flights: {available_flights}")  # Debugging line

            cnx.close()

            # Render the available_flights.html template with the fetched data
            return render_template('available_flights.html', flights=available_flights)
        else:
            return "Error: Unable to connect to the database.", 500
    except mysql.connector.Error as err:
        return f"Error: {err}", 500

if __name__ == '__main__':
    app.run(debug=True)





