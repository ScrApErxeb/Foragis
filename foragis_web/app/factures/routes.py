from flask import Blueprint, render_template
from flask_login import login_required 
from foragis_web.app.models import Facture

factures_bp = Blueprint('factures', __name__)

@factures_bp.route('/factures')
@login_required
def liste():
    factures_list = Facture.query.all()
    return render_template('factures/liste.html', factures=factures_list)