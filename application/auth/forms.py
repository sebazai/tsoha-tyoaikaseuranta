from flask_wtf import FlaskForm
from sqlalchemy.sql import text
from application import db
from application.project.models import choices_registration_form
from wtforms import PasswordField, StringField, validators, BooleanField, SelectField

class LoginForm(FlaskForm):
    username = StringField("Käyttäjätunnus", [validators.Required()])
    password = PasswordField("Salasana", [validators.Required()])

    class Meta:
        csrf = False

class RegistrationForm(FlaskForm):
    res = choices_registration_form()
    username = StringField("Uusi tunnus", [validators.Length(min=2, max=144)])
    password = PasswordField("Salasana", [validators.Length(min=8, max=144)])
    name = StringField("Nimi", [validators.Length(min=2, max=144)])
    paaprojekti = SelectField('Aseta projekti', coerce=int, choices = [(project.id, project.name) for project in res],validators=[validators.optional()]) 
    isadmin = BooleanField("Pääkäyttäjä")

    class Meta:
        csrf = False

class UpdateForm(FlaskForm):
    name = StringField("Nimi", [validators.Length(min=2, max=144)])
    password = PasswordField("Uusi salasana", [validators.Length(min=8, max=144), validators.optional()])

    class Meta:
        csrf = False


