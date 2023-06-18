import asyncio
import subprocess
import json
from datetime import datetime

from module.server.server import Webserver

class Rcs:
    def __init__(self, name, addr) -> None:
        self.name = name
        self.addr = addr
        self.NETWORK = asyncio.Queue()
        self.UNITS = {}
        self.task = {}
        
        # module
        self.webserver = Webserver( self.NETWORK, self.UNITS, (self.addr[0],self.addr[1]) )


    def run(self):
        print("Rcs 시작됨")
        try:
            self.loop = asyncio.get_event_loop()
            self.loop.create_task( self.main() )
            self.loop.run_forever()

        except Exception as e:
            print(self.name,"error run",e)

        print( "Rcs 종료됨" )


    async def main(self):
        # setup
        self.loop.create_task( self.checkQueue() )


        # server start
        await self.webserver.run()
        print("종료됨")


    async def checkQueue(self):
        while True:
            try:
                msg = await self.NETWORK.get()
                self.loop.create_task( self.logic( msg ) )

            except Exception as e:
                print(self.name,"error checkQueue",e)
                continue


    async def logic(self, msg):
        try:
            # print( msg )
            who = msg["who"]
            when = msg["when"]
            where = msg["where"]
            what = msg["what"]
            how = msg["how"]
            why = msg["why"]

            if where == "logic":
                if what == "work":
                    works = []
                    n = 0
                    while True:
                        try:
                            works.append( how[f"{str(n)}"] )
                            n += 1
                        except:
                            break

                    # print(works)

                    # 테스크포스 #################################
                    for work_json in works:
                        work = json.loads(work_json)

                        if work["work_type"] == "pnp":

                            # 작업 시작 대기
                            await self.UNITS[ work["unit_target"] ].flag_idle_cobot.wait()
                            await self.UNITS[ work["unit_target"] ].flag_idle_mobot.wait()


                            # 픽 이동 ############################################
                            await self.UNITS[ work["unit_target"] ].mobot_control(
                                f"goto { work['pick_where'] }"
                            )
                            await self.UNITS[ work["unit_target"] ].flag_idle_mobot.wait()


                            # 픽 ############################################
                            await self.UNITS[ work["unit_target"] ].cobot_control(
                                ( 16, 9000, 1, int( f"{ work['pick_dir'] }" ) )
                            )
                            await self.UNITS[ work["unit_target"] ].flag_idle_cobot.wait()
                            

                            # 플레이스 이동 ############################################
                            await self.UNITS[ work["unit_target"] ].mobot_control(
                                f"goto { work['place_where'] }"
                            )
                            await self.UNITS[ work["unit_target"] ].flag_idle_mobot.wait()

                            # 플레이스 ############################################
                            await self.UNITS[ work["unit_target"] ].cobot_control(
                                ( 16, 9000, 1, int( f"{ work['place_dir'] }" ) )
                            )
                            await self.UNITS[ work["unit_target"] ].flag_idle_cobot.wait()

                            print("작업 무사 종료")


                    ############################################


        except Exception as e:
            print( self.name,f"logic 에서 msg : {msg} 처리중에 오류",e )








if __name__ == "__main__":

    ip = subprocess.run(
        "nmcli device show wlo1 | grep IP4.ADDRESS",
        shell=True,
        capture_output=True,
        text=True
    ).stdout.split(" ")[-1].split("/")[0]

    print(ip)

    rcs = Rcs( "heaven", (ip,8000) )
    rcs.run()
