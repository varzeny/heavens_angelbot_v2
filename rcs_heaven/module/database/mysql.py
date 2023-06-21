import asyncio
import aiomysql
from datetime import datetime    # datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" )
import json

class Manager:
    def __init__( self, host, port, user, password, schema ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.schema = schema
        self.pool = None


    async def run(self):
        self.pool = await aiomysql.create_pool(
            host = self.host,
            port = self.port,
            user = self.user,
            password = self.password,
            db = self.schema
        )
        print("db pool 만들어짐")


    async def stop(self):
        self.pool.close()
        await self.pool.wait_closed()
    

    async def create_table(self, table):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"CREATE TABLE IF NOT EXISTS {table} (id INT AUTO_INCREMENT PRIMARY KEY, time DATETIME DEFAULT CURRENT_TIMESTAMP, flag_cobot BOOLEAN, flag_mobot BOOLEAN, f_status JSON )"
                )
                await conn.commit()
        print(f"--------Table {table} created successfully")


    async def update_table(self, table, data):
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    status_str = json.dumps(data[2])  # Convert the dictionary into a JSON string
                    await cur.execute(
                        f"INSERT INTO {table} (flag_cobot, flag_mobot, f_status) VALUES (%s, %s, %s)",
                        (data[0], data[1], status_str)
                    )
                    await conn.commit()
        except Exception as e:
            print("db 갱신 오류",e)


    async def read_table(self, table):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"SELECT * FROM {table}"
                )
                result = await cur.fetchall()

        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        # for i in result:
        #     print(i)
        return result


if __name__ == "__main__":
    db = Manager( "localhost", 3306, "rcs", "27033271", "rcs_heaven" )

