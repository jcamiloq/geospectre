import matplotlib
matplotlib.use('Agg') #para corregir error de threading en el main
import matplotlib.pyplot as plt

import os
from os import path
import numpy as np
import base64
import time
from shutil import copyfile
import datetime
from PIL import Image
import piexif
from fractions import Fraction

from Daos.Conexion import *
from Daos.AccesoDatos.DaoEspectros import DaoEspectros
from Daos.AccesoDatos.Logica.Espectros import Espectros
from file_management import FileManagement
import random

wavelenghtsLista = []
wavecor = []
espectrocor = []
espectrocor2 = []
rel_path = '\\testy\cult2\wavevis.txt'
wav = FileManagement.to_relative(rel_path)
with open(wav, "r") as wavevis:
    for line in wavevis:
        line = line[:-4]
        wavelenghtsLista.append(line)

def to_deg(value, loc):
    """convert decimal coordinates into degrees, munutes and seconds tuple
    Keyword arguments: value is float gps-value, loc is direction list ["S", "N"] or ["W", "E"]
    return: tuple like (25, 13, 48.343 ,'N')
    """
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg =  int(abs_value)
    t1 = (abs_value-deg)*60
    min = int(t1)
    sec = round((t1 - min)* 60, 5)
    return (deg, min, sec, loc_value)

def change_to_rational(number):
    """convert a number to rantional
    Keyword arguments: number
    return: tuple like (1, 2), (numerator, denominator)
    """
    f = Fraction(str(number))
    return (f.numerator, f.denominator)

def set_gps_location(file_name, lat, lng, altitude):
    """Adds GPS position as EXIF metadata
    Keyword arguments:
    file_name -- image file
    lat -- latitude (as float)
    lng -- longitude (as float)
    altitude -- altitude (as float)
    """
    # timeStamp = str(datetime.datetime.now())
    lat_deg = to_deg(lat, ["S", "N"])
    lng_deg = to_deg(lng, ["W", "E"])

    exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
    exiv_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))

    gps_ifd = {
        piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
        piexif.GPSIFD.GPSAltitudeRef: 1,
        piexif.GPSIFD.GPSAltitude: change_to_rational(round(altitude)),
        piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
        piexif.GPSIFD.GPSLatitude: exiv_lat,
        piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
        piexif.GPSIFD.GPSLongitude: exiv_lng,
        # piexif.GPSIFD.GPSTimeStamp: timeStamp,
    }

    exif_dict = {"GPS": gps_ifd}
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, file_name)

def getFilesBlanco(blancoCapturado):
    blancoCapturadoLista=[]
    # guardar txt de la captura
    rel_path = '/tmp/archivoTemporalBlanco.txt'
    filePath = FileManagement.to_relative(rel_path)
    appendFile = open(filePath, 'w')
    for i in range(len(blancoCapturado)):
        appendFile.write(str(blancoCapturado[i]))
    appendFile.close()
    #blanco capturado es un array de strings de tamaño 14336 que al escribirse por
    #líneas en el archivo queda de 1024----14336/14
    # abrir txt capura y guardar en []
    rel_path = '/tmp/archivoTemporalBlanco.txt'
    filePath = FileManagement.to_relative(rel_path)
    with open(filePath, "r") as blancovis:
        for line in blancovis:
            line = line[0:4]
            blancoCapturadoLista.append(line)
    # print(blancoCapturadoLista)
    return blancoCapturadoLista

def getFilesNegro(negroCapturado):
    negroCapturadoLista = []
    # Guardar txt de la captura
    rel_path = '/tmp/archivoTemporalNegro.txt'
    filePath = FileManagement.to_relative(rel_path)
    appendFile = open(filePath, 'w')
    for i in range(len(negroCapturado)):
        appendFile.write(str(negroCapturado[i]))
    appendFile.close()
    # abrir txt de la captura y gyardar en []
    rel_path = '/tmp/archivoTemporalNegro.txt'
    filePath = FileManagement.to_relative(rel_path)
    with open(filePath, "r") as negrovis:
        for line in negrovis:
            line = line[0:4]
            negroCapturadoLista.append(line)
    return negroCapturadoLista

def getFilesVuelo(vueloCapturado):
    vueloCapturadoLista=[]
    # guardar txt de la captura
    rel_path = '/tmp/archivoTemporalVuelo.txt'
    filePath = FileManagement.to_relative(rel_path)
    appendFile = open(filePath, 'w')
    for i in range(len(vueloCapturado)):
        appendFile.write(str(vueloCapturado[i]))
    appendFile.close()
    with open(filePath, "r") as blancovis:
        for line in blancovis:
            line = line[0:4]
            vueloCapturadoLista.append(line)
    return vueloCapturadoLista

