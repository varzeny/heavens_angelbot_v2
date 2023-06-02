
import struct
import asyncio






async def main():
    # header #######
    tr = 1
    pr = 0
    length = 6
    unitid = 1
    fc = 4
    # query ########
    startaddr = 7001
    rgcount = 12

    msg = struct.pack(">HHHBBHH",tr,pr,length,unitid,fc,startaddr,rgcount)
    print( msg )

    ########################################################################

    reader, writer = await asyncio.open_connection("192.168.1.2",502)

    writer.write(msg)
    await writer.drain()

    recv = await reader.read(1024)
    print(recv,recv[9:])

    data = []
    if rgcount == 1:
        data.append( struct.unpack(">H",recv[9:])[0] )
        print(data)
    else:
        for i in range(0,rgcount*2,4):
            data.append( struct.unpack(">f",recv[9+i:13+i])[0] )
        print( data )


asyncio.run(main())
