import logging
import os
import time
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
from routes.auth import auth
from routes.profile import profile  # imported the profile blueprint

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)

app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(profile, url_prefix="/profile")  # register the profile blueprint

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
    return render_template("index.html", time=time)
#--------------------new------------------------------------
@app.route("/signin", methods=["GET"])
def signin():
    return render_template("signin.html")

@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)

# --------------------------------------------------------------------------
# The following profile routes have been moved to routes/profile.py
#
# @app.route("/profile/get-education", methods=["GET"])
# def get_education():
#     ...
#
# ... (all other /profile endpoints) ...
#
# --------------------------------------------------------------------------

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
#--------------------------------------------------------------------------
# @app.route("/profile/get-user-portfolio", methods=["GET"])
# def get_user_portfolio_api():
#     email = request.args.get("email")  # Get email from query parameter
#     if not email:
#         return jsonify({"error": "Missing email"}), 400
#
#     user_portfolio = get_user_portfolio(email)
#     
#     if user_portfolio:
#         return jsonify(user_portfolio), 200
#     else:
#         return jsonify({"error": "No data found for this user"}), 404
#
# def get_user_portfolio(email):
#     """
#     Retrieves user portfolio information (education, experience, certifications, and skills) 
#     from the database using their email.
#     """
#     print(f"🚀 Function get_user_portfolio() started for email: {email}")  # Debugging
#
#     connection = None
#     try:
#         connection = get_db_connection()
#         cursor = connection.cursor(dictionary=True)
#
#         print(f"✅ Database connection established for: {email}")  # Debugging
#
#         # Query user education
#         cursor.execute("""
#             SELECT e.degree_name, e.major, e.university_name, e.country
#             FROM education e
#             JOIN portfolio_has_education pe ON e.degree_id = pe.education_degree_id
#             WHERE pe.portfolio_email = %s
#         """, (email,))
#         education = cursor.fetchall()
#         print("🎓 Education result:", education)  # Debugging
#
#         # Query user experience
#         cursor.execute("""
#             SELECT w.company_name, w.position, w.start_date, w.end_date, w.description
#             FROM WorkExperience w
#             JOIN WorkExperience_has_User_portfolio we 
#                 ON w.experience_id = we.WorkExperience_experience_id
#             WHERE we.User_portfolio_email = %s
#         """, (email,))
#         experience = cursor.fetchall()
#         print("💼 Experience result:", experience)  # Debugging
#
#         # Query user certifications
#         cursor.execute("""
#             SELECT p.name, p.provider, p.course_link, p.duration_hours
#             FROM Previous_Certification p
#             JOIN Previous_Certification_has_User_portfolio pu 
#                 ON p.Previous_Certification_id = pu.Previous_Certification_id
#             WHERE pu.User_portfolio_email = %s
#         """, (email,))
#         certifications = cursor.fetchall()
#         print("📜 Certifications result:", certifications)  # Debugging
#
#         # Query user skills
#         cursor.execute("""
#             SELECT s.name AS skill_name, s.category, s.level
#             FROM skill s
#             JOIN portfolio_has_skill ps ON s.skill_id = ps.skill_skill_id
#             WHERE ps.portfolio_email = %s
#         """, (email,))
#         skills = cursor.fetchall()
#         print("🛠 Skills result:", skills)  # Debugging
#
#         # Store everything in a structured dictionary
#         user_portfolio = {
#             "education": education if education else [],
#             "experience": experience if experience else [],
#             "certifications": certifications if certifications else [],
#             "skills": skills if skills else []
#         }
#
#         # Debug print before returning
#         print("📂 Final user_portfolio:", user_portfolio)
#
#         # If user has no data, return "nothing here" instead of None
#         if not any(user_portfolio.values()):
#             print("⚠️ No data found!")
#             return "nothing here"
#
#         return user_portfolio
#
#     except Exception as e:
#         print(f"❌ Error retrieving user portfolio for {email}: {e}")
#         return "error fetching data"
#     
#     finally:
#         if connection:
#             close_connection(connection)

# ------------------------------------------------------------------------
# Run the app
# ------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
