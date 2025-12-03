# app/abonnes/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp
from app.models import Abonne

class AbonneForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired(), Length(max=100)])
    prenom = StringField('Prénom', validators=[DataRequired(), Length(max=100)])
    cnib = StringField('CNIB', validators=[DataRequired(), Length(max=50)])
    telephone = StringField('Téléphone', validators=[Length(max=20)])
    adresse = TextAreaField('Adresse')
    submit = SubmitField('Enregistrer')