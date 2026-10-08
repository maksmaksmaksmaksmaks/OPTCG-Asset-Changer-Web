import os
import shutil
import tempfile
import urllib.request
import UnityPy
from pathlib import Path
from PIL import Image
from UnityPy.export import Texture2DConverter as T2D

RES_NAME = "sharedassets1.assets.resS"
AST_NAME = "sharedassets1.assets"
RES_URL = "https://github.com/maksmaksmaksmaksmaks/OPTCG-Asset-Changer-Web/releases/download/simdata/"


VERSION = "1.44a"
CACHE_DIR = Path("cache") / VERSION

def ensure_file(name):
    path = CACHE_DIR / name
    if not path.exists():
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        tmp = str(path) + ".part"
        urllib.request.urlretrieve(RES_URL + name, tmp)
        os.replace(tmp, path)
    return str(path)


def build_texture_bytes(img, tex):
    mips = max(1, tex.m_MipCount or 1)
    chunks = []
    for level in range(mips):
        w = max(1, tex.m_Width >> level)
        h = max(1, tex.m_Height >> level)
        level_img = img if img.size == (w, h) else img.resize((w, h), Image.LANCZOS)
        raw, out_fmt = T2D.image_to_texture2d(level_img, tex.m_TextureFormat)
        if int(out_fmt) != int(tex.m_TextureFormat):
            raise ValueError(f"unsupported texture format {tex.m_TextureFormat}")
        chunks.append(raw)
    return b"".join(chunks)


def Run(files):
    if files is None:
        print("*** Failed to load images. Exiting.")
        return

    # print("Changes:")
    # for asset_name, img_file in files.items():
    #     print(f"  {img_file} -> {asset_name}")

    out_path = None
    try:
        patches = []
        env = UnityPy.load(ensure_file(AST_NAME))

        for obj in env.objects:
            if obj.type.name != "Texture2D":
                continue

            tex = obj.read()
            if tex.m_Name not in files:
                continue

            sd = tex.m_StreamData
            if sd is None or not sd.path or sd.size == 0:
                raise Exception(f"{tex.m_Name}: pixels are not stored in a .resS file")
            if Path(sd.path).name != RES_NAME:
                raise Exception(f"{tex.m_Name}: lives in {Path(sd.path).name}, not {RES_NAME}")

            new_bytes = build_texture_bytes(files[tex.m_Name], tex)
            if len(new_bytes) != sd.size:
                raise Exception(f"{tex.m_Name}: size mismatch (new {len(new_bytes)} vs original {sd.size})")

            patches.append((sd.offset, new_bytes))

        # print(f"Replaced {len(patches)} texture(s)")
        if not patches:
            return None

        # Copy the original on disk (not in memory) and write the patches into the copy
        src = ensure_file(RES_NAME)
        fd, out_path = tempfile.mkstemp(suffix=".resS")
        os.close(fd)
        shutil.copyfile(src, out_path)
        with open(out_path, "r+b") as f:
            for offset, data in patches:
                f.seek(offset)
                f.write(data)

        return out_path

    except Exception as e:
        # print(f"\n*** Error: {e}")
        # print("ABORTED")
        if out_path and os.path.exists(out_path):
            os.remove(out_path)
        raise
