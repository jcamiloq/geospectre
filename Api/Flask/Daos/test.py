from AccesoDatos.Logica.Usuarios import Usuarios
from AccesoDatos.Logica.Waypoints import Waypoints
from AccesoDatos.Logica.Mision import Mision
from AccesoDatos.DaoMision import DaoMision
from AccesoDatos.DaoUsuarios import DaoUsuarios
from AccesoDatos.DaoWaypoints import DaoWaypoints
import Conexion

u = Usuarios()

u.contrasena = "AAAAA"
u.nombre = "Tecallas"

c = Conexion.conexion()
udao = DaoUsuarios(c)

#udao.guardarUsuario(u)
getU = udao.getUsuario(3)
print(getU)

getU.nombre = "Karen Alga"
udao.actualizarUsuario(getU)

getU2 = udao.getUsuario(3)
print(getU2.nombre)

m = Mision()
m.nombre = "M8"
m.elevacion = 0
m.velocidad = 3
m.modo_vuelo = "K"
m.modo_adq = "M"
m.usuarios_id = 3

mdao = DaoMision(c)
#m2 = mdao.guardarMision(m)

m2 = mdao.getMision(4)
print(m2.nombre)

m2.nombre = "MortalK3"
m2 = mdao.actualizarMision(m2)
#print(m2.nombre)

m2 = mdao.getMision(4)
print(m2.nombre)

w = Mision()
w.num_waypoint = 3
w.latlon = "0.03,0.03"
w.mision_id = 4

wdao = DaoWaypoints(c)
w = wdao.guardarWaypoint(w)

w.latlon = "0.02658, 0.589413"
wdao.actualizarWaypoint(w)
idw = w.id
w = wdao.getWaypoint(idw)
print(w.latlon)