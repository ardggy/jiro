import pytest
import parser

def test_任意文字パース():
    s = parser.Source("あいうえお")
    p1 = parser.anyChar()
    p2 = parser.anyChar()

    assert p1(s) == "あ"
    assert p2(s) == "い"

def test_指定文字パース():
    s = parser.Source("123")

    p1 = parser.char("1")
    p2 = parser.char("2")

    assert p1(s) == "1"
    assert p2(s) == "2"

def test_連結パーサ():
    s = parser.Source("1234")

    p1 = parser.char("1")
    p2 = parser.char("2")

    assert (p1 >> p2)(s) == "12"

def test_回数繰り返しパーサ():
    s = parser.Source("abcd")

    p = parser.alpha().replicate(3)

    assert p(s) == "abc"

def test_繰り返しパーサ():
    s = parser.Source("123a")
    p1 = parser.digit().many()
    p2 = parser.alpha()

    assert (p1 >> p2)(s) == "123a"

def test_選択パーサ():
    s = parser.Source("1234")

    # try backtrack
    p1 = parser.string("13")
    p2 = parser.string("12")

    assert (p1 | p2)(s) == "12"

def test_オプションパーサ():
    s = parser.Source("あいうえお")

    p1 = parser.char("あ")
    p2 = parser.char("う").option()
    p3 = parser.char("い")
    p4 = parser.char("う").option()

    assert (p1 >> p2 >> p3 >> p4)(s) == "あいう"

def test_文字列の最後を受理するパーサ():
    s = parser.Source("あいうえお")
    p1 = parser.string("あいうえお")
    p2 = parser.eof()

    assert (p1 >> p2)(s) == "あいうえお"

def test_文字列の途中でeofは受理しない():
    s = parser.Source("あいうえお")
    p = parser.eof()

    with pytest.raises(Exception):
        result = p(s)

def test_スペース():
    import string
    s = parser.Source(string.whitespace)
    p1 = parser.whitespace().many1()

    assert p1(s) == string.whitespace

"""
Example
"""
def test_括弧の釣り合いを受理するパーサ():
    s = parser.Source("((()))")

    """
    parens ::= "(" parens? ")"
    """
    def balanced_parens():
        def parse(s):
            r1 = parser.char("(")(s)
            r2 = balanced_parens().option()(s)
            r3 = parser.char(")")(s)
            return r1 + r2 + r3

        return parser.Parser(parse)

    assert balanced_parens()(s) == "((()))"
