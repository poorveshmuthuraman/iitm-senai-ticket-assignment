from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy


# app initialization
app = Flask(__name__)
api = Api(app)

# db config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)

# prevents circular imports
from ticketapp import routes 