from spectreUtilities import *
from sensorUtilities import *
from drone import *
from flask import Flask, request
from flask.ext.cors import CORS, cross_origin
import requests
from flask_restful import Resource, Api

import json
import psycopg2

from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
import dronekit_sitl
import time
import math
from pymavlink import mavutil
import argparse  

import urllib.request
import urllib.parse

import numpy as np
import base64
import time
from shutil import copyfile
from Daos.Conexion import *
from Daos.AccesoDatos.DaoUsuarios import DaoUsuarios
from Daos.AccesoDatos.Logica.Usuarios import Usuarios

from Daos.AccesoDatos.DaoMision import DaoMision
from Daos.AccesoDatos.Logica.Mision import Mision

from Daos.AccesoDatos.DaoTelemetria import DaoTelemetria
from Daos.AccesoDatos.Logica.Telemetria import Telemetria

from Daos.AccesoDatos.DaoSensores import DaoSensores
from Daos.AccesoDatos.Logica.Sensores import Sensores

from Daos.AccesoDatos.DaoWaypoints import DaoWaypoints
from Daos.AccesoDatos.Logica.Waypoints import Waypoints

from Daos.AccesoDatos.DaoEspectros import DaoEspectros
from Daos.AccesoDatos.Logica.Espectros import Espectros

from Daos.AccesoDatos.DaoEspway import DaoEspway
from Daos.AccesoDatos.Logica.Espway import Espway

from math import sin, cos, sqrt, atan2, radians
import queue
from threading import Thread

from file_management import FileManagement

app = Flask(__name__)

sitl = None

###########################################################################
from user_management import UserManagemet


###########################################################################
CORS(app, resources={r"/login":{"origins":"*"},
    r"/hover":{"origins":"*"},
    r"/registro":{"origins":"*"},
    r"/crearMision": {"origins": "*"} ,
    r"/conectarDron": {"origins": "*"},
    r"/obtenerTelemetria":{"origins":"*"}, 
    r"/calibrarSensores": {"origins": "*"}, 
    r"/capturarNegro": {"origins": "*"} ,
    r"/capturarBlanco": {"origins": "*"} ,
    r"/guardarBlanco": {"origins": "*"} ,
    r"/guardarNegro": {"origins": "*"} ,
    r"/capturarVuelo": {"origins": "*"} ,
    r"/guardarWaypoints": {"origins": "*"} ,
    r"/armarDron": {"origins": "*"} ,
    r"/descargarInfo": {"origins": "*"} ,
    r"/seleccionarMision": {"origins": "*"} ,
    r"/verEspectro": {"origins": "*"} ,
    })
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'

waypoints = []
elevacion = 0 
id_usuario_activo = ""
posicionDron = ""  
actitudDron = "" 
velocidadDron = ""
bateriaDron = ""


blancoCapturadoLista = []
negroCapturadoLista = []
blancoCapturado = []
negroCapturado = []
arrayWaypoints = ""
aux = ""
id_espectros= None
id_waypoints= None
ids = ""
waypoint = []
idCapturados = []
idCapturadosLista = []
caracterWaypoints = []
listaEspectros = []
numeroCapturasAsincronas = 0
intervaloCapturasAsincronas = 0
numeroWaypoint = 0
limiteBateria = 90
x = 100 - limiteBateria
# tiempoAutonomia =  (-4.655*limiteBateria)+375.52
# tiempoAutonomia = (9*(x**3)/40832)+(585*(x**2)/20416)+(2521*x/638)+(5625/1276) newton interp
tiempoAutonomia = 939.6593 + (24.08848-939.6593)/(1+ (x/88.07215)**1.896207)
print(tiempoAutonomia)
# tiempoAutonomia =  (100-limiteBateria)*4.3 #tiempo autonomia total aprox 450s
counterCal = 2
sumaBlanco = 0.0
sumaCapturado = 0.0
puntoResume = None
firstHome = None

errorCalGlobal = ""
errorCapturaGlobal = ""
errorBdGlobal = ""

def capturaVueloApi(a, n, data, i): #i para prueba, generar varias imágenes de la captura asíncrona
    global listaEspectros

    id_waypoints = waypointsDB(data['nombreMisionCrear'])

    conn = conexion()
    daoEspectros = DaoEspectros(conn)
    espectro = Espectros()
    espectro.white = a
    espectro.dark = n
    espectro.capturado = []
    espectro.resultado = []
    espectro.sensores_id = idSensorVueloVIS
    espectro = daoEspectros.guardarEspectros(espectro)
    id_espectroV = espectro.id

    c, d, e, f, sumaCapturado= capturarVueloSinc(data['sensorVueloNIR'], data['sensorVueloVIS'], data['tiempoIntegracion'], data['numeroCapturas'], id_espectroV, i)
    listaEspectros.append(id_espectroV)

    daoEspway = DaoEspway(conn)
    espway = Espway()
    espway.espectros_id = id_espectroV
    espway.waypoints_id = id_waypoints
    espway = daoEspway.guardarEspway(espway)

    conn.close()
    return data, c, d, f, sumaCapturado

def waypointsDB(nombreMisionCrear):
    global id_waypointsList, numeroWaypoint
    latlon = lat + "," + lon
    print(latlon)
    conn = conexion()
    daoMision = DaoMision(conn)
    daoWaypoints = DaoWaypoints(conn)

    mision = daoMision.getMisionNombre(nombreMisionCrear)
    idMision = mision.id
    wayp = Waypoints()
    wayp.num_waypoint = numeroWaypoint
    wayp.latlon = latlon
    wayp.mision_id = idMision
    wayp = daoWaypoints.guardarWaypoint(wayp)
    id_waypoints = wayp.id

    id_waypointsList.append(id_waypoints)

    conn.close()
    numeroWaypoint += 1
    return id_waypoints

