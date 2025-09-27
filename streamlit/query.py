import os
import sqlalchemy as sa

def get_connection():
    # Pegando credenciais das variáveis de ambiente (mais seguro!)
    server   = os.getenv("AZURE_SQL_SERVER", "db-sensor-datascience-senai-gp1.mysql.database.azure.com")
    database = os.getenv("AZURE_SQL_DATABASE", "db_qualidade_ar")
    username = os.getenv("AZURE_SQL_USER", "grupo1DataScience")
    password = os.getenv("AZURE_SQL_PASSWORD", "Senai%40134")
    ssl_cert = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DigiCertGlobalRootG2.crt.pem")

    # MySQL + pymysql
    connection_string = (
        f"mysql+pymysql://{username}:{password}@{server}:3306/{database}"
        f"?ssl_ca={ssl_cert}"
    )

    engine = sa.create_engine(connection_string)
    return engine




