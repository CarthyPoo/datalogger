# Path to save log files
LOG_PATH = "C:\ProgramData\Logfiles"

# Modbus servers
# IP address (in quotes), port number
SERVERS = [
	('127.0.0.1', 502),
	('127.0.0.1', 502)
]

# Modbus register map
# Friendly name, Modbus register number, type (U2, I2, U4, I4, F), decimals (0-9), server# (1-based)
MODBUS_REGISTERS = [
	("Channel 1", 40001, "I2", 2, 1),
	("Channel 2", 40002, "I2", 2, 1),
	("Channel 3", 40003, "I2", 2, 1),
	("Channel 4", 40004, "I2", 2, 2),
	("Channel 5", 40005, "I2", 2, 2),
	("Channel 6", 40006, "I2", 2, 2)
]

# MODBUS_REGISTERS = [
# 	("Temperature", 40001, "F", 2),
# 	("Pressure", 40003, "I2", 2),
# 	("Rate", 40004, "U2", 1),
# 	("Total", 40005, "F", 4)
# ]

# Text for up to six custom annotation buttons. Use "" for unused buttons.
ANNOTATION_1 = "Start Job"
ANNOTATION_2 = 'Pressure Test'
ANNOTATION_3 = "Reverse Circulate"
ANNOTATION_4 = "Custom 1"
ANNOTATION_5 = 'Custom 2'
ANNOTATION_6 = "Custom 3"
