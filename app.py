from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import hashlib  # For password hashing

app = Flask(__name__)
app.secret_key = "supersecretkey"

# MongoDB Connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/movie_booking"
mongo = PyMongo(app)

# Helper function for password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize admin account if it doesn't exist
def initialize_admin():
    admin = mongo.db.users.find_one({"username": "PVR"})
    if not admin:
        mongo.db.users.insert_one({
            "username": "PVR",
            "password": hash_password("admin@123"),
            "role": "admin"
        })
        print("Admin account created!")

# Home Page for Users
@app.route("/home")
def home():
    if "username" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))
    
    movies = list(mongo.db.movies.find({"time": {"$exists": True, "$ne": ""}}))  
    return render_template("index.html", movies=movies)

# Home Page for Admins
@app.route("/admin_home")
def admin_home():
    if "username" not in session or session.get("role") != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    
    movies = list(mongo.db.movies.find())
    # Get available screens for the dropdown
    screens = list(mongo.db.screens.find())
    return render_template("admin_home.html", movies=movies, screens=screens)

# User Booking Page
@app.route("/bookings")
def view_bookings():
    if "username" not in session or session.get("role") != "user":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    
    user_bookings = mongo.db.bookings.find({"user": session["username"]})
    return render_template("bookings.html", bookings=user_bookings)

# Booking a Movie
@app.route("/book/<movie_id>", methods=["GET", "POST"])
def book_movie(movie_id):
    if "username" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))
        
    movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)})

    if request.method == "POST":
        user_name = session["username"]  # Use session username to ensure correct user
        seats = request.form["seats"]

        mongo.db.bookings.insert_one({
            "user": user_name,
            "movie_id": movie_id,
            "movie_name": movie["title"],
            "show_time": movie["time"],
            "screen": movie["screen"],  # Added screen to booking
            "seats": seats
        })

        flash("Booking Successful!", "success")
        return redirect(url_for("view_bookings"))

    return render_template("book.html", movie=movie)

# Admin Page (View & Add Movies)
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "username" not in session or session.get("role") != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        movie_title = request.form["title"]
        movie_time = request.form["time"]
        movie_screen = request.form["screen"]  # Get screen from form
        
        # Add screen to movie data
        mongo.db.movies.insert_one({
            "title": movie_title, 
            "time": movie_time,
            "screen": movie_screen
        })
        
        flash("Movie Added Successfully!", "success")
        return redirect(url_for("admin"))
    
    movies = list(mongo.db.movies.find())
    # Get available screens for the dropdown
    screens = list(mongo.db.screens.find())
    return render_template("admin.html", movies=movies, screens=screens)

# View All Bookings (Admin)
@app.route("/admin/bookings")
def admin_bookings():
    if "username" not in session or session.get("role") != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    
    all_bookings = mongo.db.bookings.find()
    return render_template("admin_bookings.html", bookings=all_bookings)

# Delete Movie (Admin Only)
@app.route("/delete_movie/<movie_id>", methods=["POST"])
def delete_movie(movie_id):
    if "username" not in session or session.get("role") != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("admin"))
    
    mongo.db.movies.delete_one({"_id": ObjectId(movie_id)})
    flash("Movie deleted successfully", "success")
    return redirect(url_for("admin"))

# Manage Screens (Admin Only)
@app.route("/admin/screens", methods=["GET", "POST"])
def manage_screens():
    if "username" not in session or session.get("role") != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        screen_name = request.form["screen_name"]
        screen_capacity = request.form["capacity"]
        
        mongo.db.screens.insert_one({
            "name": screen_name,
            "capacity": screen_capacity
        })
        
        flash("Screen Added Successfully!", "success")
        return redirect(url_for("manage_screens"))
    
    screens = list(mongo.db.screens.find())
    return render_template("manage_screens.html", screens=screens)

# Delete Screen (Admin Only)
@app.route("/delete_screen/<screen_id>", methods=["POST"])
def delete_screen(screen_id):
    if "username" not in session or session.get("role") != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("manage_screens"))
    
    mongo.db.screens.delete_one({"_id": ObjectId(screen_id)})
    flash("Screen deleted successfully", "success")
    return redirect(url_for("manage_screens"))

# Login Page
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = hash_password(password)
        
        # Check if user exists
        user = mongo.db.users.find_one({"username": username})
        
        if user and user["password"] == hashed_password:
            session["username"] = username
            session["role"] = user["role"]
            
            flash("Login successful!", "success")
            if user["role"] == "admin":
                return redirect(url_for("admin_home"))
            else:
                return redirect(url_for("home"))
        else:
            flash("Invalid username or password!", "danger")
            
    return render_template("login.html")

# Register Page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        
        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return render_template("register.html")
        
        # Check if username already exists
        existing_user = mongo.db.users.find_one({"username": username})
        if existing_user:
            flash("Username already exists!", "danger")
            return render_template("register.html")
        
        # Create new user
        hashed_password = hash_password(password)
        mongo.db.users.insert_one({
            "username": username,
            "password": hashed_password,
            "role": "user"  # Default role is user
        })
        
        flash("Registration successful! You can now login.", "success")
        return redirect(url_for("login"))
        
    return render_template("register.html")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))

# Run Flask App
if __name__ == "__main__":
    initialize_admin()  # Create admin account if it doesn't exist
    app.run(debug=True)