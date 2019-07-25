

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="katytennisleague",
    password="krazy@tennis",
    hostname="katytennisleague.mysql.pythonanywhere-services.com",
    databasename="katytennisleague$default",
)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'iam-simple'
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False
