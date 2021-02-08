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

Although there are high level functions for common usecases,
the following examples are necessary to understand how and why things work.

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


### Using a CanBcmSocket for sending cyclic messages.

If you have a cyclic operation like sending the same message a 100 times per second for whatever reason,
you can use a CanBcmSocket and let the kernel do that for you.

This example code sends a message every second for as long as the CanBcmSocket is open.
Since python will close it automatically at program exit, we have to delay it by a sleep(),
so you can see in your candump shell that the message repeats every second.


```
interface="vcan0"
s = CanBcmSocket(interface=interface)
        
can_id = 0x12345678
data = bytes(range(0,0x88,0x11))
frame1 = CanFrame(can_id=can_id,
                  data=data)
        
bcm = BcmMsg(opcode=BcmOpCodes.TX_SETUP,
             flags=(BCMFlags.SETTIMER | BCMFlags.STARTTIMER),
             can_id=can_id,
             frames = [frame1,],
             ival1=0,
             ival2=1,
            )
s.send(bcm)

sleep(10)
```


### Using a CanIsoTpSocket

IsoTp is technically a wrapper to create a serial connection in between two endpoints on the CAN bus.
It is one way to send messages longer than the 8 bytes of a CanFrame.
It also takes care of flow control, so it basically works like a serial port with one exception.
You can make the assumption that a recv() operation returns a complete message in contrast to a serial port,
where incomplete messages are to be expected due to async IO.

In this example we use itotprecv as communication partner for our python code. Open a shell and execute this command.

```
isotprecv -s 7e0 -d 7e8 vcan0
```
It waits until it receives something.

```
interface = "vcan0"
rx_addr = 0x7e0
tx_addr = 0x7e8
s = CanIsoTpSocket(interface=interface, rx_addr=rx_addr, tx_addr=tx_addr)
data = bytes(list(range(64)))
s.send(data)
```

Your candump shell will show a lot of messages with can_id 0x7e0 and 0x7e8, while your isotprecv shell will print what was transfered.

```
00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F 20 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F 30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D 3E 3F 
```


# Some words about this module

This module was created in Aug 2018 when ISOTP Socket was introduced into Python 3.7.

It was originally intended as a quick hack to test socketcan on different platforms
but it turned out to be a convenient way to test stuff on the CAN Bus.

In contrast to python-can, it is pure python3 and makes use of it's features while being lightweight with few and only built-in dependencies.

Python-can also has its focus on Windows while the socketcan part did not keep up with recent developments like IsoTp and SAE J1939.

Importing python-can and it's corresponding toolset cantools is heavy, it takes 4-5 seconds on a Raspberry Pi 3B+, so not feasible.
