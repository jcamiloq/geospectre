from time import sleep, clock
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
import time
import datetime
import math
from pymavlink import mavutil
import serial
import threading
import argparse

# DEFINICION DE VARIABLES
vehicle = None
COM = 'COM4'
Modo_foto=""
Valor_modo=10.2
a = 0
exclu=1
bandFoto=0
cnt=0
GPS_FOTO=[]
TIME_FOTO=[]
point1=""
point2=""
point3=""
point4=""
altura=""
points_lat=[]
points_long=[]
DataWps=[]
band_pause=0
band_pause_2=0
band_cancel=0
acabe=0
band_RTH=0
band_cancel_2=0
flag_reanudado=0
Mision_resume=0
band_battery=0
nxt_Wp=0;
fin=0
RTH_fin=0
ActualWp=0
nextwaypoint=1
Wp_reanudacion=0
lati_r=""
longi_r=""
# velocidad=""
estado='c'
alertaProximidad = 0
# waypoints = []
# OPCIONES DE LLAMADA POR COMANDO
parser = argparse.ArgumentParser()
parser.add_argument("--connect", dest="conect",help="Puerto por el que se desea conectar el UAV Ej: Com7")
        #asigna a parser cada elemento en "dest"
parser.add_argument("--reanudar",dest="reanude",help="Valores necesarios para realizar la reanudacion con el siguiente formato : [LATITUD,LONGITUD,WP_REANUDACION]")

def initCon(alturaR, velocidadR):
    global altura, velocidad, vehicle
    altura = alturaR
    velocidad = velocidadR
    results = parser.parse_args()           #array
    connection_string=results.conect        #Com
    sitl=None
    ultimaPosicion=results.reanude                
    print("Ulti %s" %ultimaPosicion) 
    print("Cone %s" %connection_string)

    if not ultimaPosicion:
        #global flag_reanudado                      #If not: flag de reanudación
        print ("START MISION") 
        flag_reanudado=0
    if not connection_string:                           #cuando no hay COM simulación
        print ("Empieza con simulador") 
        import dronekit_sitl
        sitl = dronekit_sitl.start_default()
        connection_string = sitl.connection_string()
        print('Connecting to vehicle on: %s' % connection_string)
        vehicle = connect(connection_string, wait_ready=True)
        vehicle.wait_ready('autopilot_version')

def telem():
    global vehicle, alertaProximidad
    if vehicle:
        senalCaptura = ""
        if vehicle.commands.next:                           #Verifica si se han subido comandos
            if vehicle.commands.next <= len(waypoints):   #Verifica si se ha llegado al penultimo comando
                d = distance_to_current_waypoint()
                if d <= 0.5 and alertaProximidad != 1:        #Verifica si se ha llegado al punto de captura
                    sleep(2)
                    senalCaptura = "G"                      
                    alertaProximidad = 1
                if alertaProximidad == 1 and d >= 1:          #Verifica si se salió del punto de captura
                    alertaProximidad = 0
        # print(" Global Location: %s" % vehicle.location.global_frame)
        # print(" Global Location (relative altitude): %s" % vehicle.location.global_relative_frame)
        # print(" Local Location: %s" % vehicle.location.local_frame)
        # print(" Attitude: %s" % vehicle.attitude)
        # print(" Velocity: %s" % vehicle.velocity)
        # print(" Battery: %s" % vehicle.battery)
        # print(" Heading: %s" % vehicle.heading)
        # print(" Is Armable?: %s" % vehicle.is_armable)
        # print(" System status: %s" % vehicle.system_status.state)
        # print(" Groundspeed: %s" % vehicle.groundspeed)    # settable
        # print(" Airspeed: %s" % vehicle.airspeed)    # settable
        # print(" Mode: %s" % vehicle.mode.name)    # settable
        # print(" Armed: %s" % vehicle.armed)    # settable
        if vehicle.armed:
            armado = "T"
        else:
            armado = "F"
    return vehicle.location.global_relative_frame, vehicle.attitude, vehicle.velocity, vehicle.battery, senalCaptura, vehicle.commands.next, armado
    
