




import asyncio

from ..protocol.modbus import Modbus

class Manager:
    '''
    made by Hoa Choi of RobotCampus

        input:
            tcp
                x: 7001 7002    rx:7007 7008
                y: 7003 7004    ry:7009 7010
                z: 7005 7006    rz:7011 7012
        holding
            tcp
                x: 9001 9002    rx:9007 9008
                y: 9003 9004    ry:9009 9010
                z: 9005 9006    rz:9011 9012
            switch
                9000

    '''
    def __init__(self, Q_sbc, name, addr) -> None:
        # 초기입력
        self.Q_sbc = Q_sbc
        self.name = name
        self.addr = addr
        # 후기입력
        self.reader = None
        self.writer = None
        self.flag_idle = asyncio.Event();    self.flag_idle.set()
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
        while True:
            try:
                print( self.name,"----------------call connect" )
                self.reader, self.writer = await asyncio.open_connection(self.addr[0],self.addr[1])
                print( self.name,"success connect" )
                break

            except Exception as e:
                print( self.name,"--------error connect\n",e )


    async def handle_send(self, functionCode, rgAddr, rgCount, value = None):
        self.flag_idle.clear()
        try:
            print( self.name,"call handle_send" )
            msg = Modbus.encoding( functionCode, rgAddr, rgCount, value )
            self.writer.write( msg )
            await self.writer.drain()
            recv = await self.reader.read(1024)
            if functionCode <= 4:   # read 일 경우
                result = Modbus.decoding(recv)
                self.flag_idle.set()
                return result
            
            # read 가 아닐 경우
            try:
                msg = Modbus.encoding( 3,9000,1 )
                res = 100
                while res != 0:
                    await asyncio.sleep(1)
                    self.writer.write( msg )
                    await self.writer.drain()
                    recv = await self.reader.read(1024)
                    res = Modbus.decoding(recv)

                self.flag_idle.set()
                
            except Exception as e:
                print(self.name,"error modbus flaging")


        except Exception as e:
            print( self.name,"error handle_send\n",e )

        finally:
            print( self.name,"return handle_send" )


if __name__ == "__main__":
    
    print(f"{__name__}이 시작됨")

    print(f"{__name__}이 종료됨")


                
       
