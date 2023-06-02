

import asyncio
import struct


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
            await asyncio.sleep(1)

            # 접속 단계
            msg = await self.reader.read(1024)
            self.writer.write(b"admin\r\n")
            await self.writer.drain()
            await asyncio.sleep(1)
            print(f"{self.name}에 접속 성공")
        except:
            print(f"{self.name}에 접속 실패")
            return


        while True:
            try:
                recv = await self.reader.read(1024)

                # recv 를 분석 #
                if not recv:
                    break
                elif recv[:6] == b"Status":
                    msg = {
                        "perpose":"status",
                        "data":recv.decode(),
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
                print(f"{self.name}의 수신 대기 중 오류 발생")
                await asyncio.sleep(0.1)
                
            
            
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
        self.tcp = {
            "x":0,
            "y":0,
            "z":0,
            "rx":0,
            "ry":0,
            "rz":0
        }
    
    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(self.addr[0],self.addr[1])
            print(f"{self.name} 에 접속 성공")
        except:
            print(f"{self.addr} 에 접속 실패")
        
        
    async def readRgs(self,rg,n):
        # header #######
        tr = 1
        pr = 0
        length = 6
        unitid = 1
        fc = 4
        # query ########
        startaddr = rg
        rgcount = n
        
        msg = struct.pack(">HHHBBHH",tr,pr,length,unitid,fc,startaddr,rgcount)
        self.writer.write( msg )
        await self.writer.drain()
        recv = await self.reader.read(1024)

        # print("recv :",recv)
        data = []
        if rgcount == 1:
            data.append( struct.unpack(">H",recv[9:])[0] )

        else:
            for i in range(0,rgcount*2,4):
                data.append( struct.unpack(">f",recv[9+i:13+i])[0] )

        # print(data)
        return data

    async def writeRgs(self,rg,n,value):
        msg = ""
        self.writer.write( msg )
        await self.writer.drain()
        recv = await self.reader.read(1024)
        print(recv)
