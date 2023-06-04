import struct

class Modbus:
    """
    made by Hoa Choi of RobotCampus
        header              # 8byte #
            tr              2byte   1++
            pr              2byte   0
            bytelength      2byte   read:6 | write:6 + 1 + rgCount*2
            unitId          1byte   1
            functionCode    1byte   1~16

        read
            rgAddr          2byte   
            rgCount         2byte   valueCount*2
        write
            bytelength      1byte   valueCount*2
            value           2byte   

        0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 
        [ tranId ]  [ protoI ]  [ bytlen ] [ I ] [ C ] [ srgAddr ] [ rgCount ] [ l ]
    """
    
    port = 502
    tr = 0

    @classmethod
    def encoding( cls, functionCode, rgAddr, rgCount=1, value=() ):
        # tr 증가
        if cls.tr < 4294967295:
            cls.tr += 1
        else:
            cls.tr = 0

        data = b""

        try:
            # fc 구분 ###########################################
            # Read Coils
            if functionCode == 1:
                return
            
            # Read Discrete Inputs
            elif functionCode == 2:
                return

            # Read Holding Registers
            elif functionCode == 3:
                data = struct.pack( ">HHHBBHH", cls.tr, 0, 6, 1, functionCode, rgAddr, rgCount )
            
            # Read Input Registers
            elif functionCode == 4:
                data = struct.pack( ">HHHBBHH", cls.tr, 0, 6, 1, functionCode, rgAddr, rgCount )
            
            # Write Single Coil
            elif functionCode == 5:
                return

            # Write Single Register
            elif functionCode == 6:
                return

            # Write Multiple Coils
            elif functionCode == 15:
                return

            # Write Multiple Registers
            elif functionCode == 16:
                data = struct.pack( ">HHHBBHHB", cls.tr, 0, 6+1+rgCount*2, 1, functionCode, rgAddr, rgCount, rgCount*2 )
                if rgCount > 2:
                    for f in value:
                        data += struct.pack( ">f", f )
                else:
                    data += struct.pack( ">h", value[0] )

        except Exception as e:
            print(f"######## {cls.__name__} encoding error ########\n{e}\n################")
        finally:
            return data

    @classmethod
    def decoding( cls, recv ):
        data = []
        try:
            if recv[8] > 2: # 2개보다 큰 레지스터 즉, 값을 1개이상 읽을 경우
                for i in range( 0, recv[8], 4 ):
                    data.append( struct.unpack( ">f", recv[9:][i:i+4] )[0] )
            else:
                for i in range( 0, recv[8], 2 ):
                    data.append( struct.unpack( ">h", recv[9:][i:i+2] )[0] )
        except Exception as e:
            print(f"######## {cls.__name__} decoding error ########\n{e}\n################")
        finally:
            return data
            


if __name__=="__main__":
    import asyncio
    async def main():
        try:
            reader, writer = await asyncio.open_connection("127.0.0.1",502)
        except:
            print("접속 오류")
        

        
        writer.write( Modbus.encoding( 16,9001,12,(111.25, 6.25, 6.25, 6.25, 6.25, 6.25) ) )
        await writer.drain()
        recv = await reader.read(1024)

        writer.write( Modbus.encoding( 3,9001,12 ) )
        await writer.drain()
        recv = await reader.read(1024)
        print( Modbus.decoding(recv) )

        ############################################################################

        writer.write( Modbus.encoding( 16,9015,1,(625,) ) )
        await writer.drain()
        recv = await reader.read(1024)

        writer.write( Modbus.encoding( 3,9015,1 ) )
        await writer.drain()
        recv = await reader.read(1024)
        print( Modbus.decoding(recv) )


    asyncio.run( main() )
    print("프로그램 종료")