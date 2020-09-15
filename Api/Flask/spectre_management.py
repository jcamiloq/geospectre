import json
from Daos import Conexion
from Daos.AccesoDatos.DaoEspectros import DaoEspectros
from Daos.AccesoDatos.Logica.Espectros import Espectros

class SpectreManagement():
    @staticmethod
    def guardarBlanco(idEspectro, blanco, negro, capturado, resultado, idSensor):
        if idEspectro == None:
            conn = Conexion.conexion()
            espectro = Espectros()
            espectro.white = blanco
            espectro.dark = negro
            espectro.capturado = capturado
            espectro.resultado = resultado
            espectro.sensores_id = idSensor
            
            daoEspectros = DaoEspectros(conn)
            espectro = daoEspectros.guardarEspectros(espectro)
            idEspectro = espectro.id
            print(idEspectro)
            conn.close()
        else:
            print("else blanco")
            conn = Conexion.conexion()
            daoEspectros = DaoEspectros(conn)
            espectro = daoEspectros.getEspectros(idEspectro)
            espectro.white = blanco
            espectro = daoEspectros.actualizarEspectros(espectro)
            conn.close()

    def guardarNegro(idEspectro, blanco, negro, capturado, resultado, idSensor):
        data = {}
        data['errorBd'] = ""
        if idEspectro == None:
            conn = Conexion.conexion()
            espectro = Espectros()
            espectro.white = blanco
            espectro.capturado = capturado
            espectro.resultado = resultado
            espectro.dark = negro
            espectro.sensores_id = idSensor
            daoEspectros = DaoEspectros(conn)
            espectro = daoEspectros.guardarEspectros(espectro)
            idEspectro = espectro.id
            conn.close()
        else:
            conn = Conexion.conexion()
            daoEspectros = DaoEspectros(conn)
            espectro = daoEspectros.getEspectros(idEspectro)
            espectro.dark = negro
            espectro = daoEspectros.actualizarEspectros(espectro)
            conn.close()
