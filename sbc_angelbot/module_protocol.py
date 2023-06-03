import struct

class Modbus:
    """
        header
            tr              2byte   1++
            pr              2byte   0
            length          2byte   query:6
            unitId          1byte   1
            functionCode    1byte   1~16
        query
            rgAddr          2byte   
            rgCount         2byte
    """
    tr = 0

    @classmethod
    def encoding( cls, functionCode, rgAddr, rgCount=1, value=None ):
        # tr 증가
        if cls.tr > 65535:
            cls.tr = 0

        try:
            # fc 구분
            if functionCode == 1:return       # Read Coils
            elif functionCode == 2:return     # Read Discrete Inputs
            elif functionCode == 3:return     # Read Holding Registers
            elif functionCode == 4:           # Read Input Registers
                return struct.pack( ">HHHBBHH", cls.tr, 0, 6, 1, functionCode, rgAddr, rgCount )
            elif functionCode == 5:return     # Write Single Coil
            elif functionCode == 6:return     # Write Single Register
            elif functionCode == 15:return    # Write Multiple Coils
            elif functionCode == 16:          # Write Multiple Registers
                pass
                # return struct.pack( ">HHHBB", cls.tr, 0, length, 1, functionCode )
        except:
            print(f"{cls.__name__} encoding error")


