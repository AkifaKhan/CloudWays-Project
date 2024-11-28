from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os

app = Flask(__name__)

ssl_certificate_path = os.path.join(base_dir, 'certs', 'DigiCertGlobalRootCA.crt.pem')

# MySQL connection config
config = {
    'host': 'cloudways-server.mysql.database.azure.com',
    'user': 'lxpfgntzwv',
    'password': 'Blueberry@2001',
    'port': 3306,
    'database': 'cloudways-database',
    'ssl_ca': ssl_certificate_path,  # Dynamically constructed path
    'ssl_disabled': False
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/book_flight', methods=['GET', 'POST'])
def book_flight():
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

            if cnx.is_connected():
                print("Successfully connected to the database")
                cursor = cnx.cursor(buffered=True,dictionary=True)

                # Query to find the flight based on the form inputs
                query_flight = """
                SELECT * FROM flights
                WHERE departure_city = %s AND arrival_city = %s AND departure_date = %s
                """
                print(f"Searching for flight with Departure City: {departure_city}, Arrival City: {arrival_city}, Date: {departure_date}")

                cursor.execute(query_flight, (departure_city, arrival_city, departure_date))
                flight = cursor.fetchone()

                if flight:
                    
                    # Calculate total price and update flight seat availability
                    total_price = seats_booked * flight['price']
                    new_seats_available = flight['seats_available'] - seats_booked
                    print(total_price)

                    if new_seats_available < 0:
                        return "Error: Not enough seats available.", 400
                    
                    print(f"Flight Found: {flight}")

                    # Insert booking into the bookings table
                    query_booking = """
                    INSERT INTO bookings (flight_id, passenger_name, last_name, email, phone, seats_booked, total_price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    values_booking = (
                        flight['flight_id'], first_name, last_name, email, phone, seats_booked, total_price
                    )

                    print(f"Booking Values: {values_booking}")  # Debugging: Check the insert values

                    cursor.execute(query_booking, values_booking)
                    print("First Insert done")

                    # Update seats available in the flights table
                    query_update_seats = """
                    UPDATE flights
                    SET seats_available = %s
                    WHERE flight_id = %s
                    """
                    cursor.execute(query_update_seats, (new_seats_available, flight['flight_id']))

                    # Commit the transaction
                    cnx.commit()

                    # Close the cursor and connection
                    cursor.close()
                    cnx.close()

                    return redirect(url_for('home'))  # Redirect to home page after successful booking
                else:
                    return "Error: No matching flight found.", 404
            else:
                return "Error: Unable to connect to the database.", 500
        except mysql.connector.Error as err:
            return f"Error: {err}", 500
    else:
        try:
            # Connect to the database to fetch unique cities
            cnx = mysql.connector.connect(**config)

            if cnx.is_connected():
                with cnx.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT DISTINCT departure_city FROM flights")
                    departure_cities = [row[0] for row in cursor.fetchall()]
                    print(f"Departure Cities: {departure_cities}")  # Debugging line

                with cnx.cursor(buffered=True) as cursor:
                    # Fetch unique arrival cities
                    cursor.execute("SELECT DISTINCT arrival_city FROM flights")
                    arrival_cities = [row[0] for row in cursor.fetchall()]
                    print(f"Arrival Cities: {arrival_cities}")  # Debugging line

                # Close the     connection
                cnx.close()

                return render_template(
                    'book_flight.html', 
                    departure_cities=departure_cities, 
                    arrival_cities=arrival_cities
                )
            else:
                return "Error: Unable to connect to the database.", 500
        except mysql.connector.Error as err:
            return f"Error: {err}", 500


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



