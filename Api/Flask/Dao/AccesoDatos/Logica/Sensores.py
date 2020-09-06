class Sensores:
	def init(self, lugar = "", tipo = "", numero_serie = "", t_int = 0, numero_capt = 0, mision_id = 0, id_sensor = -1):
		self.id = id_sensor
		self.lugar = lugar
		self.tipo = tipo
		self.numero_serie = numero_serie
		self.t_int = t_int
		self.numero_capt = numero_capt
		self.mision_id = mision_id
