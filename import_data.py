import csv
import os
from datetime import datetime
from app import create_app, db
from app.models import Movie, TVShow
from utils import fetch_poster  # Ensure utils.py has the fetch_poster function

app = create_app()

def import_data(csv_filepath):
    with app.app_context():
        with open(csv_filepath, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            total_rows = 0
            imported_movies = 0
            imported_tvshows = 0
            skipped_rows = 0

            for row in reader:
                total_rows += 1
                title = row.get('title', '').strip()
                type_ = row.get('type', '').strip().lower()  # 'movie' or 'tvshow'
                genres = row.get('genres', '').strip()
                averageRating = float(row.get('averageRating', 0)) if row.get('averageRating') else None
                numVotes = int(row.get('numVotes', 0)) if row.get('numVotes') else None
                releaseYear = int(row.get('releaseYear', 0)) if row.get('releaseYear') else None

                if not title or not type_:
                    print(f"Row {total_rows}: Missing required fields. Skipping.")
                    skipped_rows += 1
                    continue

                if type_ == 'movie':
                    # Check if the movie already exists to avoid duplicates
                    existing_movie = Movie.query.filter_by(title=title).first()
                    if existing_movie:
                        print(f"Row {total_rows}: Movie '{title}' already exists. Skipping.")
                        skipped_rows += 1
                        continue

                    poster_url = fetch_poster(title, 'movie')  # Fetch poster URL
                    movie = Movie(
                        title=title,
                        genre=genres,
                        averageRating=averageRating,
                        numVotes=numVotes,
                        releaseYear=releaseYear,
                        poster_url=poster_url or 'https://via.placeholder.com/300x450.png?text=No+Image'
                    )
                    db.session.add(movie)
                    imported_movies += 1

                elif type_ == 'tvshow':
                    # Check if the TV show already exists to avoid duplicates
                    existing_tvshow = TVShow.query.filter_by(title=title).first()
                    if existing_tvshow:
                        print(f"Row {total_rows}: TV Show '{title}' already exists. Skipping.")
                        skipped_rows += 1
                        continue

                    # Assign default values for missing fields
                    seasons = 1
                    episodes = 1
                    release_date = datetime(releaseYear, 1, 1) if releaseYear else datetime.utcnow()
                    description = 'No description available.'
                    rating = 5  # Default rating

                    poster_url = fetch_poster(title, 'series')  # Fetch poster URL
                    tvshow = TVShow(
                        title=title,
                        genre=genres,
                        seasons=seasons,
                        episodes=episodes,
                        release_date=release_date,
                        description=description,
                        rating=rating,
                        poster_url=poster_url or 'https://via.placeholder.com/300x450.png?text=No+Image'
                    )
                    db.session.add(tvshow)
                    imported_tvshows += 1

                else:
                    print(f"Row {total_rows}: Unknown type '{type_}'. Skipping.")
                    skipped_rows += 1
                    continue

            # Commit all changes to the database
            db.session.commit()
            print(f"Import Completed: {imported_movies} movies and {imported_tvshows} TV shows imported.")
            print(f"Total Rows Processed: {total_rows}, Skipped: {skipped_rows}")

if __name__ == '__main__':
    # Define the path to your CSV file
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'imdb_small.csv')
    
    if os.path.exists(csv_path):
        import_data(csv_path)
    else:
        print(f"CSV file not found at path: {csv_path}")
