from multiprocessing import Queue
# import seabreeze.spectrometers as sb
import numpy as np
import io
import time
from time import sleep
# import STS_functions as sts  # This script was created in order to ease the readability of the developed script
import time
import serial
import argparse

from flask import Flask, send_file
import requests
#from flask_restful import Resource, Api
global spec_NIR_Tierra, spec_VIS_Tierra, wavelengths_NIR_Tierra, intensities_NIR_Tierra, wavelengths_VIS_Tierra, intensities_VIS_Tierra, queueTierra, outTierra
# global sensorTierraVIS, sensorTierraNIR, sensorVueloVIS, sensorVueloVIS, tiempoIntegracion, numeroCapturas

# sensorTierraVIS="1"
blanco = []

def calibrarSensores(sensorVIS, sensorNIR, tiempoIntegracion, numeroCapturas):
    print("0")
    spec_NIR = sts.setup_Spec(sb.Spectrometer.from_serial_number(sensorNIR), int(tiempoIntegracion)*1000, numeroCapturas)  # Serial, integration time (us), scans per avg. #DOUBLE
    spec_VIS = sts.setup_Spec(sb.Spectrometer.from_serial_number(sensorVIS), int(tiempoIntegracion)*1000, numeroCapturas)  # DOUBLE #SINGLE
    #out = []
    init_wl_VIS = np.array(spec_VIS.wavelengths())[0]  # The NIR wavelengths are ~ 650-1100 nm  #SINGLE      #DOUBLE
    init_wl_NIR = np.array(spec_NIR.wavelengths())[0]  # The VIS wavelengths are ~ 350-800 nm             #DOUBLE
    #init_wl_NIR = np.array(spec_VIS.wavelengths())[0]  # SINGLE
    #print("Init VIS Wavelength: {}, Init NIR Wavelength: {}".format(init_wl_VIS, init_wl_NIR))
    queue = Queue(maxsize=2)  # This queue receives the data from both the NIR and VIS spectra
    return spec_NIR, spec_VIS, queue
def read_NIR(spec_NIR, queue):
    spectrum_NIR = np.array(spec_NIR.spectrum())
    queue.put(spectrum_NIR)
def read_VIS(spec_VIS, queue):
    spectrum_VIS = np.array(spec_VIS.spectrum())
    queue.put(spectrum_VIS)
def w_file_NIR(arr1, arr2):
    global file_counter_NIR
    title = ('Captura número ' + str(file_counter_NIR))
    appendFile = open('/home/pi/Desktop/Data/DataNIR%s.txt' % (datanum), 'a')
    # appendFile.write('\n')
    appendFile.write('\n' + title + '\n')
    # appendFile.write('\n')
    saveFile.close()

    file_counter_NIR = file_counter_NIR + 1

    for i in range(len(arr1)):
        appendFile = open('/home/pi/Desktop/Data/DataNIR%s.txt' % (datanum), 'a')
        # appendFile.write('\n')
        appendFile.write('\n' + str(arr1[i]) + " " + str(arr2[i]))
        appendFile.close()
def w_file_VIS(arr1, arr2):
    global file_counter_VIS
    title = ('Captura número ' + str(file_counter_VIS))
    appendFile = open('/home/pi/Desktop/Data/DataVIS%s.txt' % (datanum), 'a')
    # appendFile.write('\n')
    appendFile.write('\n' + title + '\n')
    # appendFile.write('\n')
    saveFile.close()

    file_counter_VIS = file_counter_VIS + 1

    for i in range(len(arr1)):
        appendFile = open('/home/pi/Desktop/Data/DataVIS%s.txt' % (datanum), 'a')
        # appendFile.write('\n')
        appendFile.write('\n' + str(arr1[i]) + " " + str(arr2[i]))
        appendFile.close()

app = Flask(__name__)
# api = Api(app)

