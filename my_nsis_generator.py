from __future__ import annotations

import json
import locale
import logging
import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Final

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constantes
WINDOW_MIN_SIZE: Final = (600, 400)
CONFIG_FILE: Final = "config.json"
DEFAULT_CONFIG: Final[Dict[str, str]] = {
    'nom_programme': '',
    'chemin_installation': '',
    'icone': ''
}
ICON_PREVIEW_SIZE: Final = (32, 32)

class Config:
    """Gestion de la configuration de l'application avec pattern singleton"""
    _instance: Optional[Config] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls) -> Config:
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self) -> None:
        try:
            config_path = Path(CONFIG_FILE)
            self._config = json.loads(config_path.read_text(encoding='utf-8')) if config_path.exists() else DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {e}")
            self._config = DEFAULT_CONFIG.copy()
    
    def save_config(self, settings: dict) -> None:
        try:
            Path(CONFIG_FILE).write_text(json.dumps(settings, indent=4), encoding='utf-8')
            self._config = settings
            logger.info("Configuration sauvegardée avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la configuration: {e}")
            messagebox.showerror("Erreur", "Impossible de sauvegarder la configuration")
    
    @property
    def settings(self) -> dict:
        return self._config.copy()

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
            lang = 'fr'
        return Translations.TRANSLATIONS[lang].get(key, key)

    @classmethod
    def load_translations(cls, custom_file: Optional[str] = None) -> None:
        """Permet de charger des traductions supplémentaires depuis un fichier"""
        if custom_file and os.path.exists(custom_file):
            try:
                with open(custom_file, 'r', encoding='utf-8') as f:
                    custom_translations = json.load(f)
                    cls.TRANSLATIONS.update(custom_translations)
            except Exception as e:
                logger.error(f"Erreur lors du chargement des traductions: {e}")

class NSISScriptBuilder:
    """Classe utilitaire pour la construction du script NSIS"""
    
    @staticmethod
    def build_script(
        nom_programme: str,
        chemin_installation: str,
        icone: str,
        fichiers_a_installer: List[str],
        fichier_principal: str
    ) -> str:
        # Nom de fichier principal à utiliser dans les raccourcis
        fichier_principal_nom = Path(fichier_principal).name

        template = f'''!define APP_NAME "{nom_programme}"
!define INSTALL_DIR "{chemin_installation}"
!define ICON "{icone}"

Name "${{APP_NAME}}"
OutFile "installer.exe"
InstallDir "${{INSTALL_DIR}}"
Icon "${{ICON}}"
ShowInstDetails show

Section "Installation"
    SetOutPath "$INSTDIR"
    
    # Fichiers à installer
    {NSISScriptBuilder._generate_file_entries(fichiers_a_installer)}

    # Création des raccourcis
    {NSISScriptBuilder._generate_shortcuts(fichier_principal_nom)}

    WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

Section "Uninstall"
    {NSISScriptBuilder._generate_uninstall_commands(fichiers_a_installer)}
SectionEnd'''
        return template

    @staticmethod
    def _generate_file_entries(files: List[str]) -> str:
        return "\n".join(f'    File "{file}"' for file in files)

    @staticmethod
    def _generate_shortcuts(main_file: str) -> str:
        return f'''    CreateShortcut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\{main_file}" "" "$INSTDIR\\${{ICON}}"
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortcut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\{main_file}" "" "$INSTDIR\\${{ICON}}"
    CreateShortcut "$SMPROGRAMS\\${{APP_NAME}}\\Désinstaller.lnk" "$INSTDIR\\uninstall.exe"'''

    @staticmethod
    def _generate_uninstall_commands(files: List[str]) -> str:
        file_deletions = "\n".join(f'    Delete "$INSTDIR\\{Path(file).name}"' for file in files)
        return f'''{file_deletions}
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk"
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\Désinstaller.lnk"
    RMDir "$SMPROGRAMS\\${{APP_NAME}}"
    Delete "$INSTDIR\\uninstall.exe"
    RMDir "$INSTDIR"'''

