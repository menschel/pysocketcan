# file: test_socketcan.py
# author: (c) Menschel 2021
# description: tests for socketcan.py

from socketcan import CanFrame,CanFlags,BCMFlags,BcmMsg,BcmOpCodes

def test_can_frame_creation_with_short_id():
    can_id = 0x123
    data = bytes(range(0,0x88,0x11))
    frame1 = CanFrame(can_id=can_id,
                         data=data)
    flags = frame1.flags
    assert not (flags & CanFlags.CAN_EFF_FLAG)
    assert not (flags & CanFlags.CAN_RTR_FLAG)
    assert not (flags & CanFlags.CAN_ERR_FLAG)
    frame_as_bytes = frame1.to_bytes()
    
    assert len(frame_as_bytes) == CanFrame.get_size()
    
    frame2 = CanFrame.from_bytes(frame_as_bytes)
    assert frame1 == frame2
    
def test_can_frame_creation_with_short_id_and_short_data():
    can_id = 0x123
    data = bytes(range(0,0x44,0x11))
    frame1 = CanFrame(can_id=can_id,
                         data=data)
    flags = frame1.flags
    assert not (flags & CanFlags.CAN_EFF_FLAG)
    assert not (flags & CanFlags.CAN_RTR_FLAG)
    assert not (flags & CanFlags.CAN_ERR_FLAG)
    frame_as_bytes = frame1.to_bytes()
    
    assert len(frame_as_bytes) == CanFrame.get_size()
    
    frame2 = CanFrame.from_bytes(frame_as_bytes)
    assert frame1 == frame2
    
def test_can_frame_creation_with_short_id_and_rtr_flag():
    can_id = 0x123
    flags = CanFlags.CAN_RTR_FLAG
    data = bytes(range(0,0x88,0x11))
    frame1 = CanFrame(can_id=can_id,
                      flags=flags,
                         data=data)
    flags = frame1.flags
    assert not (flags & CanFlags.CAN_EFF_FLAG)
    assert (flags & CanFlags.CAN_RTR_FLAG)
    assert not (flags & CanFlags.CAN_ERR_FLAG)
    frame_as_bytes = frame1.to_bytes()
    
    assert len(frame_as_bytes) == CanFrame.get_size()
    
    frame2 = CanFrame.from_bytes(frame_as_bytes)
    assert frame1 == frame2
    
def test_can_frame_creation_with_short_id_and_err_flag():
    can_id = 0x123
    flags = CanFlags.CAN_ERR_FLAG
    data = bytes(range(0,0x88,0x11))
    frame1 = CanFrame(can_id=can_id,
                      flags=flags,
                         data=data)
    flags = frame1.flags
    assert not (flags & CanFlags.CAN_EFF_FLAG)
    assert not (flags & CanFlags.CAN_RTR_FLAG)
    assert (flags & CanFlags.CAN_ERR_FLAG)
    frame_as_bytes = frame1.to_bytes()
    
    assert len(frame_as_bytes) == CanFrame.get_size()
    
    frame2 = CanFrame.from_bytes(frame_as_bytes)
    assert frame1 == frame2


def test_can_frame_creation_with_long_id_and_no_eff_flag():
    can_id = 0x12345678
    data = bytes(range(0,0x88,0x11))
    frame1 = CanFrame(can_id=can_id,
                         data=data)
    flags = frame1.flags
    assert  (flags & CanFlags.CAN_EFF_FLAG)
    assert not (flags & CanFlags.CAN_RTR_FLAG)
    assert not (flags & CanFlags.CAN_ERR_FLAG)
    frame_as_bytes = frame1.to_bytes()
    
    assert len(frame_as_bytes) == CanFrame.get_size()
    
    frame2 = CanFrame.from_bytes(frame_as_bytes)
    assert frame1 == frame2


