




import asyncio
import websockets
import json
from datetime import datetime # datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" )

from module.part.ld_90 import Manager as manager_ld_90
from module.part.tm5_700 import Manager as manager_tm5_700



##################################################################
class Unit:
    def __init__(self,name) -> None:
        # early set
        self.name = name
        self.Q_unit = asyncio.Queue()
        self.part = {
            "mobot":manager_ld_90( self.Q_unit, "mobot", ("10.10.10.10",7171) ),
            "cobot":manager_tm5_700( self.Q_unit, "cobot", ("192.168.1.11",502) )
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
            print( self.name,"call handle_recv",writer.get_extra_info("peername") )
            while True:
                try:
                    recv_b = await reader.read(1024)
                    if not recv_b:
                        break
                    recv = recv_b.decode()

                except Exception as e:
                    print( self.name,"error wait recv\n",e )
                    continue

                try:
                    if recv[:6] == b"Status":
                        msg = {
                            "who":"mobot",
                            "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
                            "where":"mobot",
                            "what":"status",
                            "how":recv,
                            "why":"update"
                        }
                    else:
                        msg = json.loads( recv )

                except Exception as e:
                    print( self.name,"error trans dic\n",e )
                    continue

                try:
                    await self.Q_unit.put( msg )

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
            who = recv["who"]
            when = recv["when"]
            where = recv["where"]
            what = recv["what"]
            how = recv["how"]
            why = recv["why"]
            
            if where == "rcs":
                if why == "request":
                    pass               

                elif why == "response":
                    pass

                elif why == "update":
                    pass
                    
                else: # None
                    pass
                
            elif where == "mobot":
                if why == "request":
                    if what == "write":
                        await self.part["mobot"].handle_send( how )               

                elif why == "response":
                    if what == "state":
                        self.part["mobot"].state = how


                elif why == "update":
                    if what == "status":
                        # Status:  BatteryVoltage:  Location:  Temperature: 
                        i = [ how.find("Status:"), how.find("StateOfCharge:"), how.find("Location"), how.find("Temperature:") ]

                        data = [ how[:i[1]], how[i[1]:i[2]], how[i[2]:i[3]], how[i[3]:] ]

                        dic = { k.strip():v.strip() for k, v in (s.split(':') for s in data) }

                        self.part["mobot"].status["status"] = dic["Status"]
                        self.part["mobot"].status["battery"] = int(float(dic["StateOfCharge"]))
                        self.part["mobot"].status["location"]["x"] = int((dic["Location"].split(' '))[0])
                        self.part["mobot"].status["location"]["y"] = int((dic["Location"].split(' '))[1])
                        self.part["mobot"].status["location"]["theta"] = int((dic["Location"].split(' '))[2])
                        self.part["mobot"].status["temperature"] = int(dic["Temperature"])
                        
                else: # None
                    pass

            elif where == "cobot":
                if why == "request":
                    if what == "write":
                        await self.part["cobot"].handle_send( how[0],how[1],how[2],how[3] )
                    elif what == "read":
                        result = await self.part["cobot"].handle_send( how[0],how[1],how[2],how[3] )
                        print(result)
                        
                    elif what == "move":
                        await self.part["cobot"].handle_send( how[0],how[1],how[2],how[3] )

                elif why == "response":
                    pass

                elif why == "update":
                    if what == "status":
                        pass
                    
                else: # where == None
                    pass


            else: # who == None
                pass
                
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
