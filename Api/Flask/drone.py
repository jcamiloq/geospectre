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
sitl = None
flagReanudar = "F"
flagDetener = "F"
flagPausar = "F"
remainingWp = []
capturando = False
necesitaCalibrar = False
counterhover = 0
flagTerminar = ""
hover = False
senalCaptura = ""

COM = 'COM4'
nextwaypoint=1
Wp_reanudacion=0
estado='c'
alertaProximidad = 0
# OPCIONES DE LLAMADA POR COMANDO
parser = argparse.ArgumentParser()
parser.add_argument("--connect", dest="conect",help="Puerto por el que se desea conectar el UAV Ej: Com7")
        #asigna a parser cada elemento en "dest"
parser.add_argument("--reanudar",dest="reanude",help="Valores necesarios para realizar la reanudacion con el siguiente formato : [LATITUD,LONGITUD,WP_REANUDACION]")

def download_mission():
    """
    Downloads the current mission and returns it in a list.
    It is used in save_mission() to get the file information to save.
    """
    print(" Download mission from vehicle")
    missionlist=[]
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    for cmd in cmds:
        missionlist.append(cmd)
    return missionlist

def save_mission():
    aFileName = "D:/Tesis/Code/Api/Flask/tmp/misioncmd.txt"
    print("\nSave mission from Vehicle to file: %s" % aFileName)    
    #Download mission from vehicle
    missionlist = download_mission()
    output = ""
    #Add file-format information
    for cmd in missionlist:
        commandline="%s,%s\n" % (cmd.x,cmd.y)
        output+=commandline
    with open(aFileName, 'w') as file_:
        print(" Write mission to file")
        file_.write(output)

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

def initCon(alturaR, velocidadR, lat=None, lon=None):
    global altura, velocidad, vehicle, sitl, flagPausaSinc, flagPausa, flagTerminar
    flagTerminar = ""
    flagPausaSinc = True
    flagPausa = True
    altura = alturaR
    velocidad = velocidadR
    results = parser.parse_args()           #array
    connection_string=results.conect        #Com
    sitl=None
    ultimaPosicion=results.reanude
    if flagPausar != "T":
        #global flag_reanudado                      #If not: flag de reanudación
        print ("START MISION") 
        flag_reanudado=0
    if not connection_string:                           #cuando no hay COM simulación
        print ("Empieza con simulador") 
        import dronekit_sitl
        sitl = dronekit_sitl.start_default(lat, lon)
        connection_string = sitl.connection_string()
        print('Connecting to vehicle on: %s' % connection_string)
        vehicle = connect(connection_string, wait_ready=True)
        vehicle.wait_ready('autopilot_version')
    else:
        sitl.stop()
        sitl = None
        vehicle = None
        initCon()
    FH = str(vehicle.location.global_frame.lat)+","+str(vehicle.location.global_frame.lon)
    return FH

