# socketcan

A python 3 interface to socketcan

# Description

Goal of this project is to make socketcan available in python in a "pythonic" way.

Abstract from socket interface up to CAN Socket objects that can send or receive Frames.

Use python3 built-in functions and bytearrays wherever possible.

# Usage

Usage is intended to be simple. Create a socket that suits your application.

A CanRawSocket for simple operations.

A CanBcmSocket for cyclic operations.

A CanIsoTpSocket for serial communication over CAN, e.g. Car Diagnostics via UDS.

## Simple operations

Send a message on virtual can bus "vcan0".
It is usually available on every linux system today.
Set it up with
```
sudo ip link add type vcan
sudo ip link set vcan0 up
```

, then start candump in a separate shell

```
candump vcan0
```

and at last execute this python code

```
from socketcan import CanRawSocket, CanFrame

interface = "vcan0"
s = CanRawSocket(interface=interface)

can_id = 0x12345678
data = bytes(range(0,0x88,0x11))
frame1 = CanFrame(can_id=can_id, data=data)

s.send(frame1)
```

Now you should see an output in candump.

```
vcan0  12345678   [8]  00 11 22 33 44 55 66 77
```

This concludes the example.

# History

This module was created in Aug 2018 when ISOTP Socket was introduced into Python 3.7.

It was originally intended as a quick hack to test socketcan on different platforms
and it turned out to be a convenient way to test stuff on the CAN Bus.
