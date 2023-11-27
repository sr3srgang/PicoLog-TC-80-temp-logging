# PicoLog TC-08 temperature logging Python software for Sr3 use
last modified: 2023/10/10

## Functions
Periodically read temps and upload it to Sr group's Grafana's DB

## Initial setup
1. Download and install PicoLog SDK for the relevant system from the official download website: https://www.picotech.com/downloads
2. Install Miniforge (prefered; https://github.com/conda-forge/miniforge) or Miniconda (https://docs.conda.io/projects/miniconda/en/latest/).
3. Open VSCode, open this folder in VSCode, and create conda environment in VSCode
    - Command Palette (Ctrl+Shift+P) -> Python: Create Environment... -> Conda
    - **For Windows**, Go to Command Palette (Ctrl+Shift+P) -> Preferences: Open User Settings (JSON) and add the following item in the opened `setting.json` file, to avoid PowerShell from blocking `$PROFILE` `.ps1` file from running (corresponding to `.bashrc` file for `bash`) and thus preventing conda environment from being activated:
        ```JSON
        "terminal.integrated.profiles.windows": {
            "PowerShell": {
                "source": "PowerShell",
                "icon": "terminal-powershell",
                "args": ["-ExecutionPolicy", "Bypass"],
            }
        },
        "terminal.integrated.defaultProfile.windows": "PowerShell",
        ```
4. Open `runtest.py` and press `F5` key to let PowerShell terminal opened in VSCode and the conda environment are activated.
5. Run `conda install numpy matplotlib` in the terminal.
    - If Raspberry Pi 3B+ is used, do not use any Conda distributions and instead do everything in `venv` with system's `python`.
    - The 64-bit ARM architecture (aach64) for Raspberry Pi 4B is not supported by Pico Technology (as of 2023/10/22; see https://www.picotech.com/support/viewtopic.php?t=42162)
6. Run `python -m pip install .` (Do not miss the period at the end!)
7. Run `conda list` and check if the `picosdk` package is successfully installed (over pypi).
8. Try running `picotest.py` script by pressing `F5` key to check if picosdk successfully read the temperature from the logger.
9. Run `python -m pip install influxdb-client` (or `conda install influxdb-client` for Miniforge).
10. Open `main.py` and setup `assingment` dict variable to assign `Location` (description of where the temp is being measured) and `Channel` (TC-08 logger's channel #) of temp measurements. Set measurement period to `period` variable with the unit of second. 
11. Try running `main.py` script by pressing `F5` key to check if the app runs as it should.
12. Check if a relevant way to start up the app in the next section works.

## Starting app
### Windows
Run (doubleclick) `.\Startup_windows.lnk` shortcut file.

Tested for Windows 11.

### Linux
Run `./Startup_linux` file.

Has not been tested yet.

## Use
It will start reading temps, print in stdout, and uploading to Grafana's DB periodically. 

## Developer's notes
- Files for initial setup are from the SDK example folder (../picosdk-python-wrappers-master/)
    - setup.py, .gitignore files and picosdk/ folder were copied here as-is.
    - README.md was copied as README_SDK.md and a corresponding change was made in setup.py (see top comments as a release note therein)
- main.py is the entry point and contain all the essential codes.
- The codes are developed from the TC-08 SINGLE MODE EXAMPLE in the SDK folder (../picosdk-python-wrappers-master/usbtc08Examples/tc08SingleModeExample.py).