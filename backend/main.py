import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from PIL import Image
import io

from starlette.background import BackgroundTask
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

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
        # return {"message": "ok!"}
        if changed is None:
            return {"error": "something broke and debugging doesnt work yet :D"}

        return FileResponse(
            changed,
            media_type="application/octet-stream",
            filename="sharedassets1.assets.resS",
            background=BackgroundTask(os.remove, changed),
        )
    except Exception as e:
        print(f"Error processing textures: {e}")
        raise HTTPException(status_code=500, detail=str(e))