def get_location_metres(original_location, dNorth, dEast):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the 
    specified `original_location`. The returned Location has the same `alt` value
    as `original_location`.

    The function is useful when you want to move the vehicle around specifying locations relative to 
    the current vehicle position.
    The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.
    For more information see:
    http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    """
    earth_radius=6378137.0 #Radius of "spherical" earth
    #Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    #New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    return LocationGlobal(newlat, newlon,original_location.alt)


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


def distance_to_current_waypoint():
    """
    Gets distance in metres to the current waypoint. 
    It returns None for the first waypoint (Home location).
    """
    nextwaypoint = vehicle.commands.next
    if nextwaypoint==0:
        return None
    missionitem=vehicle.commands[nextwaypoint-1] #commands are zero indexed
    lat = missionitem.x
    lon = missionitem.y
    alt = missionitem.z
    targetWaypointLocation = LocationGlobalRelative(lat,lon,alt)
    distancetopoint = get_distance_metres(vehicle.location.global_frame, targetWaypointLocation)
    return distancetopoint

    
def distance_to_someone_waypoint(Lati1,Longi1):
    targetWaypointLocation = LocationGlobalRelative(Lati1, Longi1,altura)
    distancetopoint = get_distance_metres(vehicle.location.global_frame, targetWaypointLocation)
    return distancetopoint

def añadirMision(waypoints, altura):
    global wp
    wp = waypoints
    cmds = vehicle.commands
    my_location_alt = vehicle.location.global_frame
    my_location_alt.alt = 0.0
    vehicle.home_location = my_location_alt
    # vehicle.location.global_frame = my_location_alt
    print(" New Home Location (from attribute - altitude should be 222): %s" % vehicle.home_location)
    print(" Clear any existing commands")
    cmds.clear() 

    print(" Define/add new commands.")
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, altura))
    
    for Wps in waypoints:
        # Add new commands. The meaning/order of the parameters is documented in the Command class. 
        #Define the four MAV_CMD_NAV_WAYPOINT locations and add the commands
        pointsW=Wps.split(",")
        cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 5, 0, 0, 0, float(pointsW[0]), float(pointsW[1]),  altura))
        # cmds.add(Command())
        print(cmds)
    #add dummy waypoint "n" at point n-1 (lets us know when have reached destination)
    LastData=len(waypoints)-1
    lastpoint=waypoints[LastData]
    sep=lastpoint.split(",")
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, vehicle.home_location.lat, vehicle.home_location.lon,  altura))   
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0, vehicle.home_location.lat,vehicle.home_location.lon, 0))  
    print(" Upload new commands to vehicle")
    cmds.upload()

def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """
    global vehicle
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
    
def mision():
    global vehicle
    x = 0
    while True:
        nextwaypoint=vehicle.commands.next
        print("worker ciclo: " + str(nextwaypoint))
        print('Distance to waypoint (%s): %s' % (nextwaypoint, distance_to_current_waypoint()))
        print(str(len(wp)))
        if nextwaypoint+1==None: #Dummy waypoint - as soon as we reach waypoint 4 this is true and we exit.
            print("Exit 'standard' mission when start heading to final waypoint")
            vehicle.mode = VehicleMode("GUIDED")
            vehicle.armed = False

            while vehicle.armed:      
                print(" Waiting for disarming...")
                vehicle.armed = False
                time.sleep(1)
            break;

        time.sleep(1)
   
def estadoConectar(entrada):
    global estado
    print("edoC")
    estado='i'
        
        
def estadoInicial(entrada): #Recepción de parámetros de misión (altura, velocidad)
    global estado
    print("Estado Inicial") 
    print("Altura: %s" %altura)
    print("Velocidad: %s" %velocidad)
    print("End Flag")    
    estado = 'j'
    print("Transicion hacia j...")     
    

def estadoWaypoints(entrada): #Recepción de Waypoints
    global waypoints, estado
    waypoints = []
    print("Estado Waypoints")
    
    # estadoReturn = "Estado Inicial"
    for i in range(0, len(entrada)):
        waypoints.append(entrada[i])
    print(waypoints)
    añadirMision(waypoints, altura)    
    estado = 0
    print("Transicion hacia 0...")
    # return estadoReturn          
    
            
