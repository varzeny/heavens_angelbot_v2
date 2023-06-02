from pymodbus.client import ModbusTcpClient
import endecode_ieee754 as ed


import time


client=ModbusTcpClient("192.168.1.2",502)
client.connect()
print("!!!!")


while True:
    tcp_current = ed.check_tcp(client.read_input_registers(7001,12).registers)
    print(tcp_current)
    time.sleep(1)




client.write_registers(9001,ed.encode_short(-60.75))
v = ed.decode_short(client.read_holding_registers(9001,2).registers)
print(v)


client.close()
