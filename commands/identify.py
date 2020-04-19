
from commands.base import baseCommand
from server.ServerUtils import ServerUtils

import os
import platform

class identifyCommand(baseCommand):
    def __init__(self):
        super().__init__('identify')
    # ------------------------------
    def response(self):
        res : dict = {
            'macaddr' : ServerUtils.getMacAddress(),
            'version' : self._getConfig().getInteger('version'),
            'os'      : platform.system(),
            'arch'    : platform.machine(),
            'hostname': platform.node(),
            'node_type': 'queen' if self._getConfig().getBoolean('is_queen',False) else 'node'
        }
        return super().response(res,[],True)
    # ------------------------------
    
    # ------------------------------
    # ------------------------------
    # ------------------------------
