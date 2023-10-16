from .asyncgrizzlysms import AsyncGrizzlySms, AsyncGrizzlySmsException, NoSMSException
from typing import Coroutine
import logging

async def testApi(apiName: str, apiRoutine: Coroutine):
    print(apiName)
    try:
        response = await apiRoutine
        print(response)
        return response
    except NoSMSException:
        print("No SMS")
    except AsyncGrizzlySmsException as e:
        print("AsyncGrizzlySmsException:", e)
    return None

async def testAsyncGrizzlySms(apiKey: str):
    logger = logging.Logger('testgrizzlysms')

    logger.setLevel(logging.DEBUG)

    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    log_path = './log/test.log'

    logFormatter = logging.Formatter(log_format)
    fileHandler = logging.FileHandler(log_path)
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    agrizzlysms = AsyncGrizzlySms(apiKey, logger=logger)

    print('--- agrizzlysms test ---')

    await testApi('getBalance', agrizzlysms.getBalance())
    await testApi('getPrices', agrizzlysms.getPrices('mm','0'))
    cc = agrizzlysms.getCountryCode('RU')
    number = await testApi('getNumber', agrizzlysms.getNumber('mm',cc))
    if number:
        print(number)    
        await testApi('getSMS', agrizzlysms.getSMS(number['id']))
        await testApi('setStatus', agrizzlysms.setStatus('8', number['id']))

    print('--- agrizzlysms test completed ---')