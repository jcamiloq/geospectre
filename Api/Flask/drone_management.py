class DroneManagement():

    class __DroneManagement:
        def __init__(self):
            velocidad = None
            id_espectros = None
            firstHome = None
            numeroWaypoint = None
                        
    instance = None

    def __new__(self):
        if not DroneManagement.instance:
            DroneManagement.instance = DroneManagement.__DroneManagement()
        return DroneManagement.instance

    def __getattr__(self, attr):
        return getattr(self.instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.instance, attr, value)
