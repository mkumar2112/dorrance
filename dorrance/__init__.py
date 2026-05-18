import os

if os.getenv("DB_ENGINE", "").lower() == "mysql":
    import pymysql
    pymysql.install_as_MySQLdb()