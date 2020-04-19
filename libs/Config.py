
import os.path

class Config:
    _items : dict = {}
    _path : str = ''
    # -----------------------------------
    def __init__(self,path : str):
        # print(os.path.abspath(path))
        self._path = os.path.abspath(path)
        # read config file and parse it
        with open(self._path,'r',encoding='utf-8') as f:
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
    def getItems(self) -> dict:
        return self._items
    # -----------------------------------
    def get(self,key,default='') -> str:
        return self._items.get(key,default)
    # -----------------------------------
    def getInteger(self,key,default=0) -> int:
        # print("(debug) ",key,default,self)
        integer : str = self.get(key,'')
        if integer == '' or not integer.isdigit():
            return default
        return int(integer)
    # -----------------------------------
    def getBoolean(self,key,default=False) -> bool:
        boolean : str = self.get(key,'')
        if boolean == '': return default
        if boolean.lower() == 'false' : return False
        return True
    # -----------------------------------
    def updateItem(self,key,value:str):
        self._items[key] = value
        # write to config file
        with open(self._path,'w',encoding='utf-8') as f:
            for key,val in self._items.items():
                f.write("{} = {}\n\n".format(key,val))
