
import json
from libs.Config import Config


class baseCommand:
    _KDFSConfig : Config = None

    def __init__(self,commandName:str):
        pass
    # ------------------------------
    def response(self,res:dict):
        return json.dumps(res)
    # ------------------------------
    def _getConfig(self):
        # read kdfs config file
        if self._KDFSConfig is None:
            self._KDFSConfig = Config('../kdfs.conf')
        return self._KDFSConfig
    # ------------------------------
    # ------------------------------
    # ------------------------------
    # ------------------------------