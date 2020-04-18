
import os.path

class Config:
    _items : dict = {}
    def __init__(self,path : str):
        # print(os.path.abspath(path))
        # read config file and parse it
        with open(os.path.abspath(path),'r',encoding='utf-8') as f:
            for line in f.readlines():
                # print('line:',line)
                line = line.strip()
                # check if line is comment
                if len(line) < 1 or line[0] == '#':
                    continue
                # split and get key,value of line
                sp = line.split('=',2)
                # check if line is valid
                if len(sp) > 1:
                    self._items[sp[0].strip()] = sp[1].strip()
            
    # -----------------------------------
    def getItems(self):
        return self._items
    # -----------------------------------
    def get(self,key,default=''):
        return self._items.get(key,default)
    # -----------------------------------
    def getInteger(self,key,default=0):
        return int(self.get(key,default))
    # -----------------------------------
    def getBoolean(self,key,default=False):
        boolean : str = self.get(key,'')
        if boolean == '': return default
        if boolean.lower() == 'false' : return False
        return True
