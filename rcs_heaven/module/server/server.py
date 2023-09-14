import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles


import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from unit.angelbot import Manager as Angelbot
from unit.coffeebot import Manager as Coffee
from database.mysql import Manager as db

import json
from datetime import datetime    # datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" )


class Webserver:
    def __init__(self, NETWORK, UNITS, addr):
        self.NETWORK = NETWORK
        self.UNITS = UNITS
        self.addr = addr
        self.database = db(
            "localhost",
            3306,
            "root",
            "admin",
            "rcs_heaven"
        )

        # 서버 설정
        self.app = FastAPI()
        self.app.mount("/static", StaticFiles(directory="./module/server/static"), name="static")

        # url 연결
        self.app.post("/readTable")(self.readTable)
        self.app.post("/updateData")(self.updateData)
        self.app.post("/reqWork")(self.reqWork)
        self.app.websocket("/unit_connect")(self.unit_connect)
        self.app.get("/", response_class=HTMLResponse)(self.showPage_landing)
        self.app.get("/manageUnit", response_class=HTMLResponse)(self.showPage_manageUnit)
        self.app.post("/send2unit", response_class=HTMLResponse)(self.send2unit)
        # self.app.post("/pb_dbCreate")(self.registeUnit)
        # self.app.get("/dbRead")(self.dbRead)


    async def run(self):    ###################################################
        print("mysql 연동 시작함")
        try:
            await self.database.run()

        except Exception as e:
            print("-------- error mysql run",e)


        try:
            async with self.database.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        f"CREATE TABLE IF NOT EXISTS Goal (id INT AUTO_INCREMENT PRIMARY KEY, time DATETIME DEFAULT CURRENT_TIMESTAMP, type VARCHAR(255), x INT, y INT, theta INT)"
                    )
                    await conn.commit()
            

        except Exception as e:
            print("-------- error mysql goal")


        print("서버모듈 기동함")
        try:
            server = uvicorn.Server( uvicorn.Config( self.app, self.addr[0], self.addr[1] ) )
            await server.serve()

        except Exception as e:
            print("error 서버모듈",e)

        print("서버모듈 종료됨")



    async def updateData(self): #######################################
        data = {}
        for unit in self.UNITS.values():
            data[unit.name] = unit.status

            #db에 추가
            await self.database.update_table(unit.name,unit.status)
            # await self.database.read_table(unit.name)
            # print(data)

        return json.dumps( data )
    


    async def readTable(self, request:Request): ########################
        data = await request.json()
        data = await self.database.read_table( data["name"] )
        
        return {"data":data}


    async def unit_connect(self, ws: WebSocket):    ########################
        try:
            await ws.accept()
            name = await ws.receive_text()
            addr = ws.client.host
            if name == "unit_coffee":
                self.UNITS[name] = Coffee(name, addr, ws)
                print(name,"접속함")
            else:
                self.UNITS[name] = Angelbot(name, addr, ws)
                print(name,"접속함")

            print(self.UNITS)

        except Exception as e:
            print("접속 과정 중 오류", e)


        try:
            await self.database.create_table( name )
            print( name,"을 db에 추가함" )
        
        except Exception as e:
            print( name,"을 db에 추가 실패함",e)


        while True:
            try:
                recv = await ws.receive_text()
                # print(recv)

            except WebSocketDisconnect:
                print(name,"연결이 종료됨")
                del self.UNITS[name]
                break

            except Exception as e:
                print(name,"데이터 수신중 오류",e)
                continue


            try:
                msg = json.loads( recv )
                if (msg["why"] == "update"):
                    self.UNITS[name].status = msg["how"]
                    if msg["how"][0]:
                        self.UNITS[name].flag_idle_cobot.set()
                    else:
                        self.UNITS[name].flag_idle_cobot.clear()
                    if msg["how"][1]:
                        self.UNITS[name].flag_idle_mobot.set()
                    else:
                        self.UNITS[name].flag_idle_mobot.clear()

                    # print(self.UNITS[name].status)
                    
                    continue

                await self.NETWORK.put( msg )

            except Exception as e:
                print(name,"error unit_connect",e)
                continue



    async def reqWork(self, request: Request):  ##########################
        data = await request.json()
        # print("server가","\n--------프론트에서 요청받음--------\n",data,"\n")

        msg = {
            "who":"front",
            "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
            "where":"logic",
            "what":"work",
            "how":data,
            "why":"request"
        }
        await self.NETWORK.put( msg )

        return {"data":"success"}



    async def send2unit(self, request: Request):    #######################
        print("***************")
        msg = await request.json()
        await self.UNITS["unit_219"].handle_send( json.dumps(msg) )



    async def showPage_landing(self):   ##################################
        return FileResponse("./module/server/page/landing.html")


    async def showPage_manageUnit(self):    ###############################
        return FileResponse("./module/server/page/manageUnit.html")

    # async def registeUnit(self, request: Request):
    #     data = await request.json()
    #     print(data)

    #     newUnit = Angelbot(
    #         type=data['type'],
    #         name=data['name'],
    #         ip=data['ip'],
    #         port=data['port'],
    #         active=False,
    #         status=None,
    #         battery=None,
    #         x=None,
    #         y=None,
    #         z=None
    #     )
    #     async with async_session() as session:
    #         session.add(newUnit)
    #         await session.commit()

    #     print("db 등록 완료")
    #     return {"message": "Angelbot registered successfully"}

    # async def dbRead(self):
    #     async with async_session() as session:
    #         result = await session.execute(select(Angelbot))
    #         units = result.scalars().all()
    #         return units


if __name__ == "__main__":
    network = None  # Provide your network object
    units = {}  # Provide your units object
    addr = ("127.0.0.1",8000)  # Provide your address
    server = Webserver(network, units, addr)
    server.run()
