# myNSIS - Générateur de script NSIS

Cet outil est une application Python qui permet de **générer automatiquement** un script NSIS (_Nullsoft Scriptable Install System_) pour créer un installateur Windows.  
Il fournit une **interface graphique** avec Tkinter afin de sélectionner :

- Le nom du programme  
- Le chemin d'installation  
- L'icône du programme (fichier `.ico`)  
- Les différents fichiers à inclure dans l'installateur  
- Un fichier “principal” (par exemple l'exécutable) pour créer les raccourcis  

Une fois ces informations fournies, l'outil génère un fichier `script.nsi` prêt à être compilé avec **makensis**.

## Prérequis

- **Python 3.7+** (recommandé)  
- Le module Tkinter (généralement inclus avec Python sur Windows, sinon installez `python3-tk` sur certaines distributions Linux)  
- **NSIS** (pour compiler le script `.nsi` généré). Sur Windows, téléchargez NSIS depuis le site officiel : [nsis.sourceforge.io](https://nsis.sourceforge.io/).  

## Installation

1. Clonez ce dépôt :

   ```bash
   git clone https://github.com/Doalou/myNSIS.git
   cd myNSIS
   ```

2. (Optionnel) Créez et activez un environnement virtuel :

   ```bash
   python -m venv venv
   source venv/bin/activate    # Sur Linux/Mac
   venv\Scripts\activate       # Sur Windows
   ```

3. Installez les dépendances s'il y en a (ici, il n'y a que Tkinter qui est par défaut déjà disponible sur la plupart des systèmes) :

   ```bash
   pip install -r requirements.txt
   ```

4. Lancez l'application :

   ```bash
   python my_nsis_generator.py
   ```

## Utilisation

1. **Nom du programme** : Saisissez le nom tel qu'il apparaîtra dans l'installateur et dans les raccourcis.  
2. **Chemin d'installation** : Le chemin où sera installé votre programme par défaut (ex. `C:\Program Files\MonProgramme`).  
3. **Icône du programme** : Sélectionnez un fichier `.ico`.  
4. **Ajouter des fichiers** : Sélectionnez un ou plusieurs fichiers à inclure dans l'installateur (exécutables, bibliothèques, ressources, etc.).  
5. **Définir un fichier principal** : Sélectionnez le fichier qui servira pour le raccourci sur le Bureau et dans le Menu Démarrer (généralement l'exécutable principal).  
6. **Générer le script** : Un fichier `script.nsi` sera généré dans le répertoire courant.  

Pour créer l'installeur Windows, exécutez ensuite depuis votre terminal (où NSIS est installé) :

```bash
makensis script.nsi
```

Cela générera un fichier `installer.exe` dans le répertoire courant.

## Contributions

Les PR et suggestions sont les bienvenues ! N’hésitez pas à forker ce dépôt et à proposer vos améliorations.

## Licence

Ce projet est sous licence MIT. Consultez le fichier [LICENSE](LICENSE) pour plus de détails.
