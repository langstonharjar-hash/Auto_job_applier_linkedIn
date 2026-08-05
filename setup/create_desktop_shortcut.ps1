$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath('Desktop')
$ScriptDir = Split-Path -Parent $PSScriptRoot

# 1. Desktop GUI App Shortcut (Self-Contained App with Sidebar & Browser View)
$AppShortcutPath = Join-Path $DesktopPath "Auto Job Applier App.lnk"
$Shortcut0 = $WshShell.CreateShortcut($AppShortcutPath)
$Shortcut0.TargetPath = Join-Path $ScriptDir "run_app.bat"
$Shortcut0.WorkingDirectory = $ScriptDir
$Shortcut0.Description = "Launch Auto Job Applier Desktop Application GUI"
$Shortcut0.IconLocation = "shell32.dll,220"
$Shortcut0.Save()
Write-Host "Desktop Application shortcut created at: $AppShortcutPath"

# 2. Interactive Mode Batch Shortcut ("as is")
$InteractiveShortcutPath = Join-Path $DesktopPath "Auto Job Applier (Interactive).lnk"
$Shortcut1 = $WshShell.CreateShortcut($InteractiveShortcutPath)
$Shortcut1.TargetPath = Join-Path $ScriptDir "run_bot.bat"
$Shortcut1.WorkingDirectory = $ScriptDir
$Shortcut1.Description = "Launch Auto Job Applier LinkedIn (Interactive Mode)"
$Shortcut1.IconLocation = "shell32.dll,14"
$Shortcut1.Save()
Write-Host "Interactive shortcut created at: $InteractiveShortcutPath"

# 3. Auto Mode Batch Shortcut (No manual confirmation, random delays under 30s)
$AutoShortcutPath = Join-Path $DesktopPath "Auto Job Applier (Auto Mode).lnk"
$Shortcut2 = $WshShell.CreateShortcut($AutoShortcutPath)
$Shortcut2.TargetPath = Join-Path $ScriptDir "run_bot_auto.bat"
$Shortcut2.WorkingDirectory = $ScriptDir
$Shortcut2.Description = "Launch Auto Job Applier LinkedIn (Auto Mode - No confirmations, random delays <30s)"
$Shortcut2.IconLocation = "shell32.dll,238"
$Shortcut2.Save()
Write-Host "Auto Mode shortcut created at: $AutoShortcutPath"
