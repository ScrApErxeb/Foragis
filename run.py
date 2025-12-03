from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# Configuration simple avec chemin de DB fixe
app = Flask(__name__)
app.config['SECRET_KEY'] = 'foragis-simple-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///foragis.db'  # Dans le répertoire courant
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modèles SIMPLIFIÉS
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='admin')
    
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
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)

class Compteur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_compteur = db.Column(db.String(50), unique=True, nullable=False)
    abonne_id = db.Column(db.Integer, db.ForeignKey('abonne.id'))
    actif = db.Column(db.Boolean, default=True)
    date_installation = db.Column(db.DateTime, default=datetime.utcnow)
    localisation = db.Column(db.String(200))
    
    abonne = db.relationship('Abonne', backref='compteurs')

class Facture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abonne_id = db.Column(db.Integer, db.ForeignKey('abonne.id'))
    compteur_id = db.Column(db.Integer, db.ForeignKey('compteur.id'))
    montant_total = db.Column(db.Float, nullable=False)
    statut = db.Column(db.String(20), default='non payé')
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    abonne = db.relationship('Abonne', backref='factures')
    compteur = db.relationship('Compteur', backref='factures')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes PRINCIPALES
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'abonnes_actifs': Abonne.query.count(),
        'factures_payees': Facture.query.filter_by(statut='payé').count(),
        'factures_impayees': Facture.query.filter(Facture.statut != 'payé').count(),
    }
    
    dernieres_factures = Facture.query.order_by(Facture.date_creation.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         dernieres_factures=dernieres_factures)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Connexion réussie!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))

@app.route('/abonnes')
@login_required
def abonnes():
    abonnes_list = Abonne.query.all()
    return render_template('abonnes.html', abonnes=abonnes_list)

@app.route('/compteurs')
@login_required
def compteurs():
    compteurs_list = Compteur.query.join(Abonne).order_by(Abonne.nom).all()
    abonnes = Abonne.query.order_by(Abonne.nom).all()
    return render_template('compteurs/liste.html', compteurs=compteurs_list, abonnes=abonnes)

@app.route('/compteurs/nouveau', methods=['GET', 'POST'])
@login_required
def nouveau_compteur():
    abonnes = Abonne.query.order_by(Abonne.nom).all()
    
    if request.method == 'POST':
        numero_compteur = request.form.get('numero_compteur')
        abonne_id = request.form.get('abonne_id')
        localisation = request.form.get('localisation')
        actif = bool(request.form.get('actif'))
        
        # Validation simple
        if not numero_compteur or len(numero_compteur) < 3:
            flash('Le numéro de compteur est requis (min 3 caractères).', 'danger')
            return render_template('compteurs/form.html', abonnes=abonnes, title="Nouveau Compteur")
        
        if not abonne_id:
            flash('Veuillez sélectionner un abonné.', 'danger')
            return render_template('compteurs/form.html', abonnes=abonnes, title="Nouveau Compteur")
        
        # Vérifier si le numéro existe déjà
        existing = Compteur.query.filter_by(numero_compteur=numero_compteur).first()
        if existing:
            flash('Ce numéro de compteur existe déjà!', 'danger')
            return render_template('compteurs/form.html', abonnes=abonnes, title="Nouveau Compteur")
        
        compteur = Compteur(
            numero_compteur=numero_compteur,
            abonne_id=int(abonne_id),
            localisation=localisation,
            actif=actif
        )
        
        db.session.add(compteur)
        db.session.commit()
        
        flash(f'Compteur {compteur.numero_compteur} ajouté avec succès!', 'success')
        return redirect(url_for('compteurs'))
    
    return render_template('compteurs/form.html', abonnes=abonnes, title="Nouveau Compteur")

@app.route('/factures')
@login_required
def factures():
    factures_list = Facture.query.all()
    return render_template('factures.html', factures=factures_list)

# Initialisation
def init_db():
    with app.app_context():
        # Créer les tables
        db.create_all()
        
        # Créer l'utilisateur admin s'il n'existe pas
        if not User.query.first():
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Utilisateur admin créé: admin / admin123")
            
        # Créer des données de test
        if not Abonne.query.first():
            # Abonnés
            abonne1 = Abonne(nom="Dupont", prenom="Jean", cnib="AB123456", telephone="0123456789")
            abonne2 = Abonne(nom="Martin", prenom="Marie", cnib="CD789012", telephone="0987654321")
            db.session.add_all([abonne1, abonne2])
            db.session.commit()
            
            # Compteurs
            compteur1 = Compteur(numero_compteur="COMP001", abonne_id=1, localisation="123 Rue Principale")
            compteur2 = Compteur(numero_compteur="COMP002", abonne_id=2, localisation="456 Avenue Centrale")
            db.session.add_all([compteur1, compteur2])
            db.session.commit()
            
            # Factures
            facture1 = Facture(abonne_id=1, compteur_id=1, montant_total=15000.0, statut="non payé")
            facture2 = Facture(abonne_id=2, compteur_id=2, montant_total=12000.0, statut="payé")
            db.session.add_all([facture1, facture2])
            db.session.commit()
            
            print("✅ Données de test créées (abonnés, compteurs, factures)")

if __name__ == '__main__':
    init_db()
    print("🚀 FORAGIS avec Compteurs démarré sur http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)