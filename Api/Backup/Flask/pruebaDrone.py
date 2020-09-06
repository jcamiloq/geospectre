from drone import *
from math import sin, cos, sqrt, atan2, radians

porce = round(56.883951530008396, 2)
porce = str(porce)
print(porce)




# listaWaypoints = ["3.372788729809556,-76.5301842405155",
# "3.3727927460398406,-76.53008239457566",
# "3.372719115148618,-76.53005961324699",
# "3.372719115148618,-76.53005961324699",
# "3.372684307816279,-76.53016815957764"]
# velocidad = 5
# tiempoAutonomia = 10
# listaWaypoints = ["3.372757462307724,-76.53012457526648",
# "3.372815022469581,-76.53012927202079",
# "3.3728712440197355,-76.5301326268453",
# "3.3729321506953904,-76.53013799456451",
# "3.3729421902569374,-76.5300896850916",
# "3.3728913231439996,-76.53008431737238",
# "3.372845810461727,-76.5300796206181",
# "3.3727949433437385,-76.5300749238638",
# "3.372802305689909,-76.5300279563207",
# "3.3728632123699023,-76.53003533693462",
# "3.3729127408760737,-76.53004137561874",
# "3.372956245642943,-76.53004875623265",
# "3.372964946596083,-76.52999440807564",
# "3.3729247883501743,-76.52998367263723",
# "3.372885968710892,-76.52998031781271",
# "3.372839786724206,-76.5299702533392",
# "3.372801636385737,-76.52996220176037",
# "3.372807660123487,-76.52991120842786",
# "3.3728612044574375,-76.52992060193648",
# "3.372908725051361,-76.52992865351531",
# "3.3729723089409807,-76.52994207281336",
# "3.3729840260908905,-76.52989074523633",
# "3.372928473851384,-76.5298773259383",
# "3.3728909928205217,-76.5298692743595",
# "3.3728294168380866,-76.52985652602636",
# "3.3728367791840275,-76.52980083593958",
# "3.3728970165577246,-76.5298162681323",
# "3.3729505608867516,-76.52982633260581",
# "3.3729980814762985,-76.52983773900912"
# ]
# def calcularDistanciaMetros(waypoints):
#     puntoPausa = []
#     puntoMedio = []
#     R = 6378137.0
#     distanceT = 0
#     distanceW = 0
#     for i in range(0,len(waypoints)-1):
#         latlon1= waypoints[i]
#         latlon2= waypoints[i+1]
#         lat1 = (latlon1.split(","))[0]
#         lon1 = (latlon1.split(","))[1]
#         lat2 = (latlon2.split(","))[0]
#         lon2 = (latlon2.split(","))[1]

#         print(lat1 + "," + lon1  + "," + lat2 + "," + lon2)

#         lat1R = radians(float(lat1))
#         lat2R = radians(float(lat2))
#         lon1R = radians(float(lon1))
#         lon2R = radians(float(lon2))

#         dlon = lon2R - lon1R
#         dlat = lat2R - lat1R

#         a = sin(dlat / 2)**2 + cos(lat1R) * cos(lat2R) * sin(dlon / 2)**2
#         c = 2 * atan2(sqrt(a), sqrt(1 - a))

#         distance = R * c
#         distanceT += distance
#         distanceW += distance

#         if distanceW/float(velocidad) >= tiempoAutonomia:
#             puntoPausa.append(str(i+1))
            
#             lat1f = float(lat1)
#             lat2f = float(lat2)
#             lon1f = float(lon1)
#             lon2f = float(lon2)
#             medio1 = (lat1f+lat2f)/2
#             medio2 = (lon1f+lon2f)/2
#             puntoMedio.append(str(medio1)+","+str(medio2))
            
#             distanceW = 0
#     # print(puntoMedio)
#     print("Result:", distanceT, "metres")
#     return distanceT, puntoPausa, puntoMedio

# d, c, a, = calcularDistanciaMetros(listaWaypoints)
# print(d)





