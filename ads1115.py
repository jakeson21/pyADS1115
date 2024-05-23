#!/usr/bin/env python3

import time
import smbus2 as smbus
from enum import IntEnum 

ADS1115_ADDR = 0x48

class REG(IntEnum ):
    CONVERSION  = 0x00
    CONFIG      = 0x01

# class CFG(IntEnum ):
OS_MASK         = 1 << 15
OS_SING_CONV    = 1 << 15

MUX_MASK        = 0b111 << 12
MUX_DE_01       = 0 << 12
MUX_DE_03       = 1 << 12
MUX_DE_13       = 2 << 12
MUX_DE_23       = 3 << 12
MUX_SE_0        = 4 << 12
MUX_SE_1        = 5 << 12
MUX_SE_2        = 6 << 12
MUX_SE_3        = 7 << 12

PGA_MASK        = 0b111 << 9
PGA_6V144       = 0 << 9
PGA_4V096       = 1 << 9
PGA_2V048       = 2 << 9
PGA_1V024       = 3 << 9
PGA_0V512       = 4 << 9
PGA_0V256       = 5 << 9

MODE_MASK       = 1 << 8
MODE_CONT       = 0
MODE_SINGLE     = 1 << 8

DR_MASK         = 0b111 << 5
DR_8SPS         = 0 << 5
DR_16SPS        = 1 << 5
DR_32SPS        = 2 << 5
DR_64SPS        = 3 << 5
DR_128SPS       = 4 << 5
DR_250SPS       = 5 << 5
DR_475SPS       = 6 << 5
DR_860SPS       = 7 << 5

COMP_MODE_WIN   = 1 << 4
COMP_POL_AH     = 1 << 3
COMP_LAT_EN     = 1 << 2

COMP_QUE_MASK   = 0b11
COMP_QUE_1CONV  = 0
COMP_QUE_2CONV  = 1
COMP_QUE_4CONV  = 2
COMP_QUE_DISABLE  = 3


class ADS1115():
    def __init__(self, address=ADS1115_ADDR):
        self._address = address
        self._config = 0
        self.BUS = smbus.SMBus(1)
        # print("BUS", self.BUS)
        ret = self._init()
        print("Self Config = 0x{0:X} {0:016b}".format(self._config))

    def _init(self):
        self.setMux(MUX_SE_0)
        self.setPGA(PGA_2V048)
        self.setOpStatus(OS_SING_CONV)
        self.setDataRate(DR_128SPS)
        self.setCompQueue(COMP_QUE_DISABLE)
        self.writeConfig()
        return None
    
    def setOpStatus(self, status):
        if status:
            self._config = (self._config & ~OS_MASK) | (OS_MASK & OS_SING_CONV)
        else:
            self._config = (self._config & ~OS_MASK)

    def setMux(self, mux=MUX_SE_0):
        self._config = (self._config & ~MUX_MASK) | (MUX_MASK & mux)

    def setPGA(self, pga=PGA_1V024):
        self._config = (self._config & ~PGA_MASK) | (PGA_MASK & pga)

    def setMode(self, mode=MODE_CONT):
        self._config = (self._config & ~MODE_MASK) | (MODE_MASK & mode)

    def setDataRate(self, rate):
        self._config = (self._config & ~DR_MASK) | (DR_MASK & rate)

    def setCompQueue(self, comp=COMP_QUE_DISABLE):
        self._config = (self._config & ~COMP_QUE_MASK) | (COMP_QUE_MASK & COMP_QUE_DISABLE)
    
    def startSingleConversion(self):
        self._config = (self._config & ~MODE_MASK) | (MODE_MASK & MODE_SINGLE)
        self.setMode(OS_SING_CONV)
        self.writeConfig()
    
    def startContinuousConversion(self):
        self._config = (self._config & ~MODE_MASK) | (MODE_MASK & MODE_CONT)
        self.writeConfig()

    def readConversion(self):
        return self._read_word(int(REG.CONVERSION))

    def readConfig(self):
        return self._read_word(int(REG.CONFIG))
    
    def writeConfig(self):
        print("writing config")
        self._write_word(int(REG.CONFIG), self._config)
    
    def _write_byte(self, reg, data):
        self.BUS.write_byte_data(self._address, reg, data)

    def _write_word(self, reg, data):
        # byte swap so MSB goes first
        val = ((data & 0xFF00) >> 8) | ((data & 0xFF) << 8)
        self.BUS.write_word_data(self._address, reg, val)

    def _read_byte(self, reg):
        val =  self.BUS.read_byte_data(self._address, reg)
        return val

    def _read_word(self, reg):
        data = self.BUS.read_word_data(self._address, reg)
        val = ((data & 0xFF00) >> 8) | ((data & 0xFF) << 8)
        return val

    
if __name__ == '__main__':
    myDev = ADS1115()
    print("Read Config = 0x{0:X} {0:016b}".format(myDev.readConfig()))

    myDev.setMux(MUX_SE_0)
    myDev.writeConfig()

    myDev.startSingleConversion()
    print("conversion", myDev.readConversion())

    count = 0
    myDev.setDataRate(DR_250SPS)
    myDev.startContinuousConversion()
    while count<1000:
        time.sleep(1/250.0)
        print("conversion", count, myDev.readConversion())
        count += 1

    count = 0
    myDev.setMux(MUX_SE_0)
    while True:
        myDev.startSingleConversion()
        time.sleep(1/250.0)
        print("conversion", count, myDev.readConversion())
        
        if count == 0:
            myDev.setMux(MUX_SE_1)
            # myDev.writeConfig()
            count = 1
        elif count == 1:
            myDev.setMux(MUX_SE_2)
            # myDev.writeConfig()
            count = 2
        elif count == 2:
            myDev.setMux(MUX_SE_3)
            # myDev.writeConfig()
            count = 3
        elif count == 3:
            myDev.setMux(MUX_SE_0)
            # myDev.writeConfig()
            count = 0