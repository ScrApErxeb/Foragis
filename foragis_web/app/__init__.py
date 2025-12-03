from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Chemin ABSOLU pour la base de données
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, '..', 'data', 'foragis.db')
    
    # Configuration simple et directe
    app.config['SECRET_KEY'] = 'foragis-super-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    
    # Register blueprints
    from foragis_web.app.auth.routes import auth_bp
    from foragis_web.app.dashboard.routes import dashboard_bp
    from foragis_web.app.abonnes.routes import abonnes_bp
    from foragis_web.app.factures.routes import factures_bp
    from foragis_web.app.compteurs.routes import compteurs_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(abonnes_bp)
    app.register_blueprint(factures_bp)
    app.register_blueprint(compteurs_bp)
    
    return app