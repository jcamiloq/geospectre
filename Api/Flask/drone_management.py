class MisionManagement():

    class __MisionManagement:
        def __init__(self):
            velocidad = None
            id_espectros = None
            firstHome = None
            numeroWaypoint = None
            
    instance = None

    def __new__(self):
        if not MisionManagement.instance:
            MisionManagement.instance = MisionManagement.__MisionManagement()
        return MisionManagement.instance

    def __getattr__(self, attr):
        return getattr(self.instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.instance, attr, value)
