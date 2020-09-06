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
# global spec_NIR_Tierra, spec_VIS_Tierra, wavelengths_NIR_Tierra, intensities_NIR_Tierra, wavelengths_VIS_Tierra, intensities_VIS_Tierra, queueTierra, outTierra
# global sensorTierraVIS, sensorTierraNIR, sensorVueloVIS, sensorVueloVIS, tiempoIntegracion, numeroCapturas

# sensorTierraVIS="1"
# Serial numbers: S07678, S09818
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
  
@app.route('/sensoresTierra/<sensorTierraVIS>/<sensorTierraNIR>/<tiempoIntegracion>/<numeroCapturas>/<aux>', methods=['GET'])										#Añade el recurso
def sensoresTierra(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas, aux):
    try:
        print(sensorTierraVIS)
        if aux == "C":
            print("capturando blanco")
            start_time_A = time.time()
            x = "D:/subtext/splitTest0/Quieto 1 feb/cult2/white10.txt"
            with open(x, 'r') as f:
                intensitiesFlask = f.read()
            # print(intensitiesFlask)
            # sts.runInParallel(read_VIS(b, c), read_NIR(a, c))                                                             #DOUBLE
            # #sts.runInParallel(read_VIS)  # SINGLE
            # if queueTierra.full():  # If both the NIR and VIS spectra have been acquired successfully
            #     # print(queue.qsize()) # The queue size should be 2
            #     wavelengths_NIR, intensities_NIR, wavelengths_VIS, intensities_VIS = sts.assign_spectra(queue, init_wl_NIR, init_wl_VIS)  # SINGLE
            # else:
            #     print("Queue not full")
            end_time_A = time.time()
            duration = end_time_A - start_time_A
            print("Acquisition for {} seconds".format(duration))
            duration = str(duration)
            success = "Success"
            pass
        elif aux == "N":
            print("capturando neg")
            start_time_A = time.time()
            x = "D:/subtext/splitTest0/Quieto 1 feb/cult2/dark0.txt"
            with open(x, 'r') as f:
                intensitiesFlask = f.read()
            # sts.runInParallel(read_VIS(b, c), read_NIR(a, c))                                                             #DOUBLE
            # #sts.runInParallel(read_VIS)  # SINGLE
            # if queueTierra.full():  # If both the NIR and VIS spectra have been acquired successfully
            #     # print(queue.qsize()) # The queue size should be 2
            #     wavelengths_NIR, intensities_NIR, wavelengths_VIS, intensities_VIS = sts.assign_spectra(queue, init_wl_NIR, init_wl_VIS)  # SINGLE
            # else:
            #     print("Queue not full")
            end_time_A = time.time()
            duration = end_time_A - start_time_A
            print("Acquisition for {} seconds".format(duration))
            duration = str(duration)
            success = "Success"
            pass

        else:
            intensitiesFlask = ""
            # a, b, c = calibrarSensores(sensorTierraVIS, sensorTierraNIR, tiempoIntegracion, numeroCapturas)
            pass
        pass
    except Exception as errorCalibrarSensoresTierra:
        print("error captura/calibracion")
        raise errorCalibrarSensoresTierra
    return intensitiesFlask #+sensorTierraNIRl+tiempoIntegracionl+numeroCapturasl+success
@app.route('/sensoresVuelo/<sensorVueloVIS>/<sensorVueloNIR>/<tiempoIntegracion>/<numeroCapturas>/<aux>', methods=['GET'])                                     #Añade el recurso
def sensoresVuelo(sensorVueloVIS, sensorVueloNIR, tiempoIntegracion, numeroCapturas, aux):
    try:
        if aux == "C":
            print("capturando Vuelo")
            start_time_A = time.time()
            x = "D:/subtext/splitTest0/Quieto 1 feb/cult2/2mt0.txt"
            with open(x, 'r') as f:
                intensitiesFlask = f.read()
            # sts.runInParallel(read_VIS(b, c), read_NIR(a, c))                                                             #DOUBLE
            # #sts.runInParallel(read_VIS)  # SINGLE
            # if queueTierra.full():  # If both the NIR and VIS spectra have been acquired successfully
            #     # print(queue.qsize()) # The queue size should be 2
            #     wavelengths_NIR, intensities_NIR, wavelengths_VIS, intensities_VIS = sts.assign_spectra(queue, init_wl_NIR, init_wl_VIS)  # SINGLE
            # else:
            #     print("Queue not full")
            end_time_A = time.time()
            duration = end_time_A - start_time_A
            print("Acquisition for {} seconds".format(duration))
            duration = str(duration)
            success = "Success"
            pass
        else:
            intensitiesFlask = ""
            # a, b, c = calibrarSensores(sensorVueloVIS, sensorVueloNIR, tiempoIntegracion, numeroCapturas)
            pass
        pass
    except Exception as errorCalibrarSensoresTierra:
        print("error captura/calibracion")
        raise errorCalibrarSensoresTierra
    return intensitiesFlask 
    #+sensorTierraNIRl+tiempoIntegracionl+numeroCapturasl+success

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5005)