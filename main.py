import sys
from modules import factures, paiements, operations
from core import audit

def menu_principal():
    print("=== FORAGIS v0.8 ===")
    print("1. Gestion des factures")
    print("2. Gestion des paiements")
    print("3. Gestion des opérations")
    print("4. Audit du système")
    print("0. Quitter")
    return input("Choix: ")

def main():
    while True:
        choix = menu_principal()
        if choix == "1":
            factures.menu_factures()
        elif choix == "2":
            paiements.menu()
        elif choix == "3":
            operations.menu()
        elif choix == "4":
            audit.main()
        elif choix == "0":
            print("Fermeture du système.")
            sys.exit()
        else:
            print("Option invalide.")

if __name__ == "__main__":
    main()
