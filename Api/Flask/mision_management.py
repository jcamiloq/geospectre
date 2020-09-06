import json
from Daos import Conexion
from Daos.AccesoDatos.DaoMision import DaoMision
from Daos.AccesoDatos.Logica.Mision import Mision
from Daos.AccesoDatos.DaoUsuarios import DaoUsuarios

class MisionManagement():
    @staticmethod
    def crearMision(nombre, elevacion, velocidad, modo_vuelo, modo_adq, nombre_usuario):
        data = {}
        data['errorBd'] = ""
        try:
            conn = Conexion.conexion()
            daoUsuarios = DaoUsuarios(conn)
            usuario = daoUsuarios.getUsuarioNombre(nombre_usuario)
            idUsuario = usuario.id
            mision = Mision()
            mision.nombre = nombre
            mision.elevacion = elevacion
            mision.velocidad = velocidad
            mision.modo_vuelo = modo_vuelo
            mision.modo_adq = modo_adq
            mision.usuarios_id = idUsuario
            daoMision = DaoMision(conn)
            mision = daoMision.guardarMision(mision)
            conn.close()
            if mision == None:
                data['errorBd'] = "T"
        except:
            data['errorBd'] = "T"
            print("error en BD")
        return json.dumps(data)
