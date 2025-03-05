[Setup]
AppName=Alinka
AppVersion={#AppVersion}
DefaultDirName={autopf}\Code For Poznań\Alinka
OutputDir=.\package
OutputBaseFilename=Alinka-{#AppVersion}
Compression=lzma2
SolidCompression=yes
SetupIconFile=statics\alinka.ico

[Files]
Source: "dist\alinka\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{autodesktop}\Alinka"; Filename: "{app}\alinka.exe"; IconFilename: "{app}\statics\alinka.ico"
Name: "{autoprograms}\Alinka"; Filename: "{app}\alinka.exe"; IconFilename: "{app}\statics\alinka.ico"
