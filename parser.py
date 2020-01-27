import copy
from string import whitespace as ws
from string import digits
import functools

class Source:
    def __init__(self, string):
        self._string = string
        self._pos = 0

    def peek(self):
        return self._string[self._pos]

    def next(self):
        self._pos += 1

    def isEmpty(self):
        return self._pos >= len(self._string)

class Parser:
    def __init__(self, f):
        self.parse = f  ## function

    def __call__(self, s):
        return self.parse(s)

    def __rshift__(self, q):
        return ConcatParser(self, q)

    def __or__(self, q):
        return AlternativeParser(self, q)

    def option(self):
        return OptionParser(self)

    def many(self):
        return ManyParser(self)

    def many1(self):
        return Many1Parser(self)

    def replicate(self, count):
        return ReplicateParser(self, count)

    def try_(self):
        return TryParser(self)

class ReplicateParser(Parser):
    def __init__(self, p, count):
        self.p = p
        self.count = count

    def parse(self, s):
        rs = []
        for _ in range(self.count):
            rs.append(self.p(s))

        return "".join(rs)

class ManyParser(Parser):
    def __init__(self, p):
        self.p = p

    def parse(self, s):
        rs = []
        try:
            while (True):
                rs.append(self.p(s))
        except: pass

        return "".join(rs)

class Many1Parser(Parser):
    def __init__(self, p):
        self.p = p

    def parse(self, s):
        p = self.p >> ManyParser(self.p)

        return p.try_()(s)

class OptionParser(Parser):
    def __init__(self, p):
        self.p = p

    def parse(self, s):
        try: return self.p(s)
        except: return ""

class ConcatParser(Parser):
    def __init__(self, p, q):
        self.p = p
        self.q = q

    def parse(self, s):
        r1 = self.p(s)
        r2 = self.q(s)

        return r1 + r2

class AlternativeParser(Parser):
    def __init__(self, p, q):
        self.p = p
        self.q = q

    def parse(self, s):
        try:
            # backtrack
            return self.p.try_()(s)
        except:
            return self.q(s)

class TryParser(Parser):
    def __init__(self, p):
        self.p = p

    def parse(self, s):
        backup = copy.deepcopy(s)
        return self.p(backup)

## Error
class ParserError(Exception):
    """Error for parsing"""
    pass

## concrete parsers
def satisfy(p):
    def parse(s):
        c = s.peek()
        if (p(c)):
            s.next()
            return c
        else:
            raise ParserError(f"Parse Error: unexpected character {c} at line 1")
    return Parser(parse)

def anyChar():
    return satisfy(lambda _: True)

def alpha():
    def isalpha(c):
        return c.isalpha

    return satisfy(isalpha)

def whitespace():
    isws = lambda c: c in ws
    return satisfy(isws)

def char(ch):
    return satisfy(lambda c: c == ch)

def digit():
    return satisfy(lambda c: c in digits)

def string(st):
    char_list = map(char, list(st))

    return functools.reduce(
        lambda acc, x: acc >> x,
        char_list)

def eof():
    def parse(s):
        if (s.isEmpty()):
            return ""
        else:
            raise ParserError(f"Parse Error: unexpected EOF at line 1")

    return Parser(parse)
