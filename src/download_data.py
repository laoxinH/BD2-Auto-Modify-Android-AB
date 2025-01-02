import base64
import logging
import os

import blackboxprotobuf as bbpb
import requests
import tqdm

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# 获取脚本所在目录的父目录（项目根目录）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 配置代理
proxies = {
    'http': 'http://127.0.0.1:19668',
    'https': 'http://127.0.0.1:19668',
}
session = requests.Session()
session.proxies.update(proxies)
def get_bd2_cdn(data_name):
    content = {
        "1": 2,
        "2": 4,
        "3": "1.78.18",
        "5": "10004|5063|WEB|KR|5321e432f133f7fbbd6d200a000c3aaddbbe62e3|1733413309371",
        "6": 5,
    }

    content_d = {
        "1": {"type": "int", "name": ""},
        "2": {"type": "int", "name": ""},
        "3": {"type": "bytes", "name": ""},
        "5": {"type": "bytes", "name": ""},
        "6": {"type": "int", "name": ""},
    }
    res = session.post("https://mt.bd2.pmang.cloud/MaintenanceInfo",
                        data=base64.b64encode(bbpb.encode_message(content, content_d)))
    data = bbpb.decode_message(base64.b64decode(res.json()["data"]))[0]["1"]
    version = str(data["3"])[2:-1]
    # https://cdn.bd2.pmang.cloud/ServerData/Android/HD/{}/catalog_alpha.json
    url = f"https://cdn.bd2.pmang.cloud/ServerData/Android/HD/{version}/{data_name}"
    logging.info(f"Using version {version}")
    logging.info(f"Fetching catalog from {url}")
    return url, data_name


def download_data(data_name):
    url, name = get_bd2_cdn(data_name)
    res = session.get(url, stream=True)
    total_size = int(res.headers.get('content-length', 0))
    output_path = os.path.join(project_root, "sourcedata", data_name, "__data")

    # 判断文件的父目录是否存在，如果不存在则创建
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
        logging.info(f"Created directory: {os.path.dirname(output_path)}")

    with open(output_path, "wb") as f, tqdm.tqdm(
            desc=output_path,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as bar:
        for data in res.iter_content(chunk_size=1024):
            size = f.write(data)
            bar.update(size)

    return output_path


def get_data_size(data_name):
    url, name = get_bd2_cdn(data_name)
    res = session.head(url)
    logging.info(f"Fetching {data_name} size from {url} is {res.headers.get('Content-Length', 0)}")
    return int(res.headers.get('Content-Length', 0))



