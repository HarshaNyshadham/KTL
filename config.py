import os

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="katytennisleague",
    password="krazy@tennis",
    hostname="katytennisleague.mysql.pythonanywhere-services.com",
    databasename="katytennisleague$default",
)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.urandom(32) # or 'iam-simple'
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #SERVER_NAME='local.docker:8000'
    WTF_CSRF_TIME_LIMIT = None
    WTF_CSRF_ENABLED = False
#     WTF_CSRF_CHECK_DEFAULT = False
#     SESSION_COOKIE_SAMESITE="None"
#     SESSION_COOKIE_SECURE=True

    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'katytennisleague@gmail.com'
    MAIL_PASSWORD = 'Tenn1s@k'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
