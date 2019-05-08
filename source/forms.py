from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField,TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from source.models import user,score
from config import Config
from source import db
import sys



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):


    #print(playerChoices)
    username = StringField('Username*', validators=[DataRequired()])
    #firstname = StringField('Firstname', validators=[DataRequired()])
    firstname=SelectField('Player ID*',choices=[],validators=[DataRequired()])
#     lastname = StringField('Lastname')
    phone = StringField('Phone')
    email = StringField('Email')# validators=[Email()])
    password = PasswordField('Password*', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password*', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        userRegister = user.query.filter_by(username=username.data).first()
        if userRegister is not None:
            raise ValidationError('Please use a different username.')

#     def validate_email(self, email):
#         userRegister = user.query.filter_by(email=email.data).first()
#         if userRegister is not None:
#             raise ValidationError('Please use a different email address.')

#     def validate_phone(self, phone):
#         userRegister = user.query.filter_by(phone=phone.data).first()
#         if userRegister is not None:
#             raise ValidationError('Please use a different phone number.')

    def validate_firstname(self, firstname):
        userRegister = user.query.filter_by(firstName=firstname.data).first()
        if userRegister.username is not None:
            raise ValidationError('Player ID already in use')

class addPlayerForm(FlaskForm):
    playername=StringField('Player ID', validators=[DataRequired()])
    submit = SubmitField('Sumbit')

    def validate_playername(self, playername):
        addPlayer = user.query.filter_by(firstName=playername.data).first()
        if addPlayer is not None:
            raise ValidationError('Please use a different player name.')

class ScoreForm(FlaskForm):
    score_choice=[('0','0'),('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7')]
    player_1=StringField('player1')
    player_2=StringField('player2')
    player1_set1=SelectField('p1set1',choices=score_choice,validators=[DataRequired()])
    player1_set2=SelectField('P1Set2',choices=score_choice)
    player1_set3=SelectField('P2Set3',choices=score_choice)
    player2_set1=SelectField('Set1',choices=score_choice)
    player2_set2=SelectField('Set2',choices=score_choice)
    player2_set3=SelectField('Set3',choices=score_choice)
    submit = SubmitField('Submit')



class UploadForm(FlaskForm):
    file = FileField('excel',validators=[FileRequired(),FileAllowed(['xlsx'], 'Excel only!')])
    seasonName=StringField('Season Name', validators=[DataRequired()])

class FilterForm(FlaskForm):

    playerFilter_feild=SelectField('Player',choices=[(' ',' ')])
    deadlineFilter_feild=SelectField('Deadline',choices=[(' ',' ')])
    submit = SubmitField('Submit')
class PointTableForm(FlaskForm):

    divisionFilter_feild=SelectField('Division',choices=[(' ',' ')],validators=[DataRequired()])
    levelFilter_feild=SelectField('Level',choices=[(' ',' ')],validators=[DataRequired()])
    submit = SubmitField('Submit')
    clear = SubmitField('Clear')
