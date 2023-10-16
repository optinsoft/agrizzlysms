from distutils.core import setup
import re

s = open('agrizzlysms/version.py').read()
v = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", s, re.M).group(1)

setup(name='agrizzlysms',
    version=v,
    description='Async API wrapper for grizzlysms',
    install_requires=["aiohttp","certifi"],
    author='optinsoft',
    author_email='optinsoft@gmail.com',
    keywords=['grizzlysms','sms','async'],
    url='https://github.com/optinsoft/agrizzlysms',
    packages=['agrizzlysms']
)