# p1 = listaWaypoints[0]
# p2 = listaWaypoints[1]
# p1 = p1.split(",")
# p2 = p2.split(",")
# lat1 = p1[0]
# lon1 = p1[1]
# lat2 = p2[0]
# lon2 = p2[1]
# lat1f = float(lat1)
# lat2f = float(lat2)
# lon1f = float(lon1)
# lon2f = float(lon2)
# medio1 = (lat1f+lat2f)/2
# medio2 = (lon1f+lon2f)/2
# puntoMedio.append(str(medio1)+","+str(medio2))
# a partir de los waypoint crear una lista con ellos donde en los puntos de 
# descanso se introudzcan los way descanso
# descanso = ["1,-1","2,-2"]
# arrayPuntosDescanso = [1, 4]
# final = []
# j= 0
# punto = arrayPuntosDescanso.pop(0)
# for k in range(0,len(listaWaypoints)):
#     if punto==k:
#         final.append(descanso[j])
#         final.append(listaWaypoints[k])
#         print(arrayPuntosDescanso)
#         if arrayPuntosDescanso:
#             punto = arrayPuntosDescanso.pop(0)
#         j+=1
#     else:
#         final.append(listaWaypoints[k])
# print(final)


# R = 6378137.0
# distanceT = 0
# for i in range(0,len(waypoints)-1):
#     latlon1= waypoints[i]
#     latlon2= waypoints[i+1]
#     lat1 = (latlon1.split(","))[0]
#     lon1 = (latlon1.split(","))[1]
#     lat2 = (latlon2.split(","))[0]
#     lon2 = (latlon2.split(","))[1]

#     print(lat1 + "," + lon1  + "," + lat2 + "," + lon2)

#     lat1 = radians(float(lat1))
#     lat2 = radians(float(lat2))
#     lon1 = radians(float(lon1))
#     lon2 = radians(float(lon2))

#     dlon = lon2 - lon1
#     dlat = lat2 - lat1

#     a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
#     c = 2 * atan2(sqrt(a), sqrt(1 - a))

#     distance = R * c
#     distanceT += distance

# print("Result:", distanceT, "metres")
# import argparse





# # label = ""
# # print(label)
# # label += "1"
# # print(label)
# # label += "2"
# # print(label)

# initCon(5, 5)
# telem()
# estadoWaypoints(waypoints)
# estadoArmado(1)
# estadoDespegue(1)

# sleep(15)
# rwp = estadoPause(1, "T")
# sleep(5)
# print("reanudando")
# # FSM(1)
# initCon(10, 10)
# telem()
# estadoWaypoints(rwp)
# estadoArmado(1)
# estadoDespegue(1)

# sleep(.3)
# FSM(1)
# # print(label2)
# sleep(.3)
# FSM(waypoints)
# # print(label2)
# sleep(.3)
# e = FSM(1)
# print(e)
# sleep(.3)
# from multiprocessing import Queue
# # import seabreeze.spectrometers as sb
# import numpy as np
# import io

# # import STS_functions as sts  # This script was created in order to ease the readability of the developed script


# from flask import Flask, send_file
# import requests

# from time import sleep, clock
# from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
# import time
# import datetime
# import math
# from pymavlink import mavutil
# import serial
# import threading
# import argparse

# from flask import Flask, send_file
# import requests

# # DEFINICION DE VARIABLES
# COM = 'COM4'
# Modo_foto=""
# Valor_modo=10.2
# a = 0
# exclu=1
# bandFoto=0
# cnt=0
# GPS_FOTO=[]
# TIME_FOTO=[]
# vehicle=""
# point1=""
# point2=""
# point3=""
# point4=""
# altura=""
# points_lat=[]
# points_long=[]
# DataWps=[]
# band_pause=0
# band_pause_2=0
# band_cancel=0
# acabe=0
# band_RTH=0
# band_cancel_2=0
# flag_reanudado=0
# Mision_resume=0
# band_battery=0
# nxt_Wp=0;
# fin=0
# RTH_fin=0
# ActualWp=0
# nextwaypoint=1
# Wp_reanudacion=0
# lati_r=""
# longi_r=""
# # velocidad=""
# estado='c'
# # waypoints = []
# # OPCIONES DE LLAMADA POR COMANDO
# parser = argparse.ArgumentParser()
# parser.add_argument("--connect", dest="conect",help="Puerto por el que se desea conectar el UAV Ej: Com7")
#         #asigna a parser cada elemento en "dest"
# parser.add_argument("--reanudar",dest="reanude",help="Valores necesarios para realizar la reanudacion con el siguiente formato : [LATITUD,LONGITUD,WP_REANUDACION]")

