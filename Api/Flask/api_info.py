class WaypointInfo:
	firstHome = None #crearM, conect
	numeroWaypoint = 0 #crearM, waypointsDB
	waypointActual = 0 #telem, detener
	lat = "" #telem, detener
	lon = "" #telem, detener
	remainingWp = [] #guardDes, pausarM, detener
	puntoResume = None #guardDes
	id_waypointsList = [] #guardW, detener, waypointsDB

class SensorInfo:
	idSensorTierraVIS = "" #calibS, guardBla, guardN, detener
	idSensorTierraNIR = "" #calibS, detener
	idSensorVueloVIS = "" #calibS, detener
	idSensorVueloNIR = "" #calibS, detener
	errorCalGlobal = "" #captCon
	errorCapturaGlobal = "" #captCon
	errorBdGlobal = "" #captCon
	sumaCapturado = 0.0 #captCon
	enCapturaContinua = "" #captCon
	sumaBlanco = 0.0 #capBlan

class SpectreInfo:
	espectroBlanco = [] #capBLan, guardB, captV, detener
	espectroNegro = [] #capNe, guardN, captV, detener
	id_espectros = None #guardB, guardN, captV, detener
	counterCal = 2 #hover
	counterH = 0 #hover
