import os
from dotenv import load_dotenv
from runware import Runware, IImageInference
import asyncio
# Cargar variables del archivo .env
load_dotenv()

# Obtener la API key del entorno
RUNWARE_API_KEY = os.getenv("RUNWARE_API_KEY")

async def main() -> None:
    runware = Runware(api_key=RUNWARE_API_KEY)
    await runware.connect()

    request_image = IImageInference(
        positivePrompt="Mia khalifa",
        model="rundiffusion:130@100",
        numberResults=1,
        negativePrompt="cloudy, rainy",
        height=512,
        width=512,
    )

    images = await runware.imageInference(requestImage=request_image)
    for image in images:
        print(f"Image URL: {image.imageURL}")

if __name__ == "__main__":
    asyncio.run(main())