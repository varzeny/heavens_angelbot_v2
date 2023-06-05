


import asyncio
from datetime import datetime # datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" )


class Manager:
    def __init__(self, Q_sbc, name, addr) -> None:
        # 초기입력
        self.Q_sbc = Q_sbc
        self.name = name
        self.addr = addr
        # 후기입력
        self.reader = None
        self.writer = None
        self.state = None
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
            self.task["listen_mobot"] = asyncio.get_running_loop().create_task( self.listen_mobot() )
            print( self.name,"succes connect" )

        except Exception as e:
            print( self.name,"error connect\n",e )
            self.reader = None
            self.writer = None

        finally:
            print( self.name,"return connect" )
            return


    async def listen_mobot(self):
        try:
            print( self.name,"call listen_mobot" )
            server_mobot = await asyncio.start_server(
                self.handle_mobot,
                "10.10.10.51",
                7179
            )
            await server_mobot.serve_forever()
            
        except Exception as e:
            print( self.name,"error listen_mobot\n",e )

        finally:
            print( self.name,"return liste_mobot" )

    
    async def handle_mobot(self,reader,writer):
        try:
            print( self.name,"call handle_mobot",writer.get_extra_info("peername") )
            while True:
                try:
                    recv_b = await reader.read(1024)
                    if not recv_b:
                        break
                except Exception as e:
                    print( self.name,"error wait recv\n",e )
                    continue

                try:
                    recv = recv_b.decode()
                    if recv[:6] == "Status":
                        msg = {
                            "who":"mobot",
                            "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
                            "where":"mobot",
                            "what":"status",
                            "how":recv,
                            "why":"update"
                        }
                        await self.Q_sbc.put( msg )

                except Exception as e:
                    print( self.name,"error decode recv\n",e )
                    continue

        except Exception as e:
            print( self.name,"error handle_status\n",e )

        finally:
            print( self.name,"return handle_status" )

    
    async def handle_recv(self):
        try:
            print( self.name,"call handle_recv",self.writer.get_extra_info("peername") )
            while True:
                try:
                    recv_b = await self.reader.read(1024)
                    if not recv_b:
                        break

                except Exception as e:
                    print( self.name,"error wait recv\n",e )
                    continue

                try:
                    recv = recv_b.decode()
                    msg = {
                        "who":"mobot",
                        "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
                        "where":"mobot",
                        "what":"state",
                        "how":recv,
                        "why":"response"
                    }

                except Exception as e:
                    print( self.name,"error trans dic\n",e )
                    continue

                try:
                    await self.Q_sbc.put( msg )

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
            print( self.name,"return handle_send" )
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
