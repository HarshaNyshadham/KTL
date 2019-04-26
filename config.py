

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="Harshanand",
    password="krazy@tennis",
    hostname="Harshanand.mysql.pythonanywhere-services.com",
    databasename="Harshanand$krazyTennis",
)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'Krazy112019'
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False