# def initCon(alturaR, velocidadR):
#     global vehicle, altura, velocidad
#     altura = alturaR
#     velocidad = velocidadR
#     results = parser.parse_args()           #array
#     connection_string=results.conect        #Com
#     sitl=None
#     ultimaPosicion=results.reanude                
#     print("Ulti %s" %ultimaPosicion) 
#     print("Cone %s" %connection_string)

#     if not ultimaPosicion:
#         #global flag_reanudado                      #If not: flag de reanudación
#         print ("START MISION") 
#         flag_reanudado=0
#     if not connection_string:                           #cuando no hay COM simulación
#         print ("Empieza con simulador") 
#         import dronekit_sitl
#         sitl = dronekit_sitl.start_default()
#         connection_string = sitl.connection_string()
#         print('Connecting to vehicle on: %s' % connection_string)
#         vehicle = connect(connection_string, wait_ready=True)
#     t2 =threading.Thread(target = telem)
#     t2.setDaemon(True)
#     t2.start()
#     return vehicle

# def telem():
#     while(True):
#         if vehicle:
#             print(" Global Location: %s" % vehicle.location.global_frame)
#             print(" Global Location (relative altitude): %s" % vehicle.location.global_relative_frame)
#             print(" Local Location: %s" % vehicle.location.local_frame)
#             print(" Attitude: %s" % vehicle.attitude)
#             print(" Velocity: %s" % vehicle.velocity)
#             print(" Battery: %s" % vehicle.battery)
#             print(" Heading: %s" % vehicle.heading)
#             print(" Is Armable?: %s" % vehicle.is_armable)
#             print(" System status: %s" % vehicle.system_status.state)
#             print(" Groundspeed: %s" % vehicle.groundspeed)    # settable
#             print(" Airspeed: %s" % vehicle.airspeed)    # settable
#             print(" Mode: %s" % vehicle.mode.name)    # settable
#             print(" Armed: %s" % vehicle.armed)    # settable
#             sleep(5)
# def estadoConectar(entrada):
#     global estado
#     print("edoC")
#     estado='i'
        
        
# def estadoInicial(entrada): #Recepción de parámetros de misión (altura, velocidad)
#     global estado
#     print("Estado Inicial") 
#     print("Altura: %s" %altura)
#     print("Velocidad: %s" %velocidad)
#     print("End Flag")    
#     estado = 'j'
#     print("Transicion hacia j...")     
    

# def estadoWaypoints(entrada): #Recepción de Waypoints
#     global waypoints, estado
#     waypoints = []
#     print("Estado Waypoints")
#     # estadoReturn = "Estado Inicial"
#     for i in range(0, len(entrada)):
#         waypoints.append(entrada[i])
#     print(waypoints)
            
#     estado = 0
#     print("Transicion hacia 0...")
#     # return estadoReturn          
    
            
# def estadoArmado(entrada): #Estado de armado y arranca hilo de telemetría y recepción de comandos
#     global estado
#     señalRespuesta = ""
#     contadorHome= 0
#     contadorSatelite = 0
#     contadorControlador = 0
#     print("Estado Armado")
    
#     global vehicle
    
#     try:
#     #-----------------------------------Establecimiento de Home---------------------------------- 
#         while not vehicle.home_location:
#             cmds = vehicle.commands
#             cmds.download()
#             cmds.wait_ready()
#             if not vehicle.home_location:
#                 print(" Waiting for home location ...")
#                 sleep(1)
#                 contadorHome += 1
#                 if contadorHome>=1:
#                     señalRespuesta = "H"
#                     break

#         # We have a home location, so print it!        
#         print("\n Home location: %s" % vehicle.home_location)