def telem():
    global vehicle, alertaProximidad, flagMision
    # flagDetener = flagDetenerT
    # flagReanudar = flagReanudarT
    # flagPausar = flagPausarT
    if vehicle:
        # senalCaptura = ""
        if vehicle.location.global_relative_frame.alt<altura*0.95:
            flagMision = "F"
        else:
            flagMision = "T"
        # if vehicle.commands.next:                           #Verifica si se han subido comandos
        #     if vehicle.commands.next <= len(waypoints):   #Verifica si se ha llegado al penultimo comando
        #         d = distance_to_current_waypoint()
        #         if d <= 0.5 and alertaProximidad != 1:        #Verifica si se ha llegado al punto de captura
        #             sleep(0.5)
        #             senalCaptura = "G"                      
        #             alertaProximidad = 1
        #         if alertaProximidad == 1 and d >= 1:          #Verifica si se salió del punto de captura
        #             alertaProximidad = 0
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
        if sitl is None:
            dronConectado = "F"
        else:
            dronConectado = "T"
    print(senalCaptura + ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    dicTelem = {
        "posicionDron": vehicle.location.global_relative_frame,
        "actitudDron": vehicle.attitude,
        "velocidadDron": vehicle.airspeed,
        "bateriaDron": vehicle.battery,
        "senalCaptura": senalCaptura,
        "waypointActual": vehicle.commands.next,
        "armado": armado,
        "batteryLevel": vehicle.battery.level,
        "dronConectado": dronConectado,
        "capturando": capturando,
        "flagTerminar": flagTerminar
    }
    return dicTelem

def estadoWaypoints(entrada): #Recepción de Waypoints
    global waypoints, estado
    waypoints = []
    wpLat = []
    wpLon = []
    print("Estado Waypoints")
    
    # estadoReturn = "Estado Inicial"
    for i in range(0, len(entrada)):
        waypoints.append(entrada[i])
        points=entrada[i].split(",")
        wpLat.append(float(points[0]))
        wpLon.append(float(points[1]))
    print(waypoints)
    añadirMision(waypoints, altura)    
    estado = 0
    print("Transicion hacia 0...")
    # return estadoReturn          
         
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
        
def estadoDespegue(firstH): #Despegue y seteo de velocidad
    global estado, flag_reanudado
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", firstH)
    firstHome = firstH
    print("Taking off!")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.simple_takeoff(altura) # Take off to target altitude
    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.simple_takeoff will execute immediately).
    
    while True:
        print(" Altitude despegue: ", vehicle.location.global_relative_frame.alt)
        #Break and return from function just below target altitude.        
        if vehicle.location.global_relative_frame.alt>=altura*0.95: 
            print("Reached target altitude")
            Wpoint=0
            break
        time.sleep(1)
        print("terminó despegue")

    print("Set default/target airspeed to %s" %velocidad)
    vehicle.airspeed = velocidad
    vehicle.commands.next=0

    vehicle.mode = VehicleMode("AUTO")
    t3 =threading.Thread(target = mision, args= (firstHome,))
    # t3.setDaemon(True)
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

def capturarVueloDrone(etapa):
    global capturando
    if etapa == "A":
        capturando = True
    if etapa == "B":
        capturando = False

