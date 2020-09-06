import datetime
import os
from PIL import Image
from GPSPhoto import gpsphoto
from PIL.ExifTags import TAGS, GPSTAGS
import piexif
from fractions import Fraction
import random
from spectreUtilities import *
# for x in range(10):
#   print (random.uniform(0.3,1.3))
wavelenghtsLista = []
wavecor = []
espectrocor = []
espectrocor2 = []
num2 = "cult2"
path = ("D:/subtext/splitTest0/Quieto 1 feb/%s" % (num2))
wav = ("%s/wavevis.txt" % (path))
with open(wav, "r") as wavevis:
    for line in wavevis:
        line = line[:-4]
        wavelenghtsLista.append(line)
# rutaImagen = "D:/Tesis/Api/Flask/testy/pruebaEspectros.jpg"
def generate(lista, rutaz, lat, lon, alt, veces=1):
	for i in range(0, veces):
		ruta = rutaz +"%s.txt" %(i)
		rutaImagen = rutaz+"%s.jpg" %(i)
		appendFile = open(ruta, 'w')
		appendFile.write("")
		appendFile.close()
		d = []
		for j in range(0, len(wavelenghtsLista)):
			# print(j)
			suma = random.randint(0,1)
			# print("suma = ", suma)
			x = random.uniform(0, 0.0001)
			# print(x)
			if suma == 1:
				d.append(float(lista[j])+x)
				# d.append("\n")
			else:
				d.append(float(lista[j])-x)
				# d.append("\n")
			# print(d[j], lista[j], suma, x)
			appendFile = open(ruta, 'a')
			appendFile.write(str(d[j]) + "\n")
			appendFile.close()

		makeImageG(d, rutaImagen, lat, lon, alt)
	return d
def makeImageG(ejeYMakeImage, rutaImagen, lat, lon, alt):
    # global wavelenghtsLista
    ejeY = ""
    ejeX = ""
    espectrocor = []
    wavecor = []
    
    ejeXMakeImage = wavelenghtsLista
    ejeY = np.array(ejeYMakeImage, dtype=np.float32)
    ejeX = np.array(ejeXMakeImage, dtype=np.float32)

    for i in range(230, 890):
        espectrocor.append(ejeY[i])
    for i in range(230, 890):
        wavecor.append(ejeX[i])

    plt.figure(1)
    ax = plt.subplot(111)
    plt.plot(wavecor, espectrocor)#, label='Negro')
    ax.set_ylim(min(espectrocor), max(espectrocor))

    plt.legend()
    # rutaImagen= "D:/Tesis/Api/Flask/imagenEspectroC%s.png" %(str(j))
    resultadoMakeImage= plt.savefig(rutaImagen, format="jpg")
    plt.cla()
    plt.clf()
    plt.close()

    piexif.transplant('D:/Tesis/Api/Flask/base.jpg', rutaImagen)
    set_gps_location(rutaImagen, lat, lon, alt)
    return resultadoMakeImage


inten = []
intensitiesFlask = []
x = "D:/subtext/splitTest0/Quieto 1 feb/inten1.txt"
with open(x, 'r') as f:
    intensitiesFlask = f.read()
inten = intensitiesFlask.split("\n")
# print(inten)
d = []
i= 1


generate(inten, "D:/Tesis/Api/Flask/testy/pruebainten1", 3.3727414349040905, -76.53012274101879, 5)

# img = Image.open('D:/Tesis/Api/Flask/Usuario(camilo)Mision(wjqeqwe)Waypoint(0).png')
# img_rgb = img.convert("RGB")
# img_rgb.save('D:/Tesis/Api/Flask/colors.jpg')
# piexif.transplant('D:/Tesis/Api/Flask/base.jpg', 'D:/Tesis/Api/Flask/colors.jpg')

# def to_deg(value, loc):
#     """convert decimal coordinates into degrees, munutes and seconds tuple
#     Keyword arguments: value is float gps-value, loc is direction list ["S", "N"] or ["W", "E"]
#     return: tuple like (25, 13, 48.343 ,'N')
#     """
#     if value < 0:
#         loc_value = loc[0]
#     elif value > 0:
#         loc_value = loc[1]
#     else:
#         loc_value = ""
#     abs_value = abs(value)
#     deg =  int(abs_value)
#     t1 = (abs_value-deg)*60
#     min = int(t1)
#     sec = round((t1 - min)* 60, 5)
#     return (deg, min, sec, loc_value)

