from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi import Response
from PIL import Image
import os
import io
from starlette.middleware.cors import CORSMiddleware

import AssetChanger

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://maksmaksmaksmaksmaks.github.io"],
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
async def ping():
    #print("Files:", os.listdir("."))
    return {"message":"pong"}

@app.post("/full")
async def full(textures: list[UploadFile] = File(...)):
    try:
        images = {}
        for t in textures:
            img = Image.open(io.BytesIO(await t.read()))
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            images[t.filename] = img

        print(images)
        changed = AssetChanger.Run(images)
        if changed is None:
            return {"error": "something broke and debugging doesnt work yet :D"}

        return Response(
            content=changed,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename=sharedassets1.assets.resS"
            }, )
    except Exception as e:
        print(f"Error processing textures: {e}")
        raise HTTPException(status_code=500, detail=str(e))