def estadoArmado(entrada): #Estado de armado y arranca hilo de telemetría y recepción de comandos
    global estado, vehicle, altura
    señalRespuesta = ""
    print("Estado Armado")
    # adds_square_mission(vehicle.location.global_frame,50)
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
    
    señalRespuesta = "1"

    # try:
    #     vehicle.commands.next=0

    #     # Set mode to AUTO to start mission
    #     vehicle.mode = VehicleMode("AUTO")


    #     # Monitor mission. 
    #     # Demonstrates getting and setting the command number 
    #     # Uses distance_to_current_waypoint(), a convenience function for finding the 
    #     #   distance to the next waypoint.
    #     t3 =threading.Thread(target = worker())
    #     # t3.setDaemon(True)
    #     t3.start()
        
    #     # señalRespuesta = "1"
    #     # print('Return to launch')
    #     # vehicle.mode = VehicleMode("RTL")


    #     # #Close vehicle object before exiting script
    #     # print("Close vehicle object")
    #     # vehicle.close()

        
    # except Exception as errorArmado:
    #     señalRespuesta = "D"
    #     raise errorArmado
    # ----------------------------------------------------------------------------------------------
    
    
    print(señalRespuesta)
    # vehicle.mode = VehicleMode("LOITER")
    return señalRespuesta
         
def estadoDespegue(entrada): #Despegue y seteo de velocidad
    global estado, flag_reanudado 
    print("Estado 1")
    print("Taking off!")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.simple_takeoff(altura) # Take off to target altitude
    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.simple_takeoff will execute immediately).
    
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        #Break and return from function just below target altitude.        
        if vehicle.location.global_relative_frame.alt>=altura*0.95: 
            print("Reached target altitude")
            Wpoint=0
            break
        time.sleep(1)

    print("Set default/target airspeed to %s" %velocidad)
    vehicle.airspeed = velocidad

    vehicle.commands.next=0
    vehicle.mode = VehicleMode("AUTO")
    t3 =threading.Thread(target = mision)
    t3.setDaemon(True)
    t3.start()
            
    '''
    Transiciones 
    ''' 
    # if flag_reanudado==1:
    #     estado='r'
    #     print("Transicion hacia r...")
    #     time.sleep(5)
    # else:
    #     if entrada == 1: 
    #         estado = 'm' 
    #         print("Transicion hacia m...")
    #         time.sleep(5)

        
