# Formulaire simplifié sans WTForms
class CompteurForm:
    def __init__(self, numero_compteur=None, abonne_id=None, localisation=None, actif=True):
        self.numero_compteur = numero_compteur
        self.abonne_id = abonne_id
        self.localisation = localisation
        self.actif = actif
        self.errors = {}
    
    def validate(self):
        self.errors = {}
        if not self.numero_compteur or len(self.numero_compteur) < 3:
            self.errors['numero_compteur'] = ['Le numéro de compteur est requis (min 3 caractères).']
        if not self.abonne_id:
            self.errors['abonne_id'] = ['Veuillez sélectionner un abonné.']
        return len(self.errors) == 0