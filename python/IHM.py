import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import time
import os
from datetime import datetime

class GestionnaireEssaisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestionnaire d'essais")
        self.root.geometry("650x200")

        # Variables pour stocker les valeurs
        self.entry_var = tk.IntVar(value=1)  # Début par défaut à 1 secondes
        self.state_var = tk.StringVar(value="Prêt")  # État initial
        self.prefix_var = tk.StringVar(value="FSR_")  # Préfixe par défaut
        self.dest_dir_var = tk.StringVar(value=os.getcwd())  # Répertoire par défaut

        # Création des widgets
        self.create_widgets()

        # Attributs pour gestion des threads
        self.running = False  # Indique si le processus est en cours
        self.thread = None    # Thread du processus
        self.current_trial = 0

    def create_widgets(self):
        # Champ pour "Nombre d'essais"
        label_essais = tk.Label(self.root, text="Nombre d'essais :")
        label_essais.grid(row=0, column=1, padx=0, pady=10, sticky="e")

        self.spinbox = tk.Spinbox(self.root, from_=1, to=999, increment=1, textvariable=self.entry_var,
                                   justify="right")  # Taille ajustée
        self.spinbox.grid(row=0, column=2, padx=0, pady=10, sticky="we")

        # Champ pour "Préfixe des noms de fichiers"
        label_prefix = tk.Label(self.root, text="Préfixe des noms des fichiers de données :")
        label_prefix.grid(row=1, column=1, padx=0, pady=10, sticky="we")

        self.prefix_entry = tk.Entry(self.root, textvariable=self.prefix_var)
        self.prefix_entry.grid(row=1, column=2, padx=0, pady=10, sticky="we")

        # Champ pour "Répertoire de destination"
        label_dest_dir = tk.Label(self.root, text="Répertoire de destination :")
        label_dest_dir.grid(row=2, column=0, padx=0, pady=10, sticky="we")

        self.dest_dir_entry = tk.Entry(self.root, state="readonly")  # Taille réduite
        self.dest_dir_entry.grid(row=2, column=1,  padx=0, pady=10, sticky="we")
        self.update_dest_dir_display()  # Mise à jour pour afficher uniquement le nom du répertoire

        browse_button = tk.Button(self.root, text="Parcourir", command=self.browse_directory)
        browse_button.grid(row=2, column=2, padx=0, pady=10, sticky="we")  # Bouton déplacé

        # Label pour afficher l'état
        # state_label = tk.Label(self.root, text="État :")
        # state_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")

        self.state_display = tk.Label(self.root, textvariable=self.state_var, fg="blue")
        self.state_display.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        # Boutons Démarrer et Arrêter
        self.start_button = tk.Button(self.root, text="Démarrer", command=self.start_process)
        self.start_button.grid(row=4, column=1, padx=40, pady=10, sticky="we")

        self.stop_button = tk.Button(self.root, text="Arrêter", command=self.stop_process)
        self.stop_button.grid(row=4, column=2, padx=0, pady=10, sticky="we")

    def browse_directory(self):
        """Ouvrir une boîte de dialogue pour sélectionner un répertoire."""
        directory = filedialog.askdirectory(initialdir=self.dest_dir_var.get())
        if directory:
            self.dest_dir_var.set(directory)
            self.update_dest_dir_display()

    def update_dest_dir_display(self):
        """Met à jour l'affichage du champ pour n'afficher que le nom du répertoire."""
        current_dir = os.path.basename(self.dest_dir_var.get()) or os.path.basename(os.path.abspath(self.dest_dir_var.get()))
        self.dest_dir_entry.config(state="normal")
        self.dest_dir_entry.delete(0, tk.END)
        self.dest_dir_entry.insert(0, current_dir)
        self.dest_dir_entry.config(state="readonly")

    def start_process(self):
        """Démarrer le processus."""
        if not self.running:  # Éviter de démarrer plusieurs threads
            try:
                # Récupérer la valeur et vérifier qu'elle est valide
                delay = self.entry_var.get()
                if delay <= 1:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer un nombre valide (> 1).")
                return

            self.running = True
            self.current_trial = 0
            self.total_trials = delay
            self.state_var.set("En cours - Essai 0 sur {}".format(self.total_trials))
            self.thread = threading.Thread(target=self.run_process, args=(delay,))
            self.thread.start()
        else:
            messagebox.showinfo("Info", "Le processus est déjà en cours.")

    def run_process(self, delay):
        """Exécuter le processus avec un délai."""
        for i in range(1, delay + 1):
            if not self.running:
                self.state_var.set("Interrompu")
                return
            self.current_trial = i
            self.state_var.set(f"En cours - Essai {i} sur {delay}")
            time.sleep(1)  # Attendre une seconde
        self.state_var.set("Terminé")
        self.save_data_file()
        self.running = False

    def stop_process(self):
        """Arrêter le processus."""
        if self.running:
            self.running = False
            self.state_var.set("Interrompu")
        else:
            messagebox.showinfo("Info", "Aucun processus en cours.")

    def save_data_file(self):
        """Sauvegarder automatiquement un fichier avec le préfixe et l'horodatage."""
        prefix = self.prefix_var.get()
        dest_dir = self.dest_dir_var.get()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}{timestamp}.txt"
        filepath = os.path.join(dest_dir, filename)

        # Sauvegarder des données fictives dans le fichier
        try:
            with open(filepath, "w") as file:
                file.write(f"Fichier généré automatiquement le {timestamp}\n")
                file.write(f"Préfixe utilisé : {prefix}\n")
                file.write(f"Nombre total d'essais : {self.total_trials}\n")
                file.write("Données de l'essai : ...\n")
            messagebox.showinfo("Fichier sauvegardé", f"Fichier créé : {filepath}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder le fichier : {e}")

# Lancer l'application
if __name__ == "__main__":
    root = tk.Tk()
    app = GestionnaireEssaisApp(root)
    root.mainloop()
