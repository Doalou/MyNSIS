import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import json
import os
from tkinterdnd2 import DND_FILES, TkinterDnD
import locale

class Config:
    """Gestion de la configuration de l'application"""
    CONFIG_FILE = "config.json"
    
    @staticmethod
    def save_config(settings: dict):
        with open(Config.CONFIG_FILE, 'w') as f:
            json.dump(settings, f)
    
    @staticmethod
    def load_config() -> dict:
        if os.path.exists(Config.CONFIG_FILE):
            with open(Config.CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}

class Translations:
    """Gestion du support multilingue"""
    TRANSLATIONS = {
        'fr': {
            'app_title': "myNSIS - Générateur de script NSIS",
            'program_name': "Nom du programme :",
            'install_path': "Chemin d'installation :",
            'program_icon': "Icône du programme (.ico) :",
            # ... autres traductions
        },
        'en': {
            'app_title': "myNSIS - NSIS Script Generator",
            'program_name': "Program name:",
            'install_path': "Installation path:",
            'program_icon': "Program icon (.ico):",
            # ... autres traductions
        }
    }
    
    @staticmethod
    def get_language():
        return locale.getdefaultlocale()[0][:2]
    
    @staticmethod
    def get_text(key: str) -> str:
        lang = Translations.get_language()
        if lang not in Translations.TRANSLATIONS:
            lang = 'en'
        return Translations.TRANSLATIONS[lang].get(key, key)

def build_nsis_script(
    nom_programme: str,
    chemin_installation: str,
    icone: str,
    fichiers_a_installer: list[str],
    fichier_principal: str
) -> str:
    """
    Construit et renvoie une chaîne de caractères représentant
    le script NSIS, basé sur les informations fournies.

    :param nom_programme: Nom du programme (affiché dans l'installateur).
    :param chemin_installation: Chemin par défaut où sera installé le programme.
    :param icone: Chemin vers l'icône (au format .ico).
    :param fichiers_a_installer: Liste des chemins de fichiers à inclure dans l'installateur.
    :param fichier_principal: Chemin du fichier “principal” (exécutable ou autre).
    :return: Script NSIS (au format .nsi) sous forme de chaîne de caractères.
    """
    # Nom de fichier principal à utiliser dans les raccourcis
    fichier_principal_nom = fichier_principal.split("/")[-1]

    script = f'''!define APP_NAME "{nom_programme}"
!define INSTALL_DIR "{chemin_installation}"
!define ICON "{icone}"

Name "${{APP_NAME}}"
OutFile "installer.exe"
InstallDir "${{INSTALL_DIR}}"
Icon "${{ICON}}"
ShowInstDetails show

Section "Installation"
    SetOutPath "$INSTDIR"
'''

    # Ajout des fichiers à installer
    for fichier in fichiers_a_installer:
        script += f'    File "{fichier}"\n'

    script += f'''
    ; Créer un raccourci sur le bureau
    CreateShortcut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\{fichier_principal_nom}" "" "$INSTDIR\\${{ICON}}"

    ; Créer un raccourci dans le menu Démarrer
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortcut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\{fichier_principal_nom}" "" "$INSTDIR\\${{ICON}}"
    CreateShortcut "$SMPROGRAMS\\${{APP_NAME}}\\Désinstaller.lnk" "$INSTDIR\\uninstall.exe"

    ; Enregistrer l'installateur pour la désinstallation
    WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

Section "Uninstall"
    ; Supprimer les fichiers installés
'''
    for fichier in fichiers_a_installer:
        # On supprime juste le nom du fichier tel qu'il est dans le dossier d'installation
        script += f'    Delete "$INSTDIR\\{fichier.split("/")[-1]}"\n'

    script += '''
    ; Supprimer les raccourcis
    Delete "$DESKTOP\\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\\${APP_NAME}\\Désinstaller.lnk"
    RMDir "$SMPROGRAMS\\${APP_NAME}"

    ; Supprimer le répertoire d'installation
    RMDir "$INSTDIR"

    ; Supprimer le désinstallateur
    Delete "$INSTDIR\\uninstall.exe"
SectionEnd
'''
    return script


