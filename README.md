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

## Examples

To prepare our examples, we need to set up a virtual can bus interface "vcan0".
It is usually available on every linux system today.

```
sudo ip link add type vcan
sudo ip link set vcan0 up
```

It can be removed again by these steps but it will be gone after reboot anyways, so don't care.

```
sudo ip link set vcan0 down
sudo ip link delete vcan0

```

To watch what is happening on vcan0, open a separate shell and execute this command.

```
candump vcan0
```


### Send a CanFrame

The most simple way to send a single CanFrame is to use CanRawSocket.
It has no logic behind it, it just sends and receives CanFrames on a given interface.

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

### Receive a CanFrame

First open yet another shell and execute this command to generate can traffic.

```
cangen vcan0
```

You can watch the generated frames in your candump shell.

The following code mimics what candump is doing for a count of 10 CanFrames.

```
from socketcan import CanRawSocket, CanFrame

interface = "vcan0"
s = CanRawSocket(interface=interface)

for idx in range(10):
    frame = s.recv()
    print("vcan0  {0:8X}   [{1}]  {2}".format(frame.can_id,
                                              len(frame.data),
                                              " ".join(["{0:02X}".format(b) for b in frame.data ])
                                              )
          )
```

You can stop the cangen shell now with Ctrl+C.

### Using a CanIsoTpSocket

IsoTp is technically a wrapper to create a serial connection in between two endpoints on the CAN bus.
It is one way to send messages longer than the 8 bytes of a CanFrame.
It also takes care of flow control, so that you basically have a serial port.
You can also make the assumption that a recv() operation returns a complete message in contrast to a serial port.

TODO: Example for CanIsoTpSocket should be here.

# History

This module was created in Aug 2018 when ISOTP Socket was introduced into Python 3.7.

It was originally intended as a quick hack to test socketcan on different platforms
and it turned out to be a convenient way to test stuff on the CAN Bus.
