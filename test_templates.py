from flask import Flask, render_template
import os

app = Flask(__name__)

def test_templates():
    """Teste si tous les templates existent"""
    templates_dir = "templates"
    required_templates = [
        'base.html',
        'login.html', 
        'dashboard.html',
        'abonnes.html',
        'factures.html',
        'compteurs/liste.html',
        'compteurs/form.html'
    ]
    
    print("🧪 TEST DES TEMPLATES FORAGIS")
    print("=" * 40)
    
    # Vérifie si le dossier templates existe
    if not os.path.exists(templates_dir):
        print("❌ CRITIQUE: Le dossier 'templates/' n'existe pas!")
        return False
    
    print(f"✅ Dossier 'templates/' trouvé")
    
    # Teste chaque template
    all_ok = True
    for template in required_templates:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            print(f"✅ {template} - OK")
        else:
            print(f"❌ {template} - MANQUANT!")
            all_ok = False
    
    print("=" * 40)
    
    if all_ok:
        print("🎉 TOUS LES TEMPLATES SONT PRÊTS!")
        return True
    else:
        print("⚠️  Certains templates manquent. Création...")
        create_missing_templates()
        return False

def create_missing_templates():
    """Crée les templates manquants"""
    templates = {
        'base.html': '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FORAGIS - {% block title %}Gestion des Eaux{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-tint"></i> FORAGIS
            </a>
        </div>
    </nav>
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
</body>
</html>''',

        'login.html': '''{% extends "base.html" %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card shadow">
            <div class="card-body p-5">
                <h2 class="text-center mb-4">FORAGIS</h2>
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label">Nom d'utilisateur</label>
                        <input type="text" name="username" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Mot de passe</label>
                        <input type="password" name="password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Se connecter</button>
                </form>
                <div class="mt-3 text-center">
                    <small class="text-muted">admin / admin123</small>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

        'dashboard.html': '''{% extends "base.html" %}
{% block content %}
<h1>Tableau de Bord FORAGIS</h1>
<div class="row">
    <div class="col-md-4 mb-3">
        <div class="card text-white bg-primary">
            <div class="card-body">
                <h5>Abonnés Actifs</h5>
                <h2>{{ stats.abonnes_actifs }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-3">
        <div class="card text-white bg-success">
            <div class="card-body">
                <h5>Factures Payées</h5>
                <h2>{{ stats.factures_payees }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-3">
        <div class="card text-white bg-warning">
            <div class="card-body">
                <h5>En Attente</h5>
                <h2>{{ stats.factures_impayees }}</h2>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

        'abonnes.html': '''{% extends "base.html" %}
{% block content %}
<h1>Liste des Abonnés</h1>
<table class="table table-striped">
    <thead>
        <tr><th>Nom</th><th>Prénom</th><th>CNIB</th><th>Téléphone</th></tr>
    </thead>
    <tbody>
        {% for abonne in abonnes %}
        <tr>
            <td>{{ abonne.nom }}</td>
            <td>{{ abonne.prenom }}</td>
            <td>{{ abonne.cnib }}</td>
            <td>{{ abonne.telephone or 'N/A' }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}''',

        'factures.html': '''{% extends "base.html" %}
{% block content %}
<h1>Liste des Factures</h1>
<table class="table table-striped">
    <thead>
        <tr><th>ID</th><th>Abonné</th><th>Montant</th><th>Statut</th></tr>
    </thead>
    <tbody>
        {% for facture in factures %}
        <tr>
            <td>#{{ facture.id }}</td>
            <td>{{ facture.abonne.nom }}</td>
            <td>{{ facture.montant_total }} F</td>
            <td><span class="badge bg-{{ 'success' if facture.statut == 'payé' else 'warning' }}">{{ facture.statut }}</span></td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}''',

        'compteurs/liste.html': '''{% extends "base.html" %}
{% block content %}
<h1>Gestion des Compteurs</h1>
<table class="table table-striped">
    <thead>
        <tr><th>Numéro</th><th>Abonné</th><th>Localisation</th><th>Statut</th></tr>
    </thead>
    <tbody>
        {% for compteur in compteurs %}
        <tr>
            <td>{{ compteur.numero_compteur }}</td>
            <td>{{ compteur.abonne.nom }}</td>
            <td>{{ compteur.localisation or 'N/A' }}</td>
            <td><span class="badge bg-{{ 'success' if compteur.actif else 'secondary' }}">{{ 'Actif' if compteur.actif else 'Inactif' }}</span></td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}''',

        'compteurs/form.html': '''{% extends "base.html" %}
{% block content %}
<h1>{{ title }}</h1>
<form method="POST">
    <div class="mb-3">
        <label class="form-label">Numéro du compteur</label>
        <input type="text" name="numero_compteur" class="form-control" required>
    </div>
    <div class="mb-3">
        <label class="form-label">Abonné</label>
        <select name="abonne_id" class="form-control" required>
            <option value="">Sélectionner un abonné</option>
            {% for abonne in abonnes %}
            <option value="{{ abonne.id }}">{{ abonne.nom }} {{ abonne.prenom }}</option>
            {% endfor %}
        </select>
    </div>
    <div class="mb-3">
        <label class="form-label">Localisation</label>
        <textarea name="localisation" class="form-control" rows="3"></textarea>
    </div>
    <div class="mb-3 form-check">
        <input type="checkbox" name="actif" class="form-check-input" checked>
        <label class="form-check-label">Compteur actif</label>
    </div>
    <button type="submit" class="btn btn-primary">Enregistrer</button>
</form>
{% endblock %}'''
    }
    
    # Crée le dossier compteurs s'il n'existe pas
    os.makedirs('templates/compteurs', exist_ok=True)
    
    # Crée chaque template manquant
    for template_name, content in templates.items():
        template_path = os.path.join('templates', template_name)
        if not os.path.exists(template_path):
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📄 Créé: {template_name}")
    
    print("✅ Tous les templates ont été créés!")

if __name__ == '__main__':
    # Lance le test
    if test_templates():
        print("\n🚀 TEST RÉUSSI! L'application peut démarrer.")
    else:
        print("\n🔧 Templates créés. Relance le test.")
        test_templates()