def mision(firstHome):
    global vehicle, remainingWp, flagPausar, flagTerminar, senalCaptura
    remainingWp = []
    listaComandos = []
    previousWaypoint = 1
    senalCaptura = ""
    while True:
        while capturando:
            print("capturando en misión")
            sleep(2)
            if flagPausar == "T":
                break
        if necesitaCalibrar:
            print("Recalibrando Sensores")
            vehicle.mode = VehicleMode("GUIDED")
            sleep(2)
            save_mission()
            waypointActual = vehicle.commands.next -2
            with open("D:/Tesis/Code/Api/Flask/tmp/misioncmd.txt", "r") as m:
                for line in m:
                    listaComandos.append(line)
            point = listaComandos[waypointActual].split(",")
            point = LocationGlobalRelative(float(point[0]),float(point[1][0:-2]), altura)
            # while vehicle.mode.name != "GUIDED":
            #     vehicle.mode = VehicleMode("GUIDED")
            #     print("going to guided")
            #     sleep(0.5)
            while(distance_to_someone_waypoint(point.lat,point.lon)>=0.5):
                print("going back")
                vehicle.simple_goto(point)
                sleep(1)
            while necesitaCalibrar:
                sleep(1)
                if flagPausar == "T":
                    break
            while vehicle.mode.name != "AUTO" and flagPausar != "T":
                vehicle.mode = VehicleMode("AUTO")
                print("going to AUTO")
                sleep(0.5)
        while hover:
            print("Hovering")
            vehicle.mode = VehicleMode("GUIDED")
            point = LocationGlobalRelative(float(str(vehicle.location.global_relative_frame.lat)),float(str(vehicle.location.global_relative_frame.lon)), altura)
            if(distance_to_someone_waypoint(point.lat,point.lon)>=0.5):
                vehicle.simple_goto(point)
            sleep(1)
            if flagPausar == "T":
                break
        vehicle.mode = VehicleMode("AUTO")
        nextwaypoint=vehicle.commands.next
        if nextwaypoint > previousWaypoint:
            previousWaypoint = nextwaypoint
            senalCaptura = "G"
            sleep(2)
            # tiempoInicio = time.time()
            # tiempoFinal = 0
            # while tiempoFinal<1:
            #     senalCaptura = "G"
            #     tiempoFinal = time.time()-tiempoInicio
            
            while vehicle.mode.name != "AUTO":
                vehicle.mode = VehicleMode("AUTO")
                print("going to AUTO")
                sleep(0.3)
            senalCaptura = ""

        print("worker ciclo: " + str(nextwaypoint))
        print('Distance to waypoint (%s): %s' % (nextwaypoint, distance_to_current_waypoint()))
        # print(str(len(wp)))
        # print(remainingWp)
        # print(str(nextwaypoint)+ "=" + str(len(waypoints)+2) +"?")
        print("NecCal"+ str(necesitaCalibrar))
        
        if flagPausar == "T":
            print("llegó1111111111111111111111111111111111111111111111111111")
            # print(waypoints)
            # print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            # print(nextwaypoint)
            longitud = len(waypoints)-nextwaypoint+1
            # print(str(longitud))
            for i in range(0, longitud):
                remainingWp.append(waypoints[nextwaypoint+i-1])
            print(remainingWp)
            point = LocationGlobalRelative(float(str(vehicle.location.global_relative_frame.lat)),float(str(vehicle.location.global_relative_frame.lon)), altura)
            # while vehicle.mode.name != "GUIDED":
            vehicle.mode = VehicleMode("GUIDED")
            print("going to guided in mission")
            sleep(0.5)
            # if(distance_to_someone_waypoint(point.lat,point.lon)>=0.5):
            #     vehicle.simple_goto(point)
            #     sleep(1)
            break;
        if (nextwaypoint==int(len(waypoints))+1): #Dummy waypoint - as soon as we reach waypoint 4 this is true and we exit.
            print("Exit 'standard' mission when start heading to final waypoint")
            flagTerminar = "T"
            break;
        time.sleep(0.5)
    if flagPausar != "T":
        estadoRTL(firstHome)

def pausa():
    global vehicle, sitl, flagPausar, flagPausa
    if flagPausa:
        flagPausa = False
        while vehicle.mode.name != "GUIDED":
            vehicle.mode = VehicleMode("GUIDED")
            print("going to guided")
            sleep(0.5)
        pointy = LocationGlobalRelative(float(str(vehicle.home_location.lat)),float(str(vehicle.home_location.lon)), altura)
        vehicle.simple_goto(pointy)
        while True:
            print("Yendo a punto de pausa...")
            Distancia=distance_to_someone_waypoint(vehicle.home_location.lat,vehicle.home_location.lon)
            print("Distancia a pausa: %s" %Distancia)
            # print("altitud de retorno: ", vehicle.location.global_relative_frame.alt)
            if((Distancia<=1)):
                print("EN CASA!!!!")
                break;
            time.sleep(0.5)
        vehicle.mode = VehicleMode("LAND")
        while True:
            print("altitud de retorno: ", vehicle.location.global_relative_frame.alt)
            #Break and return from function just below target altitude.        
            if vehicle.location.global_relative_frame.alt<=1: 
                print("Altitud de descenso alcanzada")
                Wpoint=0
                break;
            time.sleep(0.5)

        vehicle.armed = False
        while vehicle.armed:
            print(" Waiting for disarming..")
            print("El vehiculo armed(true) o disarmed (false): %s" %vehicle.armed)
            time.sleep(1)
        # cmdsR = vehicle.commands
        # cmdsR.download()
        # cmdsR.wait_ready() # wait until download is complete.
        print("Close vehicle object")
        vehicle.close()
        # Shut down simulator if it was started.
        if sitl is not None:
            sitl.stop()
            sitl = None
        print("VEHICULO PAUSADO Y EN TIERRA pausa")
        flagPausar = "F"

