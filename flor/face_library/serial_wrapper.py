import cloudpickle

class SerialWrapper:

    def __init__(self, data):
        self.data = data

    def get(self):
        return self.data

    def serialize(self): # do we even need this?
        try:
            return str(cloudpickle.dumps(self.data))
        except:
            return "ERROR: failed to serialize"