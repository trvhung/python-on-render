import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

OUTPUT_DIR = "generated"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount sau khi tạo folder
app.mount("/generated", StaticFiles(directory=OUTPUT_DIR), name="generated")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3-pro-image-preview"

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)


class ImageRequest(BaseModel):
    prompt: str
    aspect_ratio: str = "16:9"
    image_size: str = "1K"


def extract_server_name(prompt: str) -> str:
    match = re.search(r"Server name:\s*([^\n\r]+)", prompt)
    if match:
        return match.group(1).strip()
    return "unknown_server"


def clean_filename(name: str) -> str:
    name = name.replace(" ", "_")
    name = re.sub(r"[^a-zA-Z0-9_\-]", "", name)
    return name


@app.post("/generate-image")
async def generate_image(data: ImageRequest):
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=data.prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=data.aspect_ratio
                ),
            ),
        )

        if not response or not response.candidates:
            raise HTTPException(status_code=500, detail="No candidates returned")

        candidate = response.candidates[0]

        if not candidate.content or not candidate.content.parts:
            raise HTTPException(status_code=500, detail="No image generated")

        server_name = extract_server_name(data.prompt)
        filename = clean_filename(server_name) + ".png"
        filepath = os.path.join(OUTPUT_DIR, filename)

        for part in candidate.content.parts:
            if part.inline_data:
                with open(filepath, "wb") as f:
                    f.write(part.inline_data.data)

                return JSONResponse({
                    "status": "success",
                    "server_name": server_name,
                    "image_url": f"/generated/{filename}"
                })

        raise HTTPException(status_code=500, detail="No image found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
