



import sys
import asyncio
import websockets
import json
from datetime import datetime # datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" )

from module.part.ld_90 import Manager as manager_ld_90
from module.part.tm5_700 import Manager as manager_tm5_700



##################################################################
class Unit:
    def __init__(self, name, addr_rcs) -> None:
        # early set
        self.name = name
        self.Q_unit = asyncio.Queue()
        self.flag_work = asyncio.Event(); self.flag_work.set()
        self.flag_idle = asyncio.Event(); self.flag_idle.set(); self.flag_idle_on=True
        self.part = {
            "mobot":manager_ld_90( self.Q_unit, "mobot", ("10.10.10.10",7171) ),
            "cobot":manager_tm5_700( self.Q_unit, "cobot", ("192.168.1.11",502) )
        }
        # late set
        self.loop = asyncio.get_event_loop()
        self.rcs = {
            "addr":addr_rcs,
            "websocket":None
        }
        self.task = {}
        self.status = {
            "flag_idle":self.flag_idle.is_set(),
            "location":{
                "x":0,
                "y":0,
                "z":0
            },
            "parts":{
                "mobot":self.part["mobot"].status,
                "cobot":self.part["cobot"].status
            }
        }


    def run(self):
        try:
            print( self.name,"call run" )
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
            self.part["mobot"].task["connect"] = self.loop.create_task( self.part["mobot"].connect() )
            self.part["cobot"].task["connect"] = self.loop.create_task( self.part["cobot"].connect() )

            # self.task["listen"] = self.loop.create_task( self.listen() )
            self.task["check_queue"] = self.loop.create_task( self.check_queue() )
            self.task["check_status"] = self.loop.create_task( self.check_status() )

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
                async for recv in self.rcs["websocket"]:
                    # print( type(recv),"recv =",recv )

                    msg = json.loads( recv )
                    await self.Q_unit.put( msg )


            except Exception as e:
                print(self.name,"--------rcs 수신대기 중 오류, 재접속 중...")
                continue
 
    ##################################################################

    async def check_status(self):

        # 접속 대기 시간
        await asyncio.sleep(5)
        print("--------status update start--------")

        while True:
            print()
            print("유닛 플래그",self.flag_idle.is_set())
            print()
            try:
                if (self.part["mobot"].flag_idle.is_set()) and (self.part["cobot"].flag_idle.is_set()):
                    self.flag_idle.set()
                else:
                    self.flag_idle.clear()
                
                self.status["flag_idle"] = self.flag_idle.is_set()
                self.status["location"] = self.status["parts"]["mobot"]["location"]

            except Exception as e:
                print(self.name,"check_status_updateFlag error\n",e)
                await asyncio.sleep(1)
                continue

            try:
                data = {
                    "why":"update",
                    "who":self.name,
                    "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
                    "where":"rcs",
                    "what":"status",
                    "how":self.status
                }
 
                msg = json.dumps( data )
                await self.handle_send( msg )

            except Exception as e:
                print(self.name,"error check_status",e)
                continue

            finally:
                await asyncio.sleep(1)


    ##################################################################

    async def handle_send(self, msg):
        try:
            await self.rcs["websocket"].send( msg )

        except Exception as e:
            print(self.name,"--------error handle_send websocket",e)


    ##################################################################

    async def check_queue(self):
        print( self.name,"----------------call check_queue" )

        while True:
            try:
                msg = await self.Q_unit.get()
                print(msg)
                if msg["what"] == "move":
                    await self.part["mobot"].handle_send( msg["how"] )

                elif msg["what"] == "pnp":
                    await self.part["cobot"].handle_send( 16, 9101, 1, (int(msg["how"]),) )

            except Exception as e:
                print( self.name,"--------error check_queue\n",e )
                continue

            # try:
            #     self.loop.create_task( self.logic( msg ) )

            # except Exception as e:
            #     print( self.name,"--------error msg2logic\n",e )
            #     continue

    ##################################################################




    # async def logic(self, msg):

    #     try:
    #         who = msg["who"]
    #         when = msg["when"]
    #         where = msg["where"]
    #         what = msg["what"]
    #         how = msg["how"]
    #         why = msg["why"]
            
    #         if why == "request":
    #             if what == "move":
    #                 await self.part["mobot"].flag_idle.wait()
    #                 self.flag_idle.clear()
    #                 await self.part["mobot"].handle_send(how)
    #                 await asyncio.sleep(2)
    #                 await self.part["mobot"].flag_idle.wait()
    #                 self.flag_idle.set()

    #             elif what == "pnp":
    #                 await self.part["cobot"].flag_idle.wait()
    #                 self.flag_idle.clear()
    #                 await self.part["cobot"].handle_send(how)
    #                 await asyncio.sleep(2)
    #                 await self.part["cobot"].flag_idle.wait()
    #                 self.flag_idle.set()
                    
    #         elif where == "mobot":
    #             if why == "request":
    #                 if what == "write":
    #                     await self.part["mobot"].handle_send( how )
    #                     print(
    #                         "--------mobot에 전달 됨--------\n",
    #                         how,
    #                         "\n-----------------------------"
    #                     )

    #         elif where == "cobot":
    #             if why == "request":
    #                 if what == "write":
    #                     await self.part["cobot"].handle_send( how[0],how[1],how[2],how[3] )
    #                     print(
    #                         "--------cobot에 전달 됨--------\n",
    #                         how,
    #                         "\n-----------------------------"
    #                     )
                            
    #     except Exception as e:
    #         print( self.name,"error logic\n",e )

    #     finally:
    #         return
        
    ##################################################################


if __name__=="__main__":
    print( "unit 프로그램이 시작" )
    unit = Unit( sys.argv[1], ( sys.argv[2], sys.argv[3] ) )
    unit.run()
    print( "unit 프로그램이 종료" )
