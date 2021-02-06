""" Socketcan

    An abstraction to socketcan interface using python objects
    @author: Patrick Menschel (menschel.p@posteo.de)
    @license: GPL v3 
"""

import socket
import struct

from enum import IntEnum
from typing import Iterable


import logging
logger = logging.getLogger("socketcan")



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
    SETTIMER =     0x01
    STARTTIMER =   0x02
    RX_FILTER_ID = 0x20

class CanFlags(IntEnum):
    CAN_ERR_FLAG = 0x20000000
    CAN_RTR_FLAG = 0x40000000
    CAN_EFF_FLAG = 0x80000000


def float_to_timeval(val):
    """ helper to split time value """
    sec = int(val)
    usec = int((val-sec)*1000000)
    return sec,usec


def timeval_to_float(sec,usec):
    """ helper to merge time values """
    return sec+(usec/1000000)


class CanFrame:
    """ A CAN frame or message, low level calls it frame, high level calls it a message
    
        @param can_id: the can bus id of the frame, integer in range 0-0x1FFFFFFF
        @param data: the data bytes of the frame
        @param flags: the flags, the 3 top bits in the MSB of the can_id
    """

    FORMAT = "IB3x8s"
    
    def __init__(self,
                 can_id: int,
                 data: bytes,
                 flags: int = 0,
                 ):

        logger.info("CanFrame creation with {0:08X} {1:08X} {2}".format(can_id,flags,data.hex()))
        self.can_id = can_id
        self.flags = flags
        if (can_id > 0x7FF) and not (CanFlags.CAN_EFF_FLAG & self.flags):
            #convenience function but at least log this mangling
            logger.debug("adding CAN_EFF_FLAG for extended can_id {0:08X}".format(can_id))
            self.flags = self.flags | CanFlags.CAN_EFF_FLAG
        self.data = data
        
    def to_bytes(self):
        """ return the byte representation of the can frame that socketcan expects """
        data = self.data
        data.ljust(8)
        return struct.pack(self.FORMAT, (self.can_id | self.flags), len(self.data), data)
    
    def __eq__(self, other):
        """ standard equality operation """
        return all((self.can_id == other.can_id,
                   self.flags == other.flags,
                   self.data == other.data
                   ))
    
    def __ne__(self, other):
        """ standard non equality operation """
        return not self.__eq__(other)
        
    
        

    @classmethod
    def from_bytes(cls,byte_repr):
        """ factory to create instance from bytes representation """
        can_id_w_flags, data_length, data = struct.unpack(cls.FORMAT,byte_repr)
        flags = (can_id_w_flags & 0xE0000000)
        can_id = (can_id_w_flags & 0x1FFFFFFF)
        logger.debug("extracted flags {0:08X}".format(flags))
        return CanFrame(can_id=can_id,
                        flags = flags,
                        data=data[:data_length])

    @classmethod
    def get_size(cls):
        """ size getter """
        return struct.calcsize(cls.FORMAT)


