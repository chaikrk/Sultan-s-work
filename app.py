import logging
import os
from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    send_from_directory,
    url_for,
jsonify
)
from flask_cors import CORS
from db import get_db_connection, close_connection
import mysql.connector
import mysql.connector.pooling

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = Flask(__name__)
CORS(app)

# ------------------------------------------------------------------------
# Helper to check if user email exists
# ------------------------------------------------------------------------
def check_email(cursor, email):
    cursor.execute("SELECT email FROM User_portfolio WHERE email = %s", (email,))
    return cursor.fetchone()

# ------------------------------------------------------------------------
# Home page (GET)
# ------------------------------------------------------------------------
@app.route("/")
def home():
    # Renders templates/index.html
    return render_template("index.html")

# ------------------------------------------------------------------------
# Sign In (GET + POST)
# ------------------------------------------------------------------------
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "GET":
        # Serve templates/signin.html
        return render_template("signin.html")

    # If POST, handle the sign-in logic
    try:
        data = request.json
        email = data["email"]
        password = data["password"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM User_portfolio WHERE email=%s AND Password=%s",
            (email, password),
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
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            close_connection(connection)

# ------------------------------------------------------------------------
# Sign Up (GET + POST)
# ------------------------------------------------------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        # Serve templates/signup.html
        return render_template("signup.html")

    # If POST, handle the sign-up logic
    try:
        data = request.json
        email = data["email"]
        fname = data["fname"]
        lname = data["lname"]
        password = data["password"]

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO User_portfolio (email, Fname, Lname, Password) VALUES (%s, %s, %s, %s)",
            (email, fname, lname, password),
        )
        connection.commit()
        logging.info(f"User registered successfully: {email}")

        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        logging.error(f"Error during signup: {e}")
        return jsonify({"error": str(e)}), 400
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            close_connection(connection)

