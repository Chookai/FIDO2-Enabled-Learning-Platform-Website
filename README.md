# change directory

`cd fido_project`

# Opening a virtual environment 
1. Installs the Python virtual environment

    `pip install virtualenv`

    
2. Creates a virtual environment in the project directory with the specified    name. For instance, myenv is created. 

    `virtualenv myenv`

3. Activates the Python virtual environment.


    # Windows Powershell
    `myenv\Scripts\activate`

    # Linux 
    `source myenv/bin/activate`

    To deactivate virtual environment

    `deactivate`
    
4. Installs all the required modules and libraries
    
    `pip install -r requirements.txt`

5. Creates table in the database by using the models created
    
    `python manage.py makemigrations`
    `python manage.py migrate`

6.  Run server with HTTPS connection

    `python manage.py runsslserver --certificate SSL_Certificates/cert.pem --key SSL_Certificates/key.pem`

   The web app is accessible in development server:  
    http://127.0.0.1:8000/

    "127.0.0.1" needs to be replace with "localhost" for WebAuthn to function. 

# Database 

The default database provided is dbSQLite3. To integrate PostgreSQL into the learning platform website, developer need to set up PostgreSQL and declare in the settings.py file. 
PostgreSQL installer can be found using the link below
    `https://www.enterprisedb.com/downloads/postgres-postgresql-downloads`

After installing the database and create an account, include the details in settings.py to link the database. 
The PORT for the database must not be the same as the port with the local developement server (8000).

# Self-signed SSL Certificates for Digital Signature 
# Reference
`https://www.ibm.com/docs/en/api-connect/2018.x?topic=overview-generating-self-signed-certificate-using-openssl`

Export password for the certificates are `Django1234`

1. Codes for generating new self-signed SSL certificate using OpenSSL
    'key' and 'certificate' are the names for the private and public key. Other names can be added
    `openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem`

2. Review the created certificate
    `openssl x509 -text -noout -in certificate.pem`

3. Combine your key and certificate in a PKCS#12 (P12) bundle
    `openssl pkcs12 -inkey key.pem -in certificate.pem -export -out certificate.p12`

4. Validate the p2 file
    `openssl pkcs12 -in certificate.p12 -noout -info`


# Self-signed SSL Certificates for HTTPS Connection 
# Source Code
`https://github.com/FiloSottile/mkcert`

1. Install the mkcert tool
    `mkcert --install`

2. Generate SSL Certificate for localhost and 127.0.0.1
    `mkcert -cert-file cert.pem -key-file key.pem localhost 127.0.0.1`

3. Install Django-sslserver
    `pip install Django-sslserver`

4. Include "sslserver" inside settings.py file under the INSTALLED_APP

5. Run Django on SSL Server
    `python manage.py runsslserver --certificate SSL_Certificates/cert.pem --key SSL_Certificate key.pem`

# SMTP Email 

The email might have some issue. Do login and check the status of the email.