This application is used to pull records over FHIR and export to cloud. 
A system account is required, as is client/secret pair provided by Vendor.
This was designed to work at our institution in conjunction with various demand management requirements, including:

- Secure key storage on Azure
- AES256 encryption of data at rest
- Non-bulk FHIR availability.

It is expected that the records of interest are known in advance prior to running the application.
For our purposes, encounters are pulled via SQL and encrypted using AES256 as input file with encounter ids.

For the first run, a crypt.bin file needs to be created for each machine:
python3 crypt/crypto_create_key.py

Encounters can be encrypted by running methods in crypt/crypt.py

To pull a list of encouners/demographics/diagnoses:
python main.py -e <encrypted_file.bin>

The -bgq parameter allows export to Google Bigquery, but must be set up once per machine. Application will prompt login.


