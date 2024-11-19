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
class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    genre = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
class TVShow(db.Model):
    __tablename__ = 'tvshow'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    seasons = db.Column(db.Interger, nullable=False)
    episodes = db.Column(db.Interger, nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    genre = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
class Favorites_List(db.Model):
    __tablename__ = 'favorites_list'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
class Recommendation(db.Model):
    __tablename__ = 'recommendation'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable = False)
    user_id = db.Column(db.Integer, nullable=False)
    source_id = db.Column(db.Integer, nullable=False)
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)
    tvshow_id = db.Column(db.Integer, nullable=False)