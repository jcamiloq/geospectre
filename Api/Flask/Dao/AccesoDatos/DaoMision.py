from .Logica.Mision import Mision

class DaoMision:
    def __init__(self, conexion):
        self.conexion = conexion

    def guardarMision(self, mision):
        sql_guardar = "INSERT INTO mision (nombre, elevacion, velocidad, modo_vuelo, modo_adq, usuarios_id) VALUES "
        sql_guardar += "(%s, %s, %s, %s, %s, %s) RETURNING *"

        try:
            cursor = self.conexion.cursor()
            cursor.execute(
                sql_guardar, 
                (
                    mision.nombre, mision.elevacion, mision.velocidad,
                    mision.modo_vuelo, mision.modo_adq, mision.usuarios_id
                )
            )
            result = cursor.fetchone()
            self.conexion.commit()
            cursor.close()
            mision.id = result[0]
            return mision
            
        except(Exception) as e:
            print("Error al insertar registro", e)
            return None


    def actualizarMision(self, mision):
        sql_guardar = "UPDATE mision SET" 
        sql_guardar += " nombre = '" + mision.nombre + "', elevacion = " + str(mision.elevacion) 
        sql_guardar += ", velocidad = " + str(mision.velocidad) 
        sql_guardar += ", modo_vuelo = '" + mision.modo_vuelo + "', modo_adq = '" + mision.modo_adq + "', "
        sql_guardar += "usuarios_id = " + str(mision.usuarios_id) + " WHERE id = " + str(mision.id)
        sql_guardar += " RETURNING *"
        
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_guardar)
            result = cursor.fetchone()
            self.conexion.commit()
            cursor.close()
            return mision
            
        except(Exception) as e:
            print("Error al actualizar el mision", e)
            return None


    def borrarMision(self, mision):
        sql_borrar = "DELETE FROM mision WHERE id = " + str(mision) + ";"
        
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_borrar)
            self.conexion.commit()
            
        except(Exception) as e:
            print("Error al actualizar la mision", e)
        
        finally:
            if(cursor):
                cursor.close()
                print("Se ha borrado la misiòn")

    def getMision(self, id_mision):
        sql_select = "SELECT * FROM mision WHERE id = " + str(id_mision)
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_select)
            record = cursor.fetchone()
            result = Mision()
            result.id = record[0]
            result.nombre = record[1]
            result.elevacion = record[2]
            result.velocidad = record[3]
            result.modo_vuelo = record[4]
            result.modo_adq = record[5]
            result.usuarios_id = record[6]
            return result

        except(Exception) as e:
            print("Error al actualizar la mision", e)
            result = None
        
        finally:
            if(cursor):
                cursor.close()
                print("Se ha cerrado el cursor")
            return result
    def getMisionNombre(self, nombreMision):
        sql_select = "SELECT * FROM mision WHERE nombre = '" + nombreMision + "'"
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_select)
            record = cursor.fetchone()
            result = Mision()
            result.id = record[0]
            result.nombre = record[1]
            result.elevacion = record[2]
            result.velocidad = record[3]
            result.modo_vuelo = record[4]
            result.modo_adq = record[5]
            result.usuarios_id = record[6]
            print(result.id)
            return result

        except(Exception) as e:
            print("Error al actualizar la mision", e)
            result = None
        
        finally:
            if(cursor):
                cursor.close()
                print("Se ha cerrado el cursor")
            return result
    def getAllMision(self, id_usuario):
        nombreMisiones = []
        sql_select = "SELECT * FROM mision WHERE usuarios_id = " + str(id_usuario)
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_select)
            record = cursor.fetchall()
            for i in range (0, len(record)):
                nombreMisiones.append(record[i][1])
                nombreMisiones.append("\n")
            print(nombreMisiones)
            return nombreMisiones

        except(Exception) as e:
            print("Error al buscar las misiones", e)
            result = None