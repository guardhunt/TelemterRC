import evdev
import time
import struct

class appcodec():
    def __init__(self):
        self.device = evdev.InputDevice("/dev/input/event2")
        self.capabilities = self.device.capabilities(verbose=True)
        self.capaRAW = self.device.capabilities(absinfo=False)
        self.config = {}
        self.state = {}

    def build(self):
        """build state dictionary for controller"""

        #build config dictionary by code and name
        for key, value in self.capabilities.items():
            for element in value:
                    if type(element[0]) is tuple:
                        self.config[element[0][1]] = element[0][0]
                    elif type(element[0]) is list:
                        self.config[element[1]] = element[0][0]
                    elif ("SYN" in str(element[0])) or ("FF" in str(element[0])):
                        pass
                    else:
                        self.config[element[1]] = element[0]
        print(self.state)
        print("")
        print(self.config)

        #build state dictionary from raw codes
        for code in self.capaRAW[1]:
            self.state[self.config[code]] = 0

        for code in self.capaRAW[3]:
            self.state[self.config[code]] = 0

        for event in self.device.read_loop():
            if event.type == evdev.ecodes.EV_KEY or event.type == evdev.ecodes.EV_ABS:
                self.update_state(event)

    def update_state(self, event):
        self.state[self.config[event.code]] = event.value
        print(self.state)
        buttons1_state = 0
        buttons1_state = buttons1_state | self.state["BTN_A"]
        buttons1_state = buttons1_state | self.state["BTN_B"] << 1
        buttons1_state = buttons1_state | self.state["BTN_NORTH"] << 2
        buttons1_state = buttons1_state | self.state["BTN_WEST"] << 3

        buttons2_state = 0
        buttons2_state = buttons2_state | self.state["BTN_START"]
        buttons2_state = buttons2_state | self.state["BTN_MODE"] << 1
        buttons2_state = buttons2_state | self.state["BTN_SELECT"] << 2
        buttons2_state = buttons2_state | self.state["BTN_TR"] << 3
        buttons2_state = buttons2_state | self.state["BTN_TL"] << 4


        packet = struct.pack('6h2c', self.state["ABS_X"], self.state["ABS_Y"], self.state["ABS_RX"], self.state["ABS_RY"], self.state["ABS_HAT0X"], self.state["ABS_HAT0Y"], buttons1_state.to_bytes(1, byteorder="big"), buttons2_state.to_bytes(1, byteorder="big"))
        print(struct.unpack('6h2c', packet))
        return packet
