from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi import Response
from PIL import Image
import io
from starlette.middleware.cors import CORSMiddleware

import AssetChanger

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins (test mode)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.post("/test")
# async def replace_textures(replacement_files: list[UploadFile] = File(...)):
#     img_bytes = await replacement_files[0].read()
#     img = Image.open(io.BytesIO(img_bytes))
#     if img.mode != "RGBA":
#         img = img.convert("RGBA")
#     changed=AssetChanger.Run(img)
##     return {"message": "ok!"}
# if changed is None:
#     return {"error": "something broke and debugging doesnt work yet :D"}
#
# return Response(
#         content=changed,
#         media_type="application/octet-stream",
#         headers={
#             "Content-Disposition": "attachment; filename=sharedassets1.assets"
#         },)

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

        return Response(
            content=changed,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename=sharedassets1.assets"
            }, )
    except Exception as e:
        print(f"Error processing textures: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
#
# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}
