
from commands.base import baseCommand
# from getmac import get_mac_address as gma
import uuid
import os
import platform

class identifyCommand(baseCommand):
    def __init__(self):
        super().__init__('identify')
    # ------------------------------
    def response(self):
        res : dict = {
            'macaddr' : self._getMacAddress(),
            'version' : self._getConfig().getInteger('version'),
            'os'      : platform.system(),
            'arch'    : platform.machine()
        }
        return super().response(res)
    # ------------------------------
    def _getMacAddress(self):
        macaddr = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
for ele in range(0,8*6,8)][::-1])
        return macaddr
    # ------------------------------
    # ------------------------------
    # ------------------------------
