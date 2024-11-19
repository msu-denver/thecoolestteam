# Sprint Planning

Date/Time: 11/19/24
Participants: Jason/Jackson/Gage/Eldar/Sadeq

Goal Statement: 

- Decide color pallette. 

airport
![pics/colors/airport.png](pics/colors/airport.png)

cupcake
![pics/colors/cupcake.png](pics/colors/cupcake.png)

earth_fire
![pics/colors/earth_fire.png](pics/colors/earth_fire.png)

highway
![pics/colors/highway.png](pics/colors/highway.png)

- Decide User Story weights

US1 - User Registration/Authentication -    POINTS:
US2 - Login/Logout                          POINTS:
US3 - User Account Control                  POINTS: 
US4 - Admin Account Control                 POINTS:
US5 - Search Movies/TV                      POINTS:
US6 - List Filtered Search - Movies/TV      POINTS:
US7 - Movie/TV Object Page                  POINTS:
US8 - User Favorites List                   POINTS:
US9 - Movie/TV User Review                  POINTS:
US10 - Movie/TV Recommendation Page         POINTS:

## Sprint 1 Work Splits ##
- 

## API and Database Notes

# API
- API source - https://rapidapi.com/octopusteam-octopusteam-default/api/imdb236
    - limited at 300 requests/min
    - API Should be 'On-Demand: Query the API for fresh data only when requested by the user (e.g., streaming availability).
    - Have a strategy for handling API failures (e.g., use stale data from the database or display an error message).

# Database (PostgreSQL)
-   movies table: ID, title, release date, genre, synopsis, etc.
    users table: User profiles.
    favorites table: User favorites.
    reviews table: User reviews.

- For PostgreSQL:
    Use SQLAlchemy with the asyncpg driver for better performance with PostgreSQL.
    Consider Alembic for database migrations.

# Data Responsibilities
-Database: Movie/TV metadata (title, release date, genres), user-generated lists, and reviews.
-API: Real-time ratings, trending movies, streaming availability.

API Should be 'On-Demand: Query the API for fresh data only when requested by the user (e.g., streaming availability).