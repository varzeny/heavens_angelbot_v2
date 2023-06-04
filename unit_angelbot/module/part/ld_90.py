


import asyncio

from module.protocol.heavensangelbot import HeavensAngelBot as protocol_10000



class Manager:
    def __init__(self, Q_sbc, name, addr) -> None:
        # 초기입력
        self.Q_sbc = Q_sbc
        self.name = name
        self.addr = addr
        # 후기입력
        self.reader = None
        self.writer = None
        self.status = {
            "status":"disconnect",
            "battery":0,
            "temperature":0,
            "location":{
                "x":0,
                "y":0,
                "theta":0
            }
        }
        # task
        self.task = {}

    async def connect(self):
        try:
            print( self.name,"call connect" )

            self.reader, self.writer = await asyncio.open_connection(self.addr[0],self.addr[1])

            # omron arcl 접속 절차
            recv = await self.reader.read(1024);        print(recv)
            self.writer.write(b"admin\r\n")
            await self.writer.drain()

            self.task["handle_recv"] = asyncio.get_running_loop().create_task( self.handle_recv() )

        except Exception as e:
            print( self.name,"error connect\n",e )
            self.reader = None
            self.writer = None

        finally:
            print( self.name,"return connect" )
            return


    async def handle_recv(self):
        try:
            print( self.name,"call handle_recv" )
            while True:
                try:
                    recv = await self.reader.read(1024)
                    if not recv:
                        break

                except Exception as e:
                    print( self.name,"error wait recv\n",e )
                    continue

                try:
                    msg = protocol_10000.encoding( data=recv, sender="mobile" )

                except Exception as e:
                    print( self.name,"error encoding\n",e )
                    continue

                try:
                    await self.Q_sbc.put( msg );   print( msg )

                except Exception as e:
                    print( self.name,"error put queue\n",e )
                    continue
                
        except Exception as e:
            print( self.name,"error handle_recv\n",e )

        finally:
            print( self.name,"return handle_recv" )
            return


    async def handle_send(self,msg):
        try:
            self.writer.write( msg.encode()+b"\r\n" )
            await self.writer.drain()

        except Exception as e:
            print( self.name,"error handle_send\n",e )

        finally:
            return


if __name__=="__main__":
    print(f"{__name__}이 시작됨")

    async def main():
        ro = Manager( asyncio.Queue(),"robot",("192.168.215.219",7171) )

        ro.task["connect"] = asyncio.create_task( ro.connect() )
        print(ro.task)
        print()
        ro.task["handle_recv"] = asyncio.create_task( ro.handle_recv() )
        print(ro.task)


    loop = asyncio.get_event_loop()
    loop.create_task( main() )
    loop.run_forever()


    print(f"{__name__}이 종료됨")
