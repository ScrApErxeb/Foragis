from flask import Blueprint, render_template
from flask_login import login_required
from foragis_web.app.models import Abonne, Facture

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    stats = {
        'abonnes_actifs': Abonne.query.count(),
        'factures_payees': Facture.query.filter_by(statut='payé').count(),
        'factures_impayees': Facture.query.filter(Facture.statut != 'payé').count(),
        'recettes_mois': 0
    }
    
    dernieres_factures = Facture.query.order_by(Facture.date_creation.desc()).limit(5).all()
    
    return render_template('dashboard/index.html',
                         stats=stats,
                         dernieres_factures=dernieres_factures)