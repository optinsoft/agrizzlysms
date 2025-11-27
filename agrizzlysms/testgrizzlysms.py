from .asyncgrizzlysms import AsyncGrizzlySms, AsyncGrizzlySmsException, NoSMSException, NoNumbersException, WrongMaxPriceException
from typing import Coroutine
import logging
from aiohttp.typedefs import StrOrURL
import sys

async def testApi(apiName: str, apiRoutine: Coroutine):
    print(apiName)
    try:
        response = await apiRoutine
        print(response)
        return response
    except NoSMSException:
        print("No SMS")
    except NoNumbersException:
        print("No numbers")
    except WrongMaxPriceException as e:
        print("WrongMaxPriceException:", e)
    except AsyncGrizzlySmsException as e:
        print("AsyncGrizzlySmsException:", e)
    return None

async def testAsyncGrizzlySms(apiKey: str, httpProxy: StrOrURL = None, connectionErrorRetries: int = 0,
                              country: str = 'US', service: str = 'mm', max_price: float = 0.08):
    logger = logging.Logger('testgrizzlysms')

    logger.setLevel(logging.DEBUG)

    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    log_path = './log/test.log'

    logFormatter = logging.Formatter(log_format)
    fileHandler = logging.FileHandler(log_path, encoding='utf8')
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    agrizzlysms = AsyncGrizzlySms(apiKey, logger=logger, http_or_socks_proxy=httpProxy, connection_error_retries=connectionErrorRetries)

    print('--- agrizzlysms test ---')

    await testApi('getBalance', agrizzlysms.getBalance())
    cc = agrizzlysms.getCountryCode(country)
    await testApi('getPrices', agrizzlysms.getPrices(service,cc))
    number = await testApi('getNumber', agrizzlysms.getNumber(service,cc,str(max_price)))
    if number:
        await testApi('getSMS', agrizzlysms.getSMS(number['id']))
        await testApi('setStatus', agrizzlysms.setStatus('8', number['id']))

    print('--- agrizzlysms test completed ---')