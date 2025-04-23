import os
import asyncio
from dotenv import load_dotenv
from runware import Runware, IImageInference

# Cargar variables del entorno
load_dotenv()
RUNWARE_API_KEY = os.getenv("RUNWARE_API_KEY")

# Función asincrónica para una sola receta
async def generate_recipe_image(nombre_receta: str) -> str:
    runware = Runware(api_key=RUNWARE_API_KEY)
    await runware.connect()

    request_image = IImageInference(
        positivePrompt=nombre_receta,
        model="rundiffusion:130@100",
        numberResults=1,
        negativePrompt="cloudy, rainy",
        height=512,
        width=512,
    )

    images = await runware.imageInference(requestImage=request_image)

    if images:
        image_url = images[0].imageURL
        print(f"✅ Imagen generada para '{nombre_receta}': {image_url}")
        return image_url
    else:
        print(f"⚠️ No se pudo generar imagen para '{nombre_receta}'")
        return ""

# Función asincrónica para múltiples recetas
async def generate_multiple_images(nombres_recetas: list[str]) -> dict:
    runware = Runware(api_key=RUNWARE_API_KEY)
    await runware.connect()

    result = {}
    for nombre in nombres_recetas:
        request_image = IImageInference(
            positivePrompt=nombre,
            model="rundiffusion:130@100",
            numberResults=1,
            negativePrompt="cloudy, rainy",
            height=512,
            width=512,
        )

        images = await runware.imageInference(requestImage=request_image)
        if images:
            image_url = images[0].imageURL
            print(f"✅ Imagen generada para '{nombre}': {image_url}")
            result[nombre] = image_url
        else:
            print(f"⚠️ No se pudo generar imagen para '{nombre}'")
            result[nombre] = ""
    return result

# Wrappers síncronos
def generate(nombre_receta: str) -> str:
    return asyncio.run(generate_recipe_image(nombre_receta))

def generate_multiple(nombres_recetas: list[str]) -> dict:
    return asyncio.run(generate_multiple_images(nombres_recetas))
import os
import asyncio
from dotenv import load_dotenv
from runware import Runware, IImageInference

# Cargar variables del entorno
load_dotenv()
RUNWARE_API_KEY = os.getenv("RUNWARE_API_KEY")

# Función asincrónica para un solo outfit
async def generate_outfit_image(nombre_outfit: str, genero: str) -> str:
    runware = Runware(api_key=RUNWARE_API_KEY)
    await runware.connect()

    prompt = f"{nombre_outfit}, estilo {genero}"

    request_image = IImageInference(
        positivePrompt=prompt,
        model="rundiffusion:130@100",
        numberResults=1,
        negativePrompt="cloudy, rainy",
        height=512,
        width=512,
    )

    images = await runware.imageInference(requestImage=request_image)

    if images:
        image_url = images[0].imageURL
        print(f"✅ Imagen generada para '{prompt}': {image_url}")
        return image_url
    else:
        print(f"⚠️ No se pudo generar imagen para '{prompt}'")
        return ""

# Función asincrónica para múltiples outfits
async def generate_multiple_outfit_images(outfits: list[dict]) -> dict:
    runware = Runware(api_key=RUNWARE_API_KEY)
    await runware.connect()

    result = {}
    for outfit in outfits:
        nombre = outfit.get("nombre_outfit")
        genero = outfit.get("genero", "")
        prompt = f"{nombre}, estilo {genero}"

        request_image = IImageInference(
            positivePrompt=prompt,
            model="rundiffusion:130@100",
            numberResults=1,
            negativePrompt="cloudy, rainy",
            height=512,
            width=512,
        )

        images = await runware.imageInference(requestImage=request_image)
        if images:
            image_url = images[0].imageURL
            print(f"✅ Imagen generada para '{prompt}': {image_url}")
            result[nombre] = image_url
        else:
            print(f"⚠️ No se pudo generar imagen para '{prompt}'")
            result[nombre] = ""
    return result

# Wrappers síncronos
def generate_outfit(nombre_outfit: str, genero: str) -> str:
    return asyncio.run(generate_outfit_image(nombre_outfit, genero))

def generate_multiple_outfits(outfits: list[dict]) -> dict:
    return asyncio.run(generate_multiple_outfit_images(outfits))