def estadoMision(entrada): #Crear y añadir comandos al dron, Recorrido de wpoints, verificación de flags de eventos asíncronos
    global estado
    global nxt_Wp
    global WpPar
    global bandFoto
    global cnt
    global band_battery
    print("Estado m")   
    print("Starting mission")
    
    #adds_square_mission(vehicle.location.global_frame,50)
    SCGI_mission(DataWps,altura)
    
    vehicle.commands.next=nxt_Wp
    
    # Set mode to AUTO to start mission
    vehicle.mode = VehicleMode("AUTO")


    # Monitor mission. 
    # Demonstrates getting and setting the command number 
    # Uses distance_to_current_waypoint(), a convenience function for finding the 
    #   distance to the next waypoint.

    n=2
    bande=1
    bande2=1
    bande3=1
    while True:
        global exclu
        global band_pause
        global band_cancel
        global nextwaypoint
        global ActualWp
        nextwaypoint=vehicle.commands.__next__
        WpPar=nextwaypoint%2
        print("PAR O IMPAR %s" %WpPar) #como se tomaban fotos, tenía que ir al doble de la distancia para la construcción del mosaico
        bateria_datos=str(vehicle.battery)
        bateria_datos_array=bateria_datos.split(",")
        Voltaje=bateria_datos_array[0]
        Level=bateria_datos_array[2]
        Voltaje=Voltaje[16:]
        Level=Level[6:]
        print('Distance to waypoint (%s): %s' % (nextwaypoint, distance_to_current_waypoint()))
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)   
        if band_pause==1:
            print("Exit 'standard' mission for PAUSED button")
            ActualWp=nextwaypoint-1
            estado = 'p'
            print("Transicion hacia p...")
            break;
        if band_RTH==1:
            print("Exit 'standard' mission for RTH button")
            estado = 3 
            print("Transicion hacia 3...")
            break;
        if band_cancel==1:
            print("Exit 'standard' mission for CANCEL button")
            estado= 'h'
            print("Transicion hacia h...")
            break;
        if float(Voltaje)<=9.0 and nextwaypoint<int(len(DataWps)+1):
            print("Exit 'standard' mission for BATTERY")
            ActualWp=nextwaypoint-1
            band_battery=1
            estado = 'p'
            print("Transicion hacia p...")
            break;
        if Modo_foto=="0":
            print("MODO DIST: Valor_modo:%s" %Valor_modo)
            if bandFoto==0:
                if WpPar==0 and nextwaypoint>1:
                    if bande==1 and nextwaypoint>1:
                        Pye=float(distance_to_current_waypoint()) - (Valor_modo)
                        print("Actualiza Pye=%s N=%s" %(Pye,n))
                        if bande2==1:
                            bande=0
                            print("ya se actualizo y salgo")
                        if nextwaypoint==n and bande3==1:
                            '''
                            msg = vehicle.message_factory.digicam_control_encode(0,0,0,0,0,0,1,0,0,0)
                            vehicle.send_mavlink(msg)
                            Pos2=[]
                            Pos=str(vehicle.location.global_frame)
                            Pos2=Pos.split("=")
                            GPS_FOTO.append(Pos2[1]+Pos2[2]+str(time.strftime("%H:%M:%S")))
                            cnt=cnt+1
                            print"TOME_FOTO_1: %s" %distance_to_current_waypoint()
                            '''
                            bande2=1
                            bande=0
                    if nextwaypoint>1 and bande2==1:
                        print("PYE: %s" %Pye)
                        if distance_to_current_waypoint()<=Pye:
                            msg = vehicle.message_factory.digicam_control_encode(0,0,0,0,0,0,1,0,0,0)
                            vehicle.send_mavlink(msg)
                            Pye=float(distance_to_current_waypoint()) - (Valor_modo)
                            Pos2=[]
                            Pos=str(vehicle.location.global_frame)
                            Pos2=Pos.split("=")
                            GPS_FOTO.append(Pos2[1]+Pos2[2]+str(time.strftime("%H:%M:%S")))
                            cnt=cnt+1
                            print("TOME_FOTO_2: %s" %distance_to_current_waypoint())
                            bande3=0
                            
                        else :
                            if distance_to_current_waypoint()<=Valor_modo:
                                print("valor menor para toma de foto")
                                if bande2==1:
                                    print("condicional menor")
                                    bande=1
                                    bande3=1
                                    n=n+1
                                    bande2=0
                else:
                    print("No es par el wp")
                    Pye=0
                    bande=1
                    bande2=1
                    bande3=1
            else:
                print("FIN TOMA DE DATOS")
                        
        if Modo_foto=="1" and exclu==1:
            print("Modo tiempo")
            t2 =threading.Thread(target = Camera)
            t2.setDaemon(True)
            t2.start()
            exclu=0
        if (nextwaypoint==int(len(DataWps)+1)):
            bandFoto=1
        if (nextwaypoint==int(len(DataWps)+1)) and (distance_to_current_waypoint()<=1): #Dummy waypoint - as soon as we reach waypoint 4 this is true and we exit.
            print("Exit 'standard' mission when start heading to FINAL waypoint ")
            bandFoto=1
            estado = 2 
            print("Transicion hacia 2...")
            break;              

