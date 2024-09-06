import simpy
import random
from datalogger import ModbusClient
from datalogger_class import Datalogger

server_address = 'localhost'
server_port = 1700

# Define the water plant's components
class Tank:
    def __init__(self, capacity):
        self.capacity = capacity
        self.level = 0

    def fill(self, amount):
        self.level += amount
        if self.level > self.capacity:
            self.level = self.capacity

    def drain(self, amount):
        self.level -= amount
        if self.level < 0:
            self.level = 0

# Define the water plant's simulation
class WaterPlant:
    def __init__(self, env, modbus_client, register_map):
        self.env = env
        self.tank = Tank(1000)
        self.modbus_client = modbus_client
        self.register_map = register_map

    def run(self):
        while True:
            # Simulate the tank's level changing
            self.tank.fill(random.randint(0, 100))
            self.tank.drain(random.randint(0, 100))

            # Update the Modbus registers
            self.modbus_client.write_register(30001, self.tank.level)
            self.modbus_client.write_register(30002, self.tank.capacity)

            # Wait for 1 second
            yield self.env.timeout(1)

# Define the registers
registers = [
    {
        'name': 'Register Map 1',
        'start': 0,
        'count': 100,
        'read_only': True,
        'description': 'Description of Register Map 1'
    },
    {
        'name': 'Register Map 2',
        'start': 100,
        'count': 50,
        'read_only': False,
        'description': 'Description of Register Map 2'
    }
]

modbus_client = ModbusClient(None, ('localhost', 1700), [registers[0]], 1)

# Create the datalogger instance, passing the ModbusClient instance and register map
datalogger = Datalogger(modbus_client, registers)

# Create the simulation environment
env = simpy.Environment()

# Create the water plant simulation, passing the ModbusClient instance and register map
water_plant = WaterPlant(env, modbus_client, registers)

# Run the simulation
env.process(water_plant.run())
env.run(until=100)