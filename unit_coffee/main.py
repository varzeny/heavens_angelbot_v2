
import sys
import asyncio
import websockets
import json
from datetime import datetime # datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" )

from indy_utils import indydcp_client as client


##################################################################
class Unit:
    def __init__(self, name="unit_coffee", addr_rcs=("192.168.212.193",8000)):
        # early set
        self.name = name
        self.Q_unit = asyncio.Queue()

        # late set
        self.loop = None
        self.rcs = {
            "addr":addr_rcs,
            "websocket":None
        }
        self.coffee = None


    def run(self):
        try:
            print( self.name,"call run" )
            # init
            self.coffee = client.IndyDCPClient(
                "192.168.215.123",
                "NRMK-Indy7"
            )
            self.coffee.connect()
            self.loop = asyncio.get_event_loop()
            self.loop.create_task( self.main() )
            self.loop.run_forever()

        except Exception as e:
            print( self.name,"error run\n",e )

        finally:
            print( self.name,"return run" )
        
    ##################################################################

    async def main(self):
        print( self.name,"----------------call main" )

        try:
            # init #############################################################
            pass
            ####################################################################
                 
        except Exception as e:
            print( self.name,"--------error main\n",e )


        # connect rcs #
        while True:
            try:
                await asyncio.sleep(2)

                print( self.name,"----------------connecting RCS",self.rcs["addr"] )
                self.rcs["websocket"] = await websockets.connect(

                    f"ws://{self.rcs['addr'][0]}:{self.rcs['addr'][1]}/unit_connect"
                )

                await self.rcs["websocket"].send(f"{self.name}")
                print(self.name,"----------------rcs 접속 성공")

            except Exception as e:
                print(self.name,"--------rcs접속 중 오류, 재접속 중...",e)
                continue


            try:
                print("recv start~~~~~~~!")
                async for recv in self.rcs["websocket"]:
                    # print( type(recv),"recv =",recv )
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print(recv)

                    for n in range(3):
                        try:
                            print(f"{n} try start_current_program")
                            self.coffee.start_current_program()
                            await asyncio.sleep(1)

                        except Exception as e:
                            print("error tart_current_program",e)
                            await asyncio.sleep(1)
                            continue

                    print("end!!!!!")
                        
                    self.coffee.disconnect()

                    

            except Exception as e:
                print(self.name,"--------rcs 수신대기 중 오류, 재접속 중...")
                continue

    ##################################################################

if __name__=="__main__":
    print( "unit 프로그램이 시작" )
    unit = Unit()
    unit.run()
    print( "unit 프로그램이 종료" )
