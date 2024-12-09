import serial
import re
from datetime import datetime
import time
import os 

# Configuration du port série pour Arduino
arduino_port = "COM6"  # Remplacez par votre port série (exemple : COM3 ou /dev/ttyUSB0)
baud_rate = 9600       # Assurez-vous que le débit en bauds correspond à celui de l'Arduino
nb_mesures_max = 10     # Nombre maximum de mesures avant d'enregistrer dans un fichier

# Initialisation de la connexion série
try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=2)
    print(f"Connecté à {arduino_port}")
except serial.SerialException as e:
    print(f"Erreur : Impossible de se connecter au port {arduino_port}")
    raise e

# Liste pour stocker les mesures
mesures = []

# Fonction pour envoyer une commande à l'Arduino
def envoyer_commande(commande):
    ser.write((commande + '\n').encode('utf-8'))  # Envoyer la commande au port série
    print(f"Commande envoyée : {commande}")

# Fonction pour extraire la valeur de mesure depuis une ligne Arduino
def extraire_mesure(ligne):
    match = re.search(r"=>\s*(-*[\d.]+)\s*kg", ligne)  # Rechercher la valeur après '=>'
    if match:
        return float(match.group(1))  # Retourner la valeur en tant que float
    return None

# Fonction pour enregistrer les mesures dans un fichier texte
def enregistrer_mesures(mesures, dossier = os.getcwd(), prefix_fichier="FSR_"):
    nom_fichier = f'{dossier}/{prefix_fichier}{datetime.now():%Y%m%d_%H%M%S}.txt'
    with open(nom_fichier, "w") as fichier:
        for essaie in mesures:
            fichier.write(f"Essaie numéro {essaie}\n")
            for i, mesure in enumerate(mesures[essaie], start=1):
                fichier.write(f"Mesure {i} : {mesure} kg\n")
    print(f"Les mesures ont été enregistrées dans le fichier : {nom_fichier}")
    return nom_fichier


def lancer_essaie():
    envoyer_commande('n')  # Envoyer la commande 'n' à l'Arduino

    listemesures = []
    print("Attente de la mesure...")

    # Lecture de la première mesure
    while len(listemesures) < nb_mesures_max:
        if ser.in_waiting > 0:  # Vérifie si des données sont disponibles
            ligne = ser.readline().decode('utf-8').strip()  # Lire une ligne et la décoder
            # print(f"Reçu : {ligne}")  # Afficher la ligne brute pour vérification
            mesure = extraire_mesure(ligne)  # Extraire la mesure
            if mesure is not None:
                if mesure != 0:  # Vérification des mesures nulles
                    listemesures.append(mesure)
                    print(f"Mesure validée : {mesure} kg")
                else:
                    print("Avertissement : Mesure nulle reçue, vérifiez le capteur.")
            else:
                print("Erreur : Données reçues non valides.")
        time.sleep(1)  # Attente entre deux lectures
    
    return listemesures


# Lancer l'application
if __name__ == "__main__":
    # Lecture et interaction
    try:
        essaie = 0
        mesures = {}
        while True:
            commande = input("Tapez 'n' pour collecter une mesure, ou 'q' pour quitter : ")

            if commande.lower() == 'q':  # Quitter le programme
                if mesures:
                    enregistrer_mesures(mesures)
                print("Arrêt du programme.")
                break

            elif commande.lower() == 'n':  # Collecter une mesure
                essaie += 1
                print(f"Début essaie {essaie}")
                mesures[essaie] = lancer_essaie()



    except KeyboardInterrupt:
        # Gestion de l'arrêt avec Ctrl+C
        print("\nArrêt du programme par l'utilisateur.")
        if mesures:
            enregistrer_mesures(mesures)
        ser.close()
        print("Connexion série fermée.")