def calcularDistanciaMetros(waypoints):
    # ----Tiempo Autonomía
    # T= potencia_bateria/consumo
    # 
    # potencia total = 4500mah
    # 
    # consumo motores = 66.6wh
    # consumo máximo = 108.8wh
    # consumo total = 399.6wh
    # consumo total máximo = 652.8 wh
    # 
    # 
    # T= 4.5*11.1/399.6 = 0.125 horas
    # 
    # Tiempo medio de vuelo = 450s
    # Tiempo mínimo de vuelo = 275.5s
    # ----Valores Simulador
    # en 831.2mts gasta 45% bat en línea recta
    # en 3 minutos gasta 42% bat en línea recta
    # en 161.22mts gasta 42%bat en modo cultivo
    # duración total aprox: 7.5 minutos
    puntoPausa = []
    puntoMedio = []
    R = 6378137.0
    distanceT = 0
    distanceW = 0
    for i in range(0,len(waypoints)-1):
        latlon1= waypoints[i]
        latlon2= waypoints[i+1]
        lat1 = (latlon1.split(","))[0]
        lon1 = (latlon1.split(","))[1]
        lat2 = (latlon2.split(","))[0]
        lon2 = (latlon2.split(","))[1]

        print(lat1 + "," + lon1  + "," + lat2 + "," + lon2)

        lat1R = radians(float(lat1))
        lat2R = radians(float(lat2))
        lon1R = radians(float(lon1))
        lon2R = radians(float(lon2))

        dlon = lon2R - lon1R
        dlat = lat2R - lat1R

        a = sin(dlat / 2)**2 + cos(lat1R) * cos(lat2R) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        distanceT += distance
        distanceW += distance

        if distanceW/float(velocidad) >= tiempoAutonomia-30:
            puntoPausa.append(str(i+1))
            
            lat1f = float(lat1)
            lat2f = float(lat2)
            lon1f = float(lon1)
            lon2f = float(lon2)
            medio1 = (lat1f+lat2f)/2
            medio2 = (lon1f+lon2f)/2
            puntoMedio.append(str(medio1)+","+str(medio2))
            
            distanceW = 0
    # print(puntoMedio)
    print("Result:", distanceT, "metres")
    return distanceT, puntoPausa, puntoMedio

def capturaContinua(numeroCapturasAsincronas, intervaloCapturasAsincronas, a, n, data, i):
    global errorCalGlobal, errorCapturaGlobal, errorBdGlobal, sumaCapturado, enCapturaContinua
    tiempo = 100
    enCapturaContinua = "T"
    while i<numeroCapturasAsincronas:
        # print("al inicio i:%s" %(i))
        if tiempo >= intervaloCapturasAsincronas:
            start_time_A = time.time()
            # time.sleep(1)
            data, c, d, f, sumaCapturado= capturaVueloApi(a, n, data, i)
            if f == "T":
                errorCalGlobal = "T"
                data['errorCal'] = "T"
            if c == "T":
                errorCapturaGlobal = "T"
                data['errorCapturaV'] = "T"
            if d =="T":
                errorBdGlobal = "T"
                data['errorBd'] = "T"
            print(c +" " + d)
            # print("dentro del if tiempo:%s" %(i))
            i = i+1

        else:
            pass
            # print("dentro del else i:%s" %(i))
        end_time_A = time.time()
        tiempo = end_time_A - start_time_A
    enCapturaContinua = "F"
        # print("tiempo:%s" %(i))
        
    # -------Llamado a Drone.py----------
    capturarVueloDrone("B")
    # -----------------------------------
    return data, sumaCapturado

@app.route('/login', methods=['POST'])
# @cross_origin(origin='*', headers=['Content-Type','Authorization'])
def login():
    data = request.get_json()
    data['errorBd'] = ""
    nombreUsuario= data["nombreUsuario"]
    password= data["password"]
    return UserManagemet.login(nombreUsuario, password)

