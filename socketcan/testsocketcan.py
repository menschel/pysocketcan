# file: testsocketcan.py
# author: (c) Menschel 2018
# description: quick and dirty tests socketcan interface via python3 sockets
#
import socket
from .socketcan_core import *


def test_can_raw():
    s = socket.socket(socket.AF_CAN,socket.SOCK_RAW,socket.CAN_RAW)
    s.bind(("vcan0",))
    
    #msg = s.recvmsg(16)
    msg = can_frame()
    buffers = memoryview(msg)
    s.recvmsg_into(buffers)
    s.sendmsg([msg[0]],)

import socket
s = socket.socket(socket.PF_CAN,socket.SOCK_DGRAM,socket.CAN_BCM)
s.connect(("vcan0",))