def estadoResume(entrada): #Ir a punto de reanudación, ir a estadomision, verificar pausa y rth
    global estado
    global nxt_Wp
    global Mision_resume
    vehicle.mode = VehicleMode("GUIDED")
    print("Going towards RESUME point  ...")
    pointy = LocationGlobalRelative(lati_r, longi_r, altura)
    vehicle.simple_goto(pointy)
    while True:
    # sleep so we can see the change in map
        Distancia=distance_to_someone_waypoint(pointy.lat,pointy.lon)
        print("Distancia a reanudacion: %s" %Distancia)
        print("altitud de retorno: ", vehicle.location.global_relative_frame.alt)
        if((Distancia<=1)):
            print("Punto reanudacion alcanzado!!!!")
            Mision_resume=1
            print("Wp de reanudacion: %s" %Wp_reanudacion)
            nxt_Wp=int(Wp_reanudacion)
            estado='m'
            print("Transicion hacia m...")
            break
        if band_RTH==1:
            print("Exit 'standard' mission for RTH button")
            estado = 3 
            print("Transicion hacia 3...")
            break;
        if band_cancel==1:
            print("Exit 'standard' mission for CANCEL button")
            estado= 'h'
            print("Transicion hacia h...")
            break;
    
def estadoRTL(entrada): #Return to launch, land, disarm, stop sitl, viene aquí si se presiona boton RTH en GUI
    global estado 
    archivo_log=abrir_log("RTL_monitoreo.txt")
    guardar_log(archivo_log,str(distance_to_someone_waypoint(vehicle.home_location.lat,vehicle.home_location.lon)),"RTL")
    cerrar_log(archivo_log)
    print("Estado 3")
    print("Returning to Launch")
    #vehicle.mode = VehicleMode("RTL")
    vehicle.mode = VehicleMode("GUIDED")
    
    pointy = LocationGlobalRelative(float(str(vehicle.home_location.lat)),float(str(vehicle.home_location.lon)), altura)
    vehicle.simple_goto(pointy)
    while True:
        print("Yendo a casa...")
        Distancia=distance_to_someone_waypoint(vehicle.home_location.lat,vehicle.home_location.lon)
        print("Distancia a casa: %s" %Distancia)
        print("altitud de retorno: ", vehicle.location.global_relative_frame.alt)
        if((Distancia<=2)):
            print("EN CASA!!!!")
            break;
        time.sleep(0.5)
    
    vehicle.mode = VehicleMode("LAND")
    while True:
        print("Distancia a casa: %s" %Distancia)
        print("altitud de retorno: ", vehicle.location.global_relative_frame.alt)
        #Break and return from function just below target altitude.        
        if vehicle.location.global_relative_frame.alt<=1: 
            print("Altitud de descenso alcanzada")
            Wpoint=0
            break
        time.sleep(0.5)
            
    time.sleep(2)       
    print("Global Location: %s" % vehicle.location.global_frame) 
    #Close vehicle object before exiting script
    global fin
    global RTH_fin
    if band_RTH!=1:
        fin=1
    else:
        RTH_fin=1
    #vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = False
    while vehicle.armed:
        print(" Waiting for disarming..")
        print("El vehiculo armed(true) o disarmed (false): %s" %vehicle.armed)
        time.sleep(1)
    print("Close vehicle object")
    vehicle.close()
    # Shut down simulator if it was started.
    if sitl is not None:
        sitl.stop()
    '''
    Transiciones 
    ''' 
    estado = 'f' 
    print("Transicion hacia f...") 

def estadoRTLfinal(entrada): #Viene aquí si se termina la misión
    global estado 
    print("Estado 2")
    print("Returning to Launch")
    #vehicle.mode = VehicleMode("RTL")
    while True:
        print("altitud de retorno: ", vehicle.location.global_relative_frame.alt)
        #Break and return from function just below target altitude.        
        if vehicle.location.global_relative_frame.alt<=1: 
            print("Altitud de descenso alcanzada")
            Wpoint=0
            break
        time.sleep(0.5)
            
    time.sleep(2)
    print("Global Location: %s" % vehicle.location.global_frame) 
    #Close vehicle object before exiting script
    global fin
    global RTH_fin
    if band_RTH!=1:
        fin=1
        print("FINALIZO")
    else:
        RTH_fin=1
    vehicle.mode = VehicleMode("STABILIZE")
    vehicle.armed = False
    while vehicle.armed:
        print(" Waiting for disarming..")
        print("El vehiculo armed(true) o disarmed (false): %s" %vehicle.armed)
        time.sleep(1)
    while True:
        global acabe
        print("pausa activa")
        if acabe==1:
            break
    print("Close vehicle object")
    vehicle.close()
    
    # Shut down simulator if it was started.
    if sitl is not None:
        sitl.stop()
    '''
    Transiciones 
    ''' 
    estado = 'f' 
    print("Transicion hacia f...") 
     

