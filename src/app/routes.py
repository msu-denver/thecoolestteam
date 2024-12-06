from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt, cache
from utils import fetch_poster
from ImdbScraper import videoScraper
from app.models import User, Movie, TVShow, Favorite, Recommendation, Review
from app.forms import RegistrationForm, LoginForm, ProfileForm, ReviewForm
from sqlalchemy.sql.expression import func
import random
import datetime
from flask_wtf import FlaskForm
from flask_caching import Cache

class DeleteForm(FlaskForm):
    pass

# Initialize Blueprint
main = Blueprint('main', __name__)

@main.route('/')
def home():
    # Take 10 movies and posters for the movie using featch poster
    movies = Movie.query.order_by(func.random()).limit(10).all()
    tvshows = TVShow.query.order_by(func.random()).limit(10).all()
    for movie in movies:
        if not movie.poster_url or movie.poster_url == 'https://via.placeholder.com/300x450.png?text=No+Image':
            movie.poster_url = fetch_poster(movie.id, 'movie')
            db.session.commit()

    for tvshow in tvshows:
        if not tvshow.poster_url or tvshow.poster_url == 'https://via.placeholder.com/300x450.png?text=No+Image':
            tvshow.poster_url = fetch_poster(tvshow.id, 'series')
            db.session.commit()


    
    return render_template('home.html', movies=movies, tvshows=tvshows)


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

# MEDIA DETAIL ROUTE
@main.route('/media/<string:media_type>/<string:media_id>', methods=['GET', 'POST'])
def media_detail(media_type, media_id):

    if media_type == 'movie':
        media = Movie.query.get_or_404(media_id)
    else:
        media = TVShow.query.get_or_404(media_id)
    
    reviews = Review.query.filter_by(movie_id=media.id if media_type == 'movie' else None, tvshow_id=media.id if media_type == 'tvshow' else None).all()
    delete_form = DeleteForm()

    dt = datetime.datetime.now() 
    access_time = int(dt.strftime("%H%M")) # military time for easy comparison


    if media.poster_url == 'https://via.placeholder.com/300x450.png?text=No+Image' or None or "N/A":
        media.poster_url = fetch_poster(media.id, 'movie' if media_type == 'movie' else 'series')
        db.session.commit()

    if media.trailer_fetch_time == None: # check if the trailer exists in database already
        trailer = videoScraper(media.id)
        media.trailer_fetch_time = access_time 
        media.trailer_url = trailer
        db.session.commit()

    if (abs(access_time - media.trailer_fetch_time)) >= 100 :  # check if movie trailer in database has expired, if so, fetch a new one and update the fetch time
        trailer = videoScraper(media.id)
        media.trailer_url = trailer
        media.trailer_fetch_time = int(dt.strftime("%H%M")) 
        db.session.commit()
        
    if request.method == 'POST':
        data = request.get_json()
        rating = data.get('rating')
        comment = data.get('comment')
        newID = db.session.query(func.max(Review.id)).scalar() + 1 if db.session.query(func.max(Review.id)).scalar() else 1

        if media_type == 'movie':
            for user_review in current_user.reviews:
                if user_review.movie_id == media_id:
                    return jsonify({'success': False, 'message': 'You already have a review for this movie'})
        else:
            for user_review in current_user.reviews:
                if user_review.tvshow_id == media_id:
                    return jsonify({'success': False, 'message': 'You already have a review for this TV show'})

        try:
            review = Review(
                id=newID,
                user_id=current_user.id, 
                rating=rating, 
                comment=comment, 
                movie_id=media_id if media_type == 'movie' else None,
                tvshow_id=media_id if media_type == 'tvshow' else None,
                author=current_user
            )
            db.session.add(review)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})

    return render_template('media_detail.html', media=media, reviews=reviews, form=delete_form, media_type=media_type, trailer=media.trailer_url)

@main.route('/profile/settings', methods=['GET', 'POST'])
@login_required
def profile_settings():
    form = ProfileForm()
    if form.validate_on_submit():
        tempPassword = current_user.password
        try:
            # Update the user's password
            if form.newPassword.data != None:
                if bcrypt.check_password_hash(current_user.password, form.oldPassword.data):
                    # Check if new password is different from the old one
                    if form.newPassword.data != form.oldPassword.data:
                        current_user.password = bcrypt.generate_password_hash(form.newPassword.data).decode('utf-8')
                        db.session.commit()
                        flash('Password updated successfully', 'success')
                        return redirect(url_for('main.profile_settings'))  # Redirect to profile settings page
                    else:
                        db.session.commit()
                        flash('New password cannot be the same as the old password.', 'danger')
                        return redirect(url_for('main.profile_settings'))  # Redirect to profile settings page
                else:
                    db.session.commit()
                    flash('Old password is incorrect', 'danger')
                    return redirect(url_for('main.profile_settings'))  # Redirect to profile settings page
            if form.newPassword.data == None:
                current_user.password = tempPassword
                db.session.commit()
                return redirect(url_for('main.profile_settings'))  # Redirect to profile settings page
            # Update the user's email
            if form.newEmail.data != current_user.email:
                if User.query.filter_by(email=form.newEmail.data).first():
                    flash('Email is already taken','danger')
                    return redirect(url_for('main.profile_settings'))  # Redirect to profile settings page
                else:   
                    current_user.email = form.newEmail.data
                    db.session.commit()
                    flash('Email updated successfully', 'success')
                    return redirect(url_for('main.profile_settings'))  # Redirect to profile settings page
            # Update the user's username
            if form.newUsername.data != current_user.username:
                if User.query.filter_by(username=form.newUsername.data).first():
                    flash('Username is already taken','danger')
                    return redirect(url_for('main.profile_settings'))  # Redirect to profile settings page
                else:
                    current_user.username = form.newUsername.data
                    db.session.commit()
                    flash('Username updated successfully', 'success')
                    return redirect(url_for('main.profile_settings'))  # Redirect to profile settings page
            return redirect(url_for('main.profile_settings'))
        except Exception as e:
            db.session.rollback()
            flash(e, 'danger')
            print(e)
    return render_template('profile_settings.html', form=form)

