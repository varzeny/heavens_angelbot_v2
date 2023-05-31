# db #############################################################
from sqlalchemy import Column, Integer, String, Boolean, select
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

DATABASE_URL = "mysql+asyncmy://root:admin@localhost/rcs_heaven"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

class Angelbot(Base):
    __tablename__ = "angelbot"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50))
    name = Column(String(50))
    ip = Column(String(50))
    port = Column(Integer)
    active = Column(Boolean, default=False)  # Default to False
    status = Column(String(100))
    battery = Column(Integer)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)

# fastapi #############################################################
import asyncio
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")




@app.get("/", response_class=HTMLResponse)
async def showPage_landing():
    return FileResponse("page/landing.html")


@app.get("/manageUnit", response_class=HTMLResponse)
async def showPage_manageUnit():
    return FileResponse("page/manageUnit.html")


@app.post("/pb_registering")
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


@app.get("/getUnits")
async def getUnits():
    async with async_session() as session:
        result = await session.execute(select(Angelbot))
        units = result.scalars().all()
        return units


##############################################################


##############################################################
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
