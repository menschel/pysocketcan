# file: testsocketcan.py
# author: (c) Menschel 2018
# description: quick and dirty tests socketcan interface via python3 sockets
#
import socket

from socketcan_core import can_frame,bcm_msg_head,CAN_EFF_FLAG,TX_SETUP,TX_DELETE,SETTIMER,STARTTIMER,TX_READ
import time
from ctypes import sizeof
#from array import array


def test_can_raw_receive(interface="vcan0"):
    #the basic steps to connect to a raw can socket
    #first define the socket
    s = socket.socket(socket.AF_CAN,socket.SOCK_RAW,socket.CAN_RAW)
    #bind it
    s.bind((interface,))
    
    #read a can_frame from the socket, that is 16bytes long
    msg = s.recv(sizeof(can_frame))
    #use the python3 buffer interface to directly cast the bytes to the can_frame structure
    can_msg = can_frame.from_buffer_copy(msg)
    
    #print the received can message in candump style
    print("{0} {1:X} [{2}] {3}".format(interface,can_msg.can_id,len(can_msg.data)," ".join(["{0:02X}".format(x) for x in can_msg.data])))
    s.close()
    return
    #now start this script / function
    #and open two shells and
    #type "candump vcan0" in the first
    #type "cansend vcan0 01a#11223344AABBCCDD" in the second
    #the output from python and from candump should look like this
    #vcan0  01A   [8]  11 22 33 44 AA BB CC DD
    
def test_can_raw_transmit(interface="vcan0"):
    #first define the socket
    s = socket.socket(socket.AF_CAN,socket.SOCK_RAW,socket.CAN_RAW)
    #bind it
    s.bind((interface,))
    
    msg = can_frame()
    msg.can_id = 0x12345678
    if msg.can_id > 0x7FF:
        msg.can_id |= CAN_EFF_FLAG
    data = [0,1,2,3,4,5,6,7]
    for i,x in enumerate(data):
        msg.data[i]=x
    msg.can_dlc = len(data)
    s.send(msg)
    s.close()
    return
    


def test_can_bcm_transmit(interface="vcan0"):#CHECK THIS WORKS NOW, so if it does not work tomorrow, there is something fishy
    #first define the socket
    s = socket.socket(socket.PF_CAN,socket.SOCK_DGRAM,socket.CAN_BCM)
    #connect instead of bind presumably because the socket is of type SOCK_DGRAM
    s.connect((interface,))
    
    msg = can_frame()
    msg.can_id = 0x123
    data = [0,1,2,3,4,5,6,7]
    for i,x in enumerate(data):
        msg.data[i]=x
    msg.can_dlc = len(data)
    
    head = bcm_msg_head()
    head.opcode = TX_SETUP
    head.flags = (SETTIMER | STARTTIMER);
    #print(head.flags)
#     head.count = 0
#     head.ival1.tv_sec = 0
#     head.ival1.tv_usec = 0
    head.ival2.tv_sec = 1
    head.ival2.tv_usec = 0
    head.can_id = msg.can_id
    head.nframes = 1
    head.frames=msg
    
    
    s.send(head)
    #a = bytearray(head)
    #print(len(a))
    
#     head.opcode = TX_READ
#     s.send(head)
#     
#     msg = s.recv(sizeof(bcm_msg_head)) 
#     res = bcm_msg_head.from_buffer_copy(msg)
    #print(res.opcode,res.flags)
    
    time.sleep(10)
    head.opcode = TX_DELETE
    s.send(head)
    s.close()
    return
    


# s = socket.socket(socket.PF_CAN,socket.SOCK_DGRAM,socket.CAN_BCM)
# s.connect(("vcan0",))

if __name__ == "__main__":
    #test_can_raw_receive()
    #test_can_raw_transmit()
    test_can_bcm_transmit()