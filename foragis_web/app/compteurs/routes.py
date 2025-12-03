from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from foragis_web.app import db
from foragis_web.app.models import Compteur, Abonne
from foragis_web.app.compteurs.forms import CompteurForm

compteurs_bp = Blueprint('compteurs', __name__)

@compteurs_bp.route('/compteurs')
@login_required
def liste():
    compteurs_list = Compteur.query.join(Abonne).order_by(Abonne.nom).all()
    abonnes = Abonne.query.order_by(Abonne.nom).all()
    return render_template('compteurs/liste.html', compteurs=compteurs_list, abonnes=abonnes)

@compteurs_bp.route('/compteurs/nouveau', methods=['GET', 'POST'])
@login_required
def nouveau():
    abonnes = Abonne.query.order_by(Abonne.nom).all()
    
    if request.method == 'POST':
        form = CompteurForm(
            numero_compteur=request.form.get('numero_compteur'),
            abonne_id=request.form.get('abonne_id'),
            localisation=request.form.get('localisation'),
            actif=bool(request.form.get('actif'))
        )
        
        if form.validate():
            # Vérifier si le numéro de compteur existe déjà
            existing = Compteur.query.filter_by(numero_compteur=form.numero_compteur).first()
            if existing:
                flash('Ce numéro de compteur existe déjà!', 'danger')
                return render_template('compteurs/form.html', abonnes=abonnes, form=form, title="Nouveau Compteur")
            
            compteur = Compteur(
                numero_compteur=form.numero_compteur,
                abonne_id=int(form.abonne_id),
                localisation=form.localisation,
                actif=form.actif
            )
            
            db.session.add(compteur)
            db.session.commit()
            
            flash(f'Compteur {compteur.numero_compteur} ajouté avec succès!', 'success')
            return redirect(url_for('compteurs.liste'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(error, 'danger')
    
    return render_template('compteurs/form.html', abonnes=abonnes, title="Nouveau Compteur")

@compteurs_bp.route('/compteurs/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
def modifier(id):
    compteur = Compteur.query.get_or_404(id)
    abonnes = Abonne.query.order_by(Abonne.nom).all()
    
    if request.method == 'POST':
        form = CompteurForm(
            numero_compteur=request.form.get('numero_compteur'),
            abonne_id=request.form.get('abonne_id'),
            localisation=request.form.get('localisation'),
            actif=bool(request.form.get('actif'))
        )
        
        if form.validate():
            # Vérifier si le numéro existe déjà (sauf pour ce compteur)
            existing = Compteur.query.filter(
                Compteur.numero_compteur == form.numero_compteur,
                Compteur.id != id
            ).first()
            
            if existing:
                flash('Ce numéro de compteur existe déjà!', 'danger')
                return render_template('compteurs/form.html', abonnes=abonnes, compteur=compteur, title="Modifier Compteur")
            
            # Mettre à jour le compteur
            compteur.numero_compteur = form.numero_compteur
            compteur.abonne_id = int(form.abonne_id)
            compteur.localisation = form.localisation
            compteur.actif = form.actif
            
            db.session.commit()
            
            flash('Compteur modifié avec succès!', 'success')
            return redirect(url_for('compteurs.liste'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(error, 'danger')
    
    return render_template('compteurs/form.html', abonnes=abonnes, compteur=compteur, title="Modifier Compteur")

@compteurs_bp.route('/compteurs/<int:id>/supprimer', methods=['POST'])
@login_required
def supprimer(id):
    compteur = Compteur.query.get_or_404(id)
    
    # Vérifier s'il y a des factures associées
    if compteur.factures:
        flash('Impossible de supprimer ce compteur car il a des factures associées.', 'danger')
        return redirect(url_for('compteurs.liste'))
    
    db.session.delete(compteur)
    db.session.commit()
    
    flash('Compteur supprimé avec succès!', 'success')
    return redirect(url_for('compteurs.liste'))

@compteurs_bp.route('/api/compteurs/abonne/<int:abonne_id>')
@login_required
def get_compteurs_abonne(abonne_id):
    """API pour récupérer les compteurs d'un abonné"""
    compteurs = Compteur.query.filter_by(abonne_id=abonne_id, actif=True).all()
    result = [{'id': c.id, 'numero': c.numero_compteur} for c in compteurs]
    return jsonify(result)