# def change_to_rational(number):
#     """convert a number to rantional
#     Keyword arguments: number
#     return: tuple like (1, 2), (numerator, denominator)
#     """
#     f = Fraction(str(number))
#     return (f.numerator, f.denominator)

# def set_gps_location(file_name, lat, lng, altitude):
#     """Adds GPS position as EXIF metadata
#     Keyword arguments:
#     file_name -- image file
#     lat -- latitude (as float)
#     lng -- longitude (as float)
#     altitude -- altitude (as float)
#     """
#     # timeStamp = str(datetime.datetime.now())
#     lat_deg = to_deg(lat, ["S", "N"])
#     lng_deg = to_deg(lng, ["W", "E"])

#     exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
#     exiv_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))

#     gps_ifd = {
#         piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
#         piexif.GPSIFD.GPSAltitudeRef: 1,
#         piexif.GPSIFD.GPSAltitude: change_to_rational(round(altitude)),
#         piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
#         piexif.GPSIFD.GPSLatitude: exiv_lat,
#         piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
#         piexif.GPSIFD.GPSLongitude: exiv_lng,
#         # piexif.GPSIFD.GPSTimeStamp: timeStamp,
#     }

#     exif_dict = {"GPS": gps_ifd}
#     exif_bytes = piexif.dump(exif_dict)
#     piexif.insert(exif_bytes, file_name)
# timeStamp = datetime.datetime.now().strftime("%H:%M:%S")
# set_gps_location('D:/Tesis/Api/Flask/colors.jpg', 3.372928734276766,-76.53028658686546, 5)




# ruta = "D:/Tesis"
# x = str(datetime.datetime.now())[11:19]
# print(x)
# nombre = "1"
# waypoint = "1"
# ruta += "/Mision("+nombre+")"+ "Waypoint("+waypoint+")"+x+".png"
# print(ruta)
# 
# 
# 
# # ----------------verficacion en el while de mision----------
# if band_pause==1:
# 	print("Exit 'standard' mission for PAUSED button")
# 	ActualWp=nextwaypoint-1
# 	estado = 'p'
# 	print("Transicion hacia p...")
# 	break;
# if band_RTH==1:
# 	print("Exit 'standard' mission for RTH button")
# 	estado = 3 
# 	print("Transicion hacia 3...")
# 	break;
# if band_cancel==1:
# 	print("Exit 'standard' mission for CANCEL button")
# 	estado= 'h'
# 	print("Transicion hacia h...")
# 	break;
# if float(Voltaje)<=9.0 and nextwaypoint<int(len(DataWps)+1):
# 	print("Exit 'standard' mission for BATTERY")
# 	ActualWp=nextwaypoint-1
# 	band_battery=1
# 	estado = 'p'
# 	print("Transicion hacia p...")
# 	break;
# if (nextwaypoint==int(len(DataWps)+1)) and (distance_to_current_waypoint()<=1): #Dummy waypoint - as soon as we reach waypoint 4 this is true and we exit.
# 	print("Exit 'standard' mission when start heading to FINAL waypoint ")
# 	bandFoto=1
# 	estado = 2 
# 	print("Transicion hacia 2...")
# 	break;
# # ------------------------PROTOCOLO PAUSA-----------------------
# # toda la función pausa pero guardar waypoint de reanudación
# # probar si sigue los comandos restantes despues de la pausa


# # .-----------------------PROTOCOLO REANUDE---------------------------
# parser.add_argument("--reanudar",dest="reanude",help="Valores necesarios para realizar la reanudacion con el siguiente formato : [LATITUD,LONGITUD,WP_REANUDACION]")

# results = parser.parse_args()			#array
# connection_string=results.conect 		#Com
# sitl=None
# Ulti_GPS=results.reanude 

# pos=Ulti_GPS 						#ULTI GPS: Posición (POS)
# Posicion_reanudar=pos.split("/")
# lati_r=Posicion_reanudar[0]
# lati_r=lati_r[1:]
# lati_r=float(lati_r)
# longi_r=float(Posicion_reanudar[1])

# vehicle.mode = VehicleMode("GUIDED")
# print("Going towards RESUME point  ...")
# pointy = LocationGlobalRelative(lati_r, longi_r, altura)
# vehicle.simple_goto(pointy)
# # while resume
# # 
# # 

