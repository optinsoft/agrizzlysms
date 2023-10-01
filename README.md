# Async API wrapper for grizzlysms

## Installation

```bash
pip install git+https://github.com/optinsoft/agrizzlysms.git
```

## Usage

```python
from agrizzlysms import AsyncGrizzlySms
import asyncio

async def test(apiKey: str):
    agrizzlysms = AsyncGrizzlySms(apiKey)
    print("getBalance\n", await agrizzlysms.getBalance())    

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test('PUT_YOUR_API_KEY_HERE'))
```
