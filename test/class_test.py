# -*- coding: UTF-8 -*-

class Base():
    val = 1
    def __init__(self) -> None:
        print(self.val)

    def hello(self):
        print('hi')

class Item(Base):
    def __init__(self) -> None:
        self.val = 2
        super().__init__()
        self.hello()

if __name__ == '__main__':
    it = Item()