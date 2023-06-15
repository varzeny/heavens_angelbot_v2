import asyncio


import uvicorn
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles


from module.unit.angelbot import Manager as angelbot


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


UNITS = {}
NETWORK = asyncio.Queue()


class Webserver:
    def __init__(self, NETWORK, UNITS) -> None:
        self.network = NETWORK
        self.units = UNITS

    @app.websocket("/unit_connect")
    async def unit_connect(websocket:WebSocket):
        try:
            await websocket.accept()

            recv = await websocket.receive_text()
            print( recv, websocket.client.host,"가 접속함" )

            UNITS[recv] = angelbot( recv, websocket.client.host, websocket )

        except Exception as e:
            print(recv,"error unit_connect 객체 생성 단계 오류")
            del UNITS[recv]

        while True:
            try:
                msg = await UNITS[recv].websocket.receive_text()
                await NETWORK.put( msg )
                print( msg )

            except Exception as e:
                print(recv,"error unit_connect 수신대기 중 오류 발생",e)
                break



    @app.get("/", response_class=HTMLResponse)
    async def showPage_landing():
        return FileResponse("page/landing.html")


    @app.get("/manageUnit", response_class=HTMLResponse)
    async def showPage_manageUnit():
        return FileResponse("page/manageUnit.html")


    @app.post("/pb_dbCreate")
    async def registeUnit(request:Request):
        data = await request.json()
        print(data)

        newUnit = Angelbot(
            type=data['type'],
            name=data['name'],
            ip=data['ip'],
            port=data['port'],
            active=False,
            status=None,
            battery=None,
            x=None,
            y=None,
            z=None
        )
        async with async_session() as session:
            session.add(newUnit)
            await session.commit()

        print("db 등록 완료")
        return {"message": "Angelbot registered successfully"}


    @app.get("/dbRead")
    async def dbRead():
        async with async_session() as session:
            result = await session.execute(select(Angelbot))
            units = result.scalars().all()
            return units




###############################################################
if __name__ == "__main__":
    server = uvicorn.run(app, host="127.0.0.1", port=8000)