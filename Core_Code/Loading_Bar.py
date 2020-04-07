class Loading_Bar:
    def __init__(self, item_num:int, target_num:int = 20, message:str = "loading: "):
        self.item_num = item_num
        self.target_num = target_num
        self.dot_inc = target_num/item_num
        self.message = message
        self.dots = 0
        self.bar = '█'
        self.empty = '_'

    def update(self, end:bool = False):
        if end:
            print(self.message + ": |" + self.bar * int(self.target_num) + "|")
        else:
            print(self.message + ": |" + self.bar * int(self.dots) + self.empty * (self.target_num-int(self.dots)) + "|", end = "\r")
            self.dots += self.dot_inc
