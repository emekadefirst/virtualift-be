import asyncio
from aerich.cli import cli

def makemigrations():
    asyncio.run(cli.main(["migrate"]))

def migrate():
    asyncio.run(cli.main(["upgrade"]))

def initdb():
    asyncio.run(cli.main(["upgrade"]))
