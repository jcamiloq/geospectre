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
from math import sin, cos, sqrt, atan2, radians
import queue
from threading import Thread

# ----------------IMPORT DAO-----------------------------
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
# -------------------------------------------------------
#------------------IMPORT MANAGEMENT--------------------
from user_management import UserManagemet
from mision_management import MisionManagement
from drone_management import DroneManagement
from spectre_management import SpectreManagement
from api_info import WaypointInfo, SpectreInfo, SensorInfo
from file_management import FileManagement
#-------------------------------------------------------

app = Flask(__name__)
sitl = None
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

limiteBateria = 85

valores_waypoints = WaypointInfo()
valores_espectros = SpectreInfo()
valores_sensores = SensorInfo()

def calcularAutonomia(limiteBateria):
    x = 100 - limiteBateria
    # tiempoAutonomia =  (-4.655*limiteBateria)+375.52
    # tiempoAutonomia = (9*(x**3)/40832)+(585*(x**2)/20416)+(2521*x/638)+(5625/1276) newton interp
    tiempoAutonomia = 939.6593 + (24.08848-939.6593)/(1+ (x/88.07215)**1.896207)
    print(tiempoAutonomia)
    # tiempoAutonomia =  (100-limiteBateria)*4.3 #tiempo autonomia total aprox 450s
    return tiempoAutonomia
     
def capturaVueloApi(a, n, data, i): #i para prueba, generar varias imágenes de la captura asíncrona
    id_waypoints = waypointsDB(data['nombreMisionCrear'])
    conn = conexion()
    daoEspectros = DaoEspectros(conn)
    espectro = Espectros()
    espectro.white = a
    espectro.dark = n
    espectro.capturado = []
    espectro.resultado = []
    espectro.sensores_id = valores_sensores.idSensorVueloVIS
    espectro = daoEspectros.guardarEspectros(espectro)
    id_espectroV = espectro.id

    c, d, e, f, valores_sensores.sumaCapturado= capturarVueloSinc(data['sensorVueloNIR'], data['sensorVueloVIS'], data['tiempoIntegracion'], data['numeroCapturas'], id_espectroV, i)

    daoEspway = DaoEspway(conn)
    espway = Espway()
    espway.espectros_id = id_espectroV
    espway.waypoints_id = id_waypoints
    espway = daoEspway.guardarEspway(espway)

    conn.close()
    return data, c, d, f, valores_sensores.sumaCapturado

def waypointsDB(nombreMisionCrear):
    latlon = valores_waypoints.lat + "," + valores_waypoints.lon
    print(latlon)
    conn = conexion()
    daoMision = DaoMision(conn)
    daoWaypoints = DaoWaypoints(conn)

    mision = daoMision.getMisionNombre(nombreMisionCrear)
    idMision = mision.id
    wayp = Waypoints()
    wayp.num_waypoint = valores_waypoints.numeroWaypoint
    wayp.latlon = latlon
    wayp.mision_id = idMision
    wayp = daoWaypoints.guardarWaypoint(wayp)
    id_waypoints = wayp.id

    valores_waypoints.id_waypointsList.append(id_waypoints)

    conn.close()
    valores_waypoints.numeroWaypoint += 1
    return id_waypoints

def calcularDistanciaMetros(waypoints, velocidad):
    tiempoAutonomia = calcularAutonomia(limiteBateria)
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

        if distanceW/float(velocidad) >= tiempoAutonomia-45:
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
    return puntoPausa, puntoMedio

def capturaContinua(numeroCapturasAsincronas, intervaloCapturasAsincronas, a, n, data, i):
    tiempo = 100
    valores_sensores.enCapturaContinua = "T"
    while i<numeroCapturasAsincronas:
        # print("al inicio i:%s" %(i))
        if tiempo >= intervaloCapturasAsincronas:
            start_time_A = time.time()
            # time.sleep(1)
            data, c, d, f, valores_sensores.sumaCapturado= capturaVueloApi(a, n, data, i)
            if f == "T":
                valores_sensores.errorCalGlobal = "T"
                data['errorCal'] = "T"
            if c == "T":
                valores_sensores.errorCapturaGlobal = "T"
                data['errorCapturaV'] = "T"
            if d =="T":
                valores_sensores.errorBdGlobal = "T"
                data['errorBd'] = "T"
            print(c +" " + d)
            # print("dentro del if tiempo:%s" %(i))
            i = i+1

        else:
            pass
            # print("dentro del else i:%s" %(i))
        end_time_A = time.time()
        tiempo = end_time_A - start_time_A
    valores_sensores.enCapturaContinua = "F"
        # print("tiempo:%s" %(i))
        
    # -------Llamado a Drone.py----------
    capturarVueloDrone("B")
    # -----------------------------------
    return data, valores_sensores.sumaCapturado

