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

import matplotlib.pyplot as plt
from os import path
import numpy as np

wavelenghts = []
blanco = []
negro = []

def getFiles():
    global wavelenghts, blanco, negro
    # num = "quieto1"
    num2 = "cult2"  # num[0:1]
    # print(num2)
    path = ("D:/subtext/splitTest0/Quieto 1 feb/%s" % (num2))
    #x = ("%s/%s.txt" % (path, num))
    # x = ("%s/2mt0.txt" % (path))
    wav = ("%s/wavevis.txt" % (path))
    blan = ("%s/white0.txt" % (path))
    neg = ("%s/dark0.txt" % (path))

    with open(wav, "r") as wavevis:
        for line in wavevis:
            #line = line[:-4]
            wavelenghts.append(line)
    # blanco-negro/medida-negro
    with open(blan, "r") as blancovis:
        for line in blancovis:
            line = line[0:4]
            blanco.append(line)
    with open(neg, "r") as negrovis:
        for line in negrovis:
            line = line[0:4]
            negro.append(line)
def makeImage():
    global image, blanco, negro, wavelenghts
    negro = np.array(negro, dtype=np.float32)
    blanco = np.array(blanco, dtype=np.float32)
    wavelenghts = np.array(wavelenghts, dtype=np.float32)

    plt.figure(1)
    ax2 = plt.subplot(121)
    plt.plot(wavelenghts, negro, label='Negro')
    ax2.set_ylim(min(blanco), max(blanco))
    plt.legend()
    ax3 = plt.subplot(122, sharey=ax2)
    plt.plot(wavelenghts, blanco, label='Blanco')
    #ax3.set_ylim(0, 50)
    # Add a legend
    plt.legend()
    # ax4 = plt.subplot(133)
    # plt.plot(wavecor, espectrocor, label='Espectro %s metros' % (num))
    # # Add a legend
    # plt.legend()z
    wm = plt.get_current_fig_manager()
    wm.window.state('zoomed')
    # Show the plot
    plt.show()
    plt.savefig("image.jpg", format="png")

getFiles()
makeImage()


# from flask import Flask
# import requests
# import numpy as np
# import urllib.request
# import urllib.parse
# app = Flask(__name__)
# @app.route('/crearArchivos', methods=['GET'])
# def crearArchivos():
#     url = "http://127.0.0.1:5005/crearArchivos"
#     print("1")
#     with urllib.request.urlopen(url) as f:
#         buf= f.read()
#         print(buf)
#         # npzfile = np.load(buf)
#         # print(npzfile['arr_0'])
#         # # print(f.read().decode('utf-8'))
#     pass
#     print("!")
#     return buf
#     # filestr = request.get_json()
#     # file = np.fromstring(filestr)
#     # print(file)
#     # 
# @app.route('/capturar', methods=['GET'])
# def capturar():
#     url = "http://127.0.0.1:5005/capturarBlanco"
#     print("1")
#     with urllib.request.urlopen(url) as f:
#         buf= f.read()
#         print(buf)
#         # npzfile = np.load(buf)
#         # print(npzfile['arr_0'])
#         # # print(f.read().decode('utf-8'))
#     pass
#     print("!")
#     return buf
# if __name__ == '__main__':
#     app.run(debug=True, host='127.0.0.1', port=5000)