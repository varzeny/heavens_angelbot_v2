




import asyncio

import module_protocol.Modbus as Modbus

class Cobot:
    def __init__(self, Q_sbc, name, addr) -> None:
        # 초기입력
        self.Q_sbc = Q_sbc
        self.name = name
        self.addr = addr
        # 후기입력
        self.reader = None
        self.writer = None
        self.tcp = {
            "x":0,
            "y":0,
            "z":0,
            "rx":0,
            "ry":0,
            "rz":0
        }
        # task
        self.task = {}


    async def connect(self):
        try:
            print(f"{self.name}에 접속 시도중...")
            self.reader, self.writer = await asyncio.open_connection(self.addr[0],self.addr[1])
            print(f"{self.name}에 접속 성공")
        except:
            print(f"{self.name}에 접속 실패")


    async def handle_send(self, functionCode, rgAddr, rgCount, value = None):
        try:
            msg = Modbus.encoding( functionCode, rgAddr, rgCount, value )
            print(msg)
        except:
            print(f"{self.name}에 msg 발신 실패")
       