@main.route('/profile/<string:id>', methods=['GET', 'POST'])
@login_required
def profile(id):
    user = User.query.get_or_404(id)
    return render_template('profile.html', user=user)

@main.route('/admin')
@login_required
def admin():
    if current_user.is_admin == False:
        flash("You are not authorized to access this page.")
        return redirect(url_for('main.home'))
    
    if current_user.id == id:
        flash("You cannot change your own admin status.")
        return redirect(url_for('main.admin'))
    
    user = User.query.get(id)
    if user:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f"User {user.username} is now {'an admin' if user.is_admin else 'not an admin'}")
    
    return render_template('admin.html')

@main.route('/add_to_favorites/<string:media_type>/<string:media_id>', methods=['POST'])
@login_required
def add_to_favorites(media_type, media_id):
    if media_type == 'movie':
        media = Movie.query.get_or_404(media_id)
    else:
        media = TVShow.query.get_or_404(media_id)
    
    favorite = Favorite.query.filter_by(user_id=current_user.id, movie_id=media.id if media_type == 'movie' else None, tvshow_id=media.id if media_type == 'tvshow' else None).first()
    if favorite:
        return jsonify({'success': False, 'message': f'{media.title} is already in your favorites.'})
    
    favorite = Favorite(user_id=current_user.id, movie_id=media.id if media_type == 'movie' else None, tvshow_id=media.id if media_type == 'tvshow' else None)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({'success': True, 'message': f'{media.title} has been added to your favorites.'})

@main.route('/remove_from_favorites/<string:media_type>/<string:media_id>', methods=['POST'])
@login_required
def remove_from_favorites(media_type, media_id):
    if media_type == 'movie':
        media = Movie.query.get_or_404(media_id)
    else:
        media = TVShow.query.get_or_404(media_id)
    
    favorite = Favorite.query.filter_by(user_id=current_user.id, movie_id=media.id if media_type == 'movie' else None, tvshow_id=media.id if media_type == 'tvshow' else None).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'success': True, 'message': f'{media.title} has been removed from your favorites.'})
    return jsonify({'success': False, 'message': f'{media.title} is not in your favorites.'})

@main.route('/clear_favorites', methods=['POST'])
@login_required
def clear_favorites():
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    for favorite in favorites:
        db.session.delete(favorite)
    db.session.commit()
    return jsonify({'success': True, 'message': 'All favorites have been cleared.'})

@main.route('/favorites')
@login_required
def favorites():
    user_favorites = current_user.favorites.all()
    favorite_movies = [fav.movie for fav in user_favorites if fav.movie_id]
    favorite_tvshows = [fav.tv_show for fav in user_favorites if fav.tvshow_id]
    return render_template('favorites.html', favorite_movies=favorite_movies, favorite_tvshows=favorite_tvshows)

# RANDOM ROUTE
@main.route('/random')
@login_required
def random_route():
    choice = random.choice(['movie', 'tvshow'])
    
    if choice == 'movie':
        random_media = Movie.query.order_by(func.random()).first()
    else:
        random_media = TVShow.query.order_by(func.random()).first()
    
    if random_media:
        if not random_media.poster_url or random_media.poster_url == 'https://via.placeholder.com/300x450.png?text=No+Image':
            random_media.poster_url = fetch_poster(random_media.id, 'movie' if choice == 'movie' else 'series')
            db.session.commit()
        return redirect(url_for('main.media_detail', media_type=choice, media_id=random_media.id))
    else:
        flash(f'No {choice}s available.', 'warning')
        return redirect(url_for('main.mainpage'))

@main.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '', type=str)
    
    # Fetch matching movies and TV shows
    movies = Movie.query.filter(Movie.title.ilike(f"%{query}%")).all()
    tv_shows = TVShow.query.filter(TVShow.title.ilike(f"%{query}%")).all()

    # Combine results with their IDs
    results = [
        {'id': movie.id, 'title': movie.title, 'type': 'movie'} for movie in movies
    ] + [
        {'id': tv_show.id, 'title': tv_show.title, 'type': 'tv_show'} for tv_show in tv_shows
    ]

    return jsonify(results)

@main.route('/search_results', methods=['GET'])
def search_results():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    cache_key = f'search_results_{query}_{page}'

    results = cache.get(cache_key)
    if not results:
        movies = Movie.query.filter(Movie.title.ilike(f"%{query}%")).order_by(Movie.title.desc()).paginate(page=page, per_page=10, error_out=False)
        tv_shows = TVShow.query.filter(TVShow.title.ilike(f"%{query}%")).order_by(TVShow.title.desc()).paginate(page=page, per_page=10, error_out=False)
        results = {
            'movies': movies.items,
            'tv_shows': tv_shows.items,
            'has_next': movies.has_next or tv_shows.has_next,
            'has_prev': movies.has_prev or tv_shows.has_prev
        }
        cache.set(cache_key, results, timeout=300)  # Cache for 5 minutes

    return render_template('search_results.html', query=query, results=results, page=page)

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

@main.route('/delete_review/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    if not current_user.is_admin:
        flash('You are not authorized to delete this review.', 'danger')
        return redirect(url_for('main.home'))
    try:
        db.session.delete(review)
        db.session.commit()
        flash('Review deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting review: {str(e)}', 'danger')
    return redirect(request.referrer)