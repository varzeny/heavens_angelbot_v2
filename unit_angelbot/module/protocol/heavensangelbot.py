import json

class HeavensAngelBot:
    '''
    made by Hoa Choi of RobotCampus
    '''

    port = 10000

    def __init__(self) -> None:
        pass

    @classmethod
    def encoding( cls, perpose=None, data=None, sender=None ):
        try:
            msg = json.dumps(
                {
                    "protocol":cls.port,
                    "perpose":perpose,
                    "data":data,
                    "sender":sender
                }
            )

        except:
            msg = "fail encoding"
            
        finally:
            return msg


    @classmethod
    def decoding( cls, recv ):
        try:
            msg = json.loads( recv )    # 문자열을 딕셔너리로

        except:
            msg = {
                "protocol":cls.port,
                "perpose":None,
                "data":recv,
                "sender":None
            }
            
        finally:
            return msg
        
    
    @classmethod
    def form( cls, recv ):
        pass