import snap7
import time
import json

class PLConnect:
    def __init__(self):
        pass
    
    def getPlcInfo(self):
        with open("data/GestureSettings.json") as jsonfile:
            plc_settings = json.load(jsonfile)
            plc_settings = plc_settings.get("plc_info")
            self.ip = plc_settings["ip"]
            self.rack = plc_settings["rack"]
            self.slot = plc_settings["slot"]
            self.db_number = plc_settings["db_number"]
            self.start_address = plc_settings["start_addres"]
            self.size = plc_settings["size"]
    
    def connection(self):
        self.getPlcInfo()
        plc = snap7.client.Client()
        plc.connect(self.ip, self.rack, self.slot)
        return plc
    
    def readDB(self, byte, bit):
        plc = self.connection()
        db = plc.db_read(self.db_number, self.start_address, self.size)
        status = snap7.util.get_bool(db, byte, bit)
        return (status)
    
    def writeDB(self, byte, bit, value):
        try:
            plc = self.connection()
            db = plc.db_read(self.db_number, self.start_address, self.size)
            snap7.util.set_bool(db, byte, bit, value)
            plc.db_write(self.db_number, self.start_address, db)
        except Exception as e:
            print("Cannot finish")
            print("because", e)
        
    
    def sendCommand(self, byte, bit):
        try:
            self.connection()
            for i  in range(1, 5):
                if i != bit:
                    print(i, bit, False)
                    self.writeDB(byte, i, False)
                else:
                    print(i, bit, True)
                    self.writeDB(byte, bit, True)
        except Exception:
            print("There's no stable connection with the PLC")
            
# plc = PLConnect()
# plc.writeDB(0, 0, False)
# plc.writeDB(0, 1, False)
# plc.writeDB(0, 2, False)
# plc.writeDB(0, 3, False)
# plc.writeDB(0, 4, False)