@app.route('/crearArchivos', methods=['GET'])										#Añade el recurso
def crearArchivos():
    x = "D:/Tesis/Api/Flask/3vis.txt"
    with open(x, 'r') as f:
        file = f.read() #rds es a 21.88m-------11.28cm es a 0.000001 coords
    return send_file("3vis.txt")
@app.route('/crearArchivo/<hole>/<a>/<b>/<c>', methods=['GET'])                                       #Añade el recurso
def crearArchivo(hole, a, b, c):
    return hole+a+b+c
    
@app.route('/sensoresTierra/<sensorVISflask>/<sensorNIRflask>/<tiempoIntegracion>/<numeroCapturas>/<calibrar>', methods=['GET'])										#Añade el recurso
def sensoresTierra(sensorVISflask, sensorNIRflask, tiempoIntegracion, numeroCapturas, calibrar):
    try:
        if calibrar == "C":
            print("capturando")
            start_time_A = time.time()
            sts.runInParallel(read_VIS(b, c), read_NIR(a, c))                                                             #DOUBLE
            #sts.runInParallel(read_VIS)  # SINGLE
            # sts.runInParallel(read_VIS)
            if queueTierra.full():  # If both the NIR and VIS spectra have been acquired successfully
                # print(queue.qsize()) # The queue size should be 2
                # wavelengths_NIR, intensities_NIR, wavelengths_VIS, intensities_VIS = sts.assign_spectra(queue, init_wl_NIR, init_wl_VIS) #DOUBLE
                wavelengths_NIR_Tierra, intensities_NIR_Tierra, wavelengths_VIS_Tierra, intensities_VIS_Tierra = sts.assign_spectra(queue, init_wl_NIR, init_wl_VIS)  # SINGLE
            else:
                print("Queue not full")
            end_time_A = time.time()
            duration = end_time_A - start_time_A
            print("Acquisition for {} seconds".format(duration))
            duration = str(duration)
            success = "Success"
            pass
        else:
            a, b, c = calibrarSensores(sensorVISflask, sensorNIRflask, tiempoIntegracion, numeroCapturas)
            pass
        pass
    except Exception as errorCalibrarSensoresTierra:
        success = "Fail Calibrar Sensores Tierra"
        raise errorCalibrarSensoresTierra
    return sensorTierraVIS#+sensorTierraNIRl+tiempoIntegracionl+numeroCapturasl+success