# TODO: make tests for BcmMsg as well
class BcmMsg:
    """ Abstract the message to BCM socket
    
        The params have been reordered for convenience
        @param opcode:
        @param flags:
        @param can_id: of can message
        @param frames: an iterable of CanFrames
        @param ival2: the interval between new repetition of frames
        @param count: of repetition
        @param ival1: the interval between each CanFrame in frames  
    """
    
    # this is a great hack, we force alignment to 8 byte boundary
    # by adding a zero length long long 
    FORMAT = "IIIllllII0q"  
    
    def __init__(self,
                 opcode: int,
                 flags: int,
                 can_id: int,
                 frames: Iterable[CanFrame],
                 ival2:  float,
                 count: int = 1,
                 ival1:  float = 0,
                 ):
        
        
        self.opcode = opcode
        self.flags = flags
        self.count = count
        self.ival1 = ival1
        self.ival2 = ival2
        self.can_id = can_id
        self.frames = frames

        
    def to_bytes(self):
        """ return the byte representation of the bcm message that socketcan expects """
        ival1_sec,ival1_usec = float_to_timeval(self.ival1)
        ival2_sec,ival2_usec = float_to_timeval(self.ival2)
        byte_repr = bytearray()
        byte_repr.extend(struct.pack(self.FORMAT, self.opcode, self.flags, 
                                     self.count, ival1_sec, ival1_usec,
                                     ival2_sec, ival2_usec, self.can_id,
                                     len(self.frames)))
        for frame in self.frames:
            byte_repr.extend(frame.to_bytes())
        
        return byte_repr
    
    def __eq__(self, other):
        """ standard equality operation """
        return all((self.opcode == other.opcode,
                   self.flags == other.flags,
                   self.count == other.count,
                   self.ival1 == other.ival1,
                   self.ival2 == other.ival2,
                   self.can_id == other.can_id,
                   self.frames == other.frames,
                   ))
    
    def __ne__(self, other):
        """ standard non equality operation """
        return not self.__eq__(other)

    @classmethod    
    def from_bytes(cls,byte_repr: bytes):
        """ factory to create instance from bytes representation """
        opcode, flags, count, ival1_sec, ival1_usec, ival2_sec, ival2_usec, \
        can_id, nframes = struct.unpack(cls.FORMAT,byte_repr[:cls.get_size()])
        ival1 = timeval_to_float(ival1_sec, ival1_usec)
        ival2 = timeval_to_float(ival2_sec, ival2_usec)
        frames = [CanFrame.from_bytes(byte_repr[idx:idx+CanFrame.get_size()]) \
                       for idx in range(cls.get_size(),len(byte_repr),CanFrame.get_size())]
        assert len(frames) == nframes
        return BcmMsg(opcode=opcode,
                      flags=flags,
                      count=count,
                      ival1=ival1,
                      ival2=ival2,
                      can_id=can_id,
                      frames=frames,
                      )

    @classmethod
    def get_size(cls):
        """ size getter """
        return struct.calcsize(cls.FORMAT)
 

class CanRawSocket:
    """ A socket to raw CAN interface
    
        @param: interface name
    """
    
    def __init__(self,interface):
        self.s = socket.socket(socket.AF_CAN,socket.SOCK_RAW,socket.CAN_RAW)
        self.s.bind((interface,))
    
    def send(self, frame: CanFrame):
        """ send a CAN frame
        
            @param frame: a CanFrame 
        """
        return self.s.send(frame.to_bytes())
    
    def recv(self):
        """ receive a CAN frame """
        data = self.s.recv(CanFrame.get_size())
        assert len(data) == CanFrame.get_size()
        frame = CanFrame.from_bytes(data)
        return frame


# Note: untested, incomplete recv function
class CanBcmSocket:
    """ A socket to broadcast manager
    
        @param: interface name
    """
    
    def __init__(self,interface: str):
        self.s = socket.socket(socket.PF_CAN,socket.SOCK_DGRAM,socket.CAN_BCM)
        self.s.connect((interface,))
    
    def send(self, bcm_msg: BcmMsg):
        """ send a bcm message to bcm socket
        
            @param bcm: A bcm message to be sent 
        """
        return self.s.send(bcm_msg.to_bytes())
    
    def recv(self):
        """ receive a bcm message from bcm socket """
        raise NotImplementedError
        data = bytearray()
        data.extend(self.s.recv(BcmMsg.get_size()))
        # TODO: implement look ahead how many can frames are to read
        assert len(data) == BcmMsg.get_size()
        bcm_msg = BcmMsg.from_bytes(data)
        return bcm_msg
    
    def setup_cyclic_transmit(self,
                              frame: CanFrame,
                              interval: int):
        """ convenience function to abstract the socket interface
        
            @param frame: A CAN frame to be sent
            @param interval: the interval it should be sent  
        """
        bcm = BcmMsg(opcode=BcmOpCodes.TX_SETUP,
             flags=(BCMFlags.SETTIMER | BCMFlags.STARTTIMER),
             can_id=frame.can_id,
             frames = [frame,],
             ival1=0,
             ival2=interval,
             )
        return self.send(bcm)


class CanIsoTpSocket:
    """ A socket to IsoTp
    
        @param interface: name
        @param rx_addr: the can_id that is received
        @param tx_addr: the can_id that is transmitted 
    """
    def __init__(self,
                 interface: str,
                 rx_addr: int,
                 tx_addr: int):
        self.s = socket.socket(socket.AF_CAN,socket.SOCK_DGRAM,socket.CAN_ISOTP)
        self.s.bind((interface, rx_addr, tx_addr))
    
    def send(self, data: bytes):
        """ wrapper for send """
        return self.s.send(data)
    
    def recv(self, bufsize: int):
        """ wrapper for receive """
        return self.s.recv(bufsize)

