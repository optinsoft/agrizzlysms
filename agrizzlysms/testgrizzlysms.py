from .asyncgrizzlysms import AsyncGrizzlySms, AsyncGrizzlySmsException, NoSMSException
from typing import Coroutine

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
    agrizzlysms = AsyncGrizzlySms(apiKey)

    print('--- agrizzlysms test ---')

    await testApi('getBalance', agrizzlysms.getBalance())
    await testApi('getPrices', agrizzlysms.getPrices('mm','0'))
    cc = agrizzlysms.getCountryCode('RU')
    number = await testApi('getNumber', agrizzlysms.getNumber('mm',cc))
    if number:
        print(number)    
        await testApi('getSMS', agrizzlysms.getSMS(number['id']))

    print('--- agrizzlysms test completed ---')