def hoverDrone(necesitaCalibrarFlag):
    global necesitaCalibrar, hover
    print("Rutina de hover" + str(necesitaCalibrarFlag))
    if necesitaCalibrarFlag == "T":
        necesitaCalibrar = True
    if necesitaCalibrarFlag == "F":
        necesitaCalibrar = False
        hover = False
    if necesitaCalibrarFlag == "H":
        hover = not hover
        print(hover)

def pausaSinc(puntoPausa):
    global vehicle, sitl, flagPausar, flagPausaSinc
    if flagPausaSinc:
        flagPausaSinc = False
        while vehicle.mode.name != "GUIDED":
            vehicle.mode = VehicleMode("GUIDED")
            print("going to guided")
            sleep(0.5)
        print(puntoPausa)
        puntoPausa = puntoPausa.split(",")
        vehicle.mode = VehicleMode("GUIDED")

        pointy = LocationGlobalRelative(float(str(puntoPausa[0])),float(str(puntoPausa[1])), altura)
        vehicle.simple_goto(pointy)
        while True:
            print("Yendo a punto de pausa sinc...")
            Distancia=distance_to_someone_waypoint(float(puntoPausa[0]),float(puntoPausa[1]))
            print("Distancia a punto de pausa sinc: %s" %Distancia)
            # print("altitud de retorno: ", vehicle.location.global_relative_frame.alt)
            if((Distancia<=1)):
                print("EN PUNTO DE PAUSA!!!!")
                break;
            time.sleep(0.5)
        vehicle.mode = VehicleMode("LAND")
        while True:
            print("altitud de retorno sinc: ", vehicle.location.global_relative_frame.alt)
            #Break and return from function just below target altitude.        
            if vehicle.location.global_relative_frame.alt<=1: 
                print("Altitud de descenso alcanzada")
                Wpoint=0
                break;
            time.sleep(0.5)

        vehicle.armed = False
        while vehicle.armed:
            print(" Waiting for disarming..")
            print("El vehiculo armed(true) o disarmed (false): %s" %vehicle.armed)
            time.sleep(1)
        # cmdsR = vehicle.commands
        # cmdsR.download()
        # cmdsR.wait_ready() # wait until download is complete.
        print("Close vehicle object")
        vehicle.close()
        # Shut down simulator if it was started.
        if sitl is not None:
            sitl.stop()
            sitl = None
        print("VEHICULO PAUSADO Y EN TIERRA pausaSinc")
        flagPausar = "F"

def estadoPause(entrada, flagPausarT): # Establece el wp mas cercano y lo guarda como punto de reanudación, land, disarm
    global estado 
    global flagPausar, cmdsR
    flagPausar = flagPausarT
    print("Estado p " + flagPausar)
    # archivo_log=abrir_log("Pausa_monitoreo.txt")
    # guardar_log(archivo_log,str(distance_to_someone_waypoint(vehicle.home_location.lat,vehicle.home_location.lon)),"PAUSA")
    # cerrar_log(archivo_log)
    t4 =threading.Thread(target = pausa)
    t4.setDaemon(True)
    t4.start()
    sleep(0.4)
    print(remainingWp)
    return remainingWp

def estadoResume(entrada, firstHome, lat=None, lon=None): #Ir a punto de reanudación, ir a estadomision, verificar pausa y rth
    print("REANUDANDO MISIÓN")
    initCon(altura, velocidad, lat, lon)
    sleep(0.2)
    estadoWaypoints(entrada)
    sleep(0.2)
    estadoArmado(1)
    sleep(0.2)
    estadoDespegue(firstHome)
  
