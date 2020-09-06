from Daos import Conexion
from Daos.AccesoDatos.DaoEspectros import DaoEspectros

class UserManagemet:
    
    @staticmethod
    def login(nombreUsuario, password):
        data = {} 
        try:
            conn = conexion()
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

