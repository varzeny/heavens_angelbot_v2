from datetime import datetime

print( datetime.now().strftime( "%y/%m/%d/%I/%M/%S/%f" ) )


class CCC:
    CONNECTED={}

    def __init__(self,name) -> None:
        CCC.CONNECTED[name] = self
        self.name = name
        self.n = 0

    def __del__(self):
        del CCC.CONNECTED[self.name]
        print(f"{self.name} 이 자신을 지움")
        print( CCC.CONNECTED )

    @classmethod
    def c_say(cls):
        print("클래스메소드 입니다")

    def say(self):
        print("인스턴스 메소드입니다")


if __name__=="__main__":
    a=CCC("a")
    b=CCC("b")

    a.n += 1

    print( a.n )
    print( b.n )

