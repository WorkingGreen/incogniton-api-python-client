import asyncio
from typing import Optional

async def delay(ms: Optional[int] = 30000) -> None:
    """
    Creates a coroutine that resolves after the specified delay
    
    Args:
        ms: Time to wait in milliseconds, defaults to 30000ms (30 seconds)
    """
    await asyncio.sleep(ms / 1000)  # Convert milliseconds to seconds for asyncio.sleep

