; MKV Cleaner Installer Script for NSIS
; Creates a completely self-contained installer requiring no dependencies

!define APP_NAME "MKV Cleaner"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Athanasia Leontarakis"
!define APP_WEBSITE "https://github.com/Anni-065/mkv-manager"
!define APP_EXECUTABLE "MKV_Cleaner.exe"
!define UNINSTALLER_NAME "Uninstall.exe"

; MUI 2.0 compatible
!include "MUI2.nsh"
!include "FileFunc.nsh"

; General
Name "${APP_NAME}"
OutFile "..\..\MKV_Cleaner_Installer.exe"
Unicode True

; Smart installation directory selection
InstallDir "$LOCALAPPDATA\${APP_NAME}"
; Fallback to Program Files if Local AppData not available
InstallDirRegKey HKLM "Software\${APP_NAME}" "InstallLocation"

; Request user privileges but don't require admin
RequestExecutionLevel user

; Compression settings for smaller installer
SetCompressor /SOLID lzma
SetCompressorDictSize 32

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Custom welcome text
!define MUI_WELCOMEPAGE_TITLE "Welcome to the ${APP_NAME} Setup"
!define MUI_WELCOMEPAGE_TEXT "This wizard will guide you through the installation of ${APP_NAME}.$\r$\n$\r$\nThis is a completely self-contained application that requires no additional software or environment variables.$\r$\n$\r$\nYou must agree to the license terms to use this software.$\r$\n$\r$\nClick 'Next' to continue."

; Custom license page
!define MUI_LICENSEPAGE_TEXT_TOP "Please review the license terms below. You must accept this agreement to install ${APP_NAME}."
!define MUI_LICENSEPAGE_TEXT_BOTTOM "If you accept the terms of the agreement, click 'I Agree' to continue. You must accept the agreement to install ${APP_NAME}."
!define MUI_LICENSEPAGE_BUTTON "I &Agree"

; Custom finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXECUTABLE}"
!define MUI_FINISHPAGE_RUN_TEXT "Launch ${APP_NAME}"
!define MUI_FINISHPAGE_LINK "Visit our website"
!define MUI_FINISHPAGE_LINK_LOCATION "${APP_WEBSITE}"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\..\LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Version Information
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey "FileVersion" "${APP_VERSION}"
VIAddVersionKey "ProductVersion" "${APP_VERSION}"
VIAddVersionKey "FileDescription" "${APP_NAME} Installer"
VIAddVersionKey "LegalCopyright" "© ${APP_PUBLISHER}"

; Installer sections
Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  
  ; Show installation progress
  DetailPrint "Installing ${APP_NAME}..."
  
  ; Copy the self-contained executable
  File "..\..\dist\${APP_EXECUTABLE}"
  
  ; Verify the file was copied successfully
  IfFileExists "$INSTDIR\${APP_EXECUTABLE}" +3 0
    MessageBox MB_ICONSTOP "Failed to install ${APP_EXECUTABLE}. Installation aborted."
    Abort
  
  ; Get file size for uninstaller
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  
  ; Create Start Menu shortcuts
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXECUTABLE}" "" "$INSTDIR\${APP_EXECUTABLE}" 0
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\Uninstall ${APP_NAME}.lnk" "$INSTDIR\${UNINSTALLER_NAME}" "" "$INSTDIR\${UNINSTALLER_NAME}" 0
  
  ; Create Desktop shortcut (optional - ask user)
  MessageBox MB_YESNO "Create desktop shortcut?" IDYES CreateDesktopShortcut IDNO SkipDesktopShortcut
  CreateDesktopShortcut:
    CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXECUTABLE}" "" "$INSTDIR\${APP_EXECUTABLE}" 0
  SkipDesktopShortcut:
  
  ; Register file associations for MKV files (optional)
  MessageBox MB_YESNO "Associate MKV files with ${APP_NAME}?" IDYES RegisterFileAssoc IDNO SkipFileAssoc
  RegisterFileAssoc:
    WriteRegStr HKCU "Software\Classes\.mkv" "" "MKVCleanerFile"
    WriteRegStr HKCU "Software\Classes\MKVCleanerFile" "" "MKV Video File"
    WriteRegStr HKCU "Software\Classes\MKVCleanerFile\shell\open\command" "" '"$INSTDIR\${APP_EXECUTABLE}" "%1"'
  SkipFileAssoc:
  
  ; Store installation folder in registry
  WriteRegStr HKLM "Software\${APP_NAME}" "InstallLocation" $INSTDIR
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\${UNINSTALLER_NAME}"
  
  ; Add to Add/Remove Programs (Windows Control Panel)
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\${UNINSTALLER_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "QuietUninstallString" "$INSTDIR\${UNINSTALLER_NAME} /S"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" "$INSTDIR\${APP_EXECUTABLE}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "URLInfoAbout" "${APP_WEBSITE}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "InstallLocation" "$INSTDIR"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "EstimatedSize" "$0"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
  
  DetailPrint "Installation completed successfully!"
SectionEnd

; Uninstaller section
Section "Uninstall"
  ; Remove the main executable
  Delete "$INSTDIR\${APP_EXECUTABLE}"
  Delete "$INSTDIR\${UNINSTALLER_NAME}"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\Uninstall ${APP_NAME}.lnk"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"
  
  ; Remove file associations
  DeleteRegKey HKCU "Software\Classes\.mkv"
  DeleteRegKey HKCU "Software\Classes\MKVCleanerFile"
  
  ; Remove installation folder if empty
  RMDir "$INSTDIR"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
  DeleteRegKey HKLM "Software\${APP_NAME}"
  DeleteRegKey HKCU "Software\${APP_NAME}"
  
  ; Clean up any remaining registry entries
  DeleteRegKey HKCU "Software\Classes\Applications\${APP_EXECUTABLE}"
SectionEnd

; Functions
Function .onInit
  ; Check if already installed and offer to uninstall
  ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString"
  StrCmp $R0 "" done
  
  MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
    "${APP_NAME} is already installed. $\n$\nClick 'OK' to remove the previous version or 'Cancel' to cancel this upgrade." \
    IDOK uninst
  Abort
  
  uninst:
    ClearErrors
    ExecWait '$R0 _?=$INSTDIR'
    
    IfErrors no_remove_uninstaller done
      Delete $R0
      RMDir $INSTDIR
    no_remove_uninstaller:
  done:
FunctionEnd
