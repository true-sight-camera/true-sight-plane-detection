from flask import Flask, request, send_file
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
  pass

app = Flask(__name__)
app.debug=True
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost:5432/capstone"

CORS(app)
db = SQLAlchemy(app, model_class=Base)

# with app.app_context():
#   from plane_detection.models import Images, Users
#   db.create_all()

from src import routes
# if __name__ == "__main__":
#   app.run(debug=True)
