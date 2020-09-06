from .Logica.Telemetria import Telemetria

class DaoTelemetria:
    def __init__(self, conexion):
        self.conexion = conexion

    def guardarTelemetria(self, telemetria):
        sql_guardar = "INSERT INTO telemetria (pitch, yaw, roll, lat, lon, alt, "
        sql_guardar += "bateriaDron, VelocidadDron, mision_id) VALUES "
        sql_guardar += "(" + str(telemetria.pitch) + ", " + str(telemetria.yaw) + ", "
        sql_guardar += str(telemetria.roll) + ", " + str(telemetria.lat) + ", " 
        sql_guardar += str(telemetria.lon) + "," + str(telemetria.alt) + ", "
        sql_guardar += str(telemetria.bateriaDron) + ",'" + telemetria.velocidadDron + "', "
        sql_guardar += str(telemetria.mision_id) + ") RETURNING *"
        
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_guardar)
            result = cursor.fetchone()
            self.conexion.commit()
            cursor.close()
            telemetria.id = result[0]
            # print("Registro guardado exitosamente")
            return telemetria
            
        except(Exception) as e:
            print("Error al insertar registro", e)
            return None


    def actualizarTelemetria(self, telemetria):
        sql_guardar = "UPDATE telemetria SET" 
        sql_guardar += " pitch = '" + str(telemetria.pitch) + "', yaw = " + str(telemetria.yaw) 
        sql_guardar += ", roll = " + str(telemetria.roll) + ", lat = " + str(telemetria.lat) 
        sql_guardar += ", lon = '" + telemetria.lon + "', alt = '" + telemetria.alt + "', "
        sql_guardar += "bateriaDron = " + str(telemetria.bateriaDron) + " velocidadDron = '" + telemetria.velocidadDron
        sql_guardar += "', mision_id = " + str(telemetria.mision_id) 
        sql_guardar += " WHERE id = " + str(telemetria.id) + " RETURNING *"
        
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_guardar)
            result = cursor.fetchone()
            self.conexion.commit()
            cursor.close()
            return telemetria
            
        except(Exception) as e:
            print("Error al actualizar el telemetria", e)
            return None


    def borrarTelemetria(self, telemetria):
        sql_borrar = "DELETE FROM telemetria WHERE id = " + str(telemetria.id) + ";"
        
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_borrar)
            
        except(Exception) as e:
            print("Error al actualizar la telemetria", e)
        
        finally:
            if(cursor):
                cursor.close()
                # print("Se ha cerrado el cursor")

    def getTelemetria(self, id_telemetria):
        sql_select = "SELECT * FROM telemetria WHERE id = " + str(id_telemetria)
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_select)
            record = cursor.fetchone()
            result = Telemetria()
            result.id = record[0]
            result.pitch = record[1]
            result.yaw = record[2]
            result.roll = record[3]
            result.lat = record[4]
            result.lon = record[5]
            result.alt = record[6]
            result.bateriaDron = record[7]
            result.velocidadDron = record[8]
            result.mision_id = record[9]
            cursor.close()
            return result

        except(Exception) as e:
            print("Error al actualizar el usuario", e)
            result = None
        
        finally:
            if(cursor):
                cursor.close()
                # print("Se ha cerrado el cursor")
            return result
