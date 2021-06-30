from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '6599acefd823b2f1826d75cb4bec276e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

db = SQLAlchemy(app)

from blogger import routes
