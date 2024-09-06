# JCT Technology Ltd Datalogger 1.0
# by Andrew Keeley (andy@pcman.ca)
# March 2018

# Modbus Client class

# standard / third party libraries
from PyQt4 import QtCore
from pymodbus.client.sync import ModbusTcpClient, ConnectionException
from pymodbus.exceptions import ModbusIOException
import struct
import datetime
import time
import threading

class ModbusClient(QtCore.QThread):
    update = QtCore.pyqtSignal(bool, list, int)  # emits status, values, servernum

    def __init__(self, parent=None, host=None, port=None, registers=None, unit_id=None, *args, **kwargs):
        super(ModbusClient, self).__init__(parent)
        self.host = host
        self.port = port
        self.registers = registers
        self.unit_id = unit_id
        self.server_address = host
        self.server_port = port
        self.stop_event = threading.Event()  # create a flag event to close
        self.regmap = self.registers[0]
        self.servernum = self.unit_id
        if self.servernum < len(self.registers):  # check if the index is within the valid range
            metrics = self.registers[self.servernum]  # Access the inner list
        else:
            metrics = []  # or some default value if the index is out of range


        # Ensure metrics contains only integers
        int_metrics = [x for x in metrics if isinstance(x, int)]
        self.inpbase = 0 if int_metrics and int_metrics[0] == 0 else (int_metrics[0] - 30001) if int_metrics else 0  # the first input register to read
        self.inpcount = len(int_metrics) 

        # Extract the holding register indices
        hld_indices = [x for x in metrics if isinstance(x, int) and 40000 <= x < 50000]
        self.hldbase = 0 if hld_indices else 0  # the first holding register to read
        self.hldcount = len(hld_indices) if hld_indices else 0
        self.mbc = ModbusTcpClient(self.server_address, self.server_port)  # create a Modbus client to server at IP address specified in config
        self.inpregs = None
        self.hldregs = None
        self.stopped = True
        self.offline = False
        
    def read(self):
        try:
            if self.inpcount:
                self.inpregs = self.mbc.read_input_registers(self.inpbase, self.inpcount)  # read input registers
            if self.hldcount:
                self.hldregs = self.mbc.read_holding_registers(self.hldbase, self.hldcount)  # read holding registers
        except ConnectionException:  # if connection failed
            self.offline = True
            return False, None
        if type(self.hldregs) is ModbusIOException:  # connected but no response!
            self.offline = True
            return False, None

        self.offline = False
        values = []  # initialise a list for the values

        for r in self.regmap:  # iterate the register map
            if r[4] == self.server + 1:
                if r[2] in ['U2', 'I2']:
                    b = self.getword(r)  # get one register as a U2
                else:
                    b = self.getdword(r)  # get two registers as a U4
                if r[2][0] == 'U':
                    values.append(b)
                elif r[2][0] == 'F':
                    values.append(struct.unpack(">f", struct.pack(">I", b))[0])
                elif r[2] == 'I4':
                    values.append(struct.unpack(">i", struct.pack(">I", b))[0])
                elif r[2] == 'I2':
                    values.append(struct.unpack(">h", struct.pack(">H", b))[0])
                else:
                    values.append(0)  # safety net

        return True, values  # return success flags and values
    
    def write_register(self, register_address, value):
        modbus_tcp_client = ModbusTcpClient(self.server_address, self.server_port)
        modbus_tcp_client.connect()
        modbus_tcp_client.write_registers(register_address, [value])
        modbus_tcp_client.close()

        
def getword(self, register):
    if 30001 <= register[1] <= 39999:
        return self.inpregs.registers[register[1] - 30001 - self.inpbase]
    elif 40001 <= register[1] <= 49999:
        return self.hldregs.registers[register[1] - 40001 - self.hldbase]
    return 0  # safety net

def getdword(self, register):
    if 30001 <= register[1] <= 39998:
        return self.inpregs.registers[register[1] - 30000 - self.inpbase] * 2 ** 16 + self.inpregs.registers[register[1] - 30001 - self.inpbase]
    elif 40001 <= register[1] <= 49999:
        return self.hldregs.registers[register[1] - 40001 - self.hldbase]
    return 0  # safety net

def resettotalisers(self):
    if not self.offline:
        try:
            self.mbc.write_register(address=110, value=0x01, unit=0)
        except ConnectionException:
            pass

def hasstopped(self):
    return self.stopped

def stop(self):
    self.stop_event.set()   # set event to stop the thread