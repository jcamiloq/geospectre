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

id_usuario_activo = ""
app = Flask(__name__)
# app.config['CORS_HEADERS'] = 'Content-Type'

# cors = CORS(app, resources={r"/enviarAltitudVelocidad": {"origins": "http://localhost:5000"}})

# api = Api(app)
CORS(app, resources={r"/crearMision": {"origins": "*"}, r"/enviarAltitudVelocidad": {"origins": "*"}, r"/login":{"origins":"*"}})
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'
parser = argparse.ArgumentParser(description='Demonstrates basic mission operations.')
parser.add_argument('--connect', 
                   help="vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None


#Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()


# # Connect to the Vehicle
# print('Connecting to vehicle on: %s' % connection_string)
# vehicle = connect(connection_string, wait_ready=True)

waypoints = []
elevacion = 0 

print("Termino esa monda")
def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't let the user try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

        
    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:      
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)      
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: #Trigger just below target alt.
            print("Reached target altitude")
            break
        time.sleep(1)
    print("Close vehicle object")
    vehicle.close()

	# Shut down simulator if it was started.
    if sitl is not None:
        sitl.stop()

@app.route('/enviarAltitudVelocidad/<elevacion>/<velocidad>', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def enviarAltitudVelocidad(elevacion, velocidad):
	elevacion = int(elevacion)
	arm_and_takeoff(elevacion);
	# return 'hola'
	x = {
		"status": elevacion
	}
	return json.dumps(x)

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
    data['errorBd'] = ""
    
    # nombreMisionCrear = data["nombreMisionCrear"]
    # elevacion = data["elevacion"]

    print('Connecting to vehicle on: %s' % connection_string)
    vehicle = connect(connection_string, wait_ready=True)
       
    print(data.get('errorBd'))
    return json.dumps(data)
# @app.route('/registro/errorBD', methods=['GET'])
# @cross_origin(origin='*', headers=['Content-Type','Authorization'])
# def errorBD():
#     return json.dumps(errorBd)


# api.add_resource(Hello, '/hello/<name>')
# api.add_resource(enviarAltitudVelocidad, '/enviarAltitudVelocidad/<elevacion>/<velocidad>')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
