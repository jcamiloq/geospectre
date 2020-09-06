from Daos import Conexion
from Daos.AccesoDatos.DaoUsuarios import DaoUsuarios

class UserManagemet:
    
    @staticmethod
    def login(nombreUsuario, password):
        data = {} 
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