# @app.route('/calibrarSensoresTierra/<sensorTierraVISl>/<sensorTierraNIRl>/<tiempoIntegracionl>/<numeroCapturasl>/<C>', methods=['GET'])                                     #Añade el recurso
# def sensoresTierra(sensorTierraVISl, sensorTierraNIRl, tiempoIntegracionl, numeroCapturasl, C):
#     global sensorTierraVIS
#     sensorTierraVIS = sensorTierraVISl
#     # sensorTierraNIR = sensorTierraNIRl
#     # tiempoIntegracion = tiempoIntegracionl
#     # numeroCapturas = numeroCapturasl
#     print("success")
#     # try:
#     #     print("0")
#     #     spec_NIR_Tierra = sts.setup_Spec(sb.Spectrometer.from_serial_number(sensorTierraNIR), int(tiempoIntegracion)*1000, numeroCapturas)  # Serial, integration time (us), scans per avg. #DOUBLE
#     #     spec_VIS_Tierra = sts.setup_Spec(sb.Spectrometer.from_serial_number(sensorTierraVIS), int(tiempoIntegracion)*1000, numeroCapturas)  # DOUBLE #SINGLE
#     #     #out = []
#     #     init_wl_VIS_Tierra = np.array(spec_VIS_Tierra.wavelengths())[0]  # The NIR wavelengths are ~ 650-1100 nm  #SINGLE      #DOUBLE
#     #     init_wl_NIR_Tierra = np.array(spec_NIR_Tierra.wavelengths())[0]  # The VIS wavelengths are ~ 350-800 nm             #DOUBLE
#     #     #init_wl_NIR = np.array(spec_VIS.wavelengths())[0]  # SINGLE
#     #     #print("Init VIS Wavelength: {}, Init NIR Wavelength: {}".format(init_wl_VIS, init_wl_NIR))
#     #     queueTierra = Queue(maxsize=2)  # This queue receives the data from both the NIR and VIS spectra
#     #     success = "Success Calibrar sensoresTierra"
#     #     pass
#     # except Exception as errorCalibrarSensoresTierra:
#     #     success = "Fail Calibrar Sensores Tierra"
#     #     raise errorCalibrarSensoresTierra
#     return sensorTierraVIS
@app.route('/capturarBlanco', methods=['GET'])                                      #Añade el recurso
def capturarBlanco():
    # a = sensorTierraVIS
    try:
        start_time_A = time.time()
        x = "D:/subtext/splitTest0/Quieto 1 feb/cult2/white0.txt"
        # x = "D:/Tesis/Api/Flask/3vis.txt"
        # with open(x, 'r') as f:
        #     for line in f:
        #         line = line[0:4]
        #         blanco.append(line)
        #     # file = blanco.read()
        with open(x, 'r') as f:
            file = f.read()
        print(len(file))
        # print(blanco)
        # sts.runInParallel(read_VIS_Tierra, read_NIR_Tierra)                                                             #DOUBLE
        # #sts.runInParallel(read_VIS)  # SINGLE
        # # sts.runInParallel(read_VIS)
        # if queueTierra.full():  # If both the NIR and VIS spectra have been acquired successfully
        #     # print(queue.qsize()) # The queue size should be 2
        #     # wavelengths_NIR, intensities_NIR, wavelengths_VIS, intensities_VIS = sts.assign_spectra(queue, init_wl_NIR, init_wl_VIS) #DOUBLE
        #     wavelengths_NIR_Tierra, intensities_NIR_Tierra, wavelengths_VIS_Tierra, intensities_VIS_Tierra = sts.assign_spectra(queueTierra, init_wl_NIR_Tierra, init_wl_VIS_Tierra)  # SINGLE
        # else:
        #     print("Queue not full")

        end_time_A = time.time()
        duration = end_time_A - start_time_A
        print("Acquisition for {} seconds".format(duration))
        duration = str(duration)
        success = "Success"
        pass
    except Exception as errorCalibrarSensoresTierra:
        success = "Fail"
        raise errorCalibrarSensoresTierra
    return file#+","+sensorTierraNIR+","+tiempoIntegracion+","+numeroCapturas #intensities_NIR_Tierra, intensities_VIS_Tierra, success

@app.route('/capturarNegro', methods=['GET'])                                      #Añade el recurso
def capturarNegro():
    # a = sensorTierraVIS
    try:
        start_time_A = time.time()
        x = "D:/Tesis/Api/Flask/3vis.txt"
        with open(x, 'r') as f:
            file = f.read()
        # sts.runInParallel(read_VIS_Tierra, read_NIR_Tierra)                                                             #DOUBLE
        # #sts.runInParallel(read_VIS)  # SINGLE
        # # sts.runInParallel(read_VIS)
        # if queueTierra.full():  # If both the NIR and VIS spectra have been acquired successfully
        #     # print(queue.qsize()) # The queue size should be 2
        #     # wavelengths_NIR, intensities_NIR, wavelengths_VIS, intensities_VIS = sts.assign_spectra(queue, init_wl_NIR, init_wl_VIS) #DOUBLE
        #     wavelengths_NIR_Tierra, intensities_NIR_Tierra, wavelengths_VIS_Tierra, intensities_VIS_Tierra = sts.assign_spectra(queueTierra, init_wl_NIR_Tierra, init_wl_VIS_Tierra)  # SINGLE
        # else:
        #     print("Queue not full")

        end_time_A = time.time()
        duration = end_time_A - start_time_A
        print("Acquisition for {} seconds".format(duration))
        duration = str(duration)
        success = "Success"
        pass
    except Exception as errorCapturarNegro:
        success = "Fail"
        raise errorCapturarNegro
    return file	
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5005)