# file: socketcan_core.py
# author: (c) Menschel 2018
# description: main file containing the structures etc
#
from ctypes import Structure,c_uint8,c_uint32,c_uint64,c_long,sizeof
from enum import IntEnum
#from builtins import int
import struct

from _collections_abc import Iterable

#why this inconsistent use of long,intXX types

#from include/uapi/linux/can/can.h
# struct can_frame {
#     canid_t can_id;  /* 32 bit CAN_ID + EFF/RTR/ERR flags */
#     __u8    can_dlc; /* frame payload length in byte (0 .. CAN_MAX_DLEN) */
#     __u8    __pad;   /* padding */
#     __u8    __res0;  /* reserved / padding */
#     __u8    __res1;  /* reserved / padding */
#     __u8    data[CAN_MAX_DLEN] __attribute__((aligned(8)));
# };

class CanFlags(IntEnum):
    CAN_EFF_FLAG = 0x80000000

class can_frame(Structure):
#     _pack_ = 1
    _fields_ = [
                ('can_id',c_uint32),
                ('can_dlc',c_uint8),
                ('__pad',c_uint8),
                ('__res0',c_uint8),
                ('__res1',c_uint8),
                ('data',c_uint8 * 8),
                ]
#     def __init__(self):
#         self.can_id = 0
#         self.can_dlc = 0
#         self.__pad = 0
#         self.__res0 = 0
#         self.__res1 = 0
#         for i in range(8):
#             self.data[i] = 0
 
# struct canfd_frame {
#     canid_t can_id;  /* 32 bit CAN_ID + EFF/RTR/ERR flags */
#     __u8    len;     /* frame payload length in byte */
#     __u8    flags;   /* additional flags for CAN FD */
#     __u8    __res0;  /* reserved / padding */
#     __u8    __res1;  /* reserved / padding */
#     __u8    data[CANFD_MAX_DLEN] __attribute__((aligned(8)));
# };
CANFD_MAX_DLEN = 64
class canfd_frame(Structure):
#     _pack_ = 1
    _fields_ = [
                ('can_id',c_uint32),
                ('len',c_uint8),
                ('flags',c_uint8),
                ('__res0',c_uint8),
                ('__res1',c_uint8),
                ('data',c_uint8 * CANFD_MAX_DLEN),
                ]
    

# struct can_filter {
#     canid_t can_id;
#     canid_t can_mask;
# };

class can_filter(Structure):
#     _pack_ = 1
    _fields_ = [
                ('can_id',c_uint32),
                ('can_mask',c_uint32),
                ]
                
#from include/uapi/linux/can/bcm.h

# struct bcm_timeval {
# 	long tv_sec;
# 	long tv_usec;
# };
# class bcm_timeval(Structure):
#     _fields_ = [
#                 ('tv_sec',c_long),
#                 ('tv_usec',c_long),
#                 ]

    
class bcm_timeval(Structure):  # <-- this obviously does not work on a 32bit raspberry pi ;-P
#     _pack_ = 1
    _fields_ = [
                ('tv_sec',c_uint64),
                ('tv_usec',c_uint64),
                ]
    
#     def __init__(self):
#         self.tv_sec = 0
#         self.tv_usec = 0


# struct bcm_msg_head {
# 	__u32 opcode;
# 	__u32 flags;
# 	__u32 count;
# 	struct bcm_timeval ival1, ival2;
# 	canid_t can_id;
# 	__u32 nframes;
# 	struct can_frame frames[0];
# };

class bcm_msg_head(Structure):
#     _pack_ = 1
    _fields_ = [
                ('opcode',c_uint32),
                ('flags',c_uint32),
                ('count',c_uint32),
                ('ival1',bcm_timeval),
                ('ival2',bcm_timeval),
                ('can_id',c_uint32),
                ('nframes',c_uint32),
                #('frames',can_frame),
                ('frames',can_frame*1)#,<-- the correct way but we have problems with variable size arrays for whatever reason
                ]
    
#     def __init__(self):
#         self.opcode = 0
#         self.flags = 0
#         self.count = 0
#         self.can_id = 0
#         self.nframes = 0

def float_to_ival(x:float) -> bytes:
    num = int(x)
    frac = (x-num)*1000000
    return struct.pack("!ll",num,frac)  # <-- 2 signed long

def bcm_msg(opcode: int,
            flags: int,
            count: int,
            ival1: float,
            ival2: float,
            can_msgs: Iterable) -> bytes:
    ret = bytearray()
    ret.extend((opcode,flags,count))
    ret.extend(float_to_ival())
    

class BcmOpCodes(IntEnum):
    TX_SETUP = 1
    TX_DELETE = 2
    TX_READ = 3
    RX_SETUP = 5
    RX_DELETE = 6
    RX_READ = 7
    RX_STATUS = 10
    RX_TIMEOUT = 11
    RX_CHANGED = 12

class BCMFlags(IntEnum):
    SETTIMER = 0x0001
    STARTTIMER = 0x0002
    RX_FILTER_ID = 0x0020

