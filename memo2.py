import json



recv = "asd:fasdfasdfsa"


try:
    msg = json.loads( recv )    # 문자열을 딕셔너리로

except:
    msg = {
        "protocol":17171,
        "perpose":None,
        "data":recv,
        "sender":None
    }
    
finally:
    print( msg )