@app.route('/login', methods=['POST'])
# @cross_origin(origin='*', headers=['Content-Type','Authorization'])
def login():
    data = request.get_json()
    nombreUsuario= data["nombreUsuario"]
    password= data["password"]
    return UserManagemet.login(nombreUsuario, password)

@app.route('/registro', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def registro():
    data = request.get_json()
    nombreUsuario= data["nombreUsuario"]
    password= data["password"]
    return UserManagemet.registro(nombreUsuario, password)

@app.route('/crearMision', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def crearMision():
    valores_waypoints.numeroWaypoint = 0
    valores_waypoints.firstHome = None
    valores_espectros.id_espectros = None
    data = request.get_json()
    data['errorBd'] = ""
    nombreUsuario = data["nombreUsuario"]
    nombreMisionCrear = data["nombreMisionCrear"]
    elevacion = data["elevacion"]
    velocidad = data["velocidad"]
    modo_vuelo = data["modoVuelo"]
    modo_adq = data["modoAdquisicion"]

    drone = DroneManagement()
    drone.velocidad = velocidad
    drone.id_espectros = valores_espectros.id_espectros
    drone.firstHome = valores_waypoints.firstHome
    drone.numeroWaypoint = valores_waypoints.numeroWaypoint

    print("nombremision = " + nombreMisionCrear + " " + "elevacion = " + elevacion + " " + "velocidad = " + velocidad + " " + "modoVuelo = " + modo_vuelo + " " + "Modo de Adquisicion =" + modo_adq)
    return MisionManagement.crearMision(
        nombreMisionCrear, elevacion, velocidad, modo_vuelo, modo_adq, nombreUsuario
    )

@app.route('/conectarDron', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def conectarDron():
    data = request.get_json()
    data['errorDrone'] = ""
    conectarDron = data["conectarDron"]
    if conectarDron:
        try:
            altura = float(data["elevacion"])
            velocidad = float(data["velocidad"])
            # ------------------------LLAMADO A DRONE.PY-------------------------
            FH = initCon(altura, velocidad)
            # -------------------------------------------------------------------
            if valores_waypoints.firstHome == None or valores_waypoints.firstHome == "":
                valores_waypoints.firstHome = FH
        except Exception as e:
            data['errorDrone'] = "T"
            print("error en conectarDron: ", e)
            raise e
        finally:
            return json.dumps(data)
    else:
        # llamar funcion de desconexiòn en drone
        try:
            print("vehiculo desconectado")
            print("simulador off")
        except:
            print("no vehicle")
        finally:
            return json.dumps(data)

@app.route('/obtenerTelemetria', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def obtenerTelemetria():
    data = request.get_json()
    nombreMisionCrear = data["nombreMisionCrear"]
    data = {}
    data['errorBd'] = ""
    # ------------------LLAMADA A DRONE.PY---------------
    dicTelem = telem()
    # ---------------------------------------------------
    posicionDron = str(dicTelem["posicionDron"])
    valores_waypoints.waypointActual = dicTelem["waypointActual"]
    actitudDron = str(dicTelem["actitudDron"])
    velocidadDron = str(dicTelem["velocidadDron"])[0:4]
    bateriaDron = str(dicTelem["bateriaDron"])
    senalCaptura = dicTelem["senalCaptura"]
    armado = dicTelem["armado"]
    batteryLevel = dicTelem["batteryLevel"]
    dronConectado = dicTelem["dronConectado"]
    capturando = dicTelem["capturando"]
    flagTerminar = dicTelem["flagTerminar"]

    posicionDron = posicionDron.split(":")[1]
    posicionDron = posicionDron.split(",")
    valores_waypoints.lat = posicionDron[0].split("=")[1]
    valores_waypoints.lon = posicionDron[1].split("=")[1]
    alt = posicionDron[2].split("=")[1]
    print('Position: %s'% posicionDron)

    #- Read the actual attitude roll, pitch, yaw
    actitudDron = actitudDron.split(":")[1]
    actitudDron = actitudDron.split(",")
    pitch = round(float(actitudDron[0].split("=")[1]), 5)
    yaw = round(float(actitudDron[1].split("=")[1]), 5)
    roll = round(float(actitudDron[2].split("=")[1].upper()), 5)
    bateriaDron = bateriaDron.split("=")[3]
    if int(batteryLevel) <= limiteBateria:
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
        telemetria.lat = valores_waypoints.lat
        telemetria.lon = valores_waypoints.lon
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

    data['lat'] = valores_waypoints.lat
    data['lon'] = valores_waypoints.lon
    data['alt'] = alt
    data['pitch'] = pitch
    data['yaw'] = yaw
    data['roll'] = roll
    data['velocidadDron'] = velocidadDron
    data['bateriaDron'] = bateriaDron

    data['senalCaptura'] = senalCaptura
    data['waypActual'] = valores_waypoints.waypointActual
    data['armado'] = armado
    data['conectado']= dronConectado
    data['capturando']= capturando
    data['flagTerminar'] = flagTerminar

    if(valores_sensores.sumaBlanco != 0.0):
        if(valores_sensores.sumaCapturado != 0.0):
            porcentageIrr = round(valores_sensores.sumaCapturado*100/valores_sensores.sumaBlanco, 2)
            porcentageIrr = str(porcentageIrr)
            data['porcentageIrr'] = str(porcentageIrr)+"%"
        else:
            data['porcentageIrr'] = "Indef"
    else:
        data['porcentageIrr'] = "Indef"
    try:
        data['errorBdCapturaContinua'] = valores_sensores.errorBdGlobal
        data['errorCalCapturaContinua'] = valores_sensores.errorCalGlobal
        data['errorCapturaContinua'] = valores_sensores.errorCapturaGlobal
        data['enCapturaContinua'] = valores_sensores.enCapturaContinua
    except Exception as e:
        return json.dumps(data)
        raise e
        
    return json.dumps(data)

@app.route('/calibrarSensores', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def calibrarSensores():
    #la calibración de todos los sensores es simultanea para tener concordancia de datos
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
        valores_sensores.idSensorTierraVIS = sensorTV.id
        
        sensorTN = Sensores()
        sensorTN.lugar = "T"
        sensorTN.tipo = "N"
        sensorTN.numero_serie = sensorTierraNIR
        sensorTN.t_int = tiempoIntegracion
        sensorTN.numero_capt = numeroCapturas
        sensorTN.mision_id = idMision
        sensorTN = daoSensores.guardarSensores(sensorTN)
        valores_sensores.idSensorTierraNIR = sensorTN.id

        sensorVV = Sensores()
        sensorVV.lugar = "V"
        sensorVV.tipo = "V"
        sensorVV.numero_serie = sensorVueloVIS
        sensorVV.t_int = tiempoIntegracion
        sensorVV.numero_capt = numeroCapturas
        sensorVV.mision_id = idMision
        sensorVV = daoSensores.guardarSensores(sensorVV)
        valores_sensores.idSensorVueloVIS = sensorVV.id

        sensorVN = Sensores()
        sensorVN.lugar = "V"
        sensorVN.tipo = "N"
        sensorVN.numero_serie = sensorVueloNIR
        sensorVN.t_int = tiempoIntegracion
        sensorVN.numero_capt = numeroCapturas
        sensorVN.mision_id = idMision
        sensorVN = daoSensores.guardarSensores(sensorVN)
        valores_sensores.idSensorVueloNIR = sensorVN.id
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
    valores_sensores.sumaBlanco = 0
    blancoCapturado = []
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
        valores_espectros.espectroBlanco= getFilesBlanco(blancoCapturado)
        for i in range(0, len(valores_espectros.espectroBlanco)):
            valores_sensores.sumaBlanco += float(valores_espectros.espectroBlanco[i])
        print("limiteCalibracion = " + str(valores_sensores.sumaBlanco))
        # print(a)
        makeImageW(valores_espectros.espectroBlanco)
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
    negroCapturado = []
    if os.path.exists(filePath):
        os.remove(filePath)
    else:
        print("Can not delete the file as it doesn't exists")
    try:
        negroCapturado = capturarNegroRpi(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas)
        valores_espectros.espectroNegro= getFilesNegro(negroCapturado)
        makeImageD(valores_espectros.espectroNegro)
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
    data = request.get_json()
    data['errorBd'] = ""
    relPathSrc = '/tmp/archivoTemporalBlanco.txt';
    relPathDes = '/tmp/archivoBlanco.txt';
    filePathSrc = FileManagement.to_relative(relPathSrc)
    filePathDes = FileManagement.to_relative(relPathDes)
    try:
        copyfile(filePathSrc, filePathDes)
        print(valores_espectros.espectroBlanco)
        SpectreManagement.guardarBlanco(valores_espectros.id_espectros, valores_espectros.espectroBlanco, [], [], [], valores_sensores.idSensorTierraVIS)
    except Exception as errorBd:
        data['errorBd'] = "T"
        print("Error de DB en guardarBlanco: ", errorBd)
        return json.dumps(data)
        raise errorBd
    return json.dumps(data)

@app.route('/guardarNegro', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def guardarNegro():
    data = request.get_json()
    data['errorBd'] = ""
    relPathSrc = '/tmp/archivoTemporalNegro.txt';
    relPathDes = '/tmp/archivoNegro.txt';
    filePathSrc = FileManagement.to_relative(relPathSrc)
    filePathDes = FileManagement.to_relative(relPathDes)
    try:
        copyfile(filePathSrc, filePathDes)
        SpectreManagement.guardarNegro(valores_espectros.id_espectros, [], valores_espectros.espectroNegro, [], [], valores_sensores.idSensorTierraVIS)
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    return json.dumps(data)

@app.route('/capturarVuelo', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def capturarVuelo():
    # obtener datos del json
    data = request.get_json()
    # -------Llamado a Drone.py----------
    capturarVueloDrone("A")
    # -----------------------------------
    try:
        if data["caracterSinc"] == 2: #PARA CAPTURA POR WAYPOINTS
            data, c, d, f, valores_sensores.sumaCapturado = capturaVueloApi(valores_espectros.espectroBlanco, valores_espectros.espectroNegro, data, 0)
            data['errorCal'] = "T" if f=="T" else "F"
            data['errorCapturaV'] = "T" if c=="T" else "F"
            data['errorBd'] = "T" if d=="T" else "F"
            # -------Llamado a Drone.py----------
            capturarVueloDrone("B")
        else:
            t3 =threading.Thread(
                target = capturaContinua, 
                args= (int(data["numeroCapturasAsincronas"]), int(data["intervaloCapturasAsincronas"]), valores_espectros.espectroBlanco, valores_espectros.espectroNegro, data, 0)
            )
            t3.setDaemon(True)
            t3.start()        
    except Exception as e:
        # -------Llamado a Drone.py----------
        capturarVueloDrone("B")
        data['errorBd'] = "T"
        raise e
    finally:
        return json.dumps(data)

@app.route('/guardarWaypoints', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def guardarWaypoints():
    valores_waypoints.id_waypointsList = []
    data = request.get_json()
    arrayWaypoints = data['waypoints'].split("\n")
    velocidad = int(data['velocidad'])
    arrayPuntosDescanso, puntoMedio =calcularDistanciaMetros(arrayWaypoints, velocidad)
    data['arrayPuntosDescanso'] = puntoMedio
    data['errorBd'] = ""
    # ---------------------------LLAMADO A DRONE.PY------------------------
    try:
        estadoWaypoints(arrayWaypoints)
    except Exception as e:
        data['errorBd'] = "T"
        raise e
        return json.dumps(data)
    # ---------------------------------------------------------------------
    return json.dumps(data)

@app.route('/guardarDescanso', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def guardarDescanso():
    data = request.get_json()
    data['errorBd'] = ""
    caract = data['caract']
    arrayWaypointsD = data['waypointsDescanso']
    try:
        # ---------------------------LLAMADO A DRONE.PY------------------------
        valores_waypoints.remainingWp, valores_waypoints.puntoResume, home = estadoPauseSinc(caract, arrayWaypointsD)
        # ---------------------------------------------------------------------
        valores_waypoints.puntoResume = str(valores_waypoints.puntoResume).split(",")
    except Exception as e:
        data['errorBd'] = "T"
        raise e
    finally:
        return json.dumps(data)

@app.route('/armarDron', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def armarDron():
    data = request.get_json()
    data['errorBd'] = ""
    data['errorArmado'] = ""
    try:
        # ----------------------------------LLAMADO A DRONE.PY------------------------------
        errorArmado = estadoArmado(1)
        # ----------------------------------------------------------------------------------
        data['errorArmado'] = errorArmado
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    finally:
        return json.dumps(data)

@app.route('/iniciarMision', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def iniciarMision():
    data = request.get_json()
    try:
    # --------------------------------LLAMADO A DRONE.PY------------------------------
        errorDespegue = estadoDespegue(valores_waypoints.firstHome)
    # ----------------------------------------------------------------------------------
        data['errorDespegue'] = ""
    except Exception as errorDespegue:
        data['errorDespegue'] = "T"
        raise errorDespegue
    finally:
        return json.dumps(data)

@app.route('/hover', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def hover():
    data = request.get_json()
    calibrarFlag = data['calibrarFlag']
    try:
        if calibrarFlag=="H":
            valores_espectros.counterH +=1
        valores_espectros.counterCal += 1
        if calibrarFlag == "H" and valores_espectros.counterCal%2 == 0 and valores_espectros.counterH < 2:
            data["volverCapturar"] = "T"
            valores_espectros.counterH = 0
        if valores_espectros.counterCal%2 == 0:
            calibrarFlag = "F"
        # ----------------------------------LLAMADO A DRONE.PY------------------------------
        hoverDrone(calibrarFlag)
       # --------------------------------------------------------------------
    except Exception as e:
        raise e
    finally:
        return json.dumps(data)

@app.route('/pausarMision', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def pausarMision():
    data = request.get_json()
    flagPausar = data['flagPausar']
    try:
    # ----------------------------------LLAMADO A DRONE.PY------------------------------
        valores_waypoints.remainingWp = estadoPause(1, flagPausar)
        data['errorPausa'] = "F"
    # ----------------------------------------------------------------------------------
    except Exception as errorPausa:
        data['errorPausa'] = "T"
        raise errorPausa
    finally:
        return json.dumps(data)

@app.route('/reanudarMision', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def reanudarMision():
    data = request.get_json()
    try:
    # ----------------------------------LLAMADO A DRONE.PY------------------------------
        if valores_waypoints.puntoResume == None:
            errorDespegue = estadoResume(valores_waypoints.remainingWp, valores_waypoints.firstHome)
        elif valores_waypoints.puntoResume[0] == "[]":
            errorDespegue = estadoResume(valores_waypoints.remainingWp, valores_waypoints.firstHome)
        else:
            errorDespegue = estadoResume(valores_waypoints.remainingWp, valores_waypoints.firstHome, float(valores_waypoints.puntoResume[0]), float(valores_waypoints.puntoResume[1]))
    # ----------------------------------------------------------------------------------
        data['errorDespegue'] = ""
    except Exception as errorDespegue:
        data['errorDespegue'] = "T"
        raise errorDespegue
    finally:
        return json.dumps(data)

@app.route('/detenerMision', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def detenerMision():
    valores_waypoints.remainingWp = []
    valores_waypoints.id_waypointsList = []
    valores_waypoints.waypointActual = 0
    valores_waypoints.lat = 0
    valores_waypoints.lon = 0
    valores_espectros.id_espectros = 0
    valores_sensores.idSensorTierraVIS= ""
    valores_sensores.idSensorTierraNIR= ""
    valores_sensores.idSensorVueloNIR= ""
    valores_sensores.idSensorVueloVIS= ""
    valores_espectros.espectroBlanco= []
    valores_espectros.espectroNegro = []
    data = request.get_json()
    try:
    # ----------------------------------LLAMADO A DRONE.PY------------------------------
        estadoCancel(1)
        data['errorDetener'] = "F"
    # ----------------------------------------------------------------------------------
    except Exception as errorDetener:
        data['errorDetener'] = "T"
        raise errorDetener
    finally:
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
    try:
        conn = conexion()
        daoUsuarios = DaoUsuarios(conn)
        usuario = daoUsuarios.getUsuarioLogin(nombreUsuario, password)
        idUsuario = usuario.id

        daoMision = DaoMision(conn)
        misiones = daoMision.getAllMision(idUsuario)
        data['misiones']= misiones
    except Exception as e:
        data['errorBd'] = "T"
        raise e
    finally:
        return json.dumps(data)

@app.route('/seleccionarMision', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def seleccionarMision():
    data = request.get_json()
    data['errorBd'] = ""
    data['waypointsList'] = ""
    misionSeleccionada = data['misionSeleccionada']
    numWaypoints = []
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
        conn.close()
        data['waypoints'] = numWaypoints
        pass
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    finally:
        return json.dumps(data)

@app.route('/borrarMision', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def borrarMision():
    data = request.get_json()
    misionSeleccionada = data['misionSeleccionada']
    try:
        conn = conexion()
        daoMision = DaoMision(conn)
        mision = daoMision.getMisionNombre(misionSeleccionada)
        idMision = mision.id
        daoMision.borrarMision(idMision)
        conn.close()
        data['errorBd'] = "F"
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    finally:
        return json.dumps(data)

@app.route('/verEspectro', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def verEspectro():
    data = request.get_json()
    data['errorBd'] = ""
    nombreMisionCrear = data['nombreMisionCrear']
    waypointSeleccionado = data['waypointSeleccionado']
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
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    finally:
        return json.dumps(data)

@app.route('/guardarEspectro', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def guardarEspectro():
    data = request.get_json()
    data['errorBd'] = ""
    nombreMisionCrear = data['nombreMisionCrear']
    waypointSeleccionado = data['waypointSeleccionado']
    ruta = str(data['ruta'])
    usuario = str(data['usuario'])
    filePath = FileManagement.to_relative(ruta)
    try:
        if os.path.isdir(filePath):
            conn = conexion()
            daoMision = DaoMision(conn)
            mision = daoMision.getMisionNombre(nombreMisionCrear)
            idMision = mision.id
            altura = mision.elevacion
            daoWaypoints = DaoWaypoints(conn)
            wayp = daoWaypoints.getWaypointByNumber(waypointSeleccionado, idMision)
            idWayp = wayp.id
            latlon = wayp.latlon.split(",")

            daoEspway = DaoEspway(conn)
            espway = daoEspway.getEspwayWaypoint(idWayp)
            idEspectro = espway.espectros_id

            daoEspectros = DaoEspectros(conn)
            espectro = daoEspectros.getEspectros(idEspectro)
            resultado = espectro.resultado
            conn.close()
            filePath += "/Usuario("+usuario+")"+"Mision("+nombreMisionCrear+")"+ "Waypoint("+waypointSeleccionado+")"
            generate(resultado, filePath, float(latlon[0]), float(latlon[1]), altura)
        else:
            data['errorCarpeta'] = "T"
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    finally:
        return json.dumps(data)

@app.route('/guardarTodos', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def guardarTodos():
    data = request.get_json()
    data['errorBd'] = ""
    nombreMisionCrear = data['nombreMisionCrear']
    ruta = str(data['ruta'])
    filePath = FileManagement.to_relative(ruta)
    usuario = str(data['usuario'])
    try:
        if os.path.isdir(filePath):
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
            print(waypointsList[0].id, waypointsList[1].id) #272" lista de obj
            for i in range(0, len(waypointsList)):
                idsWaypoints.append(waypointsList[i].id)
                latlonsWaypoints.append(waypointsList[i].latlon)
            print(idsWaypoints) #
            print("J")
            print(latlonsWaypoints)
            for i in range(0, len(idsWaypoints)):
                daoEspway = DaoEspway(conn)
                espway = daoEspway.getEspwayWaypoint(idsWaypoints[i])
                idEspectro = espway.espectros_id
                idsEspectros.append(idEspectro)

            for i in range(0, len(idsEspectros)):
                latlons = latlonsWaypoints[i].split(",")
                rutaG = filePath
                daoEspectros = DaoEspectros(conn)
                espectro = daoEspectros.getEspectros(idsEspectros[i])
                resultado = espectro.resultado
                rutaG += "/Usuario("+usuario+")"+"Mision("+nombreMisionCrear+")"+ "WaypointNumber("+str(i)+")"
                # filePath = FileManagement.to_relative(rutaG)
                generate(resultado, rutaG, float(latlons[0]), float(latlons[1]), altura)
            conn.close()
        else:
            data['errorCarpeta'] = "T"
    except Exception as errorBd:
        data['errorBd'] = "T"
        print("Error en guardarTodos: ", errorBd)
        raise errorBd
    finally:
        return json.dumps(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
