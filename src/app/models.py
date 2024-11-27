from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db, login_manager

db = SQLAlchemy()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    profile_picture = db.Column(db.String(20), nullable=False, default='default.jpg')
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.profile_picture}')"

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    genre = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)

class TVShow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    seasons = db.Column(db.Integer, nullable=False)
    episodes = db.Column(db.Integer, nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    genre = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)

class FavoritesList(db.Model):
    __tablename__ = 'favorites_list'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)

class Recommendation(db.Model):
    __tablename__ = 'recommendation'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    source_id = db.Column(db.Integer, nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)
    tvshow_id = db.Column(db.Integer, nullable=False)