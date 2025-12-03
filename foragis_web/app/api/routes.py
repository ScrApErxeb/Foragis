# app/api/routes.py
from flask import Blueprint, jsonify, request
from flask_login import login_required
from app import db
from app.models import Abonne, Facture, Paiement

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/abonnes/<int:abonne_id>', methods=['GET'])
@login_required
def get_abonne(abonne_id):
    abonne = Abonne.query.get_or_404(abonne_id)
    return jsonify({
        'id': abonne.id,
        'nom': abonne.nom,
        'prenom': abonne.prenom,
        'telephone': abonne.telephone,
        'factures': [
            {
                'id': f.id,
                'montant': f.montant_total,
                'statut': f.statut,
                'date_creation': f.date_creation.isoformat()
            } for f in abonne.factures
        ]
    })

@api_bp.route('/paiements/mobile', methods=['POST'])
def paiement_mobile():
    data = request.get_json()
    
    # Traitement paiement mobile money
    # Intégration avec les APIs de paiement
    return jsonify({'status': 'success', 'transaction_id': 'TX123456'})