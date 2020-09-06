import matplotlib
matplotlib.use('Agg') #para corregir error de threading en el main
import matplotlib.pyplot as plt
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

import os
from os import path
import numpy as np
import base64
import time
from shutil import copyfile

from spectreUtilities import *
from sensorUtilities import *

app = Flask(__name__)

sitl = None
vehicle = None
# cors = CORS(app, resources={r"/enviarAltitudVelocidad": {"origins": "http://localhost:5000"}})

# api = Api(app)
CORS(app, resources={r"/capturarVuelo": {"origins": "*"} ,r"/guardarWaypoints": {"origins": "*"} ,r"/guardarBlanco": {"origins": "*"} ,r"/guardarNegro": {"origins": "*"} ,r"/capturarNegro": {"origins": "*"} ,r"/capturarBlanco": {"origins": "*"} ,r"/crearMision": {"origins": "*"} ,r"/conectarDron": {"origins": "*"}, r"/calibrar": {"origins": "*"}, r"/enviarAltitudVelocidad": {"origins": "*"}, r"/login":{"origins":"*"}})
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'

# # Connect to the Vehicle
# print('Connecting to vehicle on: %s' % connection_string)
# vehicle = connect(connection_string, wait_ready=True)
# global wav
waypoints = []
elevacion = 0 
id_usuario_activo = ""
posicionDron = ""  
actitudDron = "" 
velocidadDron = ""
bateriaDron = ""

wavelenghtsLista = []
blancoCapturadoLista = []
negroCapturadoLista = []
blancoCapturado = []
negroCapturado = []
wavelenghtsLista = []
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
num2 = "cult2"
path = ("D:/subtext/splitTest0/Quieto 1 feb/%s" % (num2))
wav = ("%s/wavevis.txt" % (path))
with open(wav, "r") as wavevis:
    for line in wavevis:
        line = line[:-4]
        wavelenghtsLista.append(line)


# def getFilesBlanco(blancoCapturado):
#     blancoCapturadoLista=[]
#     # guardar txt de la captura
#     appendFile = open('D:/Tesis/Api/Flask/archivoTemporalBlanco.txt', 'w')
#     for i in range(len(blancoCapturado)):
#         appendFile.write(str(blancoCapturado[i]))
#     appendFile.close()
#     #blanco capturado es un array de strings de tamaño 14336 que al escribirse por
#     #líneas en el archivo queda de 1024----14336/14
#     # abrir txt capura y guardar en []
#     with open('D:/Tesis/Api/Flask/archivoTemporalBlanco.txt', "r") as blancovis:
#         for line in blancovis:
#             line = line[0:4]
#             blancoCapturadoLista.append(line)
#     # print(blancoCapturadoLista)
#     return blancoCapturadoLista

# def getFilesNegro(negroCapturado):
#     negroCapturadoLista = []
#     # Guardar txt de la captura
#     appendFile = open('D:/Tesis/Api/Flask/archivoTemporalNegro.txt', 'w')
#     for i in range(len(negroCapturado)):
#         appendFile.write(str(negroCapturado[i]))
#     appendFile.close()
#     # abrir txt de la captura y gyardar en []
#     with open('D:/Tesis/Api/Flask/archivoTemporalNegro.txt', "r") as negrovis:
#         for line in negrovis:
#             line = line[0:4]
#             negroCapturadoLista.append(line)
#     return negroCapturadoLista

# def getFilesVuelo(vueloCapturado):
#     vueloCapturadoLista=[]
#     # guardar txt de la captura
#     appendFile = open('D:/Tesis/Api/Flask/archivoTemporalVuelo.txt', 'w')
#     for i in range(len(vueloCapturado)):
#         appendFile.write(str(vueloCapturado[i]))
#     appendFile.close()
#     with open('D:/Tesis/Api/Flask/archivoTemporalVuelo.txt', "r") as blancovis:
#         for line in blancovis:
#             line = line[0:4]
#             vueloCapturadoLista.append(line)
#     return vueloCapturadoLista

