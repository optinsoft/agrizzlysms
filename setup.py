from distutils.core import setup

setup(name='agrizzlysms',
    version='1.2',
    description='Async API wrapper for grizzlysms',
    install_requires=["aiohttp","certifi"],
    author='optinsoft',
    author_email='optinsoft@gmail.com',
    keywords=['grizzlysms','sms','async'],
    url='https://github.com/optinsoft/agrizzlysms',
    packages=['agrizzlysms']
)