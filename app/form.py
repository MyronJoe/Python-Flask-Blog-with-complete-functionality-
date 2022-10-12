from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from flask_ckeditor import CKEditorField


# search form
class SearchForm(FlaskForm):
    searched = StringField('Searched', validators=[DataRequired()])
    submit = SubmitField('Submit')


    # Registration form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])

    email = EmailField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sing Up')

    # checks if username is in database already
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken')

    # checks if email is in database already

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken')

    # login form

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])

    remember = BooleanField('Remember Me')

    submit = SubmitField('Sing Up')

    # update account form

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=10)])

    email = EmailField('Email', validators=[DataRequired(), Email()])

    picture = FileField('Picture Upload', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Update')

    # checks if username & email are in database already while updating account

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This user already exist, choose a different username')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('this user already exist, choose a different email')


    # creating post form

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])

    category = SelectField('Category', validators=[DataRequired()], choices=[('Entertainment', 'Entertainment'),
                                                                             ('Politics', 'Politics'),
                                                                             ('Sports', 'Sports'),
                                                                             ('Lifestyle', 'Lifestyle'),
                                                                             ('Metro', 'Metro'),
                                                                             ('Education', 'Education'),
                                                                             ('Business', 'Business'),
                                                                             ('Agriculture', 'Agriculture'),
                                                                             ('News', 'News')])

    # content = CKEditorField('content', validators=[DataRequired()])
    content = CKEditorField('content', validators=[DataRequired()])

    picture = FileField('Picture Upload', validators=[DataRequired(), FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Post')