def estadoPauseSinc(entrada, waypointsDescanso): # guarda punto de reanudación
    global estado, waypointsD, flagPausar, home
    print("Estado pausa sinc")
    puntoPausa = waypointsDescanso
    point = []
    if entrada == 2:
        flagPausar = "T"
        distanceA = 10000
        home = str(vehicle.home_location.lat)+","+str(vehicle.home_location.lon)
        puntoPausa.append(str(vehicle.home_location.lat)+","+str(vehicle.home_location.lon))
        for i in range(0,len(puntoPausa)):
            puntoPausaA = puntoPausa[i].split(",")
            distanceB = distance_to_someone_waypoint(float(puntoPausaA[0]),float(puntoPausaA[1]))
            if distanceB <= distanceA:
                distanceA = distanceB
                point = puntoPausa[i]
        t5 =threading.Thread(target = pausaSinc, args= (point,))
        t5.setDaemon(True)
        t5.start()
        sleep(0.4)
    else:
        home = ""
    print(remainingWp)
    return remainingWp, point, home

def estadoRTL(firstH): #Return to launch, land, disarm, stop sitl, viene aquí si se presiona boton RTH en GUI
    global estado, sitl, vehicle 
    # archivo_log=abrir_log("RTL_monitoreo.txt")
    # guardar_log(archivo_log,str(distance_to_someone_waypoint(vehicle.home_location.lat,vehicle.home_location.lon)),"RTL")
    # cerrar_log(archivo_log)
    print("Returning to Launch")
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", firstH)
    firstHome = firstH.split(",")
    
    #vehicle.mode = VehicleMode("RTL")
    while vehicle.mode.name != "GUIDED":
        vehicle.mode = VehicleMode("GUIDED")
        print("going to guided")
        sleep(0.5)
    
    pointy = LocationGlobalRelative(float(firstHome[0]), float(firstHome[1]), altura)
    vehicle.simple_goto(pointy)
    while True:
        print("Yendo a casa...")
        Distancia=distance_to_someone_waypoint(pointy.lat,pointy.lon)
        print("Distancia a casa: %s" %Distancia)
        # print("altitud de retorno: ", vehicle.location.global_relative_frame.alt)
        if((Distancia<=2)):
            print("EN CASA!!!!")
            break;
        time.sleep(0.5)
    
    vehicle.mode = VehicleMode("LAND")
    while True:
        # print("Distancia a casa: %s" %Distancia)
        print("altitud de retorno: ", vehicle.location.global_relative_frame.alt)
        #Break and return from function just below target altitude.        
        if vehicle.location.global_relative_frame.alt<=0.5: 
            print("Altitud de descenso alcanzada")
            Wpoint=0
            break
        time.sleep(0.5)
            
    time.sleep(2)       
    print("Global Location: %s" % vehicle.location.global_frame) 
    #Close vehicle object before exiting script
    # global fin
    # global RTH_fin
    # if band_RTH!=1:
    #     fin=1
    # else:
    #     RTH_fin=1
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
        sitl = None
    '''
    Transiciones 
    ''' 
    estado = 'f' 
    print("Transicion hacia f...") 

def estadoCancel(entrada): #Aterriza, disarm
    global estado, vehicle, sitl, remainingWp, waypoints, alertaProximidad, altura, velocidad
    # archivo_log=abrir_log("Cancel_monitoreo.txt")
    # guardar_log(archivo_log,str(distance_to_someone_waypoint(vehicle.home_location.lat,vehicle.home_location.lon)),"CANCELA")
    # cerrar_log(archivo_log)
    print("Estado Cancel")
    if sitl is not None and vehicle is not None:
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
    vehicle = None
    sitl = None
    remainingWp = []
    waypoints = []
    alertaProximidad = 0
    altura = 0
    velocidad = 0
    print("CANCELACION REALIZADA Y EN TIERRA")

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

def main():
    pass
      
if __name__ == '__main__':
    main()
