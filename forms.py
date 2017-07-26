import datetime
from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                               Length, EqualTo)
from wtforms.fields import DateField
from models import User


#the form argument represents 'RegisterForm' and the field represents 'username'.
def name_exists(form, field):
    """checks to see if the username already exists"""
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')


def email_exists(form, field):
    """checks to see if the email already exists"""
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')


class RegisterForm(Form):
    """creates the fields for our register form on the register page"""
    username = StringField(
        #the 'Username' will go as the label in html
        'Username',
        #the validators will make it required that there is data, and that it 
        #matches the regex. 
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, "
                         "numbers, and underscores only.")
            ),
            #name_exists is a validator we created above.
            name_exists
        ])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            #'Email()' checks to see if its a legitimate email. 
            Email(),
            email_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2', message='Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    )
    

class LoginForm(Form):
    """creates the login form fields for the login page"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    
    
class PostForm(Form):
    """creates the new entry form for creating a new entry"""
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("What you learned?", validators=[DataRequired()])
    resources_to_remember = TextAreaField(
        "Resources to remember. Enter the links seperated by commas. "
        "Ex: http://www.wikipedia.com/, https://www.youtube.com/", 
        validators=[DataRequired()]
        )
    time_spent = StringField("Time spent", validators=[DataRequired()])
    tags = StringField("Add tags seperated by commas. Ex: hobbies, poetry", 
        validators=[DataRequired()])
    timestamp = DateField(
        "Enter the date as example: yyyy-mm-dd", format='%Y-%m-%d',
        default=datetime.date.today, ## Now it will call it everytime.
        validators=[DataRequired()]
    )