from os.path import (dirname, join)
from os import environ
from dotenv import load_dotenv


BASE_DIR = dirname(dirname(__file__))
load_dotenv(join(BASE_DIR, '.env'))


DEV_ENV = int(environ.get("DEV_ENV"))
DEBUG = DEV_ENV

if DEV_ENV:
    API_HOST = environ.get("DEV_API_HOST")
    DATABASE_HOST = environ.get("DEV_DB_HOST")
    DATABASE_USER = environ.get("DEV_DATABASE_USER")
    DATABASE_PASSWORD = environ.get("DEV_DATABASE_PASSWORD")
    DATABASE_NAME = '{}'.format(environ.get("DEV_DATABASE_NAME"))
else:
    DATABASE_HOST = environ.get("DB_HOST")
    DATABASE_USER = environ.get("DATABASE_USER")
    DATABASE_PASSWORD = environ.get("DATABASE_PASSWORD")
    DATABASE_NAME = '{}'.format(environ.get("DATABASE_NAME"))
    API_HOST = environ.get("API_HOST")

DATABASE_PORT = int(environ.get("DATABASE_PORT"))

API_WORKERS = int(environ.get("API_WORKERS"))
FOLDER = environ.get("SITE_FOLDER")
DEV_PORT = int(environ.get("DEV_API_PORT"))
PORT = int(environ.get("API_PORT"))
API_KEY = environ.get("API_KEY")

REDIRECT_HTML = """
<html xmlns="http://www.w3.org/1999/xhtml">
 <head>
   <title>{0}</title>
   <meta http-equiv="refresh" content="0;URL='{1}'" />
 </head>
 <body>
 </body>
</html>
""".format(environ.get("API_REDIRECT_TITLE"), environ.get("API_DESCRIPTION_URL"))
