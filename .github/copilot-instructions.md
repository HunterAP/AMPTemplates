# AMP Template Development Guide

## Architecture Overview
This repository contains AMP (Application Management Platform) templates for game servers. Each template consists of:
- **Primary config**: `{name}.kvp` - Key-value pair file with all metadata and settings
- **UI config**: `{name}config.json` - Defines configuration fields shown in AMP interface
- **Meta config**: `{name}metaconfig.json` - Additional settings beyond base config
- **Ports**: `{name}ports.json` - Network port definitions
- **Updates**: `{name}updates.json` - Update/download procedures
- **Exclusions**: `exclusions/.backupExclude{name}` - Files to exclude from backups

## Key Patterns & Conventions

### KVP File Structure
Use hierarchical key naming:
- `Meta.*` - Template metadata (author, version, requirements)
- `App.*` - Application runtime settings (executables, directories, environment)
- `$*` - Dynamic variables (e.g., `$GamePort`, `$MaxUsers`)

Example from `valheim.kvp`:
```
Meta.DisplayName=Valheim
Meta.Description=Valheim dedicated server with BepInEx and Valheim Plus support
Meta.URL=https://valheim.com/
Meta.DisplayImageSource=steam:892970
Meta.ConfigVersion=6
Meta.SteamAppId=896660
Meta.SteamWorkshopId=892970
Meta.Author=CubeCoders Limited
Meta.License=AMP Default
Meta.ConfigReleaseState=NotSpecified

App.DisplayName=Valheim
App.RootDir=./Valheim/896660/
App.BaseDirectory=./Valheim/896660/
App.ExecutableWin=valheim_server.exe
App.ExecutableLinux=./start_server_bepinex.sh
App.WorkingDir={RootDir}
App.LinuxCommandLineArgs=./valheim_server.x86_64 -name "{{ServerName}}" -port {{ApplicationPort1}} -world "{{WorldName}}" -password "{{ServerPassword}}" -public {{ServerPublic}} {{crossplay}} -modifierPreset {{preset}} {{modifier}} {{setkey}} -saveinterval {{saveinterval}}
App.WindowsCommandLineArgs=valheim_server.exe -name "{{ServerName}}" -port {{ApplicationPort1}} -world "{{WorldName}}" -password "{{ServerPassword}}" -public {{ServerPublic}} {{crossplay}} -modifierPreset {{preset}} {{modifier}} {{setkey}} -saveinterval {{saveinterval}}
App.CommandLineArgs={{$PlatformArgs}}
App.UseLinuxEnviromentPath=true
App.ApplicationPort1=2456
App.ApplicationPort2=2457
App.EnvironmentVariables={"SteamAppId":"896660","LD_LIBRARY_PATH":"./linux64:{{{{$}}}LD_LIBRARY_PATH","SteamGameId":"896660"}
App.CommandLineParameterDelimiter= 
App.CommandLineParameterFormat=-{0} "{1}"
App.CommandLineParameterFormatNoValue=-{0}
App.AdminMethod=SteamID
App.AdminMethodFormat={0}
App.MaxUsers=10
App.UseRandomAdminPassword=false
App.RCONEnabled=false
App.RCONPort=0
App.RCONPassword=
App.RequiresAuthenticationToConnect=false
App.SupportsSleepMode=false
App.UpdateIncludesPlugins=true
App.IgnoreSTDOUTAfterRCON=false
```

### JSON Configuration Format
Configuration files use consistent schema with fields like:
- `DisplayName` - Human-readable label
- `Category` - Grouping (use game-specific icons like `Valheim:stadia_controller`)
- `FieldName` - Variable name (use `$` prefix for ports/users)
- `InputType` - UI control type (`text`, `number`, `checkbox`, `enum`, `list`)
- `ParamFieldName` - Maps to command line parameter
- `IncludeInCommandLine` - Whether to include in startup args
- `EnumValues` - For dropdown selections
- `Special` - For special handling like file lists

Example from `valheimconfig.json` showing different input types:
```json
{
    "DisplayName": "Server Name",
    "Description": "Server name as it appears in the server list",
    "FieldName": "ServerName",
    "InputType": "text",
    "Category": "Valheim:stadia_controller",
    "Subcategory": "General:dns:1",
    "ParamFieldName": "name",
    "IncludeInCommandLine": false,
    "Required": true,
    "DefaultValue": "My Valheim Server - Powered by AMP"
},
{
    "DisplayName": "Server is Public",
    "Description": "Whether or not the server appears on the server list",
    "FieldName": "ServerPublic",
    "Category": "Valheim:stadia_controller",
    "Subcategory": "General:dns:1",
    "ParamFieldName": "public",
    "IncludeInCommandLine": true,
    "InputType": "checkbox",
    "DefaultValue": "1",
    "EnumValues": {
        "True": "1",
        "False": "0"
    }
},
{
    "DisplayName": "World Preset",
    "Category": "Valheim:stadia_controller",
    "Subcategory": "General:dns:1",
    "Description": "Sets the world modifiers preset",
    "FieldName": "preset",
    "InputType": "enum",
    "ParamFieldName": "preset",
    "IncludeInCommandLine": true,
    "DefaultValue": "normal",
    "EnumValues": {
        "normal": "Normal (default)",
        "casual": "Casual",
        "easy": "Easy",
        "hard": "Hard",
        "hardcore": "Hardcore",
        "immersive": "Immersive",
        "hammer": "Hammer"
    }
},
{
    "DisplayName": "Admin Players",
    "Description": "A list of Steam64 IDs for players that are in-game admins",
    "FieldName": "AdminPlayers",
    "Category": "Valheim:stadia_controller",
    "Subcategory": "General:dns:1",
    "InputType": "list",
    "Special": "listfile:./Valheim/896660/Saves/adminlist.txt"
}
```

