from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    about = db.Column(db.String)
    admin = db.Column(db.Boolean)
    passwd = db.Column(db.LargeBinary)

    def __str__(self):
        return f'{self.id},{self.name}'