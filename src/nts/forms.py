from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import Form, BooleanField, StringField, PasswordField, validators, SubmitField, TextAreaField, SelectField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from nts.models import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=4)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up',)

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'That username is taken please take different one')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'That email is taken please take different one')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login',)


class DeleteForm(FlaskForm):
    password = PasswordField('New Password')
    confirm_password = PasswordField(
        'Confirm New Password', validators=[EqualTo('password')])
    submit = SubmitField('Delete Profile',)


class AddNoteForm(FlaskForm):
    title = StringField('Title', validators=[Length(min=0, max=55)])
    content = TextAreaField('Description', validators=[
                            Length(min=1, max=10000)])
    privacy = SelectField('Select privacy of note',
                          choices=['Public', 'Private'])
    picture = FileField('Upload background picture', validators=[
                        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add note')


class EditNoteForm(FlaskForm):
    title = StringField('Title', validators=[Length(min=0, max=55)])
    content = TextAreaField('Description', validators=[
                            Length(min=1, max=10000)])
    privacy = SelectField('Select privacy of note',
                          choices=['Public', 'Private'])
    picture = FileField('Upload background picture', validators=[
                        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(
                'There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class AccountSettings(FlaskForm):
    username = StringField('Username', validators=[Length(min=2, max=20)])
    email = StringField('Email', validators=[Email()])
    submit = SubmitField('Update Profile')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    'That username is taken please take different one')

        def validate_email(self, email):
            if email.data != current_user.email:
                user = User.query.filter_by(email=email.data).first()
                if user:
                    raise ValidationError(
                        'That email is taken please take different one')


class SecuritySettings(FlaskForm):
    old_password = PasswordField('Old Password')
    password = PasswordField('New Password', validators=[Length(min=4)])
    confirm_password = PasswordField(
        'Confirm New Password', validators=[EqualTo('password')])
    submit = SubmitField('Update Profile')


class ProfileSettings(FlaskForm):
    picture = FileField('Update Profile Picture', validators=[
                        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Profile')
