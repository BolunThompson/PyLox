import scanner as s
import lparser as p
import stmt as st
from lox import run
from importlib import reload


def rp():
    global p
    p = reload(p)


def rs():
    global s
    s = reload(s)


def rst():
    global st
    st = reload(st)

