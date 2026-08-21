from aiofiles import open as a_open
from scripts.j2sync import *


async def fromfile_async(abspath: str) -> dict[str, ...]:
    async with a_open(abspath, encoding='utf8') as file:
        return from_(await file.read())


__all__ = ('to_', 'from_', 'fromfile', 'fromfile_async')
