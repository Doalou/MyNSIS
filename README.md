# myNSIS - Générateur de script NSIS

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![NSIS](https://img.shields.io/badge/NSIS-3.0%2B-orange)

> Un générateur graphique de scripts NSIS pour créer facilement des installateurs Windows

## 🚀 Fonctionnalités

- Interface graphique intuitive avec Tkinter
- Support du glisser-déposer pour les fichiers
- Prévisualisation des icônes
- Gestion des configurations (sauvegarde/chargement)
- Support multilingue (FR/EN)
- Génération automatique des raccourcis (Bureau et Menu Démarrer)
- Création automatique du désinstallateur

## 📋 Prérequis

- Python 3.7 ou supérieur
- Modules Python :
  ```
  pillow>=10.0.0
  tkinterdnd2>=0.3.0
  ```
- NSIS (Nullsoft Scriptable Install System)
  - Windows : [Télécharger NSIS](https://nsis.sourceforge.io/Download)
  - Linux : `sudo apt install nsis` (Ubuntu/Debian)

## 💻 Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/Doalou/myNSIS.git
   cd myNSIS
   ```

2. **Créer un environnement virtuel (recommandé)**
   ```bash
   python -m venv venv
   source venv/bin/activate    # Linux/Mac
   venv\Scripts\activate       # Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Utilisation

1. **Lancer l'application**
   ```bash
   python my_nsis_generator.py
   ```

2. **Configuration de base**
   - Nom du programme : nom affiché dans l'installateur
   - Chemin d'installation : dossier cible (ex: `C:\Program Files\MonApp`)
   - Icône : fichier `.ico` pour l'installateur et les raccourcis

3. **Gestion des fichiers**
   - Glisser-déposer ou utiliser le bouton "Ajouter fichier(s)"
   - Sélectionner un fichier et cliquer sur "Définir principal" pour l'exécutable
   - Possibilité de supprimer des fichiers de la liste

4. **Génération et compilation**
   - Cliquer sur "Générer le script"
   - Un fichier `script.nsi` est créé
   - Compiler avec NSIS :
     ```bash
     makensis script.nsi
     ```
   - L'installateur `installer.exe` est généré

## 🔧 Configuration avancée

- **Fichier config.json** : stocke les paramètres par défaut
- **Support multilingue** : fichiers de traduction dans le format :
  ```json
  {
    "fr": {
      "key": "value"
    }
  }
  ```

## 🤝 Contribution

1. Forker le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commiter les changements (`git commit -am 'Ajout de fonctionnalité'`)
4. Pusher la branche (`git push origin feature/amelioration`)
5. Créer une Pull Request

## 📝 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.
