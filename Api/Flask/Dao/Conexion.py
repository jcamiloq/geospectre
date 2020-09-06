import psycopg2

def conexion():
    try:
        connection = psycopg2.connect(
            host="localhost", 
            port = 5432, 
            database="geospectre", 
            user="geospectre", 
            password="12345678")

        return connection
    
    except(Exception, psycopg2.Error) as e:
        print("Error al intentar conectarse a postgres", e)





    