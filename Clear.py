from flask_pymongo import PyMongo
from flask import Flask

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/movie_booking"
mongo = PyMongo(app)

# Delete all bookings
mongo.db.bookings.delete_many({})

print("✅ All bookings have been deleted.")