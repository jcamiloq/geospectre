class Telemetria:
	def init(self, pitch = 0, yaw = 0, roll = 0, lat = 0, lon = 0, alt = 0, bateriaDron = 0, velocidadDron = 0, mision_id = 0, id_telemetria = -1):
		self.id = id_telemetria
		self.pitch = pitch
		self.yaw = yaw
		self.roll = roll
		self.lat = lat
		self.lon = lon
		self.alt = alt
		self.bateriaDron = bateriaDron
		self.velocidadDron = velocidadDron
		self.mision_id = mision_id
