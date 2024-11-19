from flask import Flask
import os
import bcrypt

app = Flask('Incidents Web App')
# app.secret_key = os.environ['SECRET_KEY']
app.secret_key = 'you will never know'
