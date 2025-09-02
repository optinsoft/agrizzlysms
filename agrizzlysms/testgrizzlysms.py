from .asyncgrizzlysms import AsyncGrizzlySms, AsyncGrizzlySmsException, NoSMSException, NoNumbersException, WrongMaxPriceException
from typing import Coroutine
import logging
from aiohttp.typedefs import StrOrURL

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

async def testAsyncGrizzlySms(apiKey: str, httpProxy: StrOrURL = None):
    logger = logging.Logger('testgrizzlysms')

    logger.setLevel(logging.DEBUG)

    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    log_path = './log/test.log'

    logFormatter = logging.Formatter(log_format)
    fileHandler = logging.FileHandler(log_path)
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    agrizzlysms = AsyncGrizzlySms(apiKey, logger=logger, http_or_socks_proxy=httpProxy)

    print('--- agrizzlysms test ---')

    await testApi('getBalance', agrizzlysms.getBalance())
    cc = agrizzlysms.getCountryCode('US')
    await testApi('getPrices', agrizzlysms.getPrices('mm',cc))
    number = await testApi('getNumber', agrizzlysms.getNumber('mm',cc,0.08))
    if number:
        await testApi('getSMS', agrizzlysms.getSMS(number['id']))
        await testApi('setStatus', agrizzlysms.setStatus('8', number['id']))

    print('--- agrizzlysms test completed ---')