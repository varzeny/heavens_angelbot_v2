import json

class W5h1:
    '''
    made by Hoa Choi of RobotCampus

        who     when    where   what    how     why     
        sender  time    recver  data    detail  type

    '''

    port = 10000

    def __init__(self) -> None:
        pass

    @classmethod
    def encoding( cls, data ):
        try:
            msg = json.dumps( data )

        except:
            msg = json.dumps( {
                "who":None,
                "when":None,
                "where":None,
                "what":None,
                "how":None,
                "why":None
            } )
            
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

