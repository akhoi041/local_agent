#ifndef MyAppName
  #define MyAppName "Talos"
#endif
#ifndef MyPublisher
  #define MyPublisher "T-Engine"
#endif
#ifndef MyVersion
  #define MyVersion "0.1.0"
#endif
#ifndef MyChannel
  #define MyChannel "Beta"
#endif
#ifndef ReleaseName
  #define ReleaseName "Talos-0.1.0-beta"
#endif
#ifndef ReleaseDir
  #define ReleaseDir "..\releases\Talos-0.1.0-beta"
#endif
#ifndef OutputDir
  #define OutputDir "..\releases\Talos-0.1.0-beta"
#endif
#ifndef IconPath
  #define IconPath "..\assets\icons\talos.ico"
#endif

[Setup]
AppId={{A6E1D2F9-4A53-4D21-9C65-C50BE530D54A}
AppName={#MyAppName}
AppVersion={#MyVersion}
AppPublisher={#MyPublisher}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir={#OutputDir}
OutputBaseFilename={#ReleaseName}-setup
SetupIconFile={#IconPath}
UninstallDisplayIcon={app}\{#MyAppName}.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
VersionInfoVersion={#MyVersion}
VersionInfoCompany={#MyPublisher}
VersionInfoDescription={#MyAppName} {#MyChannel} Installer
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a Desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "{#ReleaseDir}\{#ReleaseName}.exe"; DestDir: "{app}"; DestName: "{#MyAppName}.exe"; Flags: ignoreversion
Source: "{#ReleaseDir}\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ReleaseDir}\release_manifest.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ReleaseDir}\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs
Source: "{#ReleaseDir}\app_identity.json"; DestDir: "{app}\config"; Flags: ignoreversion
Source: "{#ReleaseDir}\default_config.json"; DestDir: "{app}\config"; Flags: ignoreversion

[Icons]
Name: "{userprograms}\{#MyAppName}\{#MyAppName}"; Filename: "{app}\{#MyAppName}.exe"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppName}.exe"
Name: "{userprograms}\{#MyAppName}\README"; Filename: "{app}\README.md"; WorkingDir: "{app}"
Name: "{userprograms}\{#MyAppName}\Release Notes"; Filename: "{app}\docs\RELEASE_NOTES.md"; WorkingDir: "{app}"
Name: "{userprograms}\{#MyAppName}\Privacy Notes"; Filename: "{app}\docs\PRIVACY.md"; WorkingDir: "{app}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppName}.exe"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppName}.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppName}.exe"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\README.md"
Type: files; Name: "{app}\release_manifest.json"
Type: dirifempty; Name: "{app}\docs"
Type: dirifempty; Name: "{app}\config"
Type: dirifempty; Name: "{app}"