### Port Definitions
Structure ports as JSON array with child ports for related services:

```json
[
  {
    "Protocol": "UDP",
    "Port": 2456,
    "Ref": "ApplicationPort1",
    "Name": "Game Port",
    "Description": "Port for game traffic",
    "ChildPorts": [
      {
        "Protocol": "UDP",
        "Port": 2457,
        "Offset": 1,
        "Ref": "ApplicationPort2",
        "Name": "Steam Query Port",
        "Description": "Port for Steam query traffic"
      }
    ]
  }
]
```

### Update Sources
Define update procedures as JSON array with platform-specific stages:

- `SteamCMD` for Steam games with app IDs and workshop support
- `GithubRelease` for downloading mods/plugins from GitHub releases
- `Executable` for custom scripts (e.g., BepInEx setup, Proton configuration)

Example from `valheimupdates.json` showing multiple update sources:
```json
[
  {
    "UpdateStageName": "SteamCMD Download",
    "UpdateSourcePlatform": "All",
    "UpdateSource": "SteamCMD",
    "UpdateSourceData": "896660",
    "UpdateSourceArgs": "892970",
    "UpdateSourceVersion": "{{Stream}}",
    "SkipOnFailure": false
  },
  {
    "UpdateStageName": "ValheimPlus Download",
    "UpdateSourcePlatform": "Windows",
    "UpdateSource": "GithubRelease",
    "UpdateSourceArgs": "Grantapher/ValheimPlus",
    "UpdateSourceData": "WindowsServer.zip",
    "UpdateSourceConditionSetting": "valheim_plus_install",
    "UpdateSourceConditionValue": "true",
    "UnzipUpdateSource": true,
    "OverwriteExistingFiles": true,
    "SkipOnFailure": false
  },
  {
    "UpdateStageName": "BepInEx Download",
    "UpdateSourcePlatform": "Linux",
    "UpdateSource": "Executable",
    "UpdateSourceData": "/bin/bash",
    "UpdateSourceArgs": "-c \"BepInExVersion=\\\"{{bepinex_version}}\\\" && if [[ -z \\\"$BepInExVersion\\\" ]]; then BepInExVersion=$(wget -qO- https://thunderstore.io/api/v1/package-metrics/denikson/BepInExPack_Valheim | jq -r \\\".latest_version\\\"); fi && wget -qO BepInEx.zip https://gcdn.thunderstore.io/live/repository/packages/denikson-BepInExPack_Valheim-$BepInExVersion.zip && echo \\\"BepInEx v$BepInExVersion downloaded\\\"\"",
    "UpdateSourceConditionSetting": "bepinex_install",
    "UpdateSourceConditionValue": "true",
    "SkipOnFailure": false
  }
]
```

## Development Workflow

### Processing Templates
Use `utilities/MassEdit.ps1` to modernize legacy templates:
- Extracts inline JSON from `App.Ports` and `App.UpdateSources` into separate files
- Replaces with `@IncludeJson[file.json]` directives
- Adds `Meta.ConfigVersion=1.1` if missing

Run from repository root:
```powershell
.\utilities\MassEdit.ps1
```

### Testing Templates
Templates are validated by AMP during import. Common issues:
- Missing required Meta fields
- Invalid JSON syntax in config files
- Port conflicts with reserved ranges

### Backup Exclusions
Create `exclusions/.backupExclude{name}` files listing directories/files to exclude:
- Game binaries and large data folders
- Temporary files and logs
- Redistributables that can be redownloaded

## Integration Points
- **Steam Integration**: Use SteamAppId in environment variables
- **Proton Compatibility**: Linux servers use Proton GE for Windows games
- **Docker Support**: Specify `Meta.SpecificDockerImage` for containerized deployments
- **Cross-platform**: Handle Windows/Linux differences in executables and paths
- **Mod Support**: BepInEx and Valheim Plus integration with conditional updates
- **Configuration Management**: INI/JSON config file mapping with AutoMap

## File Naming Conventions
- Template name: `{game}.kvp`
- Config: `{game}config.json`
- Meta config: `{game}metaconfig.json`
- Ports: `{game}ports.json`
- Updates: `{game}updates.json`
- Exclusions: `.backupExclude{game}`

## References
- [AMP Documentation](https://wiki.cubecoders.com/AMP/Templates)
- [SteamCMD Documentation](https://developer.valvesoftware.com/wiki/SteamCMD)
- [Generic AMP Module Templates Guide](https://github.com/CubeCoders/AMP/wiki/Configuring-the-'Generic'-AMP-module)
- [Proton GE GitHub](https://github.com/GloriousEggroll/proton-ge-custom)
- [Cubecoders AMP Templates](https://github.com/CubeCoders/AMPTemplates)
- [Greelan's AMP Dev Templates](https://github.com/Greelan/AMPTemplates/tree/dev)
