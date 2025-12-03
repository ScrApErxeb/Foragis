from foragis_web.app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='secretaire')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Abonne(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    cnib = db.Column(db.String(50), unique=True, nullable=False)
    telephone = db.Column(db.String(20))
    adresse = db.Column(db.Text)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    
    compteurs = db.relationship('Compteur', backref='abonne', lazy=True)
    factures = db.relationship('Facture', backref='abonne', lazy=True)
    
    def __repr__(self):
        return f'<Abonne {self.nom} {self.prenom}>'

class Compteur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_compteur = db.Column(db.String(50), unique=True, nullable=False)
    abonne_id = db.Column(db.Integer, db.ForeignKey('abonne.id'), nullable=False)
    actif = db.Column(db.Boolean, default=True)
    date_installation = db.Column(db.DateTime, default=datetime.utcnow)
    localisation = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<Compteur {self.numero_compteur}>'

class Facture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abonne_id = db.Column(db.Integer, db.ForeignKey('abonne.id'))
    compteur_id = db.Column(db.Integer, db.ForeignKey('compteur.id'))
    montant_total = db.Column(db.Float, nullable=False)
    statut = db.Column(db.String(20), default='non payé')
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_echeance = db.Column(db.DateTime)
    
    abonne = db.relationship('Abonne', backref='factures')
    compteur = db.relationship('Compteur', backref='factures')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))