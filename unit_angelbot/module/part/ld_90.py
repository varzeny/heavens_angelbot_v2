


import asyncio
from datetime import datetime # datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" )


class Manager:
    '''
    made by Hoa Choi of RobotCampus
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
        print( self.name,"----------------call connect" )

        self.task["listen_mobot"] = asyncio.get_running_loop().create_task( self.listen_mobot() )

        while True:
            try:
                self.reader, self.writer = await asyncio.open_connection(self.addr[0],self.addr[1])

                # omron arcl 접속 절차
                recv = await self.reader.read(1024);        print(recv)
                self.writer.write(b"admin\r\n")
                await self.writer.drain()

            except Exception as e:
                print(self.name,"--------error connect",e)
                continue
                
            while True:
                try:
                    recv_b = await self.reader.read(1024)
                    if not recv_b:
                        break
                    recv = recv_b.decode()
                    if recv[:6] == "Status":
                        continue
                    self.state = recv
                    
                except Exception as e:
                    print(self.name,"--------error",e)
                    continue


    async def listen_mobot(self):
        print( self.name,"----------------call listen_mobot" )
        while True:
            try:
                server_mobot = await asyncio.start_server(
                    self.handle_mobot,
                    "10.10.10.51",
                    7179
                )
                await server_mobot.serve_forever()
                break
            
            except Exception as e:
                print( self.name,"--------error listen_mobot",e )
                try:
                    server_mobot.close()
                    await server_mobot.wait_closed()

                except:
                    pass

                await asyncio.sleep(1)
                continue

    
    async def handle_mobot(self,reader,writer):
        print( self.name,"----------------call handle_mobot 7179",writer.get_extra_info("peername") )

        while True:
            try:
                recv_b = await reader.read(1024)
                if not recv_b:
                    break

            except Exception as e:
                print( self.name,"--------error wait recv",e )
                continue

            try:
                recv = recv_b.decode()

                if recv[:6] == "Status":
                    
                    # Status:  BatteryVoltage:  Location:  Temperature: 
                    i = [ recv.find("Status:"), recv.find("StateOfCharge:"), recv.find("Location"), recv.find("Temperature:") ]
                    
                    data = [ recv[:i[1]], recv[i[1]:i[2]], recv[i[2]:i[3]], recv[i[3]:] ]

                    dic = { k.strip():v.strip() for k, v  in (s.split(':')[:2] for s in data) }
                    
                    
                    self.status["status"] = dic["Status"]
                    self.status["battery"] = int(float(dic["StateOfCharge"]))
                    self.status["location"]["x"] = int((dic["Location"].split(' '))[0])
                    self.status["location"]["y"] = int((dic["Location"].split(' '))[1])
                    self.status["location"]["theta"] = int((dic["Location"].split(' '))[2])

                    self.status["temperature"] = int(dic["Temperature"])

                    ff = False
                    for s in ["Stop","Dock","Comp","Fail","Sayi","Robo"]:
                        if self.status["status"][:4] == s:
                            ff = True
                            break

                    if ff:
                        self.flag_idle.set()
                    else:
                        self.flag_idle.clear()

    

            except Exception as e:
                print( self.name,"--------error update status",e )
                continue


    async def handle_send(self,msg):
        try:
            self.flag_idle.clear()
            self.writer.write( msg.encode()+b"\r\n" )
            print("8888888888",msg)
            await self.writer.drain()

        except Exception as e:
            print( self.name,"error handle_send\n",e )


if __name__=="__main__":
    print(" mobot 이 시작됨")

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
