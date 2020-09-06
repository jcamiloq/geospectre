@echo off
start chrome file:///D:/Tesis/Code/MapDrone/MapExample.html
start cmd /k "D:/Tesis/Code/env/Scripts/activate & D:/Tesis/Code/Api/Flask/api.py"
start cmd /k "D:/Tesis/Code/env/Scripts/activate & D:/Tesis/Code/Api/Flask/flaskRaspiTierra.py"
start cmd /k "D:/Tesis/Code/env/Scripts/activate & D:/Tesis/Code/Api/Flask/flaskRaspiVuelo.py"
exit