def test_can_frame_creation_with_long_id_and_eff_flag():
    can_id = 0x12345678
    flags = CanFlags.CAN_EFF_FLAG
    data = bytes(range(0,0x88,0x11))
    frame1 = CanFrame(can_id=can_id,
                     flags=flags,
                     data=data)
    flags = frame1.flags
    assert  (flags & CanFlags.CAN_EFF_FLAG)
    assert not (flags & CanFlags.CAN_RTR_FLAG)
    assert not (flags & CanFlags.CAN_ERR_FLAG)
    frame_as_bytes = frame1.to_bytes()
    
    assert len(frame_as_bytes) == CanFrame.get_size()
    
    frame2 = CanFrame.from_bytes(frame_as_bytes)
    assert frame1 == frame2

    
def test_can_frame_creation_with_long_id_and_short_data():
    can_id = 0x12345678
    data = bytes(range(0,0x44,0x11))
    frame1 = CanFrame(can_id=can_id,
                         data=data)
    flags = frame1.flags
    assert  (flags & CanFlags.CAN_EFF_FLAG)
    assert not (flags & CanFlags.CAN_RTR_FLAG)
    assert not (flags & CanFlags.CAN_ERR_FLAG)
    frame_as_bytes = frame1.to_bytes()
    
    assert len(frame_as_bytes) == CanFrame.get_size()
    
    frame2 = CanFrame.from_bytes(frame_as_bytes)
    assert frame1 == frame2
    
    
def test_bcm_msg_creation():
    can_id = 0x123
    data = bytes(range(0,0x88,0x11))
     
    frame1 = CanFrame(can_id=can_id,
                         data=data)
    opcode = BcmOpCodes.TX_SETUP
    flags = (BCMFlags.SETTIMER | BCMFlags.STARTTIMER)
    frames = [frame1,]
    interval=0.1
    bcm1 = BcmMsg(opcode=opcode,
                 flags=flags,
                 can_id=can_id,
                 frames = frames,
                 ival2=interval,
                 )
    bcm_as_bytes = bcm1.to_bytes()
    assert len(bcm_as_bytes) == BcmMsg.get_size()+(CanFrame.get_size()*len(frames))
    
    bcm2 = BcmMsg.from_bytes(bcm_as_bytes)
    assert bcm1 == bcm2

def test_bcm_msg_creation_with_2_frames():
    can_id = 0x123
    data = bytes(range(0,0x88,0x11))
     
    frame1 = CanFrame(can_id=can_id,
                         data=data)
    can_id2 = 0x456
    data2 = bytes(range(0,0x88,0x11))
    frame2 = CanFrame(can_id=can_id2,
                         data=data2)
        
    opcode = BcmOpCodes.TX_SETUP
    flags = (BCMFlags.SETTIMER | BCMFlags.STARTTIMER)
    frames = [frame1,
              frame2,
              ]
    interval=0.1
    bcm1 = BcmMsg(opcode=opcode,
                 flags=flags,
                 can_id=can_id,
                 frames = frames,
                 ival2=interval,
                 )
    bcm_as_bytes = bcm1.to_bytes()
    assert len(bcm_as_bytes) == BcmMsg.get_size()+(CanFrame.get_size()*len(frames))
    
    bcm2 = BcmMsg.from_bytes(bcm_as_bytes)
    assert bcm1 == bcm2


def test_bcm_msg_creation_with_2_extended_frames_and_different_sizes():
    can_id = 0x12345678
    data = bytes(range(0,0x88,0x11))
     
    frame1 = CanFrame(can_id=can_id,
                         data=data)
    can_id2 = 0x1FFFF456
    data2 = bytes(range(0,0x44,0x11))
    frame2 = CanFrame(can_id=can_id2,
                         data=data2)
        
    opcode = BcmOpCodes.TX_SETUP
    flags = (BCMFlags.SETTIMER | BCMFlags.STARTTIMER)
    frames = [frame1,
              frame2,
              ]
    interval=0.1
    bcm1 = BcmMsg(opcode=opcode,
                 flags=flags,
                 can_id=can_id,
                 frames = frames,
                 ival2=interval,
                 )
    bcm_as_bytes = bcm1.to_bytes()
    assert len(bcm_as_bytes) == BcmMsg.get_size()+(CanFrame.get_size()*len(frames))
    
    bcm2 = BcmMsg.from_bytes(bcm_as_bytes)
    assert bcm1 == bcm2