@app.route('/registro', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def registro():
    data = request.get_json()
    data['errorBd'] = ""
    
    nombreUsuario= data["nombreUsuario"]
    password= data["password"]
    try:
        # reemplazar por DAO
        usuario = Usuarios()
        usuario.nombre = nombreUsuario
        usuario.contrasena = password
        conn = conexion()
        daoUsuarios = DaoUsuarios(conn)
        daoUsuarios.guardarUsuario(usuario)
        conn.close()
        if usuario == "F":
            data['errorBd']= "T"

    except:
        data['errorBd'] = "T"
    # print(data.get('errorBd'))
    return json.dumps(data)

@app.route('/crearMision', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def crearMision():
    global velocidad, id_espectros, firstHome, numeroWaypoint
    numeroWaypoint = 0
    firstHome = None
    id_espectros = None
    data = request.get_json()
    data['errorBd'] = ""
    nombreUsuario = data["nombreUsuario"]
    nombreMisionCrear = data["nombreMisionCrear"]
    elevacion = data["elevacion"]
    velocidad = data["velocidad"]
    modo_vuelo = data["modoVuelo"]
    modo_adq = data["modoAdquisicion"]

    print("nombremision = " + nombreMisionCrear + " " + "elevacion = " + elevacion + " " + "velocidad = " + velocidad + " " + "modoVuelo = " + modo_vuelo + " " + "Modo de Adquisicion =" + modo_adq)
    
    try:
        conn = conexion()
        daoUsuarios = DaoUsuarios(conn)
        usuario = daoUsuarios.getUsuarioNombre(nombreUsuario)
        idUsuario = usuario.id
        mision = Mision()
        mision.nombre = nombreMisionCrear
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
    print(data.get('errorBd'))
    return json.dumps(data)

@app.route('/conectarDron', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def conectarDron():
    global altura, firstHome
    data = request.get_json()
    data['errorDrone'] = ""
    conectarDron = data["conectarDron"]
    
    if conectarDron:
        try:
            altura = float(data["elevacion"])
            velocidad = float(data["velocidad"])
            # ------------------------LLAMADO A DRONE.PY-------------------------
            # -------------------------------------------------------------------
            FH = initCon(altura, velocidad)
            # -------------------------------------------------------------------
            # -------------------------------------------------------------------
            if firstHome == None or firstHome == "":
                firstHome = FH
        except Exception as e:
            data['errorDrone'] = "T"
            print("error en Dron")
            raise e
        pass
    else:
        # llamar funcion de desconexiòn en drone
        try:
            print("vehiculo desconectado")
            print("simulador off")
        except:
            print("no vehicle")
    print(data.get('errorDrone'))
    return json.dumps(data)

@app.route('/obtenerTelemetria', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def obtenerTelemetria():
    global waypointActual, lat, lon
    data = request.get_json()
    nombreMisionCrear = data["nombreMisionCrear"]
    # flagPausar = data["flagPausar"]
    # flagDetener = data["flagDetener"]
    # flagReanudar = data["flagReanudar"]
    data = {}
    data['errorBd'] = ""
    # ------------------LLAMADA A DRONE.PY---------------
    a, b, c, d, e, f, g, h, i, j, k = telem()
    # ---------------------------------------------------
    waypointActual = f
    posicionDron = str(a)
    posicionDron = posicionDron.split(":")[1]
    posicionDron = posicionDron.split(",")
    lat = posicionDron[0].split("=")[1]
    lon = posicionDron[1].split("=")[1]
    alt = posicionDron[2].split("=")[1]
    print('Position: %s'% posicionDron)
    print("Armado? " + g)
    # print('Position: %s'% vehicle.location.global_relative_frame)
    # print(lat)
    # print(lon)
    # print(alt)

    #- Read the actual attitude roll, pitch, yaw
    actitudDron = str(b)
    actitudDron = actitudDron.split(":")[1]
    actitudDron = actitudDron.split(",")
    pitch = round(float(actitudDron[0].split("=")[1]), 5)
    yaw = round(float(actitudDron[1].split("=")[1]), 5)
    roll = round(float(actitudDron[2].split("=")[1].upper()), 5)
    # print(pitch)
    # print(yaw)
    # print(roll)

    #- Read the actual velocity (m/s)
    velocidadDron = str(c)[0:4]
    # print('Velocity: %s'% velocidadDron)
    # print(velocidadDron)

    bateriaDron = str(d)
    bateriaDron = bateriaDron.split("=")[3]
    # print('Battery: %s'%bateriaDron)
    # print(bateriaDron)
    # print(h)
    if int(h) <= limiteBateria:
        data['flagBatt'] = "T"
    try:
        conn = conexion()
        daoMision = DaoMision(conn)
        mision = daoMision.getMisionNombre(nombreMisionCrear)
        idMision = mision.id
        telemetria = Telemetria()
        telemetria.pitch = pitch
        telemetria.yaw = yaw
        telemetria.roll = roll
        telemetria.lat = lat
        telemetria.lon = lon
        telemetria.alt = alt
        telemetria.bateriaDron = bateriaDron
        telemetria.velocidadDron = velocidadDron
        telemetria.mision_id = idMision
        daoTelemetria = DaoTelemetria(conn)
        telemetria = daoTelemetria.guardarTelemetria(telemetria)
        conn.close()
        pass
    except:
        data['errorBd'] = "T"
        print("error en BD")
        return json.dumps(data)
    # print(data.get('errorBd'))

    data['lat'] = lat
    data['lon'] = lon
    data['alt'] = alt
    data['pitch'] = pitch
    data['yaw'] = yaw
    data['roll'] = roll
    data['velocidadDron'] = velocidadDron
    data['bateriaDron'] = bateriaDron

    data['senalCaptura'] = e
    data['waypActual'] = f
    data['armado'] = g
    data['conectado']= i
    data['capturando']= j
    data['flagTerminar'] = k

    if(sumaBlanco != 0.0):
        if(sumaCapturado != 0.0):
            porcentageIrr = round(sumaCapturado*100/sumaBlanco, 2)
            porcentageIrr = str(porcentageIrr)
            data['porcentageIrr'] = str(porcentageIrr)+"%"
        else:
            data['porcentageIrr'] = "Indef"
    else:
        data['porcentageIrr'] = "Indef"
    try:
        data['errorBdCapturaContinua'] = errorBdGlobal
        data['errorCalCapturaContinua'] = errorCalGlobal
        data['errorCapturaContinua'] = errorCapturaGlobal
        data['enCapturaContinua'] = enCapturaContinua
    except Exception as e:
        return json.dumps(data)
        raise e
        
    return json.dumps(data)

@app.route('/calibrarSensores', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def calibrarSensores():
    #la calibración de todos los sensores es simultanea para tener concordancia de datos
    global idSensorTierraVIS, idSensorTierraNIR, idSensorVueloVIS, idSensorVueloNIR
    data = request.get_json()
    data['errorBd'] = ""
    data['errorCalibrarSensoresTierra'] = ""
    data['errorCalibrarSensoresVuelo'] = ""
    nombreMisionCrear = data["nombreMisionCrear"]

    sensorTierraVIS = data["sensorTierraVIS"]
    sensorTierraNIR = data["sensorTierraNIR"]
    sensorVueloVIS = data["sensorVueloVIS"]
    sensorVueloNIR = data["sensorVueloNIR"]

    tiempoIntegracion = data["tiempoIntegracion"]
    numeroCapturas = data["numeroCapturas"]

    print(nombreMisionCrear + "" + sensorTierraVIS + "" + sensorTierraNIR
     + "" + sensorVueloVIS + "" + sensorVueloNIR + "" + tiempoIntegracion + "" + numeroCapturas + "" )
    
    try:
        calibrarSensoresTierra(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas)
        data['errorCalibrarSensoresTierra']= "A"
        pass
    except Exception as errorCalibrarSensoresTierra:
        data['errorCalibrarSensoresTierra']= "T"
        # raise errorCalibrarSensoresTierra
        return json.dumps(data)
    
    try:
        calibrarSensoresVuelo(sensorVueloVIS, sensorVueloNIR, tiempoIntegracion, numeroCapturas)
        data['errorCalibrarSensoresVuelo']= "A"
        pass
    except Exception as errorCalibrarSensoresVuelo:
        data['errorCalibrarSensoresTierra']= "T"
        # raise errorCalibrarSensoresVuelo
        return json.dumps(data)

    try:
        conn = conexion()
        daoMision = DaoMision(conn)
        mision = daoMision.getMisionNombre(nombreMisionCrear)
        idMision = mision.id
        sensorTV = Sensores()
        sensorTV.lugar = "T"
        sensorTV.tipo = "V"
        sensorTV.numero_serie = sensorTierraVIS
        sensorTV.t_int = tiempoIntegracion
        sensorTV.numero_capt = numeroCapturas
        sensorTV.mision_id = idMision
        daoSensores = DaoSensores(conn)
        sensorTV = daoSensores.guardarSensores(sensorTV)
        idSensorTierraVIS = sensorTV.id
        
        sensorTN = Sensores()
        sensorTN.lugar = "T"
        sensorTN.tipo = "N"
        sensorTN.numero_serie = sensorTierraNIR
        sensorTN.t_int = tiempoIntegracion
        sensorTN.numero_capt = numeroCapturas
        sensorTN.mision_id = idMision
        sensorTN = daoSensores.guardarSensores(sensorTN)
        idSensorTierraNIR = sensorTN.id

        sensorVV = Sensores()
        sensorVV.lugar = "V"
        sensorVV.tipo = "V"
        sensorVV.numero_serie = sensorVueloVIS
        sensorVV.t_int = tiempoIntegracion
        sensorVV.numero_capt = numeroCapturas
        sensorVV.mision_id = idMision
        sensorVV = daoSensores.guardarSensores(sensorVV)
        idSensorVueloVIS = sensorVV.id

        sensorVN = Sensores()
        sensorVN.lugar = "V"
        sensorVN.tipo = "N"
        sensorVN.numero_serie = sensorVueloNIR
        sensorVN.t_int = tiempoIntegracion
        sensorVN.numero_capt = numeroCapturas
        sensorVN.mision_id = idMision
        sensorVN = daoSensores.guardarSensores(sensorVN)
        idSensorVueloNIR = sensorVN.id
        conn.close()

    except Exception as errorBdCal:
        data['errorBd'] = "T"
        print("error en BD")
        raise errorBdCal
        return json.dumps(data)    
    print(data.get('errorBd')+ "," + data.get('errorCalibrarSensoresTierra') + "," + data.get('errorCalibrarSensoresVuelo'))
    return json.dumps(data)

@app.route('/capturarBlanco', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def capturarBlanco():
    global a, sumaBlanco
    sumaBlanco = 0
    # obtener datos del json
    data = request.get_json()
    data['errorBd'] = ""
    data['errorCapturaB'] = ""
    data['espectroBlanco'] = ""
    sensorTierraVIS = data["sensorTierraVIS"]
    sensorTierraNIR = data["sensorTierraNIR"]
    nombreMisionCrear = data["nombreMisionCrear"]
    tiempoIntegracion = data["tiempoIntegracion"]
    numeroCapturas = data["numeroCapturas"]
    rel_path = '/tmp/archivoTemporalBlanco.txt';
    filePath = FileManagement.to_relative(rel_path)
    if os.path.exists(filePath):
        os.remove(filePath)
    else:
        print("Can not delete the file as it doesn't exists")
    try:
        # Comandar sensores para captura
        blancoCapturado = capturarBlancoRpi(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas)
        # construir imagen
        a= getFilesBlanco(blancoCapturado)
        for i in range(0, len(a)):
            sumaBlanco += float(a[i])
        print("limiteCalibracion = " + str(sumaBlanco))
        # print(a)
        makeImageW(a)
        rel_path = "/tmp/imagenEspectroW.png"
        filePath = FileManagement.to_relative(rel_path)
        with open(filePath, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            encoded_string = encoded_string.decode("utf-8")
            # print(encoded_string)
        data['espectroBlanco'] = encoded_string
        
    except Exception as errorCapturaB:
        data['errorCapturaB'] = "T"
        raise errorCapturaB
        return json.dumps(data)
    return json.dumps(data)

@app.route('/capturarNegro', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def capturarNegro():
    global n
    data = request.get_json()
    data['errorBd'] = ""
    data['errorCapturaN'] = ""
    data['espectroNegro'] = ""
    sensorTierraVIS = data["sensorTierraVIS"]
    sensorTierraNIR = data["sensorTierraNIR"]
    nombreMisionCrear = data["nombreMisionCrear"]
    tiempoIntegracion = data["tiempoIntegracion"]
    numeroCapturas = data["numeroCapturas"]
    rel_path = '/tmp/archivoTemporalNegro.txt';
    filePath = FileManagement.to_relative(rel_path)
    if os.path.exists(filePath):
        os.remove(filePath)
    else:
        print("Can not delete the file as it doesn't exists")
    try:
        negroCapturado = capturarNegroRpi(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas)
        n= getFilesNegro(negroCapturado)
        makeImageD(n)
        rel_path = "/tmp/imagenEspectroD.png"
        filePath = FileManagement.to_relative(rel_path)
        with open(filePath, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            encoded_string = encoded_string.decode("utf-8")
            # print(encoded_string)
        data['espectroNegro'] = encoded_string
    except Exception as errorCapturaN:
        data['errorCapturaN'] = "T"
        raise errorCapturaN
    return json.dumps(data)

@app.route('/guardarBlanco', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def guardarBlanco():
    global idSensorTierraVIS, id_espectros, a
    data = request.get_json()
    data['errorBd'] = ""
    relPathSrc = '/tmp/archivoTemporalBlanco.txt';
    relPathDes = '/tmp/archivoBlanco.txt';
    filePathSrc = FileManagement.to_relative(relPathSrc)
    filePathDes = FileManagement.to_relative(relPathDes)
    try:
        copyfile(filePathSrc, filePathDes)
        if id_espectros == None:
            conn = conexion()
            espectro = Espectros()
            espectro.white = a
            espectro.dark = []
            espectro.capturado = []
            espectro.resultado = []
            espectro.sensores_id = idSensorTierraVIS

            daoEspectros = DaoEspectros(conn)
            espectro = daoEspectros.guardarEspectros(espectro)
            id_espectros = espectro.id
            print(id_espectros)
            conn.close()
        else:
            print("else blanco")
            conn = conexion()
            daoEspectros = DaoEspectros(conn)
            espectro = daoEspectros.getEspectros(id_espectros)
            espectro.white = a
            espectro = daoEspectros.actualizarEspectros(espectro)
            conn.close()
            # conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
            # cur = conn.cursor()
            # cur.execute("""UPDATE espectros SET white=%s WHERE id=%s;""", ([a], id_espectros))
            # # id_espectros = cur.fetchone()[0]
            # # print(id_espectros)
            # conn.commit()
            # cur.close()
            # conn.close()
    except Exception as errorBd:
        data['errorBd'] = "T"
        return json.dumps(data)
        raise errorBd
    return json.dumps(data)

@app.route('/guardarNegro', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def guardarNegro():
    global id_espectros, n, idSensorTierraVIS
    data = request.get_json()
    data['errorBd'] = ""
    relPathSrc = '/tmp/archivoTemporalNegro.txt';
    relPathDes = '/tmp/archivoNegro.txt';
    filePathSrc = FileManagement.to_relative(relPathSrc)
    filePathDes = FileManagement.to_relative(relPathDes)
    try:
        copyfile(filePathSrc, filePathDes)
        if id_espectros == None:
            conn = conexion()
            espectro = Espectros()
            espectro.white = []
            espectro.capturado = []
            espectro.resultado = []
            espectro.dark = n
            espectro.sensores_id = idSensorTierraVIS
            daoEspectros = DaoEspectros(conn)
            espectro = daoEspectros.guardarEspectros(espectro)
            id_espectros = espectro.id
            conn.close()


            # conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
            # cur = conn.cursor()
            # cur.execute("""INSERT INTO espectros (dark, sensores_id) 
            #     VALUES (%s, %s) RETURNING id;""", ([n], idSensorTierraVIS))
            # id_espectros = cur.fetchone()[0]
            # conn.commit()
            # cur.close()
            # conn.close()
        else:
            conn = conexion()
            daoEspectros = DaoEspectros(conn)
            espectro = daoEspectros.getEspectros(id_espectros)
            espectro.dark = n
            espectro = daoEspectros.actualizarEspectros(espectro)
            conn.close()

            # conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
            # cur = conn.cursor()
            # cur.execute("""UPDATE espectros SET dark=%s WHERE id=%s;""", ([n], id_espectros))
            # # id_espectros = cur.fetchone()[0]
            # # print(id_espectros)
            # conn.commit()
            # cur.close()
            # conn.close()
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    return json.dumps(data)

@app.route('/capturarVuelo', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def capturarVuelo():
    global a, n, v, id_espectros, sumaCapturado
    # obtener datos del json
    data = request.get_json()
    sinc= data["caracterSinc"]
    data['errorBd'] = ""
    data['errorCapturaV'] = ""
    numeroCapturasAsincronas = int(data["numeroCapturasAsincronas"])
    intervaloCapturasAsincronas = int(data["intervaloCapturasAsincronas"])
    print("numeroCapturasAsincronas"+str(numeroCapturasAsincronas))
    print("intervalo"+str(intervaloCapturasAsincronas))
    # -------Llamado a Drone.py----------
    capturarVueloDrone("A")
    # -----------------------------------
    i=0
    tiempo = 100
    data['errorCal'] = "F"
    data['errorCapturaV'] = "F"
    data['errorBd'] = "F"
    try:
        if sinc == 2: #PARA CAPTURA POR WAYPOINTS
            data, c, d, f, sumaCapturado= capturaVueloApi(a, n, data, i)
            if f == "T":
                # print("capturarVuelo")
                data['errorCal'] = "T"
            if c == "T":
                data['errorCapturaV'] = "T"
            if d =="T":
                data['errorBd'] = "T"
            print(c +" " + d)
            capturarVueloDrone("B")
            # a = capturarVueloSinc(sensorVueloNIR, sensorVueloVIS, tiempoIntegracion, numeroCapturas, id_espectros) 
        else:
            t3 =threading.Thread(target = capturaContinua, args= (numeroCapturasAsincronas, intervaloCapturasAsincronas, a, n, data, i))
            t3.setDaemon(True)
            t3.start()
            # data, sumaCapturado = capturaContinua(numeroCapturasAsincronas, intervaloCapturasAsincronas, a, n, data, i)
        
    except Exception as e:
        capturarVueloDrone("B")
        data['errorBd'] = "T"
        raise e

    print(listaEspectros)
    return json.dumps(data)

# @app.route('/generarEspectros', methods=['POST'])
# @cross_origin(origin='*', headers=['Content-Type','Authorization'])

@app.route('/guardarWaypoints', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def guardarWaypoints():
    global id_waypointsList, arrayPuntosDescanso, listaWaypoints#, vehicle, sitl
    id_waypointsList = []
    aPD = []
    data = request.get_json()
    waypointsList = []
    nombreMisionCrear = data['nombreMisionCrear']
    arrayWaypoints = data['waypoints']
    arrayWaypoints = arrayWaypoints.split("\n")
    waypointsDic={}
    for x in range(0,len(arrayWaypoints)):
        waypointsDic["waypoint{0}".format(x)] = arrayWaypoints[x]#+arrayWaypoints[x+1]
    # print(waypointsDic)
    for i in range(0, len(waypointsDic)):
        waypointsList.append(waypointsDic["waypoint{0}".format(i)])
    a, arrayPuntosDescanso, puntoMedio =calcularDistanciaMetros(waypointsList)
    for i in range(0, len(arrayPuntosDescanso)):
        aPD.append(str(arrayPuntosDescanso[i]))
    data['arrayPuntosDescanso'] = puntoMedio
    data['errorBd'] = ""
    print(a, aPD, puntoMedio)
    listaWaypoints = waypointsList
    # ---------------------------LLAMADO A DRONE.PY------------------------
    # FSM(1)
    # sleep(.3)
    # FSM(1)
    # sleep(.3)
    # FSM(waypointsList)
    # sleep(.3)
    try:
        estadoWaypoints(waypointsList)
    except Exception as e:
        data['errorBd'] = "T"
        raise e
        return json.dumps(data)

    # ---------------------------------------------------------------------
    return json.dumps(data)

@app.route('/guardarDescanso', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def guardarDescanso():
    global remainingWp, puntoResume
    data = request.get_json()
    data['errorBd'] = ""
    waypointsDescansoList = []
    nombreMisionCrear = data['nombreMisionCrear']
    caract = data['caract']
    arrayWaypointsD = data['waypointsDescanso']
    # arrayWaypointsD = arrayWaypointsD.split("\n")
    # waypointsDic={}
    # for x in range(0,len(arrayWaypointsD)):
    #     waypointsDic["waypoint{0}".format(x)] = arrayWaypointsD[x]#+arrayWaypoints[x+1]
    # # print(waypointsDic)
    # for i in range(0, len(waypointsDic)):
    #     waypointsDescansoList.append(waypointsDic["waypoint{0}".format(i)])
    #     pass
    
    print("latlon",arrayWaypointsD)
    print("#way",arrayPuntosDescanso)
    print(caract)
    # ---------construye un array que incluye los puntos de descanso en su lugar---------
    # waypointsFinal = []
    # j= 0
    # punto = arrayPuntosDescanso.pop(0)
    # for k in range(0,len(listaWaypoints)):
    #     if punto==k:
    #         waypointsFinal.append(arrayWaypointsD[j])
    #         waypointsFinal.append(listaWaypoints[k])
    #         print(arrayPuntosDescanso)
    #         if arrayPuntosDescanso:
    #             punto = arrayPuntosDescanso.pop(0)
    #         j+=1
    #     else:
    #         waypointsFinal.append(listaWaypoints[k])
    # print(waypointsFinal)

    # ---------------------------LLAMADO A DRONE.PY------------------------
    
    remainingWp, puntoResume, home = estadoPauseSinc(caract, arrayWaypointsD)
    # ---------------------------------------------------------------------
    puntoResume = str(puntoResume).split(",")
    
    return json.dumps(data)

@app.route('/armarDron', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def armarDron():
    data = request.get_json()
    data['errorBd'] = ""
    data['errorArmado'] = ""
    # ----------------------------------LLAMADO A DRONE.PY------------------------------
    errorArmado = estadoArmado(1)
    # sleep(0.3)
    # FSM(1)
    # ----------------------------------------------------------------------------------
    # print(errorArmado)
    data['errorArmado'] = errorArmado
    try:
        # i
        pass
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    return json.dumps(data)

@app.route('/iniciarMision', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def iniciarMision():
    data = request.get_json()
    try:
    # --------------------------------LLAMADO A DRONE.PY------------------------------
        errorDespegue = estadoDespegue(firstHome)
        # sleep(0.3)
        # FSM(1)
    # ----------------------------------------------------------------------------------
        data['errorDespegue'] = ""
        # print(errorDespegue)
    except Exception as errorDespegue:
        data['errorDespegue'] = "T"
        raise errorDespegue
    return json.dumps(data)

@app.route('/hover', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def hover():
    global counterCal
    data = request.get_json()
    calibrarFlag = data['calibrarFlag']
    print("CAl"+ str(calibrarFlag))
    counterCal += 1
    print(counterCal)
    print(str(counterCal%2))
    if calibrarFlag == "H" and counterCal%2 == 0:
        data["volverCapturar"] = "T"
    if counterCal%2 == 0:
        calibrarFlag = "F"
    # ----------------------------------LLAMADO A DRONE.PY------------------------------
    hoverDrone(calibrarFlag)
   # --------------------------------------------------------------------
    return json.dumps(data)

@app.route('/pausarMision', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def pausarMision():
    global remainingWp
    data = request.get_json()
    flagPausar = data['flagPausar']
    try:
    # ----------------------------------LLAMADO A DRONE.PY------------------------------
        remainingWp = estadoPause(1, flagPausar)
        # print(remainingWp)
        data['errorPausa'] = "F"
        # sleep(0.3)
        # FSM(1)
    # ----------------------------------------------------------------------------------
    except Exception as errorPausa:
        data['errorPausa'] = "T"
        raise errorPausa
    return json.dumps(data)

@app.route('/reanudarMision', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def reanudarMision():
    data = request.get_json()
    # flagPausar = data['flagPausar']
    try:
    # ----------------------------------LLAMADO A DRONE.PY------------------------------
        if puntoResume == None:
            errorDespegue = estadoResume(remainingWp, firstHome)
        else:
            errorDespegue = estadoResume(remainingWp, firstHome, float(puntoResume[0]), float(puntoResume[1]))
        # sleep(0.3)
        # FSM(1)
    # ----------------------------------------------------------------------------------
        data['errorDespegue'] = ""
    except Exception as errorDespegue:
        data['errorDespegue'] = "T"
        raise errorDespegue
        return json.dumps(data)
    return json.dumps(data)

@app.route('/detenerMision', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def detenerMision():
    global remainingWp, id_waypointsList, waypointActual, lat, lon, idSensorTierraVIS, idSensorTierraNIR, idSensorVueloVIS, idSensorVueloNIR 
    global a, n, v, id_espectros
    remainingWp = []
    id_waypointsList = []
    waypointActual = 0
    lat = 0
    lon = 0
    idSensorTierraVIS = ""
    idSensorTierraNIR = ""
    idSensorVueloNIR = ""
    idSensorVueloVIS = ""
    a = []
    v = []
    n = []
    id_espectros = 0
    data = request.get_json()
    # flagPausar = data['flagPausar']
    try:
    # ----------------------------------LLAMADO A DRONE.PY------------------------------
        estadoCancel(1)
        data['errorDetener'] = "F"
        # sleep(0.3)
        # FSM(1)
    # ----------------------------------------------------------------------------------
    except Exception as errorDetener:
        data['errorDetener'] = "T"
        raise errorDetener
    return json.dumps(data)

@app.route('/descargarInfo', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def descargarInfo():
    data = request.get_json()
    nombreUsuario = data['user']
    password = data['password']
    data = {}
    data['errorBd'] = ""
    nombreMisiones = []

    conn = conexion()
    daoUsuarios = DaoUsuarios(conn)
    usuario = daoUsuarios.getUsuarioLogin(nombreUsuario, password)
    idUsuario = usuario.id

    daoMision = DaoMision(conn)
    misiones = daoMision.getAllMision(idUsuario)
    data['misiones']= misiones
    return json.dumps(data)

@app.route('/seleccionarMision', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def seleccionarMision():
    data = request.get_json()
    data['errorBd'] = ""
    data['waypointsList'] = ""
    misionSeleccionada = data['misionSeleccionada']
    numWaypoints = []
    # sensores = []
    # espectros = []
    # espectro = []
    
    try:
        # Obtengo ID de mision
        conn = conexion()
        daoMision = DaoMision(conn)
        mision = daoMision.getMisionNombre(misionSeleccionada)
        idMision = mision.id

        # Obtengo lista IDs sensores 201, 202, 203
        daoSensores = DaoSensores(conn)
        sensores = daoSensores.getSensoresMision(idMision)

        # Por cada ID de sensores obtengo ID de espectros 137, 138, 139
        for i in range(len(sensores)):
            daoEspectros = DaoEspectros(conn)
            espectros = daoEspectros.getEspectrosSensores(sensores[i])

            # Por cada ID de espectros retorno el RESULTADO del espectro
            # y verifico si está vacío
            for j in range(len(espectros)):
                espectro = daoEspectros.getEspectros(espectros[j])
                idEspectro = espectro.id
                print(idEspectro)
                resultado = espectro.resultado

                # Si está vació borro el waypoint, y el espectro
                # CASCADE espway
                if len(resultado)== 0:
                    daoEspway = DaoEspway(conn)
                    espway = daoEspway.getEspwayEspectro(idEspectro)
                    print("llego al if")
                    if espway == None:
                        print("if")
                        daoEspectros.borrarEspectros(idEspectro)
                    else:
                        print("else")
                        idWaypoint = espway.waypoints_id

                        daoWaypoints = DaoWaypoints(conn)
                        daoWaypoints.borrarWaypoint(idWaypoint)

                        daoEspectros.borrarEspectros(idEspectro)

        daoWaypoints = DaoWaypoints(conn)
        waypointsList = daoWaypoints.getAllWaypoints(idMision)
        for i in range(0, len(waypointsList)):
            numWaypoints.append(str(waypointsList[i].num_waypoint))
        # poner generate

        print(numWaypoints)
        conn.close()
        data['waypoints'] = numWaypoints
        pass
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    return json.dumps(data)

@app.route('/borrarMision', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def borrarMision():
    data = request.get_json()
    misionSeleccionada = data['misionSeleccionada']
    print(misionSeleccionada)
    try:
        conn = conexion()
        daoMision = DaoMision(conn)
        mision = daoMision.getMisionNombre(misionSeleccionada)
        idMision = mision.id
        print(idMision)
        daoMision.borrarMision(idMision)
        conn.close()
        data['errorBd'] = "F"
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    return json.dumps(data)

@app.route('/verEspectro', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def verEspectro():
    data = request.get_json()
    data['errorBd'] = ""
    data['waypointsList'] = ""
    data['espectroC'] = ""
    data['espectroR'] = ""
    nombreMisionCrear = data['nombreMisionCrear']
    waypointSeleccionado = data['waypointSeleccionado']
    print(waypointSeleccionado)
    try:
        conn = conexion()
        daoMision = DaoMision(conn)
        mision = daoMision.getMisionNombre(nombreMisionCrear)
        idMision = mision.id

        daoWaypoints = DaoWaypoints(conn)
        wayp = daoWaypoints.getWaypointByNumber(waypointSeleccionado, idMision)
        idWayp = wayp.id

        daoEspway = DaoEspway(conn)
        espway = daoEspway.getEspwayWaypoint(idWayp)
        idEspectro = espway.espectros_id

        daoEspectros = DaoEspectros(conn)
        espectro = daoEspectros.getEspectros(idEspectro)
        resultado = espectro.resultado
        conn.close()

        b = makeImageC(resultado, 1)

        with open(b, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            encoded_string = encoded_string.decode("utf-8")
        data['espectroC'] = encoded_string

        # with open("D:/Tesis/Api/Flask/imagenEspectroC2.png", "rb") as image_file:
        #     encoded_string = base64.b64encode(image_file.read())
        #     encoded_string = encoded_string.decode("utf-8")
        # data['espectroR'] = encoded_string
        pass
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    return json.dumps(data)

@app.route('/guardarEspectro', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def guardarEspectro():
    data = request.get_json()
    data['errorBd'] = ""
    data['waypointsList'] = ""
    data['espectroC'] = ""
    data['espectroR'] = ""
    nombreMisionCrear = data['nombreMisionCrear']
    waypointSeleccionado = data['waypointSeleccionado']
    ruta = str(data['ruta'])
    usuario = str(data['usuario'])
    print(waypointSeleccionado)
    try:
        if os.path.isdir(ruta):
            conn = conexion()
            daoMision = DaoMision(conn)
            mision = daoMision.getMisionNombre(nombreMisionCrear)
            idMision = mision.id
            altura = mision.elevacion
            daoWaypoints = DaoWaypoints(conn)
            wayp = daoWaypoints.getWaypointByNumber(waypointSeleccionado, idMision)
            idWayp = wayp.id
            latlon = wayp.latlon
            latlon = latlon.split(",")

            daoEspway = DaoEspway(conn)
            espway = daoEspway.getEspwayWaypoint(idWayp)
            idEspectro = espway.espectros_id

            daoEspectros = DaoEspectros(conn)
            espectro = daoEspectros.getEspectros(idEspectro)
            resultado = espectro.resultado
            conn.close()
            ruta += "/Usuario("+usuario+")"+"Mision("+nombreMisionCrear+")"+ "Waypoint("+waypointSeleccionado+")"
            filePath = FileManagement.to_relative(ruta)
            # print(ruta)
            generate(resultado, filePath, float(latlon[0]), float(latlon[1]), altura)
        else:
            data['errorCarpeta'] = "T"
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    return json.dumps(data)

@app.route('/guardarTodos', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def guardarTodos():
    data = request.get_json()
    data['errorBd'] = ""
    nombreMisionCrear = data['nombreMisionCrear']
    ruta = str(data['ruta'])
    usuario = str(data['usuario'])
    try:
        if os.path.isdir(ruta):
            data['errorCarpeta'] = ""
            idsWaypoints = []
            idsEspectros = []
            latlonsWaypoints = []
            conn = conexion()
            daoMision = DaoMision(conn)
            mision = daoMision.getMisionNombre(nombreMisionCrear)
            idMision = mision.id
            altura = mision.elevacion
            daoWaypoints = DaoWaypoints(conn)
            waypointsList = daoWaypoints.getAllWaypoints2(idMision)
            for i in range(0, len(waypointsList)):
                idsWaypoints.append(waypointsList[i].id)
                latlonsWaypoints.append(waypointsList[i].latlon)
            print(idsWaypoints)

            for i in range(0, len(idsWaypoints)):
                daoEspway = DaoEspway(conn)
                espway = daoEspway.getEspwayWaypoint(idsWaypoints[i])
                idEspectro = espway.espectros_id
                idsEspectros.append(idEspectro)
            print(idsEspectros)

            for i in range(0, len(idsEspectros)):
                latlons = latlonsWaypoints[i].split(",")
                rutaG = ruta
                daoEspectros = DaoEspectros(conn)
                espectro = daoEspectros.getEspectros(idsEspectros[i])
                resultado = espectro.resultado
                rutaG += "/Usuario("+usuario+")"+"Mision("+nombreMisionCrear+")"+ "WaypointNumber("+str(i)+")"
                filePath = FileManagement.to_relative(rutaG)
                print(rutaG)
                generate(resultado, filePath, float(latlons[0]), float(latlons[1]), altura)

                # generate(resultado, rutaG, float(latlons[0]), float(latlons[1]), 5)
            conn.close()
        else:
            data['errorCarpeta'] = "T"
        # with open("D:/Tesis/Api/Flask/imagenEspectroC2.png", "rb") as image_file:
        #     encoded_string = base64.b64encode(image_file.read())
        #     encoded_string = encoded_string.decode("utf-8")
        # data['espectroR'] = encoded_string
        pass
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    return json.dumps(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
