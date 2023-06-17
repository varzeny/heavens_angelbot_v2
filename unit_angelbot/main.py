




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
        self.part = {
            "mobot":manager_ld_90( self.Q_unit, "mobot", ("10.10.10.10",7171) ),
            "cobot":manager_tm5_700( self.Q_unit, "cobot", ("192.168.1.11",502) )
        }
        # late set
        self.loop = None
        self.rcs = {
            "addr":addr_rcs,
            "websocket":None
        }
        self.task = {}


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
        
    ##################################################################

    async def main(self):
        print( self.name,"----------------call main" )
        try:
            # init #
            self.task["check_queue"] = self.loop.create_task( self.check_queue() )
            self.task["listen"] = self.loop.create_task( self.listen() )
            self.task["check_status"] = self.loop.create_task( self.check_status() )

            self.part["mobot"].task["connect"] = self.loop.create_task( self.part["mobot"].connect() )
            self.part["cobot"].task["connect"] = self.loop.create_task( self.part["cobot"].connect() )
                 
        except Exception as e:
            print( self.name,"--------error main\n",e )

        # connect rcs #
        while True:
            try:
                await asyncio.sleep(2)
                print(self.rcs["addr"])
                print( self.name,"----------------connecting RCS" )
                self.rcs["websocket"] = await websockets.connect(f"ws://{self.rcs['addr'][0]}:{self.rcs['addr'][1]}/unit_connect")
                await self.rcs["websocket"].send(f"{self.name}")
                print(self.name,"----------------rcs 접속 성공")

            except Exception as e:
                print(self.name,"--------rcs접속 중 오류, 재접속 중...",e)
                continue

            try:
                async for recv in self.rcs["websocket"]:
                    print( type(recv),"recv =",recv )
                    msg = json.loads( recv.decode() )
                    await self.Q_unit.put( msg )


            except Exception as e:
                print(self.name,"--------rcs 수신대기 중 오류, 재접속 중...")
                continue
 
    ##################################################################

    async def check_status(self):

        # 접속 대기 시간
        await asyncio.sleep(5)

        while True:
            try:
                data = {
                    "who":self.name,
                    "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
                    "where":"rcs",
                    "what":"status",
                    "how":(self.part['cobot'].flag_idle.is_set(), self.part['mobot'].flag_idle.is_set(), self.part['mobot'].status),
                    "why":"update"
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
            print(self.name,"--------error websocket",e)


    ##################################################################

    # async def listen(self):
    #     print( "----------------call listen",self.name )
    #     while True:
    #         try:
    #             server = await websockets.serve(
    #                 self.handle_client,
    #                 "127.0.0.1",
    #                 9000
    #             )

    #         except Exception as e:
    #             print("--------오류 listen")

    #         finally:
    #             await server.wait_closed()


    # ##################################################################

    # async def handle_client(self, websocket, path):
    #     print(websocket.remote_address,"가 접속함")
    #     try:
    #         async for msg in websocket:
    #             print( msg )

    #         print( websocket.remote_address,"접속 끊어짐" )

    #     except Exception as e:
    #         print( "----------------error handle_client",e )
    
    ##################################################################

    async def check_queue(self):
        print( self.name,"----------------call check_queue" )

        while True:
            try:
                msg = await self.Q_unit.get()

            except Exception as e:
                print( self.name,"--------error check_queue\n",e )
                continue

            try:
                self.loop.create_task( self.logic( msg ) )

            except Exception as e:
                print( self.name,"--------error msg2logic\n",e )
                continue

    ##################################################################

    async def logic(self, msg):

        try:
            who = msg["who"]
            when = msg["when"]
            where = msg["where"]
            what = msg["what"]
            how = msg["how"]
            why = msg["why"]
            
            if where == "unit":
                if why == "request":
                    if what == "connect":
                        pass

                elif why == "response":
                    pass

                elif why == "update":
                    pass
                    
            elif where == "mobot":
                if why == "request":
                    if what == "write":
                        await self.part["mobot"].handle_send( how )

            elif where == "cobot":
                if why == "request":
                    if what == "write":
                        await self.part["cobot"].handle_send( how[0],how[1],how[2],how[3] )
                    elif what == "read":
                        result = await self.part["cobot"].handle_send( how[0],how[1],how[2], how[3] )
                        if who == "rcs":
                            print(result,"를 rcs로 전송")
                        elif who == "unit":
                            print(result,"를 unit이 사용")

                elif why == "response":
                    pass

                elif why == "update":
                    if what == "status":
                        pass
                            
        except Exception as e:
            print( self.name,"error logic\n",e )

        finally:
            return
        
    ##################################################################


if __name__=="__main__":
    print( "unit 프로그램이 시작" )
    unit = Unit("unit_219",("127.0.0.1",8000))
    unit.run()
    print( "unit 프로그램이 종료" )
