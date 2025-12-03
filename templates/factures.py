{% extends "base.html" %}

{% block content %}
<h1 class="mb-4">Liste des Factures</h1>

<div class="card shadow">
    <div class="card-body">
        {% if factures %}
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Abonné</th>
                        <th>Compteur</th>
                        <th>Montant</th>
                        <th>Statut</th>
                        <th>Date Création</th>
                    </tr>
                </thead>
                <tbody>
                    {% for facture in factures %}
                    <tr>
                        <td>#{{ facture.id }}</td>
                        <td>{{ facture.abonne.nom }} {{ facture.abonne.prenom }}</td>
                        <td>{{ facture.compteur.numero_compteur if facture.compteur else 'N/A' }}</td>
                        <td>{{ facture.montant_total }} F</td>
                        <td>
                            <span class="badge bg-{{ 'success' if facture.statut == 'payé' else 'warning' }}">
                                {{ facture.statut }}
                            </span>
                        </td>
                        <td>{{ facture.date_creation.strftime('%d/%m/%Y') }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <p class="text-muted">Aucune facture pour le moment.</p>
        {% endif %}
    </div>
</div>
{% endblock %}