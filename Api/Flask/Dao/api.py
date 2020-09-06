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

app = Flask(__name__)

sitl = None
vehicle = None

CORS(app, resources={r"/capturarVuelo": {"origins": "*"} ,r"/guardarWaypoints": {"origins": "*"} ,r"/guardarBlanco": {"origins": "*"} ,r"/guardarNegro": {"origins": "*"} ,r"/capturarNegro": {"origins": "*"} ,r"/capturarBlanco": {"origins": "*"} ,r"/crearMision": {"origins": "*"} ,r"/conectarDron": {"origins": "*"}, r"/calibrar": {"origins": "*"}, r"/enviarAltitudVelocidad": {"origins": "*"}, r"/login":{"origins":"*"}})
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

@app.route('/login', methods=['POST'])
# @cross_origin(origin='*', headers=['Content-Type','Authorization'])
def login():
    data = request.get_json()
    data['errorBd'] = ""
    nombreUsuario= data["nombreUsuario"]
    password= data["password"]
    try: 
        conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
        cur = conn.cursor()
        cur.execute("""SELECT * FROM usuarios WHERE nombre = %s AND contrasena = %s ;""",(nombreUsuario, password))
        query_results = cur.fetchall()
        if query_results[0][1] == "":
            data['errorBd'] = "T"
            pass
        print(query_results[0][1])

    except:
        data['errorBd'] = "T"
    return json.dumps(data)

