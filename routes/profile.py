from flask import Blueprint, request, jsonify, render_template
from db import get_db_connection, close_connection
import logging

profile = Blueprint('profile', __name__)

# ------------------------------------------------------------------------
# Helper to check if user email exists
# ------------------------------------------------------------------------
def check_email(cursor, email):
    cursor.execute("SELECT email FROM User_portfolio WHERE email = %s", (email,))
    return cursor.fetchone()

# ------------------------------------------------------------------------
# GET Endpoints
# ------------------------------------------------------------------------
@profile.route("/get-education", methods=["GET"])
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

@profile.route("/get-experience", methods=["GET"])
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

@profile.route("/get-certification", methods=["GET"])
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

@profile.route("/get-skill", methods=["GET"])
def get_skill():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Missing email"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT email FROM User_portfolio WHERE email = %s", (email,))
        if not cursor.fetchone():
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
        if cursor:
            cursor.close()
        close_connection(connection)

# ------------------------------------------------------------------------
# POST Endpoints
# ------------------------------------------------------------------------
@profile.route("/add-education", methods=["POST"])
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

@profile.route("/add-experience", methods=["POST"])
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

@profile.route("/add-certification", methods=["POST"])
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

@profile.route("/add-skill", methods=["POST"])
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
# DELETE Endpoints (Updated to use DELETE method and query parameters)
# ------------------------------------------------------------------------
@profile.route("/delete-education", methods=["DELETE"])
def delete_education():
    degree_id = request.args.get("id")
    # Optionally, you could get email from query parameters if needed:
    email = request.args.get("email")
    if not degree_id:
        return jsonify({"error": "Missing degree id"}), 400

    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        if email:
            cursor.execute("DELETE FROM portfolio_has_education WHERE education_degree_id = %s AND portfolio_email = %s", (degree_id, email))
        else:
            cursor.execute("DELETE FROM portfolio_has_education WHERE education_degree_id = %s", (degree_id,))
        connection.commit()

        cursor.execute("DELETE FROM education WHERE degree_id = %s", (degree_id,))
        connection.commit()

        return jsonify({"message": "Education record deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        close_connection(connection)

@profile.route("/delete-experience", methods=["DELETE"])
def delete_experience():
    experience_id = request.args.get("id")
    email = request.args.get("email")
    if not experience_id:
        return jsonify({"error": "Missing experience id"}), 400

    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        if email:
            cursor.execute("DELETE FROM WorkExperience_has_User_portfolio WHERE WorkExperience_experience_id = %s AND User_portfolio_email = %s", (experience_id, email))
        else:
            cursor.execute("DELETE FROM WorkExperience_has_User_portfolio WHERE WorkExperience_experience_id = %s", (experience_id,))
        connection.commit()

        cursor.execute("DELETE FROM WorkExperience WHERE experience_id = %s", (experience_id,))
        connection.commit()

        return jsonify({"message": "Experience record deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        close_connection(connection)

@profile.route("/delete-certification", methods=["DELETE"])
def delete_certification():
    certification_id = request.args.get("id")
    email = request.args.get("email")
    if not certification_id:
        return jsonify({"error": "Missing certification id"}), 400

    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        if email:
            cursor.execute("DELETE FROM Previous_Certification_has_User_portfolio WHERE Previous_Certification_id = %s AND User_portfolio_email = %s", (certification_id, email))
        else:
            cursor.execute("DELETE FROM Previous_Certification_has_User_portfolio WHERE Previous_Certification_id = %s", (certification_id,))
        connection.commit()

        cursor.execute("DELETE FROM Previous_Certification WHERE Previous_Certification_id = %s", (certification_id,))
        connection.commit()

        return jsonify({"message": "Certification record deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        close_connection(connection)

@profile.route("/delete-skill", methods=["DELETE"])
def delete_skill():
    skill_id = request.args.get("id")
    email = request.args.get("email")
    if not skill_id:
        return jsonify({"error": "Missing skill id"}), 400

    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        if email:
            cursor.execute("DELETE FROM portfolio_has_skill WHERE skill_skill_id = %s AND portfolio_email = %s", (skill_id, email))
        else:
            cursor.execute("DELETE FROM portfolio_has_skill WHERE skill_skill_id = %s", (skill_id,))
        connection.commit()

        cursor.execute("DELETE FROM skill WHERE skill_id = %s", (skill_id,))
        connection.commit()

        return jsonify({"message": "Skill record deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        close_connection(connection)
