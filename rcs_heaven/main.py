import asyncio
import subprocess
import json
import subprocess
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

        try:    # mysql 실행
            print("mysql 실행")
            subprocess.run(
                "sudo systemctl start mysql",
                shell=True,
                check=True
            )

        except Exception as e:
            print( "mysql 시작 오류", e )


        # server start
        try:
            await self.webserver.run()

        except Exception as e:
            print(self.name,"error uvicorn server",e)

        finally:
            self.loop.stop()

            try:    # mysql 정지
                print("mysql 정지")
                subprocess.run(
                    "sudo systemctl stop mysql",
                    shell=True,
                    check=True
                )

            except Exception as e:
                print( "mysql 정지 오류", e )
        
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
        # print("로직 시작",msg)
        # print(datetime.now())

        try:
            # print( msg )
            who = msg["who"]
            when = msg["when"]
            where = msg["where"]
            what = msg["what"]
            how = msg["how"]
            why = msg["why"]

        except Exception as e:
            print("메세지 포맷화 관련 오류",e)

        try:
            if why == "request":
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

                        # 테스크포스 #############################################
                        for work_json in works:
                            work = json.loads(work_json)
                            await asyncio.sleep(1)


                            if work["work_type"] == "cobotCmd": ####################

                                # 작업 시작 대기
                                await self.UNITS[ work["work_unit"] ].flag_idle_cobot.wait()
                                await self.UNITS[ work["work_unit"] ].flag_idle_mobot.wait()

                                # cobot에 명령 전달
                                await self.UNITS[ work["work_unit"] ].cobot_control(
                                    (16, 9101, 1, (int( f"{ work['work_cmd'] }" ),))
                                )

                                # 작업 종료 기다리기
                                await asyncio.sleep(4)
                                await self.UNITS[ work["work_unit"] ].flag_idle_cobot.wait()
                                print(self.UNITS[ work["work_unit"] ],"cobotCmd 작업 완료")


                            elif work["work_type"] == "mobotCmd": ####################

                                # 작업 시작 대기
                                await self.UNITS[ work["work_unit"] ].flag_idle_cobot.wait()
                                await self.UNITS[ work["work_unit"] ].flag_idle_mobot.wait()

                                # mobot에 명령 전달
                                await self.UNITS[ work["work_unit"] ].mobot_control(
                                    f"{work['work_cmd']}"
                                )

                                # 작업 종료 기다리기
                                await asyncio.sleep(4)
                                await self.UNITS[ work["work_unit"] ].flag_idle_mobot.wait()
                                print(self.UNITS[ work["work_unit"] ],"mobotCmd 작업 완료")


                            elif work["work_type"] == "coffeeCmd": ####################
                                print("1111111111")
                                # 작업 시작 대기
                                await self.UNITS[ work["work_unit"] ].flag_idle_coffee.wait()
                                print("2222222222222")
                                # coffee 에 명령전달
                                await self.UNITS[ work["work_unit"] ].coffee_control()
                                print("333333333333333")
                                # 작업 종료 기다리기
                                await asyncio.sleep(55)
                                await self.UNITS[ work["work_unit"] ].flag_idle_coffee.wait()
                                print(self.UNITS[ work["work_unit"] ],"coffeeCmd 작업 완료")
                            
                        ###################################################
                
                elif where == "rcs":    #why: request, who:front, where:rcs, what:work, how:메세지들 
                    if what == "work":
                        
                        for data in how:
                            act = json.loads(data)
                            # print(act)
                            if act["why"] == "direct":
                                self.UNITS[act["where"]].work.append(self.UNITS[act["where"]].work_n+1,act)

                            self.UNITS[act["where"]].work.append(act)
                            await asyncio.sleep(1)



                elif where == "unit_219":
                    if what == "move":
                        await self.UNITS[where].flag_idle.wait()
                        await self.UNITS[where].handle_send( json.dumps(msg))
                        await asyncio.sleep(2)


                elif where == "unit_coffee":
                    if what == "make":
                        if how == "coffee":
                            await self.UNITS[where].handle_send( json.dumps(msg) )

        except Exception as e:
            print( self.name,f"logic 에서 msg : {msg} 처리중에 오류",e )


        finally:
            print("로직 종료!")








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
