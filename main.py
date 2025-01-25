from flask import Flask, request, send_file
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


app = Flask(__name__)
app.debug=True
CORS(app)

class Base(DeclarativeBase):
  pass

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost:5432/capstone"

db = SQLAlchemy(app)

# db.init_app(app)

# with app.app_context():
#   from plane_detection import models
#   db.create_all()

from plane_detection.src import routes

if __name__ == "__main__":
  app.run(debug=True)