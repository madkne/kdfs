
import os

class minimalUitls:
    # ----------------------------------------
    @staticmethod
    def convertBytesToHumanly(sizei:int):
        units = ['K','M','G','T']
        size = f"{sizei}B"
        for unit in units:
            if sizei > 1000:
                sizei /= 1000
                size = f"{sizei:.1f}{unit}"
        
        return size
    # ----------------------------------------
    @staticmethod
    def checkIsBinaryFile(filename:str):
        """Return true if the given filename is binary."""
        fin = open(filename, 'rb')
        try:
            CHUNKSIZE = 1024
            while 1:
                chunk = fin.read(CHUNKSIZE)
                if b'\0' in chunk: # found null byte
                    return True
                if len(chunk) < CHUNKSIZE:
                    break # done
        except:
            pass
        finally:
            fin.close()

        return False
    # ----------------------------------------
    @staticmethod
    def getAllFilesList(pathi:str,is_recursion=False,just_files=False):
        files = os.listdir(pathi)
        finalFiles = []
        while len(files) > 0:
            filei = files[0]
            # get abs path
            newPath = os.path.join(pathi,filei)
            if is_recursion and os.path.isdir(newPath):
                try:
                    tmp_files = os.listdir(os.path.join(pathi,newPath))
                    for tmpi in tmp_files:
                        files.append(os.path.join(filei,tmpi))
                except:
                    pass
            # append to finalFiles list
            if (just_files and os.path.isfile(newPath)) or not just_files:
                finalFiles.append(filei)
            # remove filename from files list
            files.remove(filei)

        # print('files:',finalFiles,files)
        return finalFiles

    # ----------------------------------------
    @staticmethod
    def searchTextByRegex(text,find) -> list:
        """
            get a text and a find regex string and return founded expressions in text as list
            > tests:
            - minimalUitls.searchTextByRegex("This is 4the first of four chapters on 7the important ","%__ #the ")
            - "hello.md","%.md"
            - "hello.md","%.ms"
        """
        # init vars
        results = []
        findInd = 0
        result = ''
        i = 0
        loopCounter = 0
        lastNotAcceptIndex = -1
        # iterate text chars
        # and loopCounter < len(text)
        while i < len(text) :
            loopCounter += 1
            accept = False
            # check for current find index
            if findInd < len(find):
                # if exist next char of find
                nextch = None
                if findInd+1 < len(find): nextch = find[findInd+1]
                # print(f"({i})ch:",text[i],find[findInd],findInd,nextch,result)
                # if find char is '%'
                if find[findInd] == '%':
                    accept = True
                    if nextch is not None:
                        if nextch == text[i]:
                            findInd += 1
                        elif nextch == '_': 
                            findInd += 1
                        elif nextch == '#' and (i+1 < len(text) and text[i+1].isdigit()):
                            findInd += 1
                    
                # if find char is '_'
                elif find[findInd] == '_':
                    accept = True
                    findInd += 1
                # if find char is '#'
                elif find[findInd] == '#' and text[i].isdigit():
                    accept = True
                    findInd += 1

                # if find char is normal char
                if text[i] == find[findInd]:
                    accept = True
                    findInd += 1

            
            # if not accepted, then empty result!
            if not accept: 
                # break
                # print('not accept:',result,i,findInd,lastNotAcceptIndex,i-findInd)
                result = ''
                if lastNotAcceptIndex < i-findInd:
                    i -= findInd
                else:
                    i -= findInd-1

                lastNotAcceptIndex = i+1

                findInd = 0
            else:
                # print('accept:',text[i],result,findInd)
                result += text[i]
                if findInd == len(find):
                    results.append(result)
                    result = ''
                    findInd = 0
            
            # increase i index
            i += 1

        # append result to list,if is last char of find
        if result != '' and findInd+1 == len(find):
            results.append(result)
        # return result list
        return results


