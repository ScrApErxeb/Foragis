# app/factures/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime, timedelta

class FactureForm(FlaskForm):
    abonne_id = SelectField('Abonné', coerce=int, validators=[DataRequired()])
    compteur_id = SelectField('Compteur', coerce=int, validators=[DataRequired()])
    mois = StringField('Mois', validators=[DataRequired()], 
                      default=datetime.now().strftime('%Y-%m'))
    volume_m3 = DecimalField('Volume (m³)', validators=[DataRequired(), NumberRange(min=0)])
    date_echeance = DateField('Date d\'échéance', 
                             default=datetime.now() + timedelta(days=30))
    submit = SubmitField('Générer la Facture')

class PaiementForm(FlaskForm):
    montant = DecimalField('Montant', validators=[DataRequired(), NumberRange(min=0.01)])
    mode_paiement = SelectField('Mode de paiement', 
                               choices=[('cash', 'Espèces'), ('carte', 'Carte'), 
                                       ('virement', 'Virement'), ('mobile', 'Mobile Money')])
    reference = StringField('Référence')
    submit = SubmitField('Enregistrer le Paiement')

class ReleveForm(FlaskForm):
    compteur_id = SelectField('Compteur', coerce=int, validators=[DataRequired()])
    mois = StringField('Mois', validators=[DataRequired()],
                      default=datetime.now().strftime('%Y-%m'))
    volume_m3 = DecimalField('Volume consommé (m³)', 
                           validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Enregistrer le Relevé')