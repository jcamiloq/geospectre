from .Logica.Espectros import Espectros

class DaoEspectros:
    def __init__(self, conexion):
        self.conexion = conexion

    def guardarEspectros(self, espectros):
        sql_guardar = "INSERT INTO espectros (white, dark, capturado, resultado, sensores_id) VALUES "
        sql_guardar += "(%s, %s, %s, %s, %s) RETURNING *"
        try:
            cursor = self.conexion.cursor()
            cursor.execute(
                sql_guardar, 
                (
                    espectros.white, espectros.dark, espectros.capturado, 
                    espectros.resultado,espectros.sensores_id 
                ) 
            )

            result = cursor.fetchone()
            self.conexion.commit()
            cursor.close()
            espectros.id = result[0]
            print("Espectro guardado con éxito")
            return espectros
            
        except(Exception) as e:
            print("Error al guardar espectro", e)
            return None

    def actualizarEspectros(self, espectros):
        sql_guardar = "UPDATE espectros SET "
        sql_guardar += "white = %s, dark = %s, capturado = %s, resultado = %s, "
        sql_guardar += "sensores_id = %s WHERE id = %s"
        # print(sql_guardar)
        try:
            cursor = self.conexion.cursor()
            cursor.execute(
                sql_guardar,
                (
                    espectros.white,
                    espectros.dark,
                    espectros.capturado,
                    espectros.resultado,
                    espectros.sensores_id,
                    espectros.id
                )
            )
            self.conexion.commit()
            cursor.close()
            return espectros
            
        except(Exception) as e:
            print("Error al actualizar el espectro", e)
        return None


    def borrarEspectros(self, espectros):
        sql_borrar = "DELETE FROM espectros WHERE id = " + str(espectros) + ";"
        
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_borrar)
            
        except(Exception) as e:
            print("Error al actualizar la espectros", e)
        
        finally:
            if(cursor):
                cursor.close()
                print("Se ha cerrado el cursor")

    def getEspectrosSensores(self, id_sensores):
        idEspectros = []
        sql_select = "SELECT * FROM espectros WHERE sensores_id = " + str(id_sensores)
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_select)
            record = cursor.fetchall()
            for i in range (0, len(record)):
                idEspectros.append(record[i][0])
                # idEspectros.append("\n")
            print(idEspectros)
            return idEspectros
            # record = cursor.fetchone()
            # result = Sensores()
            # result.id = record[0]
            # result.lugar = record[1]
            # result.tipo  = record[2]
            # result.numero_serie = record[3]
            # result.t_int = record[4]
            # result.numero_capt = record[5]
            # result.mision_id = record[6]
            # return result

        except(Exception) as e:
            print("Error al retornar los espectros", e)
            result = None

    def getEspectros(self, id_espectros):
        sql_select = "SELECT * FROM espectros WHERE id = " + str(id_espectros)
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_select)
            record = cursor.fetchone()
            result = Espectros()
            result.id = record[0]
            result.white = record[1]
            result.dark = record[2]
            result.capturado = record[3]
            result.resultado = record[4]
            result.sensores_id = record[5]
            # print(record)
            return result

        except(Exception) as e:
            print("Error al retornar el espectro", e)
            result = None
        
        finally:
            if(cursor):
                cursor.close()
                print("Se ha cerrado el cursor")
            return result