def makeImageW(ejeYMakeImage):
    global wavelenghtsLista
    ejeXMakeImage = wavelenghtsLista
    print(len(ejeXMakeImage))
    print(len(ejeYMakeImage))
    # print(ejeXMakeImage)
    ejeY = np.array(ejeYMakeImage, dtype=np.float32)
    ejeX = np.array(ejeXMakeImage, dtype=np.float32)

    plt.figure(1)
    ax = plt.subplot(111)
    plt.plot(ejeX, ejeY)#, label='Negro')
    ax.set_ylim(min(ejeY), max(ejeY))
    plt.legend()
    rutaImagen= "/tmp/imagenEspectroW.png"
    filePath = FileManagement.to_relative(rutaImagen)
    resultadoMakeImage= plt.savefig(filePath, format="png")
    plt.cla()
    plt.clf()
    plt.close()
    return resultadoMakeImage

def makeImageD(ejeYMakeImage):
    global wavelenghtsLista
    ejeXMakeImage = wavelenghtsLista
    print(len(ejeXMakeImage))
    print(len(ejeYMakeImage))
    # print(ejeXMakeImage)
    ejeY = np.array(ejeYMakeImage, dtype=np.float32)
    ejeX = np.array(ejeXMakeImage, dtype=np.float32)

    plt.figure(1)
    ax = plt.subplot(111)
    plt.plot(ejeX, ejeY)#, label='Negro')
    ax.set_ylim(min(ejeY), max(ejeY))
    plt.legend()

    rutaImagen= "/tmp/imagenEspectroD.png"
    filePath = FileManagement.to_relative(rutaImagen)
    
    resultadoMakeImage= plt.savefig(filePath, format="png")
    plt.cla()
    plt.clf()
    plt.close()
    return resultadoMakeImage

def makeImageC(ejeYMakeImage, j):
    ejeY = ""
    ejeX = ""
    espectrocor = []
    wavecor = []
    # global wavelenghtsLista
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
    rutaImagen= "/tmp/imagenEspectroC%s.png" %(str(datetime.datetime.now())[18:19])
    filePath = FileManagement.to_relative(rutaImagen)
    resultadoMakeImage= plt.savefig(filePath, format="png")
    plt.cla()
    plt.clf()
    plt.close()
    return filePath

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
    filePath = FileManagement.to_relative(rel_path)
    piexif.transplant('/testy/base.jpg', rutaImagen)
    set_gps_location(rutaImagen, lat, lon, alt)
    return resultadoMakeImage

def generate(lista, rutaz, lat, lon, alt, veces=1):
    for i in range(0, veces):
        ruta = rutaz +"%s.txt" %(i)
        rutaImagen = rutaz+"%s.jpg" %(i)
        appendFile = open(ruta, 'w')
        appendFile.write("")
        appendFile.close()
        d = []
        for j in range(0, len(wavelenghtsLista)):
            # suma = random.randint(0,1)
            # x = random.uniform(0, 0.5)
            # if suma == 1:
            #     d.append(float(lista[j])+x)
            # else:
            d.append(float(lista[j]))
            appendFile = open(ruta, 'a')
            appendFile.write(str(d[j]) + "\n")
            appendFile.close()

        makeImageG(d, rutaImagen, lat, lon, alt)
    return d

def calcularEspectro(ids):
    global wavelenghtsLista

    # stringDark= """SELECT dark FROM espectros WHERE id='%s';""" %(ids)
    # stringCapturado= """SELECT dark FROM espectros WHERE id='%s';""" %(ids)
    # stringWhite= """SELECT dark FROM espectros WHERE id='%s';""" %(ids)
    
    medida= []
    blanco= []
    negro= []
    negrolist= []
    blancolist= []
    suma= []
    resta= []
    espectroCal= []
    espectrocor= []
    wavecor= []

    conn = conexion()
    daoEspectros = DaoEspectros(conn)
    espectro = daoEspectros.getEspectros(ids)
    blanco = espectro.white
    negro = espectro.dark
    medida = espectro.capturado
    

    # conn = psycopg2.connect(host="localhost", port = 5432, database="geospectre", user="postgres", password="kmiikiintero050K")
    # cur = conn.cursor()
    # cur.execute(stringDark)
    # negro = cur.fetchone()[0][0]
    # cur.execute(stringWhite)
    # blanco = cur.fetchone()[0][0]
    # cur.execute(stringCapturado)
    # medida = cur.fetchone()[0][0]
    # cur.close()
    # conn.close()

    for i in range(0, len(wavelenghtsLista)):
        suma.append(float(blanco[i]) - float(negro[i]))
    # print(str(resta))
    for i in range(0, len(wavelenghtsLista)):
        resta.append(float(medida[i]) - float(negro[i]))
    for i in range(0, len(wavelenghtsLista)):
        if suma[i] == 0:
            suma[i] = 1
        espectroCal.append((float(resta[i]) / float(suma[i]))*100)

    espectro.resultado = espectroCal
    espectro = daoEspectros.actualizarEspectros(espectro)
    conn.close()
    return espectroCal