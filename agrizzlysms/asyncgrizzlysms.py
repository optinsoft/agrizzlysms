import aiohttp
import ssl
import certifi
import json
from urllib.parse import urlencode

class AsyncGrizzlySmsException(Exception):
    pass

class NoSMSException(AsyncGrizzlySmsException):
    pass

class AsyncGrizzlySms:
    def __init__(self, apiKey: str, apiUrl: str = 'https://api.grizzlysms.com/stubs/handler_api.php'):
        self.apiKey = apiKey
        self.apiUrl = apiUrl

    def checkResponse(self, respList: list, successCode: str, noSmsCode: str):
        if len(successCode) > 0:
            if len(respList) > 0:            
                code = respList[0]
                if successCode.endswith('_'):
                    if not code.startswith(successCode):
                        if len(noSmsCode) > 0 and code == noSmsCode:
                            raise NoSMSException("No SMS")
                        raise AsyncGrizzlySmsException(f'Error "{code}": {":".join(respList)}')
                else:
                    if code != successCode:
                        if len(noSmsCode) > 0 and code == noSmsCode:
                            raise NoSMSException("No SMS")
                        raise AsyncGrizzlySmsException(f'Error "{code}": {":".join(respList)}')
            else:
                raise AsyncGrizzlySmsException(f"Empty response")
        return respList

    async def doListRequest(self, url: str, successCode: str = 'ACCESS_', noSmsCode: str = ''):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        conn = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=conn, raise_for_status=False) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    respText = await resp.text()
                    raise AsyncGrizzlySmsException(f"Request failed:\nStatus Code: {resp.status}\nText: {respText}")
                try:
                    respText = await resp.text()
                    respList = respText.split(':')
                except ValueError as e:
                    raise AsyncGrizzlySmsException(f"Request failed: {str(e)}")
                return self.checkResponse(respList, successCode, noSmsCode)

    async def doJsonRequest(self, url: str, successResponseCode: str = '1', noSmsCode: str = ''):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        conn = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=conn, raise_for_status=False) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    respText = await resp.text()
                    raise AsyncGrizzlySmsException(f"Request failed:\nStatus Code: {resp.status}\nText: {respText}")
                try:
                    respText = await resp.text()
                    respJson = json.loads(respText)
                except ValueError as e:
                    raise AsyncGrizzlySmsException(f"Request failed: {str(e)}")
                return respJson

    async def getNumber(self, service: str, country: str):
        url = self.apiUrl + '?' + urlencode({'action':'getNumber','service':service,'api_key':self.apiKey,'country':country})
        respList = await self.doListRequest(url, 'ACCESS_NUMBER')
        return {"response": 1, "id": respList[1], "number": respList[2]}

    async def setStatus(self, status: str, id: str):
        url = self.apiUrl + '?' + urlencode({'action':'setStatus','status':status,'id:':id,'api_key':self.apiKey})
        respList = await self.doListRequest(url)
        return {"response": 1, "text": ":".join(respList)}
    
    async def getStatus(self, id: str):
        url = self.apiUrl + '?' + urlencode({'action':'getStatus','id':id,'api_key':self.apiKey})
        respList = await self.doListRequest(url)
        return {"response": 1, "status": ":".join(respList)}
    
    async def getSMS(self, id: str):
        url = self.apiUrl + '?' + urlencode({'action':'getStatus','id':id,'api_key':self.apiKey})
        respList = await self.doListRequest(url, 'STATUS_OK', 'STATUS_WAIT_CODE')
        return {"response": 1, "sms": respList[1]}

    async def getBalance(self):
        url = self.apiUrl + '?' + urlencode({'action':'getBalance','api_key':self.apiKey})
        respList = await self.doListRequest(url)
        return {"response": 1, "amount": respList[1]}
    
    async def getPrices(self, service: str, country: str):
        url = self.apiUrl + '?' + urlencode({'action':'getPrices','service':service,'api_key':self.apiKey,'country':country})
        respJson = await self.doJsonRequest(url)
        return {"response": 1, "prices":respJson}