def estadoFinal(entrada): #Recibe estado 2 y 3 de RTL
    global estado 
    print("Estado f")
    

def estadoCancel(entrada): #Aterriza, disarm
    global estado
    global band_cancel_2
    archivo_log=abrir_log("Cancel_monitoreo.txt")
    guardar_log(archivo_log,str(distance_to_someone_waypoint(vehicle.home_location.lat,vehicle.home_location.lon)),"CANCELA")
    cerrar_log(archivo_log)
    print("Estado h")
    vehicle.mode = VehicleMode("LAND")
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        #Break and return from function just below target altitude.        
        if vehicle.location.global_relative_frame.alt<=2: 
            print("Altitud de descenso alcanzada")
            break
        time.sleep(0.5)
    
    time.sleep(5)
    band_cancel_2=1
    #vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = False
    while vehicle.armed:
        print(" Waiting for disarming..")
        print("El vehiculo armed(true) o disarmed (false): %s" %vehicle.armed)
        time.sleep(1)
    print("Close vehicle object")
    vehicle.close()
    # Shut down simulator if it was started.
    if sitl is not None:
        sitl.stop()
    print("CANCELACION REALIZADA Y EN TIERRA")

def estadoPause(entrada): # Establece el wp mas cercano y lo guarda como punto de reanudación, land, disarm
    global estado 
    global band_pause_2
    print("Estado p")
    archivo_log=abrir_log("Pausa_monitoreo.txt")
    guardar_log(archivo_log,str(distance_to_someone_waypoint(vehicle.home_location.lat,vehicle.home_location.lon)),"PAUSA")
    cerrar_log(archivo_log)
    vehicle.mode = VehicleMode("GUIDED")

    if(ActualWp>=1):
        Distancia_ant=distance_to_someone_waypoint(points_lat[ActualWp-1],points_long[ActualWp-1])
        Distancia_sig=distance_to_someone_waypoint(points_lat[ActualWp],points_long[ActualWp])
        if(Distancia_ant<=Distancia_sig):
            puntoc=LocationGlobalRelative(points_lat[ActualWp-1],points_long[ActualWp-1],altura)
            ps=1
            print("Va al anterior")
        else:
            puntoc=LocationGlobalRelative(points_lat[ActualWp],points_long[ActualWp],altura)
            print("Va al siguiente")
            ps=0
        vehicle.simple_goto(puntoc)
        
        while True:
            if ps==1:
                Distancia=distance_to_someone_waypoint(points_lat[ActualWp-1],points_long[ActualWp-1])
            else:
                Distancia=distance_to_someone_waypoint(points_lat[ActualWp],points_long[ActualWp])
            print("Distancia a Wp para bajar: %s" %Distancia)
            print("altitud : ", vehicle.location.global_relative_frame.alt)
            if((Distancia<=3)):
                print("Punto reanudacion alcanzado!!!!")
                break;
            time.sleep(0.5)
        
        print("Llego al punto de bajar")
        vehicle.mode = VehicleMode("LAND")
        while True:
            print(" Altitude: ", vehicle.location.global_relative_frame.alt)
            #Break and return from function just below target altitude.        
            if vehicle.location.global_relative_frame.alt<=2: 
                print("Altitud de descenso alcanzada")
                Wpoint=0
                break
            time.sleep(0.5)
            
        time.sleep(5)
        band_pause_2=1
        #vehicle.mode = VehicleMode("GUIDED")
        vehicle.armed = False
        while vehicle.armed:
            print(" Waiting for disarming..")
            print("El vehiculo armed(true) o disarmed (false): %s" %vehicle.armed)
            time.sleep(1)
        while True:
            global acabe
            print("pausa activa")
            if acabe==1:
                break
        print("Close vehicle object")
        vehicle.close()
        
        # Shut down simulator if it was started.
        if sitl is not None:
            sitl.stop()
        
    else:
        vehicle.mode = VehicleMode("GUIDED")
        pointy = LocationGlobalRelative(float(str(vehicle.home_location.lat)),float(str(vehicle.home_location.lon)), altura)
        vehicle.simple_goto(pointy)
        while True:
            print("Yendo a casa...")
            Distancia=distance_to_someone_waypoint(vehicle.home_location.lat,vehicle.home_location.lon)
            print("Distancia a casa: %s" %Distancia)
            print("altitud de retorno: ", vehicle.location.global_relative_frame.alt)
            if((Distancia<=2)):
                print("EN CASA!!!!")
                break;
            time.sleep(0.5)
        vehicle.mode = VehicleMode("LAND")
        while True:
            print("Distancia a casa: %s" %Distancia)
            print("altitud de retorno: ", vehicle.location.global_relative_frame.alt)
            #Break and return from function just below target altitude.        
            if vehicle.location.global_relative_frame.alt<=1: 
                print("Altitud de descenso alcanzada")
                Wpoint=0
                break
            time.sleep(0.5)

        band_pause_2=1
        #vehicle.mode = VehicleMode("GUIDED")
        vehicle.armed = False
        while vehicle.armed:
            print(" Waiting for disarming..")
            print("El vehiculo armed(true) o disarmed (false): %s" %vehicle.armed)
            time.sleep(1)
        print("Close vehicle object")
        vehicle.close()
        # Shut down simulator if it was started.
        if sitl is not None:
            sitl.stop()
    print("VEHICULO PAUSADO Y EN TIERRA")
        