class Application(ttk.Frame):
    """
    Classe principale de l'application Tkinter pour générer un script NSIS.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Style
        self.style = ttk.Style()
        self.style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        self.style.configure('Section.TLabelframe', padding=10)

        # Variables
        self.nom_programme_var = tk.StringVar()
        self.chemin_installation_var = tk.StringVar()
        self.icone_var = tk.StringVar()
        self.fichiers_a_installer = []
        self.fichier_principal = None
        self.icon_preview = None

        # Chargement de la config
        self.load_saved_config()
        
        self.create_widgets()
        self.setup_dnd()

    def create_widgets(self):
        """Création des widgets avec un design amélioré"""
        # Menu
        self.create_menu()
        
        # Frame principale avec notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Onglet Configuration
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="Configuration")
        
        # Section informations générales
        info_frame = ttk.LabelFrame(self.config_frame, text="Informations générales", style='Section.TLabelframe')
        info_frame.pack(fill=tk.X, pady=5)
        
        # Nom du programme
        ttk.Label(info_frame, text=Translations.get_text('program_name')).pack()
        ttk.Entry(info_frame, textvariable=self.nom_programme_var).pack(fill=tk.X)
        
        # Chemin d'installation
        ttk.Label(info_frame, text=Translations.get_text('install_path')).pack()
        path_frame = ttk.Frame(info_frame)
        path_frame.pack(fill=tk.X)
        ttk.Entry(path_frame, textvariable=self.chemin_installation_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="...", width=3, command=self.choisir_chemin).pack(side=tk.LEFT)

        # Section icône
        icon_frame = ttk.LabelFrame(self.config_frame, text="Icône", style='Section.TLabelframe')
        icon_frame.pack(fill=tk.X, pady=5)
        
        # Preview de l'icône
        self.preview_canvas = tk.Canvas(icon_frame, width=32, height=32)
        self.preview_canvas.pack(side=tk.LEFT, padx=5)
        
        icon_select_frame = ttk.Frame(icon_frame)
        icon_select_frame.pack(fill=tk.X, expand=True)
        ttk.Entry(icon_select_frame, textvariable=self.icone_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(icon_select_frame, text="Parcourir", command=self.choisir_icone).pack(side=tk.LEFT)

        # Section fichiers
        files_frame = ttk.LabelFrame(self.config_frame, text="Fichiers à installer", style='Section.TLabelframe')
        files_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        buttons_frame = ttk.Frame(files_frame)
        buttons_frame.pack(fill=tk.X)
        ttk.Button(buttons_frame, text="Ajouter fichier(s)", command=self.ajouter_fichier).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Définir principal", command=self.definir_fichier_principal).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Supprimer", command=self.supprimer_fichier).pack(side=tk.LEFT, padx=2)

        # Liste des fichiers avec scrollbar
        list_frame = ttk.Frame(files_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.liste_fichiers = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.liste_fichiers.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.liste_fichiers.yview)

        # Barre de progression
        self.progress = ttk.Progressbar(self, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)

        # Boutons d'action
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill=tk.X)
        ttk.Button(buttons_frame, text="Générer le script", command=self.generer_script).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Quitter", command=self.quit_app).pack(side=tk.RIGHT)

    def create_menu(self):
        """Création de la barre de menu"""
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Sauvegarder configuration", command=self.save_config)
        file_menu.add_command(label="Charger configuration", command=self.load_config)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.quit_app)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self.show_about)

    def setup_dnd(self):
        """Configuration du drag and drop"""
        self.liste_fichiers.drop_target_register(DND_FILES)
        self.liste_fichiers.dnd_bind('<<Drop>>', self.drop_files)

    def drop_files(self, event):
        """Gestion du drop de fichiers"""
        files = event.data.split()
        for file in files:
            # Nettoyer le chemin (enlever les {} sous Windows)
            file = file.strip('{}')
            self.fichiers_a_installer.append(file)
            self.liste_fichiers.insert(tk.END, file)

    def update_icon_preview(self, icon_path):
        """Mise à jour de la prévisualisation de l'icône"""
        try:
            icon = Image.open(icon_path)
            icon = icon.resize((32, 32), Image.Resampling.LANCZOS)
            self.icon_preview = ImageTk.PhotoImage(icon)
            self.preview_canvas.create_image(16, 16, image=self.icon_preview)
        except Exception:
            self.preview_canvas.delete("all")

    # ... (autres méthodes existantes avec ajustements mineurs)

    def show_about(self):
        """Affiche la boîte de dialogue À propos"""
        messagebox.showinfo(
            "À propos",
            "myNSIS Generator\nVersion 1.0\n\nCréé par [Votre nom]\n2024"
        )

    def save_config(self):
        """Sauvegarde la configuration actuelle"""
        config = {
            'nom_programme': self.nom_programme_var.get(),
            'chemin_installation': self.chemin_installation_var.get(),
            'icone': self.icone_var.get()
        }
        Config.save_config(config)
        messagebox.showinfo("Info", "Configuration sauvegardée")

    def load_saved_config(self):
        """Charge la configuration sauvegardée"""
        config = Config.load_config()
        self.nom_programme_var.set(config.get('nom_programme', ''))
        self.chemin_installation_var.set(config.get('chemin_installation', ''))
        self.icone_var.set(config.get('icone', ''))

    def choisir_icone(self):
        """Ouvre un dialog pour sélectionner le fichier .ico."""
        icone = filedialog.askopenfilename(filetypes=[("Fichiers ICO", "*.ico")])
        if icone:
            self.icone_var.set(icone)
            self.update_icon_preview(icone)

    def ajouter_fichier(self):
        """Ouvre un dialog pour sélectionner un ou plusieurs fichiers à ajouter."""
        fichiers = filedialog.askopenfilenames()
        for fichier in fichiers:
            self.fichiers_a_installer.append(fichier)
            self.liste_fichiers.insert(tk.END, fichier)

    def definir_fichier_principal(self):
        """
        Définir le fichier principal (exécutable, etc.) à partir
        de la sélection dans la Listbox.
        """
        try:
            selection_index = self.liste_fichiers.curselection()[0]
        except IndexError:
            messagebox.showinfo("Info", "Veuillez sélectionner un fichier dans la liste.")
            return
        self.fichier_principal = self.liste_fichiers.get(selection_index)
        messagebox.showinfo("Fichier principal défini", f"Fichier principal : {self.fichier_principal}")

    def supprimer_fichier(self):
        """
        Supprime le fichier sélectionné de la liste interne et de la Listbox.
        """
        try:
            selection_index = self.liste_fichiers.curselection()[0]
        except IndexError:
            messagebox.showinfo("Info", "Veuillez sélectionner un fichier à supprimer.")
            return

        element = self.liste_fichiers.get(selection_index)
        self.liste_fichiers.delete(selection_index)
        self.fichiers_a_installer.remove(element)
        if self.fichier_principal == element:
            self.fichier_principal = None
            messagebox.showinfo("Info", "Le fichier principal a été supprimé. Veuillez en définir un autre.")

    def generer_script(self):
        """
        Génère le fichier script.nsi à partir des infos récoltées (nom,
        chemin, icône, fichiers). Affiche un message de confirmation.
        """
        nom_programme = self.nom_programme_var.get().strip()
        chemin_installation = self.chemin_installation_var.get().strip()
        icone = self.icone_var.get().strip()

        # Vérifications basiques
        if not nom_programme:
            messagebox.showwarning("Attention", "Veuillez renseigner un nom de programme.")
            return
        if not chemin_installation:
            messagebox.showwarning("Attention", "Veuillez renseigner un chemin d'installation.")
            return
        if not self.fichiers_a_installer:
            messagebox.showwarning("Attention", "Veuillez ajouter au moins un fichier à installer.")
            return
        if not self.fichier_principal:
            messagebox.showwarning("Attention", "Veuillez définir un fichier principal.")
            return

        script = build_nsis_script(
            nom_programme,
            chemin_installation,
            icone,
            self.fichiers_a_installer,
            self.fichier_principal
        )

        # Enregistrement du script NSIS
        with open("script.nsi", "w", encoding="utf-8") as f:
            f.write(script)

        messagebox.showinfo("Information", "Le script NSIS a été généré avec succès :\nscript.nsi")

    def choisir_chemin(self):
        """Ouvre un dialog pour sélectionner le chemin d'installation."""
        chemin = filedialog.askdirectory()
        if chemin:
            self.chemin_installation_var.set(chemin)

    def quit_app(self):
        """Quitte l'application."""
        self.master.destroy()


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = Application(master=root)
    app.mainloop()