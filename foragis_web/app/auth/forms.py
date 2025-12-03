# Solution sans Flask-WTF pour éviter les problèmes de compatibilité
class LoginForm:
    def __init__(self, username=None, password=None, remember_me=False):
        self.username = username
        self.password = password
        self.remember_me = remember_me
        self.errors = {}
    
    def validate(self):
        self.errors = {}
        if not self.username:
            self.errors['username'] = ['Le nom d\'utilisateur est requis.']
        if not self.password:
            self.errors['password'] = ['Le mot de passe est requis.']
        return len(self.errors) == 0