class Application(ttk.Frame):
    """
    Classe principale de l'application Tkinter pour générer un script NSIS.
    """
    def __init__(self, master: Optional[tk.Tk] = None):
        super().__init__(master)
        self.master = master
        self.config = Config()
        self.fichiers_a_installer: List[str] = []
        self.fichier_principal: Optional[str] = None
        
        self.setup_window()
        self.setup_variables()
        self.create_widgets()
        self.setup_dnd()
        self.load_saved_config()

    def setup_window(self) -> None:
        """Configuration de la fenêtre principale"""
        self.master.title(Translations.get_text('app_title'))
        self.master.minsize(*WINDOW_MIN_SIZE)
        self.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    def setup_variables(self) -> None:
        """Initialisation des variables"""
        self.nom_programme_var = tk.StringVar()
        self.chemin_installation_var = tk.StringVar()
        self.icone_var = tk.StringVar(value="")
        self.icon_preview: Optional[ImageTk.PhotoImage] = None

        # Style
        self.style = ttk.Style()
        self.style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        self.style.configure('Section.TLabelframe', padding=10)

    def create_widgets(self):
        """Création des widgets"""
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
            "myNSIS Generator\nVersion 1.0\n\nCréé par Doalo\n2024"
        )

    def save_config(self):
        """Sauvegarde la configuration actuelle"""
        config = {
            'nom_programme': self.nom_programme_var.get(),
            'chemin_installation': self.chemin_installation_var.get(),
            'icone': self.icone_var.get()
        }
        self.config.save_config(config)
        messagebox.showinfo("Info", "Configuration sauvegardée")

    def load_saved_config(self):
        """Charge la configuration sauvegardée"""
        config = self.config.settings
        self.nom_programme_var.set(config.get('nom_programme', ''))
        self.chemin_installation_var.set(config.get('chemin_installation', ''))
        self.icone_var.set(config.get('icone', ''))

    def load_config(self):
        """Charge une configuration depuis un fichier"""
        try:
            file_path = filedialog.askopenfilename(
                defaultextension=".json",
                filetypes=[("Fichiers JSON", "*.json")],
                title="Charger une configuration"
            )
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.nom_programme_var.set(config.get('nom_programme', ''))
                    self.chemin_installation_var.set(config.get('chemin_installation', ''))
                    self.icone_var.set(config.get('icone', ''))
                    if config.get('icone'):
                        self.update_icon_preview(config['icone'])
                    logger.info(f"Configuration chargée depuis {file_path}")
                    messagebox.showinfo("Succès", "Configuration chargée avec succès")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {e}")
            messagebox.showerror(
                "Erreur",
                "Impossible de charger la configuration"
            )

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

    def generer_script(self) -> None:
        """Génère le script NSIS avec validation des entrées"""
        try:
            # Validation des entrées
            if not self.validate_inputs():
                return
                
            script = NSISScriptBuilder.build_script(
                self.nom_programme_var.get().strip(),
                self.chemin_installation_var.get().strip(),
                self.icone_var.get().strip(),
                self.fichiers_a_installer,
                self.fichier_principal
            )
            
            script_path = Path("script.nsi")
            script_path.write_text(script, encoding='utf-8')
            
            messagebox.showinfo(
                "Succès",
                f"Le script NSIS a été généré avec succès:\n{script_path.absolute()}"
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du script: {e}")
            messagebox.showerror(
                "Erreur",
                "Une erreur est survenue lors de la génération du script."
            )

    def validate_inputs(self) -> bool:
        """Valide les entrées utilisateur"""
        if not self.nom_programme_var.get().strip():
            messagebox.showwarning("Attention", "Veuillez renseigner un nom de programme.")
            return False
            
        if not self.chemin_installation_var.get().strip():
            messagebox.showwarning("Attention", "Veuillez renseigner un chemin d'installation.")
            return False
            
        if not self.fichiers_a_installer:
            messagebox.showwarning("Attention", "Veuillez ajouter au moins un fichier à installer.")
            return False
            
        if not self.fichier_principal:
            messagebox.showwarning("Attention", "Veuillez définir un fichier principal.")
            return False
            
        return True

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