#         print("\nSet new home location")
#         # Home location must be within 50km of EKF home location (or setting will fail silently)
#         # In this case, just set value to current location with an easily recognisable altitude (222)
#         my_location_alt = vehicle.location.global_frame
#         my_location_alt.alt = 0.0
#         vehicle.home_location = my_location_alt
#         print(" New Home Location (from attribute - altitude should be 222): %s" % vehicle.home_location)

#         #Confirm current value on vehicle by re-downloading commands
#         cmds = vehicle.commands
#         cmds.download()
#         cmds.wait_ready()
#         print(" New Home Location (from vehicle - altitude should be 222): %s" % vehicle.home_location)
#     # -----------------------------------------------------------------------------------------------
#     # --------------------------------------Chequeo Pre-Armado---------------------------------------
#         print("Chequeo Pre-Armado")
#         while not vehicle.gps_0:
#             print("Waiting for satellite fix")
#             contadorSatelite += 1
#             if contadorSatelite>=10:
#                 señalRespuesta += "S"
#                 break
#             sleep(1)
#         # Don't let the user try to arm until autopilot is ready
#         while not vehicle.is_armable:
#             print(" Waiting for vehicle to initialise...")
#             contadorControlador += 1
#             print(str(contadorControlador))
#             if contadorControlador>=10:
#                 señalRespuesta += "C"
#                 break
#             time.sleep(1)
#         if vehicle.battery.voltage<9:
#             print("Battery is too low")
#             señalRespuesta += "B"
#         else: 
#             print("Arming motors")
#             # Copter should arm in GUIDED mode
#             vehicle.mode = VehicleMode("STABILIZE")
#             vehicle.armed = True    

#             # Confirm vehicle armed before attempting to take off
#             while not vehicle.armed:      
#                 print(" Waiting for arming...")
#                 time.sleep(1)
#         pass
#     except Exception as errorArmado:
#         señalRespuesta = "D"
#         raise errorArmado
#     # ----------------------------------------------------------------------------------------------
#     t3 =threading.Thread(target = estadoDespegue(1))
#     # t2.setDaemon(True)
#     t3.start()
    
#     print(señalRespuesta)

#     return señalRespuesta
         
# def estadoDespegue(entrada): #Despegue y seteo de velocidad
#     global estado, flag_reanudado 
#     print("Estado 1")
#     #adds_square_mission(vehicle.location.global_frame,50)
#     print("Taking off!")
#     vehicle.mode = VehicleMode("GUIDED")
#     vehicle.simple_takeoff(10) # Take off to target altitude
#     # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
#     #  after Vehicle.simple_takeoff will execute immediately).
    
#     while True:
#         print(" Altitude: ", vehicle.location.global_relative_frame.alt)
#         #Break and return from function just below target altitude.        
#         if vehicle.location.global_relative_frame.alt>=altura*0.95: 
#             print("Reached target altitude")
#             Wpoint=0
#             break
#         time.sleep(1)

#     print("Set default/target airspeed to %s" %velocidad)
#     vehicle.airspeed = velocidad
    
            
#     '''
#     Transiciones 
#     ''' 
#     if flag_reanudado==1:
#         estado='r'
#         print("Transicion hacia r...")
#         time.sleep(5)
#     else:
#         if entrada == 1: 
#             estado = 'm' 
#             print("Transicion hacia m...")
#             time.sleep(5)


   
# app = Flask(__name__)
# @app.route('/sensoresVuelo/<sensorVueloVIS>', methods=['GET'])                                     #Añade el recurso
# def sensoresVuelo(sensorVueloVIS):
#     indicador = sensorVueloVIS
#     print(indicador)
#     # while True:
#     # initCon(10, 10)
#     if indicador == "1":
#         initCon(10, 10)
#     if indicador == "2":
#         estadoConectar(1)
#     if indicador == "3":
#         estadoWaypoints(waypoints)
#     if indicador == "4":
#         estadoArmado(1)
#     if indicador == "5":
#         estadoDespegue(1)
#     else:
#         print("efe")
#     return indicador 

# if __name__ == '__main__':
#     app.run(debug=True, host='127.0.0.1', port=8080)
    

