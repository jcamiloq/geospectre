import json
from Daos import Conexion
from Daos.AccesoDatos.DaoUsuarios import DaoUsuarios
from Daos.AccesoDatos.Logica.Usuarios import Usuarios

class UserManagemet:
    
    @staticmethod
    def login(nombreUsuario, password):
        data = {}
        data['errorBd'] = ""
        try:
            conn = Conexion.conexion()
            daoUsuarios = DaoUsuarios(conn)
            usuario = daoUsuarios.getUsuarioLogin(nombreUsuario, password)
            
            if usuario == None:
                data['errorBd'] = "T"
            else:
                print(usuario.nombre)
        except Exception as e:
            data['errorBd'] = "T"
            raise e
        return json.dumps(data)

    @staticmethod
    def registro(nombreUsuario, password):
        data = {}
        data['errorBd'] = ""

        try:
            usuario = Usuarios()
            usuario.nombre = nombreUsuario
            usuario.contrasena = password
            conn = Conexion.conexion()
            daoUsuarios = DaoUsuarios(conn)
            daoUsuarios.guardarUsuario(usuario)
            conn.close()
            if usuario == "F":
                data['errorBd']= "T"

        except:
            data['errorBd'] = "T"
        return json.dumps(data)
