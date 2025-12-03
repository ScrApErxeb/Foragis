

from flask import Blueprint, render_template
from flask_login import login_required 
from foragis_web.app.models import Abonne

abonnes_bp = Blueprint('abonnes', __name__)

@abonnes_bp.route('/abonnes')
@login_required
def liste():
    abonnes_list = Abonne.query.all()
    return render_template('abonnes/liste.html', abonnes=abonnes_list)