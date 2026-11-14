#define MyAppName "AudiobookForge"
; Version comes from version.py (__version__ = "x.y.z"); override with /DMyAppVersion=x.y.z
#ifndef MyAppVersion
  #define VersionFile FileOpen(AddBackslash(SourcePath) + "version.py")
  #if !VersionFile
    #error version.py not found
  #endif
  #define VersionLine FileRead(VersionFile)
  #expr FileClose(VersionFile)
  #define VersionStart Pos('"', VersionLine) + 1
  #define VersionRest Copy(VersionLine, VersionStart)
  #define MyAppVersion Copy(VersionRest, 1, Pos('"', VersionRest) - 1)
#endif
#if MyAppVersion == ""
  #error Could not read __version__ from version.py
#endif
; AppId is overridable only so test builds do not collide with a real install
#ifndef MyAppId
  #define MyAppId "AudiobookForge"
#endif
#define MyAppPublisher "AudiobookForge"
#define MyAppExeName "AudiobookForge.exe"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
VersionInfoVersion={#MyAppVersion}
UninstallDisplayName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
DisableDirPage=no
OutputDir=release
OutputBaseFilename=AudiobookForgeSetup
SetupIconFile=assets\app_icon.ico
UninstallDisplayIcon={app}\assets\app_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
; /CURRENTUSER installs per-user without admin rights (used for test installs)
PrivilegesRequiredOverridesAllowed=commandline
ShowLanguageDialog=yes
UsePreviousLanguage=no
LanguageDetectionMethod=uilanguage

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "czech"; MessagesFile: "compiler:Languages\Czech.isl"
Name: "slovak"; MessagesFile: "compiler:Languages\Slovak.isl"
Name: "slovenian"; MessagesFile: "compiler:Languages\Slovenian.isl"
Name: "croatian"; MessagesFile: "hrv.isl"
Name: "romanian"; MessagesFile: "Romanian.isl"
Name: "hungarian"; MessagesFile: "compiler:Languages\Hungarian.isl"
Name: "catalan"; MessagesFile: "compiler:Languages\Catalan.isl"
Name: "afrikaans"; MessagesFile: "af.isl"
Name: "swahili"; MessagesFile: "sw.isl"
Name: "estonian"; MessagesFile: "est.isl"
Name: "latvian"; MessagesFile: "lav.isl"
Name: "lithuanian"; MessagesFile: "lit.isl"
Name: "finnish"; MessagesFile: "compiler:Languages\Finnish.isl"
Name: "danish"; MessagesFile: "compiler:Languages\Danish.isl"
Name: "norwegian"; MessagesFile: "compiler:Languages\Norwegian.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"
Name: "swedish"; MessagesFile: "compiler:Languages\Swedish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopShortcut}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

; No [Dirs] permissions: the install folder stays read-only for standard users.
; Settings live in %APPDATA%\AudiobookForge, models in %LOCALAPPDATA%\AudiobookForge,
; audiobooks in the folder the user picks (default Documents\AudiobookForge).

[Files]
; dist\AudiobookForge already contains ffmpeg\ffmpeg.exe, ffmpeg\LICENSE.txt and
; THIRD_PARTY_NOTICES.md (added by build_folder.bat from scripts\fetch_ffmpeg.ps1).
#if !FileExists(AddBackslash(SourcePath) + "dist\AudiobookForge\ffmpeg\ffmpeg.exe")
  #error dist\AudiobookForge\ffmpeg\ffmpeg.exe missing - run build_folder.bat (it fetches the pinned ffmpeg)
#endif
#if !FileExists(AddBackslash(SourcePath) + "dist\AudiobookForge\ffmpeg\LICENSE.txt")
  #error dist\AudiobookForge\ffmpeg\LICENSE.txt missing - run build_folder.bat
#endif
Source: "dist\AudiobookForge\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

; No UninstallDelete section: the uninstaller removes only the files it installed.
; config.json, downloaded models and generated audiobooks are kept.

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  { Versions up to 1.0.5 granted Users:Modify on the install folder.
    Reset it to inherited permissions so an upgrade does not keep that hole open. }
  if (CurStep = ssPostInstall) and IsAdminInstallMode then
    Exec(ExpandConstant('{sys}\icacls.exe'), '"' + ExpandConstant('{app}') + '" /reset /T /C /Q',
      '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  SettingsDir: String;
begin
  if CurUninstallStep <> usPostUninstall then
    exit;
  SettingsDir := ExpandConstant('{userappdata}\{#MyAppName}');
  if UninstallSilent or not FileExists(SettingsDir + '\config.json') then
    exit;
  { Default button is "Yes" = keep settings. }
  if MsgBox(FmtMessage(CustomMessage('KeepSettingsPrompt'), [SettingsDir]),
            mbConfirmation, MB_YESNO or MB_DEFBUTTON1) = IDNO then
  begin
    DeleteFile(SettingsDir + '\config.json');
    RemoveDir(SettingsDir);
  end;
end;

[CustomMessages]
KeepSettingsPrompt=Keep your AudiobookForge settings?%n%n%1\config.json%n%nChoose No to delete them. Generated audiobooks and downloaded voice models are never removed.
polish.KeepSettingsPrompt=Zachować ustawienia AudiobookForge?%n%n%1\config.json%n%nWybierz Nie, aby je usunąć. Wygenerowane audiobooki i pobrane modele głosów nigdy nie są usuwane.

english.CreateDesktopShortcut=Create a desktop shortcut
english.AdditionalIcons=Additional icons:
english.LaunchProgram=Launch %1

polish.CreateDesktopShortcut=Utwórz skrót na pulpicie
polish.AdditionalIcons=Dodatkowe skróty:
polish.LaunchProgram=Uruchom %1

czech.CreateDesktopShortcut=Vytvořit zástupce na ploše
czech.AdditionalIcons=Další ikony:
czech.LaunchProgram=Spustit %1

slovak.CreateDesktopShortcut=Vytvorit zastupcu na pracovnej ploche
slovak.AdditionalIcons=Dalsie ikony:
slovak.LaunchProgram=Spustit %1

slovenian.CreateDesktopShortcut=Ustvari bliznjico na namizju
slovenian.AdditionalIcons=Dodatne ikone:
slovenian.LaunchProgram=Zazeni %1

croatian.CreateDesktopShortcut=Napravi precac na radnoj povrsini
croatian.AdditionalIcons=Dodatne ikone:
croatian.LaunchProgram=Pokreni %1

romanian.CreateDesktopShortcut=Creeaza o scurtatura pe desktop
romanian.AdditionalIcons=Pictograme suplimentare:
romanian.LaunchProgram=Lanseaza %1

hungarian.CreateDesktopShortcut=Asztali parancsikon letrehozasa
hungarian.AdditionalIcons=Tovabbi ikonok:
hungarian.LaunchProgram=%1 inditasa

catalan.CreateDesktopShortcut=Crea una drecera a l'escriptori
catalan.AdditionalIcons=Icones addicionals:
catalan.LaunchProgram=Executa %1

afrikaans.CreateDesktopShortcut=Skep 'n lessenaar kortpad
afrikaans.AdditionalIcons=Bykomende ikone:
afrikaans.LaunchProgram=Begin %1

swahili.CreateDesktopShortcut=Tengeneza njia ya mkato kwenye desktop
swahili.AdditionalIcons=Ikoni za ziada:
swahili.LaunchProgram=Endesha %1

estonian.CreateDesktopShortcut=Loo toolaua otsetee
estonian.AdditionalIcons=Lisai koonid:
estonian.LaunchProgram=Kaivita %1

latvian.CreateDesktopShortcut=Izveidot darbvirsmas isceju
latvian.AdditionalIcons=Papildu ikonas:
latvian.LaunchProgram=Palaist %1

lithuanian.CreateDesktopShortcut=Sukurti nuoroda darbalaukyje
lithuanian.AdditionalIcons=Papildomos piktogramos:
lithuanian.LaunchProgram=Paleisti %1

finnish.CreateDesktopShortcut=Luo pikakuvake tyopoydalle
finnish.AdditionalIcons=Lisakuvakkeet:
finnish.LaunchProgram=Kaynnista %1

danish.CreateDesktopShortcut=Opret genvej pa skrivebordet
danish.AdditionalIcons=Yderligere ikoner:
danish.LaunchProgram=Start %1

norwegian.CreateDesktopShortcut=Opprett snarvei pa skrivebordet
norwegian.AdditionalIcons=Ekstra ikoner:
norwegian.LaunchProgram=Start %1

german.CreateDesktopShortcut=Desktopverknüpfung erstellen
german.AdditionalIcons=Zusätzliche Symbole:
german.LaunchProgram=%1 starten

french.CreateDesktopShortcut=Créer un raccourci sur le bureau
french.AdditionalIcons=Icônes supplémentaires :
french.LaunchProgram=Lancer %1

spanish.CreateDesktopShortcut=Crear un acceso directo en el escritorio
spanish.AdditionalIcons=Iconos adicionales:
spanish.LaunchProgram=Iniciar %1

italian.CreateDesktopShortcut=Crea un collegamento sul desktop
italian.AdditionalIcons=Icone aggiuntive:
italian.LaunchProgram=Avvia %1

russian.CreateDesktopShortcut=Создать ярлык на рабочем столе
russian.AdditionalIcons=Дополнительные значки:
russian.LaunchProgram=Запустить %1

ukrainian.CreateDesktopShortcut=Створити ярлик на робочому столі
ukrainian.AdditionalIcons=Додаткові ярлики:
ukrainian.LaunchProgram=Запустити %1

turkish.CreateDesktopShortcut=Masaüstü kısayolu oluştur
turkish.AdditionalIcons=Ek simgeler:
turkish.LaunchProgram=%1 uygulamasını başlat

portuguese.CreateDesktopShortcut=Criar atalho no ambiente de trabalho
portuguese.AdditionalIcons=Ícones adicionais:
portuguese.LaunchProgram=Iniciar %1

brazilianportuguese.CreateDesktopShortcut=Criar atalho na área de trabalho
brazilianportuguese.AdditionalIcons=Ícones adicionais:
brazilianportuguese.LaunchProgram=Iniciar %1

dutch.CreateDesktopShortcut=Snelkoppeling op het bureaublad maken
dutch.AdditionalIcons=Extra pictogrammen:
dutch.LaunchProgram=%1 starten

swedish.CreateDesktopShortcut=Skapa genväg på skrivbordet
swedish.AdditionalIcons=Ytterligare ikoner:
swedish.LaunchProgram=Starta %1
