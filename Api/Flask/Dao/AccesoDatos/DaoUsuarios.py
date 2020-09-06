from .Logica import Usuarios

class DaoUsuarios:
	def __init__(self, conexion):
		self.conexion = conexion

	def guardarUsuario(self, usuario):
		sql_guardar = "INSERT INTO usuarios (nombre, contrasena) VALUES "
		sql_guardar += "(\'" + usuario.nombre + "\', \'" + usuario.contrasena + "\') "
		sql_guardar += " RETURNING *"
		
		# try:
		cursor = self.conexion.cursor()
		cursor.execute(sql_guardar)
		result = cursor.fetchone()
		self.conexion.commit()
		cursor.close()
		print("Registro guardado con exito")
		usuario.id = result[0]
		return usuario

		# except(Exception) as e:
		# 	print("Error al insertar registro", e)
		# 	usuario = "F"
		# 	return usuario
		

	def actualizarUsuario(self, usuario):
		sql_guardar = "UPDATE usuarios SET nombre = \'" + usuario.nombre 
		sql_guardar+= "\', contrasena = \'" + usuario.contrasena + "\' WHERE "
		sql_guardar += "id = " + str(usuario.id) + ";"
		print(sql_guardar)
		try:
			cursor = self.conexion.cursor()
			cursor.execute(sql_guardar)
			self.conexion.commit()
			return usuario

		except(Exception) as e:
			print("Error al actualizar el usuario", e)
		
		finally:
			if(cursor):
				cursor.close()
				print("Se ha cerrado el cursor")

	def borrarUsuario(self, usuario):
		sql_borrar = "DELETE FROM usuarios WHERE id = " + str(usuario.id) + ";"
		
		try:
			cursor = self.conexion.cursor()
			cursor.execute(sql_borrar)
			self.conexion.commit()
			cursor.close()
			
		except(Exception) as e:
			print("Error al actualizar el usuario", e)
		

	def getUsuario(self, id_usuario):
		sql_select = "SELECT * FROM usuarios WHERE id = " + str(id_usuario)
		try:
			cursor = self.conexion.cursor()
			cursor.execute(sql_select)
			record = cursor.fetchone()
			result = Usuarios.Usuarios()
			result.id = record[0]
			result.nombre = record[1]
			result.contrasena = record[2]
			return result

		except(Exception) as e:
			print("Error al actualizar el usuario", e)
			result = None
		
		finally:
			if(cursor):
				cursor.close()
				print("Se ha cerrado el cursor")
			return result
	def getUsuarioLogin(self, nombre, contrasena):
		sql_select = "SELECT * FROM usuarios WHERE nombre = %s AND contrasena = %s" 
		try:
			cursor = self.conexion.cursor()
			cursor.execute(sql_select, (nombre, contrasena))
			record = cursor.fetchone()
			result = Usuarios.Usuarios()
			result.id = record[0]
			result.nombre = record[1]
			result.contrasena = record[2]
			return result

		except(Exception) as e:
			print("Error al actualizar el usuario", e)
			result = None
		
		finally:
			if(cursor):
				cursor.close()
				print("Se ha cerrado el cursor")
			return result

	def getUsuarioNombre(self, nombre):
		sql_select = "SELECT id FROM usuarios WHERE nombre = '"+nombre+"'" 
		# print(sql_select)
		try:
			cursor = self.conexion.cursor()
			cursor.execute(sql_select)
			record = cursor.fetchone()
			result = Usuarios.Usuarios()
			# print(record)
			result.id = record[0]
			# result.nombre = record[1]
			# result.contrasena = record[2]
			return result

		except(Exception) as e:
			print("Error al actualizar el usuario", e)
			result = None
		
		finally:
			if(cursor):
				cursor.close()
				print("Se ha cerrado el cursor")
			return result