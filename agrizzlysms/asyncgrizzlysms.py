import aiohttp
import ssl
import certifi
import json
from urllib.parse import urlencode
import logging
from functools import reduce
from aiohttp_socks import ProxyConnector

class AsyncGrizzlySmsException(Exception):
    pass

class NoSMSException(AsyncGrizzlySmsException):
    pass

class EarlyCancelException(AsyncGrizzlySmsException):
    pass

class BannedException(AsyncGrizzlySmsException):
    pass

class AsyncGrizzlySms:
    def __init__(self, apiKey: str, apiUrl: str = 'https://api.grizzlysms.com/stubs/handler_api.php', logger: logging.Logger = None, http_timeout: int = 15,
                 http_or_socks_proxy: aiohttp.typedefs.StrOrURL = None):
        self.logger = logger
        self.apiKey = apiKey
        self.apiUrl = apiUrl
        self.http_timeout = http_timeout
        self.http_proxy = http_or_socks_proxy if http_or_socks_proxy is not None and http_or_socks_proxy.startswith("http") else  None
        self.socks_proxy = http_or_socks_proxy if http_or_socks_proxy is not None and http_or_socks_proxy.startswith("socks") else None
        self.iso_country_dict = {
            "AF":"74", "AL":"155", "DZ":"58", "AO":"76",
            "AI":"181", "AG":"169", "AR":"39", "AM":"148",
            "AW":"179", "AU":"175", "AT":"50", "AZ":"35",
            "BS":"122", "BH":"145", "BD":"60", "BB":"118",
            "BY":"51", "BE":"82", "BZ":"124", "BJ":"120",
            "BM":"158", "BO":"92", "BA":"108", "BW":"123",
            "BR":"73", "BN":"121", "BG":"83", "BF":"152",
            "BI":"119", "KH":"24", "CM":"41", "CA":"36",
            "CV":"186", "KY":"170", "CF":"125", "TD":"42",
            "CL":"151", "CN":"3", "CO":"33", "KM":"133",
            "CR":"93", "HR":"45", "CY":"77", "CZ":"63",
            "DK":"172", "DJ":"168", "DM":"126", "DO":"109",
            "CG":"18", "EC":"105", "EG":"21", "GB":"16",
            "GQ":"167", "ER":"176", "EE":"34", "ET":"71", 
            "FI":"163", "FR":"78", "GF":"162", "GA":"154",
            "GM":"28", "GE":"128", "DE":"43", "GH":"38",
            "GR":"129", "GD":"127", "GP":"160", "GT":"94",
            "GN":"68", "GW":"130", "GY":"131", "HT":"26",
            "HN":"88", "HK":"14", "HU":"84", "IS":"132",
            "IN":"22", "ID":"6", "IR":"10016", "IQ":"47",
            "IE":"23", "IL":"13", "IT":"86", "CI":"27",
            "JM":"103", "JP":"182", "JO":"116", "KZ":"2",
            "KE":"8", "KW":"100", "KG":"11", "LA":"25",
            "LV":"49", "LB":"153", "LS":"136", "LR":"135",
            "LY":"102", "LI":"10348", "LT":"44", "LU":"165",
            "MO":"20", "MG":"17", "MW":"137", "MY":"7",
            "MV":"159", "ML":"69", "MR":"114", "MU":"157",
            "MX":"54", "MD":"85", "MC":"144", "MN":"72",
            "ME":"171", "MS":"180", "MA":"37", "MZ":"80",
            "MM":"5", "NA":"138", "NP":"81", "NL":"48",
            "NC":"185", "NZ":"67", "NI":"90", "NE":"139",
            "NG":"19", "MK":"183", "NO":"174", "OM":"107",
            "PK":"66", "PA":"112", "PG":"79", "PY":"87",
            "PE":"65", "PH":"4", "PL":"15", "PT":"117",
            "PR":"97", "QA":"111", "CD":"150", "RE":"146",
            "RO":"32", "RU":"0", "RW":"140", "KN":"134",
            "LC":"164", "VC":"166", "SV":"101", "WS":"10231",
            "ST":"178", "SA":"53", "SN":"61", "RS":"29",
            "SC":"184", "SL":"115", "SG":"10351", "SX":"10349",
            "SK":"141", "SI":"59", "SO":"149", "ZA":"31",
            "KP":"10350", "SS":"177", "ES":"56", "LK":"64",
            "SR":"142", "SZ":"106", "SE":"46", "CH":"173",
            "TW":"55", "TJ":"143", "TZ":"9", "TH":"52",
            "TL":"91", "TG":"99", "TO":"10227", "TT":"104",
            "TN":"89", "TR":"62", "TM":"161", "UG":"75",
            "UA":"1", "AE":"95", "US":"187", "US":"12",
            "UY":"156", "UZ":"40", "VE":"70", "VN":"10",
            "YE":"30", "ZM":"147", "ZW":"96"            
        }
        self.country_iso_dict = {}
        for item in self.iso_country_dict.items(): 
            self.country_iso_dict[item[1]] = item[0]

    def checkResponse(self, respList: list, successCode: str, noSmsCode: str):
        if len(successCode) > 0:
            if len(respList) > 0:            
                code = respList[0]
                if successCode.endswith('_'):
                    if not code.startswith(successCode):
                        if len(noSmsCode) > 0 and code == noSmsCode:
                            raise NoSMSException("No SMS")
                        if "EARLY_CANCEL_DENIED" == code:
                            raise EarlyCancelException("Yearly cancel denied")
                        if "BANNED" == code:
                            raise BannedException(f'Banned {":".join(respList[1:])}')
                        raise AsyncGrizzlySmsException(f'Error "{code}": {":".join(respList)}')
                else:
                    if code != successCode:
                        if len(noSmsCode) > 0 and code == noSmsCode:
                            raise NoSMSException("No SMS")
                        if "EARLY_CANCEL_DENIED" == code:
                            raise EarlyCancelException("Yearly cancel denied")
                        if "BANNED" == code:
                            raise BannedException(f'Banned {":".join(respList[1:])}')                        
                        raise AsyncGrizzlySmsException(f'Error "{code}": {":".join(respList)}')
            else:
                raise AsyncGrizzlySmsException(f"Empty response")
        return respList

    def logRequest(self, query, response: dict):
        if not self.logger is None:
            def escapeString(s):
                return s.replace('\\','\\\\').replace('"', '\\"').replace("\r",'\\r').replace("\n","\\n")
            self.logger.debug(
                'query: {'+reduce(lambda x,y: (x+', ' if len(x) > 0 else '')+y+':"'+('*...*' if y== 'api_key' else escapeString(query[y]))+'"', query.keys(),'')+'}'+
                ', response {'+reduce(lambda x,y: (x+', ' if len(x) > 0 else '')+y+':"'+escapeString(str(response[y]))+'"', response.keys(),'')+'}'
            )

    async def doListRequest(self, query: dict, successCode: str = 'ACCESS_', noSmsCode: str = ''):
        url = self.apiUrl + '?' + urlencode(query)
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        conn = ProxyConnector.from_url(self.socks_proxy, ssl=ssl_context) if self.socks_proxy is not None else aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=conn, raise_for_status=False, timeout=aiohttp.ClientTimeout(total=self.http_timeout)) as session:
            async with session.get(url, timeout=self.http_timeout, proxy=self.http_proxy) as resp:
                if resp.status != 200:
                    respText = await resp.text()
                    self.logRequest(query, {'status':resp.status,'text':respText})
                    raise AsyncGrizzlySmsException(f"Request failed:\nStatus Code: {resp.status}\nText: {respText}")
                try:
                    respText = await resp.text()
                    self.logRequest(query, {'status':resp.status,'text':respText})
                    respList = respText.split(':')
                except ValueError as e:
                    raise AsyncGrizzlySmsException(f"Request failed: {str(e)}")
                return self.checkResponse(respList, successCode, noSmsCode)

    async def doJsonRequest(self, query: dict):
        url = self.apiUrl + '?' + urlencode(query)
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        conn = ProxyConnector.from_url(self.socks_proxy, ssl=ssl_context) if self.socks_proxy is not None else aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=conn, raise_for_status=False, timeout=aiohttp.ClientTimeout(total=self.http_timeout)) as session:
            async with session.get(url, timeout=self.http_timeout, proxy=self.http_proxy) as resp:
                if resp.status != 200:
                    respText = await resp.text()
                    self.logRequest(query, {'status':resp.status,'text':respText})
                    raise AsyncGrizzlySmsException(f"Request failed:\nStatus Code: {resp.status}\nText: {respText}")
                try:
                    respText = await resp.text()
                    self.logRequest(query, {'status':resp.status,'text':respText})
                    respJson = json.loads(respText)
                except ValueError as e:
                    raise AsyncGrizzlySmsException(f"Request failed: {str(e)}")
                return respJson

    async def getNumber(self, service: str, country_code: str, max_price: str = ''):
        query = {'api_key':self.apiKey,'action':'getNumber','service':service,'country':country_code}
        if max_price:
            query['maxPrice'] = str(max_price)
        respList = await self.doListRequest(query, 'ACCESS_NUMBER')
        return {"response": 1, "id": respList[1], "number": respList[2]}

    async def setStatus(self, status: str, id: str):
        query = {'api_key':self.apiKey,'action':'setStatus','status':status,'id':id}
        respList = await self.doListRequest(query)
        return {"response": 1, "text": ":".join(respList)}
    
    async def getStatus(self, id: str):
        query = {'api_key':self.apiKey,'action':'getStatus','id':id}
        respList = await self.doListRequest(query)
        return {"response": 1, "status": ":".join(respList)}
    
    async def getSMS(self, id: str):
        query = {'api_key':self.apiKey,'action':'getStatus','id':id}
        respList = await self.doListRequest(query, 'STATUS_OK', 'STATUS_WAIT_CODE')
        return {"response": 1, "sms": respList[1]}

    async def getBalance(self):
        query = {'api_key':self.apiKey,'action':'getBalance'}
        respList = await self.doListRequest(query)
        return {"response": 1, "amount": respList[1]}
    
    async def getPrices(self, service: str, country_code: str):
        query = {'api_key':self.apiKey,'action':'getPrices','service':service,'country':country_code}
        respJson = await self.doJsonRequest(query)
        return {"response": 1, "prices":respJson}

    def getCountryCode(self, iso_country: str):
        return self.iso_country_dict[iso_country]
    
    def getIsoCountry(self, country_code: str, default: str):
        return self.country_iso_dict.get(country_code, default)
