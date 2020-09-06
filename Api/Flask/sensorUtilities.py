import urllib.request
import urllib.parse
import os
from os import path
from spectreUtilities import *
from Daos.Conexion import *
from Daos.AccesoDatos.DaoEspectros import DaoEspectros
from Daos.AccesoDatos.Logica.Espectros import Espectros

def calibrarSensoresTierra(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas):
    print("Calibrando Sensores Tierra")
    aux = "L"
    url = "http://127.0.0.1:5005/sensoresTierra/%s/%s/%s/%s/%s" %(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas, aux)
    with urllib.request.urlopen(url) as f:
        print(f.read().decode('utf-8'))
        print("Calibrados")
    
def capturarBlancoRpi(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas):
    # global blancoCapturado
    print("Capturando blanco referencia")
    aux = "C"
    url = "http://127.0.0.1:5005/sensoresTierra/%s/%s/%s/%s/%s" %(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas, aux)
    with urllib.request.urlopen(url) as f:
        blancoCapturado = f.read().decode('utf-8')
        print("captura realizada")
    return blancoCapturado

def capturarNegroRpi(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas):
    print("Capturando Dark referencia")
    aux = "N"
    url = "http://127.0.0.1:5005/sensoresTierra/%s/%s/%s/%s/%s" %(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas, aux)
    with urllib.request.urlopen(url) as f:
        NegroCapturado = f.read().decode('utf-8')
        print("captura realizada")
    return NegroCapturado

def calibrarSensoresVuelo(sensorVueloVIS, sensorVueloNIR, tiempoIntegracion, numeroCapturas):
    print("Calibrando Sensores Vuelo")
    aux = "L"
    url = "http://127.0.0.1:5050/sensoresVuelo/%s/%s/%s/%s/%s" %(sensorVueloVIS, sensorVueloNIR, tiempoIntegracion, numeroCapturas, aux)
    with urllib.request.urlopen(url) as f:
        print(f.read().decode('utf-8'))
        print("Calibrados")

def capturarVueloRpi(sensorVueloVIS, sensorVueloNIR, tiempoIntegracion, numeroCapturas):
    # global blancoCapturado
    print("Capturando")
    aux = "C"
    url = "http://127.0.0.1:5050/sensoresVuelo/%s/%s/%s/%s/%s" %(sensorVueloVIS, sensorVueloNIR, tiempoIntegracion, numeroCapturas, aux)
    with urllib.request.urlopen(url) as f:
        vueloCapturado = f.read().decode('utf-8')
        print("captura realizada")
    return vueloCapturado

def capturarVueloSinc(sensorVueloNIR, sensorVueloVIS, tiempoIntegracion, numeroCapturas, id_espectros, i):
    errorCal = "F"
    errorBd = "F"
    errorCapturaV = ""
    rel_path = '/tmp/archivoTemporalVuelo.txt';
    filePath = FileManagement.to_relative(rel_path)
    try:
        sumaCapturado = 0.0
        if os.path.exists(filePath):
            os.remove(filePath)
        else:
            print("Can not delete the file as it doesn't exists")
        vueloCapturado = capturarVueloRpi(sensorVueloVIS, sensorVueloNIR, tiempoIntegracion, numeroCapturas)
        # print("vuelocapturado "+vueloCapturado)
        v = getFilesVuelo(vueloCapturado)
        for i in range(0,len(v)):
            sumaCapturado += float(v[i])
        # TODO: Comparar el viejo con el nuevo, y si está mal volver a capturar
        # Obtener blanco referencia
        conn = conexion()
        daoEspectros = DaoEspectros(conn)
        espectro = daoEspectros.getEspectros(id_espectros)
        blancoRef = espectro.white
        # print(blancoRef)
        contador = 0
        for i in range(0,len(v)):
            if float(v[i])>float(blancoRef[i]):
                print(float(v[i]),float(blancoRef[i]))
                contador+= 1
            if contador > 100:
                break
        if contador>100:
            errorCal = "T"
            return errorBd, errorCapturaV, id_espectros, errorCal, sumaCapturado


        # ---------------------------------------------------------------------
        # print("v")
        # print(v)
        errorCapturaV = ""
    except Exception as e:
        errorCapturaV = "T"
        raise e
    
    try:
        conn = conexion()
        daoEspectros = DaoEspectros(conn)
        espectro = daoEspectros.getEspectros(id_espectros)
        espectro.capturado = v
        espectro.resultado = []
        espectro = daoEspectros.actualizarEspectros(espectro)
        conn.close()

        # conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
        # cur = conn.cursor()
        # cur.execute("""UPDATE espectros SET capturado=%s WHERE id=%s;""", ([v], id_espectros))
        # conn.commit()
        # # cur.close()
        # # conn.close() 
        
        espectroCalculado = calcularEspectro(id_espectros)
        # makeImageC(espectroCalculado, i)
        # cur.execute("""UPDATE espectros SET resultado=%s WHERE id=%s RETURNING id;""", ([espectroCalculado], id_espectros))
        # idLastEspectre = cur.fetchone()[0]
        # conn.commit()
        # cur.close()
        # conn.close()
        errorBd = ""  
    except Exception as errorBd:
        errorBd = "T"
        raise errorBd
    return errorBd, errorCapturaV, id_espectros, errorCal, sumaCapturado