Tech Stack:
Python 2.7.13 
  (Additional Libraries - Simpy)

Program used - [Modbus Slave]([url](https://www.modbustools.com/modbus_slave.html))





          +---------------+
          |  modbusrx.py  |
          +---------------+
                  |
                  |  creates ModbusClient instance
                  |
                  v
          +---------------+
          |  ModbusClient  |
          |  (modbus.py)   |
          +---------------+
                  |
                  |  reads input and holding registers
                  |  from Modbus server every second
                  |
                  v
          +---------------+
          |  Logger       |
          |  (processes    |
          |   updated values) |
          +---------------+
                  |
                  |  stores data in circular buffer
                  |
                  v
          +---------------+
          |  Recorder     |
          |  (records data |
          |   from circular buffer) |
          +---------------+
                  |
                  |  persists data to file or database
                  |
                  v
          +---------------+
          |  Persist      |
          |  (persists data |
          |   to file or database) |
          +---------------+
