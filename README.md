# validin-maltego
Maltego transforms for Validin APIs

# Usage
The Validin Maltego Transform currently only supports local transform usage.

## Dependencies
This maltego transform requires python 3.8 or greater and pip, use your favorite package manager to install python or download directly from the [official python website](https://www.python.org/downloads/). If you have python already installed, continue to the next step. 
You will need to install the maltego-trx and requests packages, if you don't have them already.
Check your installation of these packages using the commands below:
```
pip show maltego-trx
pip show requests
```

If these packages are not installed:
```
pip install maltego-trx
pip install requests
```

## Setup
To Use the Validin Maltego Transform:
1. Clone this repo locally.
2. In the settings.py file of the repository, add your Validin API Key. Can be found by viewing your profile on [Validin](https://app.validin.com/profile)
3. Open Maltego and using Import Config, import the validin.mtz file from the repository

<img width="1350" alt="Screenshot 2024-09-04 at 4 08 05 PM" src="https://github.com/user-attachments/assets/e1181a2c-c220-4f91-9a50-ba539bc4077d">

4. In the transforms tab, select the transform manager, and select all the transforms that start with "Validin - ". In the bottom right of the transform manager, do the following 2 things:
- Change the "Command Line" field to point to your python installation. E.g. `C://Users/sreekarmadabushi/bin/python3.exe`
- Change the "Working directory" field to point to the directory of the validin-maltego repo that you have cloned locally. E.g. `C://Users/sreekarmadabushi/Documents/Validin/validin-maltego/`

<img width="1350" src="https://github.com/user-attachments/assets/ff03a320-3ac3-4ac3-9f50-462444f4b5fe">

5. Happy Hunting!

## Usage
1. Validin currently supports transforms on the following data types:
 - maltego.DNSName
 - maltego.IPv4Address
 - maltego.IPv6Address
 - maltego.Hash
 - maltego.JARMFingerprint
 - maltego.SSLCertificateHash
 - maltego.Phrase