@app.route('/registro', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def registro():
    data = request.get_json()
    data['errorBd'] = ""
    
    nombreUsuario= data["nombreUsuario"]
    password= data["password"]
    try:
        # reemplazar por DAO
        conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
        cur = conn.cursor()
        # cur.execute("""INSERT INTO usuarios (nombre, contrasena) VALUES ('nombreUsuario', 'password')""")
        cur.execute("""INSERT INTO usuarios (nombre, contrasena) VALUES (%s, %s);""", (nombreUsuario, password))
        # cur.execute("""DELETE FROM usuarios;""")
        cur.execute("""SELECT * FROM usuarios;""")
        
        query_results = cur.fetchall()
        print(query_results)
        conn.commit()
        cur.close()
        conn.close()
    except:
        data['errorBd'] = "T"
        

    print(data.get('errorBd'))
    return json.dumps(data)

@app.route('/crearMision', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def crearMision():
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
        conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
        cur = conn.cursor()
        cur.execute("""INSERT INTO mision (nombre, elevacion, velocidad, modo_vuelo, modo_adq, usuarios_id) 
            VALUES (%s, %s, %s, %s, %s, (SELECT id FROM usuarios WHERE nombre=%s));""", (nombreMisionCrear, elevacion, velocidad, modo_vuelo, modo_adq, nombreUsuario))
        # cur.execute("""DELETE FROM usuarios;""")
        cur.execute("""SELECT * FROM mision WHERE nombre= %s AND elevacion = %s AND velocidad = %s;""", (nombreMisionCrear, elevacion, velocidad))
        query_results = cur.fetchall()
        print(query_results)
        conn.commit()
        cur.close()
        conn.close()
    except:
        data['errorBd'] = "T"
        print("error en BD")
    print(data.get('errorBd'))
    return json.dumps(data)

@app.route('/conectarDron', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def conectarDron():
    data = request.get_json()
    data['errorDrone'] = ""
    conectarDron = data["conectarDron"]
    altura = float(data["elevacion"])
    velocidad = float(data["velocidad"])
    global vehicle, sitl
    if conectarDron:
        try:
            # --------------LLAMADO A DRONE.PY----------------
            vehicle = initCon(altura, velocidad)
            # ------------------------------------------------
        except:
            data['errorDrone'] = "T"
            print("error en Dron") 
        pass
    else:
        try:
            vehicle.close()
            print("vehiculo desconectado")
            sitl.stop()
            print("simulador off")
        except:
            print("no vehicle")
    print(data.get('errorDrone'))
    return json.dumps(data)

@app.route('/obtenerTelemetria', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def obtenerTelemetria():
    data = request.get_json()
    nombreMisionCrear = data["nombreMisionCrear"]
    data = {}
    data['errorBd'] = ""
    global vehicle

    posicionDron = str(vehicle.location.global_relative_frame)
    posicionDron = posicionDron.split(":")[1]
    posicionDron = posicionDron.split(",")
    lat = posicionDron[0].split("=")[1]
    lon = posicionDron[1].split("=")[1]
    alt = posicionDron[2].split("=")[1]
    print('Position: %s'% posicionDron)
    # print('Position: %s'% vehicle.location.global_relative_frame)
    # print(lat)
    # print(lon)
    # print(alt)

    #- Read the actual attitude roll, pitch, yaw
    actitudDron = str(vehicle.attitude)
    actitudDron = actitudDron.split(":")[1]
    actitudDron = actitudDron.split(",")
    pitch = round(float(actitudDron[0].split("=")[1]), 5)
    yaw = round(float(actitudDron[1].split("=")[1]), 5)
    roll = round(float(actitudDron[2].split("=")[1].upper()), 5)
    # print(pitch)
    # print(yaw)
    # print(roll)

    #- Read the actual velocity (m/s)
    velocidadDron = str(vehicle.velocity)
    # print('Velocity: %s'% velocidadDron)
    # print(velocidadDron)

    bateriaDron = str(vehicle.battery)
    bateriaDron = bateriaDron.split("=")[3]
    # print('Battery: %s'%bateriaDron)
    # print(bateriaDron)

    print("conectado")
    try:
        conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
        cur = conn.cursor()
        cur.execute("""INSERT INTO telemetria (pitch, yaw, roll, lat, lon, alt, bateriaDron, velocidadDron, mision_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, (SELECT id FROM mision WHERE nombre=%s));""", (pitch, yaw, roll, lat, lon, alt, bateriaDron, velocidadDron, nombreMisionCrear))
        # cur.execute("""DELETE FROM usuarios;""")
        # cur.execute("""SELECT * FROM telemetria WHERE mision_id=(SELECT id FROM mision WHERE nombre=%s);""", (nombreMisionCrear))
        conn.commit()
        print(cur.rowcount)
        cur.close()
        conn.close()
        pass
    except:
        data['errorBd'] = "T"
        print("error en BD")
    print(data.get('errorBd'))

    data['lat'] = lat
    data['lon'] = lon
    data['alt'] = alt
    data['pitch'] = pitch
    data['yaw'] = yaw
    data['roll'] = roll
    data['velocidadDron'] = velocidadDron
    data['bateriaDron'] = bateriaDron

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
        raise errorCalibrarSensoresTierra
    
    try:
        calibrarSensoresVuelo(sensorVueloVIS, sensorVueloNIR, tiempoIntegracion, numeroCapturas)
        data['errorCalibrarSensoresVuelo']= "A"
        pass
    except Exception as errorCalibrarSensoresVuelo:
        data['errorCalibrarSensoresTierra']= "T"
        raise errorCalibrarSensoresVuelo

    try:
        conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
        cur = conn.cursor()
        sql= """INSERT INTO sensores (lugar, tipo, numero_serie, t_int, numero_capt, mision_id) 
            VALUES ('T', 'V', %s, %s, %s, (SELECT id FROM mision WHERE nombre=%s)) RETURNING id;"""
        #TIERRA VIS
        cur.execute(sql, (sensorTierraVIS, tiempoIntegracion, numeroCapturas, nombreMisionCrear))
        idSensorTierraVIS = cur.fetchone()[0]
        #TIERRA NIR
        cur.execute(sql , (sensorTierraNIR, tiempoIntegracion, numeroCapturas, nombreMisionCrear))
        idSensorTierraNIR = cur.fetchone()[0]
        #VUELO VIS
        cur.execute(sql , (sensorVueloVIS, tiempoIntegracion, numeroCapturas, nombreMisionCrear))
        idSensorVueloVIS = cur.fetchone()[0]
        #VUELO NIR
        cur.execute(sql, (sensorVueloNIR, tiempoIntegracion, numeroCapturas, nombreMisionCrear))
        idSensorVueloNIR = cur.fetchone()[0]

        # cur.execute("""DELETE FROM usuarios;""")
        cur.execute("""SELECT * FROM sensores;""")
        query_results = cur.fetchall()
        print(query_results)
        conn.commit()
        cur.close()
        conn.close()
        pass
    except Exception as errorBdCal:
        data['errorBd'] = "T"
        print("error en BD")
        raise errorBdCal    
    print(data.get('errorBd')+ "," + data.get('errorCalibrarSensoresTierra') + "," + data.get('errorCalibrarSensoresVuelo'))
    return json.dumps(data)

@app.route('/capturarBlanco', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def capturarBlanco():
    global a
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
    filePath = 'D:/Tesis/Api/Flask/archivoTemporalBlanco.txt';
    if os.path.exists(filePath):
        os.remove(filePath)
    else:
        print("Can not delete the file as it doesn't exists")
    try:
        # Comandar sensores para captura
        blancoCapturado = capturarBlancoRpi(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas)
        # construir imagen
        a= getFilesBlanco(blancoCapturado)
        print(a)
        makeImage(a)
        with open("D:/Tesis/Api/Flask/imagenEspectro.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            encoded_string = encoded_string.decode("utf-8")
            # print(encoded_string)
        data['espectroBlanco'] = encoded_string
        
    except Exception as errorCapturaB:
        data['errorCapturaB'] = "T"
        raise errorCapturaB
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
    filePath = 'D:/Tesis/Api/Flask/archivoTemporalNegro.txt';
    if os.path.exists(filePath):
        os.remove(filePath)
    else:
        print("Can not delete the file as it doesn't exists")
    try:
        negroCapturado = capturarNegroRpi(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas)
        n= getFilesNegro(negroCapturado)
        makeImage(n)
        with open("D:/Tesis/Api/Flask/imagenEspectro.png", "rb") as image_file:
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
    filePathSrc = 'D:/Tesis/Api/Flask/archivoTemporalBlanco.txt';
    filePathDes = 'D:/Tesis/Api/Flask/archivoBlanco.txt';
    try:
        copyfile(filePathSrc, filePathDes)
        if id_espectros == None:
            conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
            cur = conn.cursor()
            cur.execute("""INSERT INTO espectros (white, sensores_id) 
                VALUES (%s, %s) RETURNING id;""", ([a], idSensorTierraVIS))
            id_espectros = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
        else:
            conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
            cur = conn.cursor()
            cur.execute("""UPDATE espectros SET white=%s WHERE id=%s;""", ([a], id_espectros))
            # id_espectros = cur.fetchone()[0]
            # print(id_espectros)
            conn.commit()
            cur.close()
            conn.close()
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    return json.dumps(data)
@app.route('/guardarNegro', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def guardarNegro():
    global id_espectros, n, idSensorTierraVIS
    data = request.get_json()
    data['errorBd'] = ""
    filePathSrc = 'D:/Tesis/Api/Flask/archivoTemporalNegro.txt';
    filePathDes = 'D:/Tesis/Api/Flask/archivoNegro.txt';
    try:
        copyfile(filePathSrc, filePathDes)
        if id_espectros == None:
            conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
            cur = conn.cursor()
            cur.execute("""INSERT INTO espectros (dark, sensores_id) 
                VALUES (%s, %s) RETURNING id;""", ([n], idSensorTierraVIS))
            id_espectros = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
        else:
            conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
            cur = conn.cursor()
            cur.execute("""UPDATE espectros SET dark=%s WHERE id=%s;""", ([n], id_espectros))
            # id_espectros = cur.fetchone()[0]
            # print(id_espectros)
            conn.commit()
            cur.close()
            conn.close()
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    return json.dumps(data)

@app.route('/capturarVuelo', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def capturarVuelo():
    global numeroWaypoint, a, n
    numeroWaypoint = numeroWaypoint+1
    global v, id_espectros, listaEspectros
    # obtener datos del json
    data = request.get_json()
    nombreMisionCrear = data["nombreMisionCrear"]
    sensorVueloVIS = data["sensorVueloVIS"]
    sensorVueloNIR = data["sensorVueloNIR"]
    tiempoIntegracion = data["tiempoIntegracion"]
    numeroCapturas = data["numeroCapturas"]
    sinc= data["caracterSinc"]
    data['errorBd'] = ""
    data['errorCapturaV'] = ""
    numeroCapturasAsincronas = int(data["numeroCapturasAsincronas"])
    intervaloCapturasAsincronas = int(data["intervaloCapturasAsincronas"])
    print("numeroCapturasAsincronas"+str(numeroCapturasAsincronas))
    print("intervalo"+str(intervaloCapturasAsincronas))

    i=0
    tiempo = 100
    while i<numeroCapturasAsincronas:
        # print("al inicio i:%s" %(i))
        if tiempo >= intervaloCapturasAsincronas:
            start_time_A = time.time()
            # time.sleep(1)
            if sinc == "":
                a = capturarVueloSinc(sensorVueloNIR, sensorVueloVIS, tiempoIntegracion, numeroCapturas, id_espectros)
            else:
                # GENERAR NUEVO INGRESO EN ESPECTROS CON REFERENCIA WHITE Y DARK
                conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
                cur = conn.cursor()
                cur.execute("""INSERT INTO espectros (white, sensores_id) 
                    VALUES (%s, %s) RETURNING id;""", ([a], idSensorTierraVIS))
                id_espectros = cur.fetchone()[0]
                conn.commit()
                cur.close()
                conn.close() 
                conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
                cur = conn.cursor()
                cur.execute("""UPDATE espectros SET dark=%s WHERE id=%s;""", ([n], id_espectros))
                # id_espectros = cur.fetchone()[0]
                # print(id_espectros)
                conn.commit()
                cur.close()
                conn.close()
                c, b = capturarVueloSinc(sensorVueloNIR, sensorVueloVIS, tiempoIntegracion, numeroCapturas, id_espectros)
                listaEspectros.append(b)
            # print("dentro del if tiempo:%s" %(i))
            i = i+1
        else:
            pass
            # print("dentro del else i:%s" %(i))
        end_time_A = time.time()
        tiempo = end_time_A - start_time_A
        # print("tiempo:%s" %(i))

    print(listaEspectros)
    return json.dumps(data)

# @app.route('/generarEspectros', methods=['POST'])
# @cross_origin(origin='*', headers=['Content-Type','Authorization'])

@app.route('/guardarWaypoints', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def guardarWaypoints():
    global id_waypointsList#, vehicle, sitl
    id_waypointsList = []
    data = request.get_json()
    data['errorBd'] = ""
    waypointsList = []
    caracterWaypoints = data['caracter']
    nombreMisionCrear = data['nombreMisionCrear']
    arrayWaypoints = data['waypoints']
    arrayWaypoints = arrayWaypoints.split("\n")
    waypointsDic={}
    for x in range(0,len(arrayWaypoints)):
        waypointsDic["waypoint{0}".format(x)] = arrayWaypoints[x]#+arrayWaypoints[x+1]
    print(waypointsDic)
    for i in range(0, len(waypointsDic)):
        waypointsList.append(waypointsDic["waypoint{0}".format(i)])
        pass
    print(waypointsList)
    print("Empieza mision: "+ nombreMisionCrear)
    # ---------------------------LLAMADO A DRONE.PY------------------------
    FSM(1)
    sleep(.3)
    FSM(1)
    sleep(.3)
    FSM(waypointsList)
    sleep(.3)
    # ULTIMO
    # ---------------------------------------------------------------------
    points_lat=[]
    points_long=[]
    for x in waypointsList:                 
        print("cada wp: %s" %x)
        points=x.split(",")
        if " " in points[1]:
            plong = points[1].replace(" ", "")
        else:
            plong = points[1]
        print(plong)
        points_lat.append(float(points[0]))
        points_long.append(float(plong))
        print ("cada wp lat: %s" %points[0])
        print ("cada wp long: %s" %plong)
        # points_lat.append(float(points[0]))
        # points_long.append(float(points[1]))
        # print ("cada wp lat: %s" %points[0])
        # print ("cada wp long: %s " %points[1])
    try:
        if caracterWaypoints==1: #meter num_wayp
            for i in range(0, len(waypointsList)):
                conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
                cur = conn.cursor()
                cur.execute("""INSERT INTO waypoints (latlon, num_waypoint, mision_id) 
                    VALUES (%s, %s, (SELECT id FROM mision WHERE nombre=%s)) RETURNING id;""", (waypointsList[i], i, nombreMisionCrear))
                id_waypoints = cur.fetchone()[0]
                print(id_waypoints)
                id_waypointsList.append(id_waypoints)
                conn.commit()
                cur.close()
                conn.close()
            print(id_waypointsList)
        if caracterWaypoints == 2:
            for i in range(0, len(waypointsList)):
                conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
                cur = conn.cursor()
                cur.execute("""UPDATE waypoints SET latlon=%s WHERE id=%s;""", (waypointsList[i], i))
                conn.commit()
                cur.close()
                conn.close()
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    return json.dumps(data)

@app.route('/descargarInfo', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def descargarInfo():
    data = request.get_json()
    data = {}
    data['errorBd'] = ""
    nombreMisiones = []
    conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
    cur = conn.cursor()
    cur.execute("""SELECT * FROM mision;""")
    misiones = cur.fetchall()
    for i in range (0, len(misiones)):
        nombreMisiones.append(misiones[i][1])
        nombreMisiones.append("\n")
    print(nombreMisiones)
    data['misiones']= nombreMisiones
    # try:
    #     # if caracterWaypoints=="1":
    #     #     conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
    #     #     cur = conn.cursor()
    #     #     cur.execute("""INSERT INTO waypoints (white, sensores_id) 
    #     #         VALUES (%s, %s) RETURNING id;""", ([waypointsDic], nombreMisionCrear))
    #     #     id_waypoints = cur.fetchone()[0]
    #     #     conn.commit()
    #     #     cur.close()
    #     #     conn.close()
    #     # if caracterWaypoints == "2":
    #     #     conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
    #     #     cur = conn.cursor()
    #     #     cur.execute("""UPDATE espectros SET white=%s WHERE id=%s;""", ([a], id_waypoints))
    #     #     conn.commit()
    #     #     cur.close()
    #     #     conn.close()
    #     pass
    # except Exception as errorBd:
    #     data['errorBd'] = "T"
    #     raise errorBd
    return json.dumps(data)

@app.route('/seleccionarMision', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def seleccionarMision():
    data = request.get_json()
    data['errorBd'] = ""
    data['waypointsList'] = ""
    misionSeleccionada = data['misionSeleccionada']
    nombreWaypoints = []
    
    try:
        stringsql = """SELECT * FROM mision WHERE nombre='%s';""" %(misionSeleccionada)
        conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
        cur = conn.cursor()
        cur.execute(stringsql)
        idMision = cur.fetchall()[0][0]
        print(idMision)
        cur.close()
        conn.close()
        stringsql = """SELECT latlon FROM waypoints WHERE mision_id='%s';""" %(idMision)
        print(stringsql)
        conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
        cur = conn.cursor()
        cur.execute(stringsql)
        waypointsList = (cur.fetchall())
        # waypointsList = (cur.fetchall())
        # for i in range (0, len(waypointsList)):
        #     nombreWaypoints.append(waypointsList[i][1])
        # print(nombreWaypoints)
        print(waypointsList)
        cur.close()
        conn.close()
        data['waypoints'] = waypointsList
        pass
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    return json.dumps(data)
# api.add_resource(Hello, '/hello/<name>')
# api.add_resource(enviarAltitudVelocidad, '/enviarAltitudVelocidad/<elevacion>/<velocidad>')

@app.route('/seleccionarWaypoint', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def seleccionarWaypoint():
    data = request.get_json()
    data['errorBd'] = ""
    data['waypointsList'] = ""
    misionSeleccionada = data['misionSeleccionada']
    nombreWaypoints = []
    # DEJË AHí PORQUE ES MAS FACIL RECIBIR EL WAYPOINT PUNTUAL DEL DRON AL MISMO TIEMPO
    # QUE SE HACE LA CAPTURA, SE RECIBIRÍA WAYPOINT Y ESPECTRO EN LA MISMA FUNCIöN
    try:
        stringsql = """SELECT * FROM mision WHERE nombre='%s';""" %(misionSeleccionada)
        conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
        cur = conn.cursor()
        cur.execute(stringsql)
        idMision = cur.fetchall()[0][0]
        print(idMision)
        cur.close()
        conn.close()
        stringsql = """SELECT latlon FROM waypoints WHERE mision_id='%s';""" %(idMision)
        print(stringsql)
        conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
        cur = conn.cursor()
        cur.execute(stringsql)
        waypointsList = (cur.fetchall())
        # waypointsList = (cur.fetchall())
        # for i in range (0, len(waypointsList)):
        #     nombreWaypoints.append(waypointsList[i][1])
        # print(nombreWaypoints)
        print(waypointsList)
        
        cur.close()
        conn.close()
        data['waypoints'] = waypointsList
        pass
    except Exception as errorBd:
        data['errorBd'] = "T"
        raise errorBd
    return json.dumps(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
