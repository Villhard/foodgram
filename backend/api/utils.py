from string import ascii_letters


class Base52:
    SYMBOLS = ascii_letters

    @staticmethod
    def to_base52(num):
        num = int(num)
        if num == 0:
            return Base52.SYMBOLS[0]
        base52 = []
        while num:
            num, remainder = divmod(num, 52)
            base52.append(Base52.SYMBOLS[remainder])
        return ''.join(reversed(base52))

    @staticmethod
    def from_base52(base52):
        num = 0
        for char in base52:
            num = num * 52 + Base52.SYMBOLS.index(char)
        return num