# def makeImage(ejeXMakeImage, ejeYMakeImage):
#     print(len(ejeXMakeImage))
#     print(len(ejeYMakeImage))
#     # print(ejeXMakeImage)
#     ejeY = np.array(ejeYMakeImage, dtype=np.float32)
#     ejeX = np.array(ejeXMakeImage, dtype=np.float32)

#     plt.figure(1)
#     ax = plt.subplot(111)
#     plt.plot(ejeX, ejeY)#, label='Negro')
#     ax.set_ylim(min(ejeY), max(ejeY))
#     plt.legend()
#     rutaImagen= "D:/Tesis/Api/Flask/imagenEspectro.png"
#     resultadoMakeImage= plt.savefig(rutaImagen, format="png")
#     plt.cla()
#     plt.clf()
#     plt.close()
#     return resultadoMakeImage

# def calibrarSensoresTierra(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas):
#     print("Calibrando Sensores Tierra")
#     aux = "L"
#     url = "http://127.0.0.1:5005/sensoresTierra/%s/%s/%s/%s/%s" %(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas, aux)
#     with urllib.request.urlopen(url) as f:
#         print(f.read().decode('utf-8'))
#         print("Calibrados")
    
# def capturarBlancoRpi(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas):
#     # global blancoCapturado
#     print("Capturando blanco referencia")
#     aux = "C"
#     url = "http://127.0.0.1:5005/sensoresTierra/%s/%s/%s/%s/%s" %(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas, aux)
#     with urllib.request.urlopen(url) as f:
#         blancoCapturado = f.read().decode('utf-8')
#         print("captura realizada")
#     return blancoCapturado

# def capturarNegroRpi(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas):
#     print("Capturando Dark referencia")
#     aux = "N"
#     url = "http://127.0.0.1:5005/sensoresTierra/%s/%s/%s/%s/%s" %(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas, aux)
#     with urllib.request.urlopen(url) as f:
#         NegroCapturado = f.read().decode('utf-8')
#         print("captura realizada")
#     return NegroCapturado

# def calibrarSensoresVuelo(sensorVueloVIS, sensorVueloNIR, tiempoIntegracion, numeroCapturas):
#     print("Calibrando Sensores Vuelo")
#     aux = "L"
#     url = "http://127.0.0.1:5005/sensoresVuelo/%s/%s/%s/%s/%s" %(sensorVueloVIS, sensorVueloNIR, tiempoIntegracion, numeroCapturas, aux)
#     with urllib.request.urlopen(url) as f:
#         print(f.read().decode('utf-8'))
#         print("Calibrados")

# def capturarVueloRpi(sensorVueloVIS, sensorVueloNIR, tiempoIntegracion, numeroCapturas):
#     # global blancoCapturado
#     print("Capturando")
#     aux = "C"
#     url = "http://127.0.0.1:5005/sensoresVuelo/%s/%s/%s/%s/%s" %(sensorVueloVIS, sensorVueloNIR, tiempoIntegracion, numeroCapturas, aux)
#     with urllib.request.urlopen(url) as f:
#         vueloCapturado = f.read().decode('utf-8')
#         print("captura realizada")
#     return vueloCapturado

