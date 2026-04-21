#define MyAppName "AudiobookForge"
#define MyAppVersion "1.0"
#define MyAppPublisher "AudiobookForge"
#define MyAppExeName "AudiobookForge.exe"

[Setup]
AppId=AudiobookForge
AppName={#MyAppName}
AppVersion={#MyAppVersion}
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
ShowLanguageDialog=yes
UsePreviousLanguage=no
LanguageDetectionMethod=uilanguage

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "czech"; MessagesFile: "compiler:Languages\Czech.isl"
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

[Dirs]
Name: "{app}"; Permissions: users-modify

[Files]
Source: "dist\AudiobookForge\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[CustomMessages]
english.CreateDesktopShortcut=Create a desktop shortcut
english.AdditionalIcons=Additional icons:
english.LaunchProgram=Launch %1

polish.CreateDesktopShortcut=Utwórz skrót na pulpicie
polish.AdditionalIcons=Dodatkowe skróty:
polish.LaunchProgram=Uruchom %1

czech.CreateDesktopShortcut=Vytvořit zástupce na ploše
czech.AdditionalIcons=Další ikony:
czech.LaunchProgram=Spustit %1

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
