from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ✅ MongoDB Connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/movie_booking"
mongo = PyMongo(app)

# ✅ Home Page for Users
@app.route("/login")
def home():
    movies = list(mongo.db.movies.find({"time": {"$exists": True, "$ne": ""}}))  
    return render_template("index.html", movies=movies)

# ✅ Home Page for Admins
@app.route("/admin_home")
def admin_home():
    if "username" not in session or session.get("role") != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    
    movies = list(mongo.db.movies.find())
    return render_template("admin_home.html", movies=movies)

# ✅ User Booking Page
@app.route("/bookings")
def view_bookings():
    if "username" not in session or session.get("role") != "user":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    
    user_bookings = mongo.db.bookings.find({"user": session["username"]})
    return render_template("bookings.html", bookings=user_bookings)

# ✅ Booking a Movie
@app.route("/book/<movie_id>", methods=["GET", "POST"])
def book_movie(movie_id):
    movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)})

    if request.method == "POST":
        user_name = session["username"]  # Use session username to ensure correct user
        seats = request.form["seats"]

        mongo.db.bookings.insert_one({
            "user": user_name,
            "movie_id": movie_id,
            "movie_name": movie["title"],
            "show_time": movie["time"],
            "seats": seats
        })

        flash("Booking Successful!", "success")
        return redirect(url_for("view_bookings"))

    return render_template("book.html", movie=movie)

# ✅ Admin Page (View & Add Movies)
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "username" not in session or session.get("role") != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        movie_title = request.form["title"]
        movie_time = request.form["time"]
        mongo.db.movies.insert_one({"title": movie_title, "time": movie_time})
        flash("Movie Added Successfully!", "success")
        return redirect(url_for("admin"))
    
    movies = list(mongo.db.movies.find())
    return render_template("admin.html", movies=movies)

# ✅ View All Bookings (Admin)
@app.route("/admin/bookings")
def admin_bookings():
    if "username" not in session or session.get("role") != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    
    all_bookings = mongo.db.bookings.find()
    return render_template("admin_bookings.html", bookings=all_bookings)

# ✅ Delete Movie (Admin Only)
@app.route("/delete_movie/<movie_id>", methods=["POST"])
def delete_movie(movie_id):
    if "username" not in session or session.get("role") != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("admin"))
    
    mongo.db.movies.delete_one({"_id": ObjectId(movie_id)})
    flash("Movie deleted successfully", "success")
    return redirect(url_for("admin"))

# ✅ Login Page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        role = request.form["role"]  # 'user' or 'admin'
        
        session["username"] = username
        session["role"] = role  # Store role in session

        if role == "admin":
            return redirect(url_for("admin_home"))
        else:
            return redirect(url_for("home"))

    return render_template("login.html")

# ✅ Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))

# ✅ Run Flask App
if __name__ == "__main__":
    app.run(debug=True)