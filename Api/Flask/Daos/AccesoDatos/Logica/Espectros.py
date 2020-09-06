class Espectros:
	def init(self, white = [], dark = [], capturado = [], resultado = [], sensores_id = 0, id_espectros = -1):
		self.id = id_espectros
		self.white = white
		self.dark = dark
		self.capturado = capturado
		self.resultado = resultado
		self.sensores_id = sensores_id