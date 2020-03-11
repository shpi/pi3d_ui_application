import sys
import ctypes
import fcntl
import logging


class I2C_MSG_S(ctypes.Structure):
    _fields_ = [("addr", ctypes.c_uint16),
                ("flags", ctypes.c_uint16),
                ("len", ctypes.c_uint16),
                ("buf", ctypes.c_char_p), ]


I2C_MSG_P = ctypes.POINTER(I2C_MSG_S)


class I2C_RDWR_S(ctypes.Structure):
    _fields_ = [("i2c_msg", I2C_MSG_P),
                ("nmsgs", ctypes.c_int), ]


I2C_TIMEOUT = 0x0702
I2C_RDWR = 0x0707
I2C_SMBUS = 0x0720
I2C_M_WR = 0x00
I2C_M_RD = 0x01


class I2C:
    def __init__(self, bus=None):
        # Initialize attributes
        self.device = ""
        self.name = ""
        self.addr = None
        self._dev = None
        if bus is not None:
            self.open(bus)

    def open(self, bus):
        self.device = "i2c-%s" % bus
        self._dev = open("/dev/%s" % self.device, 'rb')
        try:
            info = open("/sys/class/i2c-dev/%s/name" % self.device)
            self.name = info.readline().strip()
        except IOError as e:
            logging.warning(e)
            self.name = ""

    def close(self):
        if self._dev is not None:
            self._dev.close()
        self.device = ""
        self.name = ""
        self.addr = None
        self._dev = None

    """def get_funcs(self): #TODO neither I2C_FUNCS nor FUNCS are defined so this will fail
        if self._dev is None:
            raise IOError("Device not open")
        funcs = ctypes.c_ulong()
        _ret = fcntl.ioctl(self._dev.fileno(), I2C_FUNCS, funcs)
        return {key: True if funcs.value & val else False
                for key, val in FUNCS.iteritems()}"""

    def set_addr(self, addr):
        self.addr = int(addr)

    def set_timeout(self, timeout):
        if self._dev is None:
            raise IOError("Device not open")
        ret = fcntl.ioctl(self._dev.fileno(), I2C_TIMEOUT, timeout)
        return ret

    def read(self, nRead, addr=None):
        if self._dev is None:
            raise IOError("Device not open")
        if addr is None:
            addr = self.addr
        if addr is None:
            raise ValueError("No slave address specified!")
        if 0 > nRead > 65535:
            raise ValueError("Number of bytes must be 0 - 65535")
        read_msg = I2C_MSG_S(addr, I2C_M_RD, nRead, None)
        read_data = ctypes.create_string_buffer(nRead)
        read_msg.buf = ctypes.cast(read_data, ctypes.c_char_p)
        rdwr = I2C_RDWR_S(ctypes.pointer(read_msg), 1)
        ret = fcntl.ioctl(self._dev.fileno(), I2C_RDWR, rdwr)
        if ret != 1:
            raise IOError("Tried to send 1 message but %d sent" % ret, ret)
        return [ord(c) for c in read_data]

    def write(self, data, addr=None):
        if self._dev is None:
            raise IOError("Device not open")
        if addr is None:
            addr = self.addr
        if addr is None:
            raise ValueError("No slave address specified!")
        if len(data) > 5:
            raise ValueError("Cannot write more than 5 bytes at a time.")
        write_msg = I2C_MSG_S(addr, I2C_M_WR, len(data), None)
        if sys.version < '3':
            write_msg.buf = "".join(chr(x & 0xFF) for x in data)
        else:
            write_msg.buf = "".join(chr(x & 0xFF) for x in data).encode("L1")
        rdwr = I2C_RDWR_S(ctypes.pointer(write_msg), 1)
        ret = fcntl.ioctl(self._dev.fileno(), I2C_RDWR, rdwr)
        if ret != 1:
            raise IOError("Tried to send 1 message but %d sent" % ret, ret)
        return ret

    def rdwr(self, data, nRead, addr=None):
        if self._dev is None:
            raise IOError("Device not open")
        if addr is None:
            addr = self.addr
        if addr is None:
            raise ValueError("No slave address specified!")
        if len(data) > 16:
            raise ValueError("Write exceeds FIFO size!")
        if 0 > nRead > 32767:
            raise ValueError("Number of bytes must be 0 - 32767")
        write_msg = I2C_MSG_S(addr, I2C_M_WR, len(data), None)
        if sys.version < '3':
            write_msg.buf = "".join(chr(x & 0xFF) for x in data)
        else:
            write_msg.buf = "".join(chr(x & 0xFF) for x in data).encode("L1")
        nRead &= 0x7FFF
        read_msg = I2C_MSG_S(addr, I2C_M_RD, nRead, None)
        read_data = ctypes.create_string_buffer(nRead)
        read_msg.buf = ctypes.cast(read_data, ctypes.c_char_p)
        msgs = (I2C_MSG_S * 2)(write_msg, read_msg)
        rdwr = I2C_RDWR_S(msgs, 2)
        ret = fcntl.ioctl(self._dev.fileno(), I2C_RDWR, rdwr)
        if ret != 2:
            raise IOError("Tried to send 2 messages but %d sent" % ret, ret)
        return [ord(c) for c in read_data]
