from flask import Blueprint, request, jsonify, render_template
from db import get_db_connection, close_connection
import bcrypt
import logging

auth = Blueprint("auth", __name__)
#--------------------signup--------------------------------
@auth.route("/signup", methods=["POST"])
def signup():
    connection = None
    try:
        data = request.json
        email = data["email"]
        fname = data["fname"]
        lname = data["lname"]
        password = data["password"]

        # Hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO User_portfolio (email, Fname, Lname, Password) VALUES (%s, %s, %s, %s)",
            (email, fname, lname, hashed_password.decode("utf-8")),
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
#--------------------signin--------------------------------
@auth.route("/signin", methods=["POST"])
def signin():
    connection = None
    try:
        data = request.json
        email = data["email"]
        password = data["password"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Retrieve user data
        cursor.execute("SELECT * FROM User_portfolio WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user:
            # Ensure password is a string before comparing
            stored_hashed_password = user["Password"]
            if isinstance(stored_hashed_password, bytes):  # Convert bytes to string if necessary
                stored_hashed_password = stored_hashed_password.decode("utf-8")

            # Compare hashed password with entered password
            if bcrypt.checkpw(password.encode("utf-8"), stored_hashed_password.encode("utf-8")):
                logging.info(f"User logged in successfully: {email}")
                return jsonify({"message": "Login successful!"}), 200

        logging.warning(f"Failed login attempt for: {email}")
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        logging.error(f"Error during signin: {e}")
        return jsonify({"error": str(e)}), 400
    finally:
        if connection:
            close_connection(connection)
