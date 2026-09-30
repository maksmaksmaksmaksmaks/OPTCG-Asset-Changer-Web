import UnityPy
from pathlib import Path
from PIL import Image
from UnityPy.export import Texture2DConverter as T2D


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
        # print(f"  {img_file} -> {asset_name}")

    try:
        modified_count = 0
        buffers = {}  # resS file name -> bytearray
        env = UnityPy.load("sharedAssets1.assets")

        for obj in env.objects:
            if obj.type.name != "Texture2D":
                continue

            tex = obj.read()
            tex_name = tex.m_Name

            if tex_name not in files:
                continue

            sd = tex.m_StreamData
            if sd is None or not sd.path or sd.size == 0:
                raise Exception(f"{tex_name}: pixels are not stored in a .resS file")

            new_bytes = build_texture_bytes(files[tex_name], tex)
            if len(new_bytes) != sd.size:
                raise Exception(f"{tex_name}: size mismatch (new {len(new_bytes)} vs original {sd.size})")

            res_name = Path(sd.path).name
            if res_name not in buffers:
                buffers[res_name] = bytearray(Path(res_name).read_bytes())

            buffers[res_name][sd.offset:sd.offset + sd.size] = new_bytes
            modified_count += 1

        # print(f"Replaced {modified_count} texture(s)")

        if modified_count == 0:
            return None
        if len(buffers) > 1:
            raise Exception(f"Textures span several .resS files: {list(buffers)}")

        return bytes(next(iter(buffers.values())))

    except Exception as e:
        # print(f"\n*** Error: {e}")
        # print("ABORTED")
        raise