# ------------------------------------------------------------------------
# Profile GET routes (education, experience, certification, skill)
# ------------------------------------------------------------------------
@app.route("/profile/get-education", methods=["GET"])
def get_education():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Missing email"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        if not check_email(cursor, email):
            return jsonify({"error": "Email not found"}), 404

        query = """
            SELECT e.degree_id AS id, e.degree_name, e.major, e.university_name, e.country
            FROM education e
            JOIN portfolio_has_education pe ON e.degree_id = pe.education_degree_id
            WHERE pe.portfolio_email = %s
        """
        cursor.execute(query, (email,))
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Exception as e:
        logging.error(f"Error in get-education: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        close_connection(connection)

@app.route("/profile/get-experience", methods=["GET"])
def get_experience():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Missing email"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        if not check_email(cursor, email):
            return jsonify({"error": "Email not found"}), 404

        query = """
            SELECT w.experience_id AS id, w.company_name, w.position,
                   w.start_date, w.end_date, w.description
            FROM WorkExperience w
            JOIN WorkExperience_has_User_portfolio we
              ON w.experience_id = we.WorkExperience_experience_id
            WHERE we.User_portfolio_email = %s
        """
        cursor.execute(query, (email,))
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Exception as e:
        logging.error(f"Error in get-experience: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        close_connection(connection)

@app.route("/profile/get-certification", methods=["GET"])
def get_certification():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Missing email"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        if not check_email(cursor, email):
            return jsonify({"error": "Email not found"}), 404

        query = """
            SELECT p.Previous_Certification_id AS id, p.name, p.provider,
                   p.course_link, p.duration_hours
            FROM Previous_Certification p
            JOIN Previous_Certification_has_User_portfolio pu
              ON p.Previous_Certification_id = pu.Previous_Certification_id
            WHERE pu.User_portfolio_email = %s
        """
        cursor.execute(query, (email,))
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Exception as e:
        logging.error(f"Error in get-certification: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        close_connection(connection)

@app.route("/profile/get-skill", methods=["GET"])
def get_skill():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Missing email"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        if not check_email(cursor, email):
            return jsonify({"error": "Email not found"}), 404

        query = """
            SELECT s.skill_id AS id, s.name, s.category, s.level
            FROM skill s
            JOIN portfolio_has_skill ps ON s.skill_id = ps.skill_skill_id
            WHERE ps.portfolio_email = %s
        """
        cursor.execute(query, (email,))
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Exception as e:
        logging.error(f"Error in get-skill: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        close_connection(connection)

# ------------------------------------------------------------------------
# Profile ADD routes (POST)
# ------------------------------------------------------------------------
@app.route("/profile/add-education", methods=["POST"])
def add_education():
    data = request.json
    logging.info(f"Received data for add-education: {data}")
    required_fields = ["email", "degree", "major", "university", "country"]
    if not all(field in data for field in required_fields):
        logging.error("Missing required fields in request data")
        return jsonify({"error": "Missing required fields"}), 400

    connection = get_db_connection()
    if not connection:
        logging.error("Failed to establish database connection")
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor()

        if not check_email(cursor, data["email"]):
            logging.error(f"Email {data['email']} does not exist in User_portfolio")
            return jsonify({"error": "Email not found in User_portfolio"}), 404

        insert_education_query = """
            INSERT INTO education (degree_name, major, university_name, country)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(
            insert_education_query,
            (data["degree"], data["major"], data["university"], data["country"]),
        )
        connection.commit()
        degree_id = cursor.lastrowid
        logging.info(f"Inserted education with degree_id: {degree_id}")

        insert_portfolio_query = """
            INSERT INTO portfolio_has_education (education_degree_id, portfolio_email)
            VALUES (%s, %s)
        """
        cursor.execute(insert_portfolio_query, (degree_id, data["email"]))
        connection.commit()

        logging.info("Education added successfully")
        return jsonify({"message": "Education added successfully"}), 200

    except Exception as e:
        logging.error(f"Database operation error: {e}")
        return jsonify({"error": "Database operation failed"}), 500
    finally:
        cursor.close()
        close_connection(connection)

@app.route("/profile/add-experience", methods=["POST"])
def add_experience():
    data = request.json
    logging.info(f"Received data for add-experience: {data}")
    required_fields = ["email", "company", "position", "start_date", "end_date", "description"]
    if not all(field in data for field in required_fields):
        logging.error("Missing required fields in request data")
        return jsonify({"error": "Missing required fields"}), 400

    connection = get_db_connection()
    if not connection:
        logging.error("Failed to establish database connection")
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor()

        if not check_email(cursor, data["email"]):
            logging.error(f"Email {data['email']} does not exist in User_portfolio")
            return jsonify({"error": "Email not found in User_portfolio"}), 404

        insert_experience_query = """
            INSERT INTO WorkExperience (company_name, position, start_date, end_date, description)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(
            insert_experience_query,
            (
                data["company"],
                data["position"],
                data["start_date"],
                data["end_date"],
                data["description"],
            ),
        )
        connection.commit()
        experience_id = cursor.lastrowid
        logging.info(f"Inserted experience with experience_id: {experience_id}")

        insert_portfolio_query = """
            INSERT INTO WorkExperience_has_User_portfolio
            (WorkExperience_experience_id, User_portfolio_email)
            VALUES (%s, %s)
        """
        cursor.execute(insert_portfolio_query, (experience_id, data["email"]))
        connection.commit()

        logging.info("Experience added successfully")
        return jsonify({"message": "Experience added successfully"}), 200

    except Exception as e:
        logging.error(f"Database operation error: {e}")
        return jsonify({"error": "Database operation failed"}), 500
    finally:
        cursor.close()
        close_connection(connection)

@app.route("/profile/add-certification", methods=["POST"])
def add_certification():
    data = request.json
    logging.info(f"Received data for add-certification: {data}")
    required_fields = ["email", "cert_name", "provider", "course_link", "duration_hours"]
    if not all(field in data for field in required_fields):
        logging.error("Missing required fields in request data")
        return jsonify({"error": "Missing required fields"}), 400

    connection = get_db_connection()
    if not connection:
        logging.error("Failed to establish database connection")
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor()

        if not check_email(cursor, data["email"]):
            logging.error(f"Email {data['email']} does not exist in User_portfolio")
            return jsonify({"error": "Email not found in User_portfolio"}), 404

        insert_certification_query = """
            INSERT INTO Previous_Certification (name, provider, course_link, duration_hours)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(
            insert_certification_query,
            (data["cert_name"], data["provider"], data["course_link"], data["duration_hours"]),
        )
        connection.commit()
        certification_id = cursor.lastrowid
        logging.info(f"Inserted certification with id: {certification_id}")

        insert_portfolio_query = """
            INSERT INTO Previous_Certification_has_User_portfolio
            (Previous_Certification_id, User_portfolio_email)
            VALUES (%s, %s)
        """
        cursor.execute(insert_portfolio_query, (certification_id, data["email"]))
        connection.commit()

        logging.info("Certification added successfully")
        return jsonify({"message": "Certification added successfully"}), 200

    except Exception as e:
        logging.error(f"Database operation error: {e}")
        return jsonify({"error": "Database operation failed"}), 500
    finally:
        cursor.close()
        close_connection(connection)

@app.route("/profile/add-skill", methods=["POST"])
def add_skill():
    data = request.json
    logging.info(f"Received data for add-skill: {data}")
    required_fields = ["email", "skill_name", "category", "skill_level"]
    if not all(field in data for field in required_fields):
        logging.error("Missing required fields in request data")
        return jsonify({"error": "Missing required fields"}), 400

    connection = get_db_connection()
    if not connection:
        logging.error("Failed to establish database connection")
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor()

        if not check_email(cursor, data["email"]):
            logging.error(f"Email {data['email']} does not exist in User_portfolio")
            return jsonify({"error": "Email not found in User_portfolio"}), 404

        insert_skill_query = """
            INSERT INTO skill (name, category, level)
            VALUES (%s, %s, %s)
        """
        cursor.execute(
            insert_skill_query,
            (data["skill_name"], data["category"], data["skill_level"]),
        )
        connection.commit()
        skill_id = cursor.lastrowid
        logging.info(f"Inserted skill with id: {skill_id}")

        insert_portfolio_query = """
            INSERT INTO portfolio_has_skill (portfolio_email, skill_skill_id)
            VALUES (%s, %s)
        """
        cursor.execute(insert_portfolio_query, (data["email"], skill_id))
        connection.commit()

        logging.info("Skill added successfully")
        return jsonify({"message": "Skill added successfully"}), 200

    except Exception as e:
        logging.error(f"Database operation error: {e}")
        return jsonify({"error": "Database operation failed"}), 500
    finally:
        cursor.close()
        close_connection(connection)

# ------------------------------------------------------------------------
# Run the app
# ------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    #--------------------------------------------------------------------------
#try for chat
#--------------------------------------------------------------------------
@app.route("/chat", methods=["GET"])
def chat():
    try:
        return render_template("chat.html")
    except Exception as e:
        logging.error(f"Error rendering chat.html: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500
@app.route("/portfolio", methods=["GET"])
def portfolio():
    return render_template("portfolio.html")
