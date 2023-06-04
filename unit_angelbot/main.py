




import asyncio
import websockets
import json

from module.part.ld_90 import Manager as manager_ld_90
from module.part.tm5_700 import Manager as manager_tm5_700

from module.protocol.heavensangelbot import HeavensAngelBot as protocol_10000


##################################################################
class Unit:
    def __init__(self,name) -> None:
        # early set
        self.name = name
        self.Q_unit = asyncio.Queue()
        self.part = {
            "mobot":manager_ld_90( self.Q_unit, "mobot", ("10.10.10.10",7171) ),
            "cobot":manager_tm5_700( self.Q_unit, "cobot", ("192.168.1.2",502) )
        }
        # late set
        self.loop = None

    def run(self):
        try:
            print( self.name,"call run" )
            self.loop = asyncio.get_event_loop()
            self.loop.create_task( self.main() )
            self.loop.run_forever()

        except Exception as e:
            print( self.name,"error run\n",e )

        finally:
            print( self.name,"return run" )
            return 
        
    ##################################################################

    async def main(self):
        try:
            print( self.name,"call main" )

            self.loop.create_task( self.check_queue() )
            self.loop.create_task( self.listen() )

            self.loop.create_task( self.part["mobot"].connect() )
            self.loop.create_task( self.part["cobot"].connect() )

        except Exception as e:
            print( self.name,"error main\n",e )

        finally:     
            print( self.name,"return main" )
            return
        
    ##################################################################

    async def listen(self):
        try:
            print( self.name,"call listen" )
            
            server = await asyncio.start_server(
                self.handle_recv,
                "127.0.0.1",
                7179
            )
            await server.serve_forever()

        except Exception as e:
            print( self.name,"error listen\n",e )

        finally:
            print( self.name,"return listen" )
            return

    async def handle_recv(self, reader, writer):
        try:
            print( self.name,"call handle_recv" )
            while True:
                try:
                    recv = await reader.read(1024)
                    if not recv:
                        break

                except Exception as e:
                    print( self.name,"error wait recv\n",e )
                    continue

                try:
                    await self.Q_unit.put( recv )

                except Exception as e:
                    print( self.name,"error put queue\n",e )
                    continue
                
        except Exception as e:
            print( self.name,"error handle_recv\n",e )
        
        finally:
            print( self.name,"return handle_recv" )
            return

    ##################################################################

    async def check_queue(self):
        try:
            print( self.name,"call check_queue" )
            while True:
                try:
                    recv = await self.Q_unit.get()

                except Exception as e:
                    print( self.name,"error check_queue\n",e )
                    continue

                try:
                    self.loop.create_task( self.logic( recv ) )

                except Exception as e:
                    print( self.name,"error recv2logic\n",e )
                    continue

        except Exception as e:
            print( self.name,"error check_queue\n",e )

        finally:
            print( self.name,"return check_queue" )
            return

    ##################################################################

    async def logic(self, recv):
        try:

            try:
                msg = protocol_10000.decoding( recv )

            except Exception as e:
                print( self.name,"error logic\n",e )
                return

            protocol = msg["protocol"]
            perpose = msg["perpose"]
            data = msg["data"]
            sender = msg["sender"]
            
            if protocol == 10000:   # protocol HeavensAngelbot
                if sender == "rcs":
                    if perpose == "request":
                        if data[1] == "mobot":
                            await self.part["mobot"].handle_send( data[2] )

                        elif data[1] == "cobot":
                            await self.part["cobot"].handle_send( 
                                data[2]["functioncode"],
                                data[2]["rgAddr"],
                                data[2]["rgCount"],
                                data[2]["value"]    # tuple or list
                             )

                        elif data == "disconnect":
                            pass

                        

                    elif perpose == "response":
                        pass
                        

                    else:
                        pass
                   
                else:   #sender == part or None
                    pass
            else:
                print( self.name,"take msg = unknown protocol" )
                
        except Exception as e:
            print( self.name,"error logic\n",e )

        finally:
            return
        
    ##################################################################


if __name__=="__main__":
    print( "unit 프로그램이 시작" )
    unit = Unit("unit_219")
    unit.run()
    print( "unit 프로그램이 종료" )