'''
#Finite State Machine (FSM)
'''    
def FSM(entrada):
    print("FSM") 
    global estado 
    switch = {
        'c' :estadoConectar,
        'i':estadoInicial,
        'j':estadoWaypoints, 
        0 :estadoArmado, 
        1 :estadoDespegue, 
        2 :estadoRTLfinal,
        3 :estadoRTL,
        'm':estadoMision,
        'r':estadoResume,
        'h':estadoCancel,
        'f':estadoFinal,
        'p':estadoPause,
    } 
    func = switch.get(estado, lambda: None) 
    return func(entrada) 

def avanceEstados(flag_reanudado):
    if flag_reanudado==0:
        print("FSM normal")
        FSM(1)
        sleep(.3)
        while True:
            dataInmatlab = portCOMx.readline()
            dataInmatlab=str(dataInmatlab)
            print("Esperando INICIO: %s" %dataInmatlab)
            if dataInmatlab=="I":
                print("Inicio de mision correcto")
                break
            time.sleep(0.2)
        FSM(1)
        sleep(.3)
        FSM(1)
        sleep(.3)
        print("check")
        FSM(1)
        sleep(.3) 
        print("check2")
        FSM(1)
        sleep(.3) 
        FSM(1)  
        sleep(.3)
        FSM(0)  
        sleep(2)
        #Completo
    else:
        print("FSM reanudacion")
        FSM(1)
        sleep(.3)
        '''
        while True:
            dataInmatlab = portCOMx.readline()
            dataInmatlab=str(dataInmatlab)
            print "Esperando REANUDACION: %s" %dataInmatlab
            if dataInmatlab=="P":
                print "reanudacion de mision correcto"
                break
            time.sleep(0.2)
        '''
        FSM(1)
        sleep(.3)
        FSM(1)
        sleep(.3)
        print("check")
        FSM(1)
        sleep(.3) 
        print("check2")
        FSM(1)
        sleep(.3)
        FSM(1)  
        sleep(.3)
        FSM(1)  
        sleep(.3)
        FSM(0)  
        sleep(2)

def main():
    
    pass
      
if __name__ == '__main__':
    main()
