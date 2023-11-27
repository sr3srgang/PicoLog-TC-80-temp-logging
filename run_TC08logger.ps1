# PowerShell script to startup PicoLog TC-08 python logging software in Windows
# Tested in Windows 11.
# Shall be run by "Startup_windows.lnk" shortcut file; Do not move/copy the short cut file
# out of this folder or it will not work. Create a shortcut for this shortcut for out-of-place use.

# set console title
$host.ui.RawUI.WindowTitle = "TC08logger"

# activate local conda environment
$conda_path = "$PWD\.conda"
conda activate "$conda_path"
Write-Host "Local conda environment activated: $conda_path`n"

# run the main script
$py_path = ".\main.py"
Write-Host ">>> Starting app: $py_path ...`n" 
python $py_path
write-host "`n<<< End of the script: $py_path`n"

# wait for pressing any key before closing terminala
write-host "Press any key to continue..."
[void][System.Console]::ReadKey($true)