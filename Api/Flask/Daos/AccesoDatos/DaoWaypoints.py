from .Logica.Waypoints import Waypoints

class DaoWaypoints:
    def __init__(self, conexion):
        self.conexion = conexion

    def guardarWaypoint(self, waypoint):
        sql_guardar = "INSERT INTO waypoints (num_waypoint, latlon, mision_id) VALUES "
        sql_guardar += "(" + str(waypoint.num_waypoint) + ", '" + waypoint.latlon + "',"
        sql_guardar += str(waypoint.mision_id) + ") RETURNING *;"
        
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_guardar)
            result = cursor.fetchone()
            self.conexion.commit()
            cursor.close()
            print("Registro guardado con exito")
            waypoint.id = result[0]
            return waypoint 
            
        except(Exception) as e:
            print("Error al insertar registro", e)
            return None

    def actualizarWaypoint(self, waypoint):
        sql_guardar = "UPDATE waypoints SET num_waypoint = " + str(waypoint.num_waypoint) 
        sql_guardar += ", latlon = '" + waypoint.latlon + "', mision_id = " + str(waypoint.mision_id) 
        sql_guardar += " WHERE id = " + str(waypoint.id) + ";"
        
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_guardar)
            self.conexion.commit()
            cursor.close()
            return waypoint
            
        except(Exception) as e:
            print("Error al actualizar el waypoint", e)
            return None

    def borrarWaypoint(self, waypoint):
        sql_borrar = "DELETE FROM waypoints WHERE id = " + str(waypoint) + ";"
        
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_borrar)
            self.conexion.commit()
            cursor.close()
            
        except(Exception) as e:
            print("Error al actualizar el waypoint", e)


    def getWaypoint(self, id_waypoint):
        sql_select = "SELECT * FROM waypoints WHERE id = " + str(id_waypoint)
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_select)
            record = cursor.fetchone()
            result = Waypoints.Waypoints()
            result.id = record[0]
            result.num_waypoint = record[1]
            result.latlon = record[2]
            result.mision_id = record[3]
            cursor.close()
            return result

        except(Exception) as e:
            print("Error al actualizar el usuario", e)
            result = None
        
        finally:
            if(cursor):
                cursor.close()
                print("Se ha cerrado el cursor")
            return result

    def getWaypointByNumber(self, num_waypoint, id_Mision):
        sql_select = "SELECT * FROM waypoints WHERE num_waypoint = %s" %(num_waypoint)
        sql_select+= " AND mision_id = "+ str(id_Mision)
        # print(sql_select)
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_select)
            record = cursor.fetchone()
            result = Waypoints()
            result.id = record[0]
            result.num_waypoint = record[1]
            result.latlon = record[2]
            result.mision_id = record[3]
            cursor.close()
            return result

        except(Exception) as e:
            print("Error al actualizar el usuario", e)
            result = None
        
        finally:
            if(cursor):
                cursor.close()
                print("Se ha cerrado el cursor")
            return result

    def getAllWaypoints(self, id_Mision):
        latlonLista = {}
        sql_select = "SELECT * FROM waypoints WHERE mision_id = " + str(id_Mision)
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_select)
            record = cursor.fetchall()
            # print(record)
            latlonLista = record
            for i in range (0, len(record)):
                result = Waypoints()
                result.id = record[i][0]
                result.num_waypoint = record[i][1]
                result.latlon = record[i][2]
                result.mision_id = record[i][3]
                latlonLista[i] = result
                # latlonLista.append(result)
                # latlonLista.append("\n")
            # print(latlonLista)
            cursor.close()
            return latlonLista

        except(Exception) as e:
            print("Error al actualizar el usuario", e)
            latlonLista = None
        
        finally:
            if(cursor):
                cursor.close()
                print("Se ha cerrado el cursor")
            return latlonLista

    def getAllWaypoints2(self, id_Mision):
        objetos = []
        sql_select = "SELECT * FROM waypoints WHERE mision_id = " + str(id_Mision)
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_select)
            record = cursor.fetchall()
            # print(record)
            for i in range (0, len(record)):
                result = Waypoints()
                result.id = record[i][0]
                result.num_waypoint = record[i][1]
                result.latlon = record[i][2]
                result.mision_id = record[i][3]
                objetos.append(result)
            cursor.close()
            return objetos

        except(Exception) as e:
            print("Error al actualizar el usuario", e)
            objetos = None
        
        finally:
            if(cursor):
                cursor.close()
                print("Se ha cerrado el cursor")
            return objetos