# Buttonhole

### Development ###
#### Requirements ####
- Python >= 3.8
- Poetry >= 1.1.7
- MySQL Server >= 8
#### Set up ####
###### Execute commands ######
```shell
$ git clone git@github.com:Sylver11/buttonhole.git
$ cd flask_react
$ python3 -m virtualenv venv
$ source venv/bin/activate
$ python setup.py install
```

###### Set environement variables ######
```shell
$ export SQLALCHEMY_DATABASE_URI = <ConnString>
$ export SECRET_KEY = <SecretKey>
$ export FLASK_APP = application/__init__.py
$ export FLASK_ENV = development
$ export FLASK_DEBUG = True
$ export TEST_USER_EMAIL = <Email>
$ export TEST_USER_FIRSTNAME = <Firstname>
$ export TEST_USER_LASTNAME = <Lastname>
$ export TEST_USER_PASSWORD = <Password>
$ export SERVER_ADMIN = <AdminEmailAddress>
$ export SERVER_NAME = <Servername>
$ export MAIL_SERVER = <MailServer>
$ export MAIL_USERNAME = <Email>
$ export MAIL_PASSWORD = <AppPassword>
$ export DB_DEFAULT_VALUES_ACTIVE = <True/False>
```
> Note: You can also define the variables inside a .env file

###### Now execute ######
```shell
$ flask run
```

:thumbsup:
