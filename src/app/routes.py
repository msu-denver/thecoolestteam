from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from utils import fetch_poster
from app.models import User, Movie, TVShow, Favorite, Recommendation, Review
from app.forms import RegistrationForm, LoginForm, ReviewForm
from sqlalchemy.sql.expression import func
import random
from datetime import datetime

# Initialize Blueprint
main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.mainpage'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.mainpage'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.mainpage'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('signup.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

@main.route('/mainpage')
@login_required
def mainpage():
    return render_template('mainpage.html')  # Ensure this template exists


## MOVIE ROUTE ##

@main.route('/movie/<int:movie_id>', methods=['GET', 'POST'])
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    reviews =  Review.query.filter_by(movie_id = movie.id).all()

    if movie.poster_url == 'https://via.placeholder.com/300x450.png?text=No+Image' or None or "N/A":

        movie.poster_url = fetch_poster(movie.title, 'movie')
        db.session.commit()

    return render_template('movie_detail.html', movie=movie, reviews=reviews)


## TV SHOW ROUTE ##
@main.route('/tvshow/<int:tvshow_id>', methods=['GET', 'POST'])
def tvshow_detail(tvshow_id):
    tvshow = TVShow.query.get_or_404(tvshow_id)
    reviews =  Review.query.filter_by(tvshow_id = tvshow.id).all()
    
    if tvshow.poster_url == 'https://via.placeholder.com/300x450.png?text=No+Image' or None:
        tvshow.poster_url = fetch_poster(tvshow.title, 'series')
        db.session.commit()

    return render_template('tvshow_detail.html', tvshow=tvshow, reviews=reviews)


## MOVIE REVIEW ROUTE ##
@main.route('/movie_review/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def movie_review(movie_id):
    form = ReviewForm()
    lastReview = db.session.query(Review).order_by(Review.id.desc()).first() # obtains most recent review in database
    movie =  Movie.query.filter_by(id=movie_id).first()
    newID = 0

    for user_review in current_user.reviews:
        if user_review.movie_id == movie_id:
            flash('You already have a review for this movie', 'danger')
            return redirect(url_for('main.movie_detail', movie_id=movie_id))

    if lastReview != None:
        newID = lastReview.id + 1 

    if form.validate_on_submit(): 

        try:
        
            review = Review (id=newID,
                            user_id=current_user.id, 
                            rating=form.rating.data, 
                            comment=form.comment.data, 
                            movie_id=movie_id, 
                            author=current_user)
            
            db.session.add(review)
            db.session.commit()

        except Exception as e:
                
                db.session.rollback()  # Rollback in case of an error
                flash(e, 'danger')
                return render_template('movie_review.html', form=form, movie=movie)

        return redirect(url_for('main.movie_detail', movie_id=movie_id))
    
    return render_template('movie_review.html', form=form, movie=movie)


## TV REVIEW ROUTE ##
@main.route('/tvshow_review/<int:tvshow_id>', methods=['GET', 'POST'])
@login_required
def tvshow_review(tvshow_id):
    form = ReviewForm()
    lastReview = db.session.query(Review).order_by(Review.id.desc()).first() # obtains most recent review in database
    tvshow =  TVShow.query.filter_by(id=tvshow_id).first()
    newID = 0

    for user_review in current_user.reviews:
        if user_review.tvshow_id == tvshow_id:
            flash('You already have a review for this tv show', 'danger')
            return redirect(url_for('main.tvshow_detail', tvshow_id=tvshow_id))

    if lastReview != None:
        newID = lastReview.id + 1 

    if form.validate_on_submit(): 
        
        try:

            review = Review (id=newID,
                            user_id=current_user.id, 
                            rating=form.rating.data, 
                            comment=form.comment.data, 
                            tvshow_id=tvshow_id,
                            author=current_user)
            
            db.session.add(review)
            db.session.commit()
        
        except Exception as e:
                
                db.session.rollback()  # Rollback in case of an error
                flash(e, 'danger')
                return render_template('tvshow_review.html', form=form, tvshow=tvshow)

        return redirect(url_for('main.tvshow_detail', tvshow_id=tvshow_id))
    
    return render_template('tvshow_review.html', form=form, tvshow=tvshow)

  

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@main.route('/favorites')
@login_required
def favorites():
    user_favorites = current_user.favorites.all()
    return render_template('favorites.html', favorites=user_favorites)

@main.route('/random')
@login_required
def random_route():  # Renamed function
    # Decide randomly to choose a movie or a TV show
    choice = random.choice(['movie', 'tvshow'])
    
    if choice == 'movie':
        # Fetch a random movie
        random_movie = Movie.query.order_by(func.random()).first()
        if random_movie:
            # Ensure poster_url is present
            if not random_movie.poster_url or random_movie.poster_url == 'https://via.placeholder.com/300x450.png?text=No+Image':
                random_movie.poster_url = fetch_poster(random_movie.title, 'movie')
                db.session.commit()
            return render_template('movie_detail.html', movie=random_movie)
        else:
            flash('No movies available.', 'warning')
            return redirect(url_for('main.mainpage'))
    
    else:
        # Fetch a random TV show
        random_tvshow = TVShow.query.order_by(func.random()).first()
        if random_tvshow:
            # Ensure poster_url is present
            if not random_tvshow.poster_url or random_tvshow.poster_url == 'https://via.placeholder.com/300x450.png?text=No+Image':
                random_tvshow.poster_url = fetch_poster(random_tvshow.title, 'series')
                db.session.commit()
            return render_template('tvshow_detail.html', tvshow=random_tvshow)
        else:
            flash('No TV shows available.', 'warning')
            return redirect(url_for('main.mainpage'))

@main.route('/search')
def search():
    query = request.args.get('query')
    if query:
        # Implement search logic here
        # For demonstration, we'll just flash the search query
        flash(f'Search functionality is not yet implemented. You searched for: {query}', 'info')
    return redirect(url_for('main.home'))

## ERROR HANDLING ##

@main.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


## DEBUGGING ##

@main.route('/debug_db')
def debug_db():
    movie_count = Movie.query.count()
    tvshow_count = TVShow.query.count()

    return f"Movies: {movie_count}, TV Shows: {tvshow_count}, Current User ID:{current_user.id}"
