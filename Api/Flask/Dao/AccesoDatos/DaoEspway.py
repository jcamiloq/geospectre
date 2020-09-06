from .Logica.Espway import Espway

class DaoEspway:
    def __init__(self, conexion):
        self.conexion = conexion

    def guardarEspway(self, espway):
        sql_guardar = "INSERT INTO espway (espectros_id, waypoints_id) VALUES "
        sql_guardar += "(%s, %s) RETURNING *" 

        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_guardar, (espway.espectros_id, espway.waypoints_id))
            result = cursor.fetchone()
            self.conexion.commit()
            cursor.close()
            espway.id = result[0]
            return espway
            
        except(Exception) as e:
            print("Error al insertar registro", e)
            return None


    def actualizarEspway(self, espway):
        sql_guardar = "UPDATE espway SET" 
        sql_guardar += " espectros_id = %s, waypoints_id = %s" 
        
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_guardar, (espway.espectros_id, espway.waypoints_id))
            result = cursor.fetchone()
            self.conexion.commit()
            cursor.close()
            return result
            
        except(Exception) as e:
            print("Error al actualizar el espway", e)
            return None

    def borrarEspway(self, espway):
        sql_borrar = "DELETE FROM espway WHERE id = " + str(espway.id) + ";"
        
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_borrar)
            
        except(Exception) as e:
            print("Error al actualizar la espway", e)
        
        finally:
            if(cursor):
                cursor.close()
                print("Se ha cerrado el cursor")

    def getEspway(self, id_espway):
        sql_select = "SELECT * FROM espway WHERE id = " + str(id_espway)
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_select)
            record = cursor.fetchone()
            result = Espway()
            result.id = record[0]
            result.espectros_id = record[1]
            result.waypoints_id = record[2]
            return result

        except(Exception) as e:
            print("Error al actualizar el usuario", e)
            result = None
        
        finally:
            if(cursor):
                cursor.close()
                print("Se ha cerrado el cursor")
            return result

    def getEspwayWaypoint(self, waypoints_id):
        sql_select = "SELECT * FROM espway WHERE waypoints_id = %s" %(waypoints_id)
        # print(sql_select)
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_select)
            record = cursor.fetchone()
            result = Espway()
            result.espectros_id = record[0]
            result.waypoints_id = record[1]
            return result

        except(Exception) as e:
            print("Error al actualizar el usuario", e)
            result = None
        
        finally:
            if(cursor):
                cursor.close()
                print("Se ha cerrado el cursor")
            return result
    def getEspwayEspectro(self, espectros_id):
        sql_select = "SELECT * FROM espway WHERE espectros_id = %s" %(espectros_id)
        # print(sql_select)
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_select)
            record = cursor.fetchone()
            result = Espway()
            result.espectros_id = record[0]
            result.waypoints_id = record[1]
            return result

        except(Exception) as e:
            print("Error al retornar espway", e)
            result = None
        
        finally:
            if(cursor):
                cursor.close()
                print("Se ha cerrado el cursor")
            return result
