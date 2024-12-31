import logging
import os

import UnityPy
from PIL import Image
from UnityPy.enums import TextureFormat

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def replace_spine_files(data_dir, replace_dir, target_dir):
    #判断target_dir的父目录是否存在
    if not os.path.exists(os.path.dirname(target_dir)):
        os.makedirs(os.path.dirname(target_dir))
        logging.info(f"Created directory: {os.path.dirname(target_dir)}")
    # Traverse all bundle files in the target directory.
    UnityPy.config.FALLBACK_UNITY_VERSION = '2022.3.22f1'
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            logging.info(f"Processing {file}")
            if file == "__data":  # check file name
                bundle_path = os.path.join(root, file)
                # load bundle
                env = UnityPy.load(bundle_path)
                # Traverse all objects in the bundle.
                for obj in env.objects:
                    if obj.type.name == 'TextAsset':
                        data = obj.read()
                        # print(f"dataname={data.m_Name}")
                        # edit skel
                        if data.m_Name.endswith('.skel'):
                            for root1, dirs1, files1 in os.walk(replace_dir):
                                for file1 in files1:
                                    if file1 == data.m_Name:
                                        fp = os.path.join(root1, file1)
                                        logging.info(f"fp={fp}")
                                        with open(fp, 'rb') as f:
                                            data.m_Script = f.read().decode("utf-8", "surrogateescape")
                                        data.save()
                                        logging.info(f"Replaced {data.m_Name} in {bundle_path}")
                                    # edit atlas
                        if data.m_Name.endswith('.atlas'):
                            for root1, dirs1, files1 in os.walk(replace_dir):
                                for file1 in files1:
                                    if file1 == data.m_Name:
                                        fp = os.path.join(root1, file1)
                                        # skip folders with json and no skel
                                        json_path = os.path.join(root1, data.m_Name.replace('.atlas', '.json'))
                                        skel_path = os.path.join(root1, data.m_Name.replace('.atlas', '.skel'))
                                        # print(json_path)
                                        if os.path.exists(json_path):
                                            if not os.path.exists(skel_path):
                                                logging.info(
                                                    f".json file found for {data.m_Name}, no skel, skipping...")
                                                continue
                                        logging.info(f"fp={fp}")
                                        with open(fp, 'rb') as f:
                                            data.m_Script = f.read().decode("utf-8", "surrogateescape")
                                        data.save()
                                        logging.info(f"Replaced {data.m_Name} in {bundle_path}")


                    elif obj.type.name == 'Texture2D':
                        # edit png
                        data = obj.read()
                        # print(f"dataname={data.m_Name}")
                        for root1, dirs1, files1 in os.walk(replace_dir):
                            for file1 in files1:
                                if file1 == f"{data.m_Name}.png":
                                    # skip folders with json and no skel
                                    json_path = os.path.join(root1, f"{data.m_Name}.json")
                                    skel_path = os.path.join(root1, f"{data.m_Name}.skel")
                                    if os.path.exists(json_path):
                                        if not os.path.exists(skel_path):
                                            logging.info(f".json file found for {data.m_Name}, no skel, skipping...")
                                            continue
                                    fp = os.path.join(root1, file1)
                                    logging.info(f"fp={fp}")
                                    pil_img = Image.open(fp)
                                    data.set_image(img=pil_img, target_format=TextureFormat.RGBA32)
                                    # data.save()
                                    # config = ASTCConfig(ASTCProfile.LDR_SRGB, 4, 4)
                                    # context = ASTCContext(config)
                                    # img = Image.open(fp).convert("RGBA")
                                    # image = ASTCImage(ASTCType.U8, *img.size, data=img.tobytes())
                                    # swizzle = ASTCSwizzle.from_str("RGBA")
                                    # print(f"compressing {file1}")
                                    # comp = context.compress(image, swizzle)

                                    # data.image_data = comp
                                    # data.m_CompleteImageSize  = len(comp)
                                    # data.m_TextureFormat = TextureFormat.ASTC_RGB_4x4
                                    data.save()
                                    logging.info(f"Replaced {data.m_Name} in {bundle_path}")

                # save & compress
                with open(target_dir, "wb") as f:
                    logging.info(f"Saving {bundle_path}")
                    envdata = env.file.save(packer="lz4")
                    f.write(envdata)
                    logging.info(f"Saved {bundle_path}")
