import httpx
from PIL import Image
import io

async def read_img_url(url: str) -> Image.Image:
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            # Stream into BytesIO
            buffer = io.BytesIO()
            async for chunk in response.aiter_bytes():
                buffer.write(chunk)
            buffer.seek(0)
            return Image.open(buffer)
