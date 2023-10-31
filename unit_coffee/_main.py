from pyModbusTCP.client import ModbusClient

class Mb:
    def __init__(self, addr, port) -> None:
        self.client = ModbusClient( addr, port )

    def rg_read(self, rg_num):
        data = self.client.read_holding_registers(rg_num,1)
        print(data)

    def rg_write(self, rg_num, value):
        # self.client.write_single_register(rg_num, value)
        self.client.write_multiple_registers(rg_num,value)


if __name__ == "__main__":
    print("프로그램 시작")
    target_1 = Mb("192.168.215.124",502)
    target_2 = Mb("192.168.215.123",502)

    
    target_1.rg_write(11,[1])
    target_1.rg_write(1,[1])
    
    target_2.rg_write(11,[1])
    target_2.rg_write(1,[1])


    print("프로그램 종료")
