from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Optional
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=2, max=20)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired()
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ReviewForm(FlaskForm):

    comment = TextAreaField('Comment', validators=[
        DataRequired()
    ])

    rating = IntegerField ('Rating', validators=[
        DataRequired(), NumberRange(min=0, max=10, message="Rating must be a number from 0 to 10 ")
    ])

    submit = SubmitField('Post Review')
    
class ProfileForm(FlaskForm):
    oldPassword = StringField('Old Password', validators=[Optional()])
    newPassword = StringField('New Password', validators=[Optional()])
    newEmail = StringField('New Email', validators=[Optional()])
    newUsername = StringField('New Username', validators=[Optional()])
    newProfilepicture = FileField('New Profile Picture', validators=[Optional()])
    changePassword = SubmitField('Change Password')
    changeEmail = SubmitField('Change Email')
    changeUsername = SubmitField('Change Username')
    changeProfilepicture = SubmitField('Change Profile Picture')