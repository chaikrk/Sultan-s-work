from flask import Blueprint, request, jsonify
from db import get_db_connection, close_connection
import logging

profile = Blueprint('profile', __name__)

# Route to handle education addition
@profile.route('/add-education', methods=['POST'])
def add_education():
    connection = None
    try:
        data = request.json
        email = data['email']
        degree_name = data['degree_name']
        major = data['major']
        university_name = data['university_name']
        country = data['country']

        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert education details
        cursor.execute(
            "INSERT INTO education (degree_name, major, university_name, country) VALUES (%s, %s, %s, %s)",
            (degree_name, major, university_name, country)
        )
        connection.commit()
        degree_id = cursor.lastrowid

        # Link to user
        cursor.execute(
            "INSERT INTO portfolio_has_education (education_degree_id, portfolio_email) VALUES (%s, %s)",
            (degree_id, email)
        )
        connection.commit()

        return jsonify({"message": "Education added successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        if connection:
            close_connection(connection)

# Route to handle experience addition
@profile.route('/add-experience', methods=['POST'])
def add_experience():
    connection = None
    try:
        data = request.json
        email = data['email']
        company_name = data['company_name']
        position = data['position']
        start_date = data['start_date']
        end_date = data['end_date']
        description = data['description']

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO WorkExperience (company_name, position, start_date, end_date, description) VALUES (%s, %s, %s, %s, %s)",
            (company_name, position, start_date, end_date, description)
        )
        connection.commit()
        experience_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO WorkExperience_has_User_portfolio (WorkExperience_experience_id, User_portfolio_email) VALUES (%s, %s)",
            (experience_id, email)
        )
        connection.commit()

        return jsonify({"message": "Experience added successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        if connection:
            close_connection(connection)

# Route to handle certification addition
@profile.route('/add-certification', methods=['POST'])
def add_certification():
    connection = None
    try:
        data = request.json
        email = data.get('email')
        name = data.get('name')
        provider = data.get('provider')
        course_link = data.get('course_link')
        duration_hours = data.get('duration_hours')

        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert into Previous_Certification
        insert_cert_query = """
            INSERT INTO Previous_Certification (name, provider, course_link, duration_hours)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_cert_query, (name, provider, course_link, duration_hours))
        connection.commit()
        certification_id = cursor.lastrowid

        # Insert into Previous_Certification_has_User_portfolio
        insert_user_cert_query = """
            INSERT INTO Previous_Certification_has_User_portfolio (Previous_Certification_id, User_portfolio_email)
            VALUES (%s, %s)
        """
        cursor.execute(insert_user_cert_query, (certification_id, email))
        connection.commit()

        return jsonify({"message": "Certification added successfully!"}), 201

    except Exception as e:
        logging.error(f"Database operation failed: {e}")  # Logs the actual error
        return jsonify({"error": "Database operation failed", "details": str(e)}), 500

    finally:
        if connection:
            close_connection(connection)

# Route to handle skill addition
@profile.route('/add-skill', methods=['POST'])
def add_skill():
    connection = None
    try:
        data = request.json
        email = data['email']
        name = data['name']
        category = data['category']
        level = data['level']

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO skill (name, category, level) VALUES (%s, %s, %s)",
            (name, category, level)
        )
        connection.commit()
        skill_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO portfolio_has_skill (skill_skill_id, portfolio_email) VALUES (%s, %s)",
            (skill_id, email)
        )
        connection.commit()

        return jsonify({"message": "Skill added successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        if connection:
            close_connection(connection)

# Route to delete education
@profile.route('/delete-education', methods=['POST'])
def delete_education():
    connection = None
    try:
        data = request.json
        degree_id = data['degree_id']
        email = data['email']

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM portfolio_has_education WHERE education_degree_id = %s AND portfolio_email = %s", (degree_id, email))
        connection.commit()

        cursor.execute("DELETE FROM education WHERE degree_id = %s", (degree_id,))
        connection.commit()

        return jsonify({"message": "Education record deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        if connection:
            close_connection(connection)

# Route to delete experience
@profile.route('/delete-experience', methods=['POST'])
def delete_experience():
    connection = None
    try:
        data = request.json
        experience_id = data['experience_id']
        email = data['email']

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM WorkExperience_has_User_portfolio WHERE WorkExperience_experience_id = %s AND User_portfolio_email = %s", (experience_id, email))
        connection.commit()

        cursor.execute("DELETE FROM WorkExperience WHERE experience_id = %s", (experience_id,))
        connection.commit()

        return jsonify({"message": "Experience record deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        if connection:
            close_connection(connection)

# Route to delete certification
@profile.route('/delete-certification', methods=['POST'])
def delete_certification():
    connection = None
    try:
        data = request.json
        certification_id = data['Previous_Certification_id']
        email = data['email']

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM Previous_Certification_has_User_portfolio WHERE Previous_Certification_id = %s AND User_portfolio_email = %s", (certification_id, email))
        connection.commit()

        cursor.execute("DELETE FROM Previous_Certification WHERE Previous_Certification_id = %s", (certification_id,))
        connection.commit()

        return jsonify({"message": "Certification record deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        if connection:
            close_connection(connection)

# Route to delete skill
@profile.route('/delete-skill', methods=['POST'])
def delete_skill():
    connection = None
    try:
        data = request.json
        skill_id = data['skill_id']
        email = data['email']

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM portfolio_has_skill WHERE skill_skill_id = %s AND portfolio_email = %s", (skill_id, email))
        connection.commit()

        cursor.execute("DELETE FROM skill WHERE skill_id = %s", (skill_id,))
        connection.commit()

        return jsonify({"message": "Skill record deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        if connection:
            close_connection(connection)
