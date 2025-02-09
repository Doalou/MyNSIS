# Standard NSIS template
!define APP_NAME "${NOM_PROGRAMME}"
!define INSTALL_DIR "${CHEMIN_INSTALLATION}"
!define ICON "${ICONE}"

Name "${APP_NAME}"
OutFile "installer.exe"
InstallDir "${INSTALL_DIR}"
Icon "${ICON}"
ShowInstDetails show

# Interface moderne
!include "MUI2.nsh"
!define MUI_ABORTWARNING

# Pages d'installation
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

# Pages de désinstallation
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

# Langues
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "English"

Section "Installation"
    SetOutPath "$INSTDIR"
    
    # Fichiers à installer
    ${FICHIERS}

    # Création des raccourcis
    ${RACCOURCIS}

    # Informations de désinstallation
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    # Enregistrement dans Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
                     "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
                     "UninstallString" "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
    ${UNINSTALL_COMMANDS}
    
    # Suppression de l'entrée dans Add/Remove Programs
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
SectionEnd
