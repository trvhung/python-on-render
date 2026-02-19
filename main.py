import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3-pro-image-preview"

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

class ImageRequest(BaseModel):
    prompt: str
    aspect_ratio: str = "16:9"
    image_size: str = "1K"

@app.post("/generate-image")
async def generate_image(data: ImageRequest):
    try:
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=data.prompt)],
            )
        ]

        config = types.GenerateContentConfig(
            image_config=types.ImageConfig(
                aspect_ratio=data.aspect_ratio,
                image_size=data.image_size,
            ),
            response_modalities=["IMAGE"],
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=config,
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data:
                return Response(
                    content=part.inline_data.data,
                    media_type=part.inline_data.mime_type
                )

        raise HTTPException(status_code=500, detail="No image generated")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
