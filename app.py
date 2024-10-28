import pymongo
import pytz
import re
import logging
import os
import time
import requests

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_from_directory,
    flash,
    abort,
)
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from passlib.hash import pbkdf2_sha256
from werkzeug.utils import secure_filename
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", b'_5#y2L"F4Q8z\n\xec]/')
IST = pytz.timezone("Asia/Kolkata")
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/ByteBucket"
mongo = PyMongo(app)


users = mongo.db.users
users.create_index("username", unique=True)
users.create_index("email", unique=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler("app.log", maxBytes=1024 * 1024, backupCount=10)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def register_user(username, password, phone, role, email, timestamp):
    password_regex = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    if not re.match(password_regex, password):
        return (
            False,
            "Password must be at least 8 characters long and contain at least one letter, one special character, and one digit.",
        )

    if not re.match(email_regex, email):
        return False, "Invalid email address."

    hashed_password = pbkdf2_sha256.hash(password)

    try:
        users.insert_one(
            {
                "username": username,
                "password": hashed_password,
                "phone": phone,
                "email": email,
                "role": role,
                "created_at": timestamp,
                "updated_at": timestamp,
            }
        )
        return True, None
    except pymongo.errors.DuplicateKeyError:
        return False, "Username or email already exists."
    except Exception as e:
        logger.error("Error occurred during user registration: %s", str(e))
        return False, "An error occurred during user registration."


def verify_user(username, password):
    username_regex = r"^[a-zA-Z0-9_.-]+$"
    if not re.match(username_regex, username):
        return False

    try:
        user_data = users.find_one({"username": username})
        if user_data and pbkdf2_sha256.verify(password, user_data["password"]):
            update_time = datetime.now(IST).strftime("%H:%M %d/%m/%Y")
            users.update_one(
                {"username": username}, {"$set": {"updated_at": update_time}}
            )
            return True
        else:
            return False
    except Exception as e:
        logger.error("Error occurred during user verification: %s", str(e))
        return False


@app.route("/")
def index():
    if "username" in session:
        username = session["username"]
        user_folder = os.path.join(app.config["UPLOAD_FOLDER"], username)

        return render_template("index.html", username=username)
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if verify_user(username, password):
            session["username"] = username
            session.permanent = True
            app.permanent_session_lifetime = timedelta(
                minutes=30
            )  # Set session timeout
            logger.info("User %s logged in successfully.", username)
            return redirect(url_for("index"))
        else:
            logger.warning("Failed login attempt for username: %s", username)
            return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        phone = request.form["phone"]
        email = request.form["email"]
        role = request.form["role"]
        timestamp = datetime.now().strftime("%H:%M %d/%m/%Y")

        success, error_message = register_user(
            username, password, phone, role, email, timestamp
        )
        if success:
            logger.info("User %s registered successfully", username)
            return redirect(url_for("login"))
        else:
            logger.error(
                "Failed user registration for username: %s - %s",
                username,
                error_message,
            )
            return render_template(
                "register.html",
                error=error_message,
                username=username,
                phone=phone,
                email=email,
                role=role,
            )
    return render_template("register.html")


@app.route("/files", methods=["GET", "POST"])
def files():
    if "username" in session:
        username = session["username"]
        user_folder = os.path.join(app.config["UPLOAD_FOLDER"], username)
        if os.path.exists(user_folder):
            categories = [
                d
                for d in os.listdir(user_folder)
                if os.path.isdir(os.path.join(user_folder, d))
                and os.listdir(os.path.join(user_folder, d))
            ]
            files = {
                category: os.listdir(os.path.join(user_folder, category))
                for category in categories
            }
            return render_template(
                "files.html", username=username, categories=categories, files=files
            )
        else:
            return render_template(
                "files.html", username=username, categories=[], files={}
            )
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    if "username" in session:
        username = session.pop("username", None)
        if username:
            logger.info("User %s logged out.\n\n", username)
    return redirect(url_for("index"))


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)

        files = request.files.getlist("file")
        if not files or all(file.filename == "" for file in files):
            flash("No selected file")
            return redirect(request.url)

        categories = []
        for index in range(len(files)):
            category = request.form.get(f"category_{index}", "Other")
            categories.append(category)

        user_folder = os.path.join(app.config["UPLOAD_FOLDER"], username)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        for index, file in enumerate(files):
            if file.filename == "":
                continue
            category = categories[index]
            category_folder = os.path.join(user_folder, category)

            if not os.path.exists(category_folder):
                os.makedirs(category_folder)

            original_filename = secure_filename(file.filename)
            file_path = os.path.join(category_folder, original_filename)

            if os.path.exists(file_path):
                name, extension = os.path.splitext(original_filename)
                counter = 1
                while os.path.exists(file_path):
                    new_filename = f"{name}_{counter}{extension}"
                    file_path = os.path.join(category_folder, new_filename)
                    counter += 1

            file.save(file_path)

            logger.info(
                "File '%s' uploaded by user '%s' in category '%s'",
                original_filename,
                username,
                category,
            )

        return redirect(url_for("files"))

    return render_template("upload.html", username=username)


@app.route("/delete_file/<category>/<filename>", methods=["POST"])
def delete_file(category, filename):
    if "username" in session:
        username = session["username"]
        user_folder = os.path.join(app.config["UPLOAD_FOLDER"], username)
        category_folder = os.path.join(user_folder, category)
        file_path = os.path.join(category_folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info("File '%s' deleted by user '%s'", filename, username)
    return redirect(url_for("files"))


@app.route("/download_file/<category>/<filename>")
def download_file(category, filename):

    if "username" in session:
        username = session["username"]
        user_folder = os.path.join(app.config["UPLOAD_FOLDER"], username)
        category_folder = os.path.join(user_folder, category)

        file_path = os.path.join(category_folder, filename)
        if os.path.exists(file_path):
            return send_from_directory(category_folder, filename, as_attachment=True)

    return redirect(url_for("index"))


@app.route("/view_file/<category>/<filename>")
def view_file(category, filename):
    if "username" in session:
        username = session["username"]
        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"], username, category, filename
        )

        if os.path.exists(file_path):
            return send_from_directory(
                os.path.join(app.config["UPLOAD_FOLDER"], username, category),
                filename,
            )
        else:
            abort(404)
            return render_template("files", error="Can't open file.")
    else:
        return redirect(url_for("login"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user_data = users.find_one({"username": username})

    if request.method == "POST":
        email = request.form["email"]
        phone = request.form["phone"]
        role = request.form["role"]
        updated_at = datetime.now().strftime("%H:%M %d/%m/%Y")

        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, email):
            flash("Invalid email address")
            return render_template("profile.html", user=user_data)

        try:
            users.update_one(
                {"username": username},
                {
                    "$set": {
                        "email": email,
                        "phone": phone,
                        "role": role,
                        "updated_at": updated_at,
                    }
                },
            )
            logger.info("User %s updated their profile.", username)
            flash("Profile updated successfully")
        except pymongo.errors.DuplicateKeyError:
            flash("Email already exists.")
        except Exception as e:
            logger.error("Error occurred during profile update: %s", str(e))
            flash("An error occurred while updating the profile.")

        return redirect(url_for("profile"))

    return render_template("profile.html", user=user_data, username=username)


if __name__ == "__main__":
    app.run(debug=True)