def calcularEspectro(ids):
    stringDark= """SELECT dark FROM espectros WHERE id='%s';""" %(ids)
    stringCapturado= """SELECT dark FROM espectros WHERE id='%s';""" %(ids)
    stringWhite= """SELECT dark FROM espectros WHERE id='%s';""" %(ids)
    global wavelenghtsLista
    medida= []
    blanco= []
    negro= []
    negrolist= []
    blancolist= []
    suma= []
    resta= []
    espectro= []
    espectrocor= []
    wavecor= []
    conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
    cur = conn.cursor()
    cur.execute(stringDark)
    negro = cur.fetchone()[0][0]
    cur.execute(stringWhite)
    blanco = cur.fetchone()[0][0]
    cur.execute(stringCapturado)
    medida = cur.fetchone()[0][0]
    cur.close()
    conn.close()

    for i in range(0, len(wavelenghtsLista)):
        suma.append(float(blanco[i]) - float(negro[i]))
    # print(str(resta))
    for i in range(0, len(wavelenghtsLista)):
        resta.append(float(medida[i]) - float(negro[i]))
    for i in range(0, len(wavelenghtsLista)):
        if suma[i] == 0:
            suma[i] = 1
        espectro.append(float(resta[i]) / float(suma[i]))

    # espectroVuelo = np.array(medida, dtype=np.float32)
    # negro = np.array(negro, dtype=np.float32)
    # blanco = np.array(blanco, dtype=np.float32)
    # wavelenghtsLista = np.array(wavelenghtsLista, dtype=np.float32)
    # #espectro = (medida - negro) / (blanco - negro)
    # espectro = np.array(espectro, dtype=np.float32)

    
    # for i in range(141, 850):
    #     espectrocor.append(espectro[i])
    # print(str(espectrocor))
    # for i in range(141, 850):
    #     wavecor.append(wavelenghts[i])
    return espectro

def capturarVueloSinc(sensorVueloNIR, sensorVueloVIS, tiempoIntegracion, numeroCapturas, id_espectros):
    filePath = 'D:/Tesis/Api/Flask/archivoTemporalVuelo.txt';
    if os.path.exists(filePath):
        os.remove(filePath)
    else:
        print("Can not delete the file as it doesn't exists")
    vueloCapturado = capturarVueloRpi(sensorVueloVIS, sensorVueloNIR, tiempoIntegracion, numeroCapturas)
    v = getFilesVuelo(vueloCapturado)
    try:
        conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
        cur = conn.cursor()
        cur.execute("""UPDATE espectros SET capturado=%s WHERE id=%s;""", ([v], id_espectros))
        conn.commit()
        # cur.close()
        # conn.close() 
        
        espectroCalculado = calcularEspectro(id_espectros)
        cur.execute("""UPDATE espectros SET resultado=%s WHERE id=%s RETURNING id;""", ([espectroCalculado], id_espectros))
        idLastEspectre = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        error = ""  
    except Exception as errorBd:
        error = "T"
        raise errorBd
    return error, idLastEspectre

print("Termino esa monda")


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
    global vehicle, sitl

    # parser = argparse.ArgumentParser(description='Demonstrates basic mission operations.')
    # parser.add_argument('--connect', 
    #                help="vehicle connection target string. If not specified, SITL automatically started and used.")
    # args = parser.parse_args()
    # connection_string = args.connect

    #Start SITL if no connection string specified
    # if not connection_string:
    #     import dronekit_sitl
    #     sitl = dronekit_sitl.start_default()
    #     connection_string = sitl.connection_string()

    if conectarDron:
        try:
            # global vehicle, sitl

            parser = argparse.ArgumentParser(description='Demonstrates basic mission operations.')
            parser.add_argument('--connect', 
                           help="vehicle connection target string. If not specified, SITL automatically started and used.")
            args = parser.parse_args()
            connection_string = args.connect

            # Start SITL if no connection string specified
            if not connection_string:
                import dronekit_sitl
                sitl = dronekit_sitl.start_default()
                connection_string = sitl.connection_string()
    #     
            # url = "http://127.0.0.1:5005/conectarDron"
            # with urllib.request.urlopen(url) as f:
            #     print(f.read().decode('utf-8'))
            #     print("Conectado")
            print('Connecting to vehicle on: %s' % connection_string)
            vehicle = connect(connection_string, wait_ready=True)
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
        makeImage(wavelenghtsLista, a)
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
        makeImage(wavelenghtsLista, n)
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
    global id_waypointsList
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
    # aqui quede
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
