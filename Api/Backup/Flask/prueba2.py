import matplotlib
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
from time import sleep
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
nombreMisionCrear = "201"
waypointSeleccionado = 0
conn = conexion()
daoMision = DaoMision(conn)
mision = daoMision.getMisionNombre(nombreMisionCrear)
idMision = mision.id
print(idMision)
daoWaypoints = DaoWaypoints(conn)
wayp = daoWaypoints.getWaypointByNumber(waypointSeleccionado, idMision)
idWayp = wayp.id
print(idWayp)
daoEspway = DaoEspway(conn)
espway = daoEspway.getEspwayWaypoint(idWayp)
idEspectro = espway.espectros_id
print(idEspectro)

daoEspectros = DaoEspectros(conn)
espectro = daoEspectros.getEspectros(idEspectro)
capturado = espectro.capturado
resultado = espectro.resultado
conn.close()
print(capturado)
print(resultado)

# data = {'a':"a", 'b':"b", 'c':"c"}
# data['a'] = "hgfd"
# data['b'] = "b"
# data['c'] = "c"
# data['d'] = "d"
# print(data['a'])
# app = Flask(__name__)
# def er():
#     url = "http://127.0.0.1:8080/sensoresVuelo/1"
#     with urllib.request.urlopen(url) as f:
#         print(f.read().decode('utf-8'))
# def er1():
#     url = "http://127.0.0.1:8080/sensoresVuelo/2"
#     with urllib.request.urlopen(url) as f:
#         print(f.read().decode('utf-8'))
# def er2():
#     url = "http://127.0.0.1:8080/sensoresVuelo/3"
#     with urllib.request.urlopen(url) as f:
#         print(f.read().decode('utf-8'))
# def er3():
#     url = "http://127.0.0.1:8080/sensoresVuelo/4"
#     with urllib.request.urlopen(url) as f:
#         print(f.read().decode('utf-8'))
# def er4():
#     url = "http://127.0.0.1:8080/sensoresVuelo/5"
#     with urllib.request.urlopen(url) as f:
#         print(f.read().decode('utf-8'))
# def er5():
#     url = "http://127.0.0.1:8080/sensoresVuelo/6"
#     with urllib.request.urlopen(url) as f:
#         print(f.read().decode('utf-8'))
# if __name__ == '__main__':
#     er()
#     er1()
#     er2()
#     er3()
#     er4()
#     er5()
    # poner una mision completa aqui para verificar que el error nosea por eso
    # 

# from pruebaDrone import *
# 
# 
# idref= None
# sensorTierraVIS = "1"
# num2 = "cult2"
# path = ("D:/subtext/splitTest0/Quieto 1 feb/%s" % (num2))
# wav = ("%s/wavevis.txt" % (path))
# medida= []
# blanco= []
# negro= []
# negrolist= []
# blancolist= []
# suma= []
# resta= []
# espectro= []
# wavelenghts= []
# espectrocor= []
# wavecor= []
# string= ""
# inti= 17
# # idMision = []
# numeroCapturasAsincronas = 5
# intervaloCapturasAsincronas = 2.0
# asda = "3.372769, -76.530163"
# b= "3.372769,-76.530163"
# asa = 1
# nombreUsuario = ['2','3','4','5','6']
# password = ['1','2','3','4','5']


# main()


print(psycopg2.__version__)

# nombreMisiones = []
# conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
# cur = conn.cursor()
# cur.execute("""SELECT * FROM mision;""")
# misiones = cur.fetchall()
# cur.close()
# conn.close()
# # for i in range (0, len(misiones)):
# #     nombreMisiones.append(misiones[i][1])
# #     stringsql = """SELECT id FROM mision WHERE nombre=%s;"""
# #     conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
# #     cur = conn.cursor()
# #     cur.execute(stringsql, (nombreMisiones[i])
# #     idMision = cur.fetchall()[0]
# #     cur.close()
# #     conn.close()
# listaSensoresMision = []
# listaWaypointsMision = []
# for i in range(0, len(misiones)):
# 	listaSensoresMision = []
# # RETORNAR ID DE MISION
# 	nombreMisiones.append(misiones[i][1])
# 	print(nombreMisiones[i])
# 	stringsql = """SELECT id FROM mision WHERE nombre=%s;"""
# 	conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
# 	cur = conn.cursor()
# 	cur.execute(stringsql, (nombreMisiones[i]))
# 	idMision = cur.fetchall()[0][0]
# 	print("el id de mision es:" + str(idMision))
# 	cur.close()
# 	conn.close()
# 	# RETORNAR ID DE SENSORES DE ESA MISION
# 	stringsql = """SELECT id FROM sensores WHERE mision_id=%s;"""
# 	conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
# 	cur = conn.cursor()
# 	cur.execute(stringsql, (nombreMisiones[i]))
# 	idSensores = cur.fetchall()
	
# 	for q in range(0, len(idSensores)):
# 		listaSensoresMision.append(idSensores[q])
# 	print(listaSensoresMision)
# 	cur.close()
# 	conn.close()

# 	# stringsql = """SELECT id FROM mision WHERE nombre=%s;"""
# 	# conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
# 	# cur = conn.cursor()
# 	# cur.execute(stringsql, (nombreMisiones[i]))
# 	# idMision = cur.fetchall()[0]
# 	# cur.close()
# 	# conn.close()

