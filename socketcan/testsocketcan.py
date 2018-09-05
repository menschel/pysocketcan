# file: testsocketcan.py
# author: (c) Menschel 2018
# description: quick and dirty tests socketcan interface via python3 sockets
#
import socket

from socketcan_core import * 
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
    


def test_can_fd_raw_transmit(interface="vcan0"):
    #first define the socket
    s = socket.socket(socket.AF_CAN,socket.SOCK_RAW,socket.CAN_RAW_FD_FRAMES)
    #bind it
    s.bind((interface,))
    
    msg = canfd_frame()
    
    msg.can_id = 0x12345678
    if msg.can_id > 0x7FF:
        msg.can_id |= CAN_EFF_FLAG
    data = list(range(64))
    for i,x in enumerate(data):
        msg.data[i]=x
    msg.len = len(data)
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
    head.frames[0]=msg
    
    
    s.send(head)

    time.sleep(10)
    
    head.ival2.tv_sec = 2
    head.ival2.tv_usec = 0
    head.flags = SETTIMER
    s.send(head)
    time.sleep(10)
    head.flags = 0
    head.frames[0].data[0]=0x22
    s.send(head)
    time.sleep(10)
    
    head.opcode = TX_DELETE
    s.send(head)
    s.close()
    return
    

def test_isotp_transmit(interface="vcan0",rx_addr=0x7E0,tx_addr=0x7E8):
    #first define the socket
    s = socket.socket(socket.AF_CAN,socket.SOCK_DGRAM,socket.CAN_ISOTP)
    #bind it
    s.bind((interface, rx_addr, tx_addr))
    
    data = bytes(list(range(64)))

    s.send(data)
    s.close()

#works unbelievable nice
# isotprecv -s 7e0 -d 7e8 vcan0
# 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F 20 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F 30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D 3E 3F 
    return


def test_isotp_receive(interface="vcan0",rx_addr=0x7E0,tx_addr=0x7E8):
    import threading
    worker = threading.Thread(target=lambda : test_isotp_transmit(interface=interface,rx_addr=tx_addr,tx_addr=rx_addr))
    
    
    #first define the socket
    s = socket.socket(socket.AF_CAN,socket.SOCK_DGRAM,socket.CAN_ISOTP)
    #bind it
    s.bind((interface, rx_addr, tx_addr))
    
#    data = bytes(list(range(64)))

    data = bytearray(s.recv(64))
    worker.start()
    print(data)
    s.close()
#echo 11 22 33 44 55 66 DE AD BE EF | isotpsend -s 7e0 -d 7e8 vcan0
    return

def test_can_bcm_receive(interface="vcan0"):
    import threading
    worker = threading.Thread(target=lambda : test_can_bcm_transmit(interface=interface))
    worker.start()
    s = socket.socket(socket.PF_CAN,socket.SOCK_DGRAM,socket.CAN_BCM)
    #connect instead of bind presumably because the socket is of type SOCK_DGRAM
    s.connect((interface,))
    
    
    head = bcm_msg_head()
    head.opcode = RX_SETUP
    head.flags = (SETTIMER | STARTTIMER | RX_FILTER_ID);
    head.can_id = 0x123
    head.ival1.tv_sec = 1
    head.ival1.tv_usec = 500000
    head.ival2.tv_sec = 0
    head.ival2.tv_usec = 0    
    head.nframes = 0
    s.send(head)
    
    try:
        for i in range(40):
            #head.opcode = RX_READ
            msg = s.recv(sizeof(bcm_msg_head))
            #print(s.recvmsg(sizeof(bcm_msg_head)))
            rxhead = bcm_msg_head.from_buffer_copy(msg)
            print("Loop {0} Opcode {1}".format(i,rxhead.opcode))
    except:
        print("something went wrong")
    finally:
        head.opcode = RX_DELETE
        s.send(head)
    
    worker.join(100)
    print("end")
    return
    
    
    
if __name__ == "__main__":
#     test_can_bcm_receive()
#     test_can_raw_receive()
#     test_can_raw_transmit()
#     test_can_bcm_transmit()
#     test_can_fd_raw_transmit()
#     test_isotp_transmit()
    test_isotp_receive()
