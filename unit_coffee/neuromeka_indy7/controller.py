import asyncio
import struct

from pyModbusTCP.client import ModbusClient


class Controller:
    def __init__(self, addr:list):

        self.target = ModbusClient(
            host=addr[0],
            port=addr[1]
        )
        self.flag_idle = asyncio.Event()
        self.status = None



    async def run(self):
        self.flag_idle.set()
        self.target.open()
        asyncio.get_running_loop().create_task(self.updateStatus())

    async def stop(self):
        self.target.close()

    async def reg2float(self, high, low):
        # 두 개의 16비트 값을 하나의 32비트 값으로 합치기
        combined = (high << 16) | low
        # 32비트 값을 IEEE 754 형식의 float으로 변환
        result = struct.unpack('!f', struct.pack('!I', combined))[0]
        return result
    

    async def updateStatus(self):
        while True:
            try:
                result = self.target.read_holding_registers(
                    reg_addr=1700,
                    reg_nb=12
                )
                tcp = []
                for i in range(0,11,2):
                    # print(result[i],result[i+1])
                    f = await self.reg2float(result[i],result[i+1])
                    tcp.append(f)
                self.status = tcp
                # print("협동로봇 tcp 데이터\n",tcp)

            except Exception as e:
                print("협동로봇 tcp 데이터 가져오기 실패\n",e)

            finally:
                await asyncio.sleep(1)


    async def reg_write(self, regs_addr, regs_value:list):
        try:
            if self.target.is_open:
                result = self.target.write_multiple_registers(
                    regs_addr = regs_addr,
                    regs_value = regs_value,
                )
                return result
            
        except Exception as e:
            print("error reg_write\n",e)


    async def reg_read(self, reg_addr, reg_nb):
        try:
            if self.target.is_open:
                result = self.target.read_holding_registers(
                    reg_addr = reg_addr,
                    reg_nb = reg_nb
                )
                return result
            
        except Exception as e:
            print("error reg_read\n",e)


if __name__=="__main__":

    async def main():
        con = Controller(("192.168.215.124",502))
        asyncio.get_running_loop().create_task(con.run())

        n=0
        while True:
            tasks = asyncio.all_tasks()
            print(n,tasks)
            n+=1
            await asyncio.sleep(1)


    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()