# 	for x in range(0,5):
# 	    stringsql = """INSERT INTO espway (espectros_id, waypoints_id) VALUES (%s, %s);"""
# 	    conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
# 	    cur = conn.cursor()
# 	    cur.execute(stringsql, (nombreUsuario[x], password[x]))
# 	    cur.execute("""SELECT * FROM espway""")
# 	    # asda.append(cur.fetchall())
# 	    a = cur.fetchall()[0]
# 	    cur.close()
# 	    conn.close()	
# 	    print(a)








# stringsql = """SELECT latlon FROM waypoints WHERE mision_id='%s';""" %(idMision)
# stringsql = """INSERT into espectros (white, sensores_id) VALUES ('%s', '%s');""", ([asda], asa)

# print(strinBgsql)
# cur.execute("""INSERT INTO espectros (white, sensores_id) 
                    # VALUES (%s, %s) RETURNING id;""", ([asda], asa))

# waypointsList = (cur.fetchall())
# waypointsList = list(waypointsList)
# waypointsList = (cur.fetchall())
# for i in range (0, len(waypointsList)):
#     nombreWaypoints.append(waypointsList[i][1])
# print(nombreWaypoints)
# print(waypointsList)



# misionSeleccionada = "'2'"
# stringsql = """SELECT * FROM mision WHERE nombre=%s;""" %(misionSeleccionada)
# print(stringsql)
# conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
# cur = conn.cursor()
# cur.execute(stringsql)
# idMision = cur.fetchall()[0][0]
# print(idMision)
# cur.close()
# conn.close()
# stringsql = """SELECT * FROM waypoints WHERE mision_id='%s';""" %(idMision)
# print(stringsql)
# conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
# cur = conn.cursor()
# cur.execute(stringsql)
# idMision = (cur.fetchall()[0][1])
# print(idMision)
# idMision= (idMision[0])
# print(idMision)
# cur.close()
# conn.close()





# # nombreMisiones = []
# # conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
# # cur = conn.cursor()
# # cur.execute("""SELECT * FROM mision;""")
# # misiones = cur.fetchall()
# # for i in range (0, len(misiones)):
# #     nombreMisiones.append(misiones[i][1])
# # # nombreMisiones = list(nombreMisiones)
# # print(nombreMisiones)




# # vis 337.2 to 828.9
# # nir 631.3 to 1121
# # with open(wav, "r") as wavevis:
# #     for line in wavevis:
# #         line = line[:-4]
# #         wavelenghts.append(line)
# # x = "D:/subtext/splitTest0/Quieto 1 feb/cult2/2mt0.txt"
# # # with open(x, 'r') as f:
# # #     a = f.read()
# # # inti = idref
# # # inti = str(inti)
# # with open(x, "r") as blancovis:
# #     for line in blancovis:
# #         line = line[0:4]
# #         medida.append(line)
# # string = """SELECT dark FROM espectros WHERE id=%s""" %(inti)
# # print(string)
# # conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
# # cur = conn.cursor()
# # cur.execute(string)
# # negro = cur.fetchone()[0][0]
# # cur.execute("""SELECT white FROM espectros WHERE id='1'""")
# # blanco = cur.fetchone()[0][0]

# # for i in range(0, len(wavelenghts)):
# #     suma.append(float(blanco[i]) - float(negro[i]))
# # # print(str(resta))
# # for i in range(0, len(wavelenghts)):
# #     resta.append(float(medida[i]) - float(negro[i]))
# # for i in range(0, len(wavelenghts)):
# #     if suma[i] == 0:
# #         suma[i] = 1
# #     espectro.append(float(resta[i]) / float(suma[i]))

# # medida = np.array(medida, dtype=np.float32)
# # negro = np.array(negro, dtype=np.float32)
# # blanco = np.array(blanco, dtype=np.float32)
# # wavelenghts = np.array(wavelenghts, dtype=np.float32)
# # #espectro = (medida - negro) / (blanco - negro)
# # espectro = np.array(espectro, dtype=np.float32)

# # for i in range(141, 850):
# #     espectrocor.append(espectro[i])
# # print(str(espectrocor))
# # for i in range(141, 850):
# #     wavecor.append(wavelenghts[i])
# # end_time_A = time.time()
# # duration = end_time_A - start_time_A
# # print("Acquisition for {} seconds".format(duration))
# # # plt.figure(2)
# # # ax2 = plt.subplot(131)
# # # plt.plot(wavelenghts, negro, label='')
# # # ax2.set_ylim(min(blanco), max(blanco))
# # # plt.legend()
# # # ax3 = plt.subplot(132, sharey=ax2)
# # # plt.plot(wavelenghts, blanco, label='')
# # # #ax3.set_ylim(0, 50)
# # # # Add a legend
# # # plt.legend()
# # # ax4 = plt.subplot(133)
# # # plt.plot(wavecor, espectrocor, label='')
# # # # Add a legend
# # # plt.legend()
# # # wm = plt.get_current_fig_manager()
# # # wm.window.state('zoomed')
# # # # Show the plot
# # # plt.show()

