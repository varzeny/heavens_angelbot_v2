

import asyncio


##############################################################################

class Part:
    def __init__(self, queue, name, addr) -> None:
        self.queue = queue
        self.name = name
        self.addr = addr


##############################################################################
class Part_Mobile(Part):
    def __init__(self, queue, name, addr) -> None:
        super().__init__(queue, name, addr)
        self.reader = None
        self.writer = None

    
    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(self.addr[0],self.addr[1])

            # 접속 단계
            msg = await self.reader.read(1024)
            self.writer.write(b"admin\r\n")
            await self.writer.drain()

            while True:
                recv = await self.reader.read(1024)
                if not recv:
                    break
                elif recv[:6] == b"Status":
                    msg = {
                        "perpose":"status",
                        "data":recv.deccode(),
                        "sender":self.name
                    }
                else:
                    msg = {
                        "perpose":"nothing",
                        "data":recv.decode(),
                        "sender":self.name
                    }
                await self.queue.put(msg)
        except:
            print(f"{self.addr} 통신 오류 발생")

    async def sendMsg(self,msg):
        try:
            self.writer.write( msg.encode()+b"\r\n" )
            await self.writer.drain()
        except:
            print(f"{self.addr}에 발신 실패")

##############################################################################
class Part_Cobot(Part):
    def __init__(self, queue, name, addr) -> None:
        super().__init__(queue, name, addr)
        self.reader = None
        self.writer = None
    
    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(self.addr[0],self.addr[1])

            while True:
                recv = await self.reader.read(1024)
                if not recv:
                    break
                await self.queue.put(recv)
        except:
            print(f"{self.addr} 통신 오류 발생")