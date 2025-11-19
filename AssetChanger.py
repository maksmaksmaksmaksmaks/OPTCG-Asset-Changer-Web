import UnityPy

def Run(files):
    print(f"Changes:")
    for asset_name, img_file in files.items():
        print(f"  {img_file} -> {asset_name}")
    if files is None:
        print("*** Failed to load images. Exiting.")
        return

    try:
        modified_count = 0
        env = UnityPy.load("sharedAssets1.assets")
        for obj in env.objects:
            if obj.type.name != "Texture2D":
                continue

            tex = obj.read()
            tex_name = tex.m_Name

            # Check if a replacement exists for this texture
            if tex_name in files:
                replacement_img = files[tex_name]

                # Resize replacement if needed
                if replacement_img.size != (tex.m_Width, tex.m_Height):
                    replacement_img = replacement_img.resize((tex.m_Width, tex.m_Height))

                try:
                    tex.image = replacement_img
                    tex.save()
                    modified_count += 1
                except Exception as e:
                    print(f"*** Failed to replace {tex_name}: {e}")
                    exit(1)

        print(f"Replaced {modified_count} texture(s)")
        return env.file.save()

    except Exception as e:
        print(f"\n*** Error: {e}")
        print(f"ABORTED")
        exit(1)


