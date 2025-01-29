from flask import Blueprint, request, jsonify
from db import get_db_connection, close_connection
import logging

# Define the auth Blueprint
auth = Blueprint('auth', __name__)  # This is what 'auth' refers to
# Test Route (Optional)
@auth.route('/test', methods=['GET'])
def test():
    return "Auth blueprint is working!"

# Sign Up Route
@auth.route('/signup', methods=['POST'])
def signup():
    connection = None
    try:
        data = request.json
        email = data['email']
        fname = data['fname']
        lname = data['lname']
        password = data['password']

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO User_portfolio (email, Fname, Lname, Password) VALUES (%s, %s, %s, %s)",
            (email, fname, lname, password)
        )
        connection.commit()
        logging.info(f"User registered successfully: {email}")

        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        logging.error(f"Error during signup: {e}")
        return jsonify({"error": str(e)}), 400
    finally:
        if connection:
            close_connection(connection)

# Sign In Route
@auth.route('/signin', methods=['POST'])
def signin():
    connection = None
    try:
        data = request.json
        email = data['email']
        password = data['password']

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM User_portfolio WHERE email=%s AND Password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        if user:
            logging.info(f"User logged in successfully: {email}")
            return jsonify({"message": "Login successful!"}), 200
        else:
            logging.warning(f"Failed login attempt for: {email}")
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        logging.error(f"Error during signin: {e}")
        return jsonify({"error": str(e)}), 400
    finally:
        if connection:
            close_connection(connection)
