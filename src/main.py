import json
import logging
import os
import time

from download_data import get_data_size, download_data
from source_data_list import data
from unity_tools import replace_spine_files

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# 获取脚本所在目录的父目录（项目根目录）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 默认ab资源文件下载目录
ab_data_dir = os.path.join(project_root, "sourcedata")
# 默认ab资源替换目录
replace_data_dir = os.path.join(project_root, "replace")
# 目标路径
target_data_dir = os.path.join(project_root, "targetdata")
# 数据存储json文件
data_json = os.path.join(project_root, "data.json")


def run():
    # 需要替换资源的ab文件路径列表
    source_dirs = []
    # 获取当前时间字符串
    time_str = time.strftime("%Y-%m-%d(%H%M%S)", time.localtime())

    # 判断ab资源文件下载目录和ab资源替换目录是否存在
    if not os.path.exists(ab_data_dir):
        os.makedirs(ab_data_dir)
        logging.info(f"Created directory: {ab_data_dir}")
    # 遍历data
    for itme in data:
        # 获取ab资源文件大小
        data_size = get_data_size(itme["data_name"])
        source_dir = os.path.join(replace_data_dir, itme["data_name"])
        if itme["replace_data"] != "":
            source_dir = os.path.join(replace_data_dir, itme["replace_data"])
        if not os.path.exists(source_dir):
            os.makedirs(source_dir)
            logging.info(f"Created directory: {source_dir}")
        logging.info(f"Data size: {data_size}")
        data_dir = os.path.join(ab_data_dir, itme["data_name"])
        target_data = os.path.join(target_data_dir, time_str, itme["data_name"], "__data")
        if itme["target_data"] != "":
            target_data = os.path.join(target_data_dir, time_str, itme["target_data"], "__data")

        if not os.path.exists(os.path.join(data_dir, "__data")) or os.path.getsize(
                os.path.join(data_dir, "__data")) != data_size:
            logging.info(
                f"Data file {itme['data_name']} not found or need update, downloading...")
            download_data(itme["data_name"])

        # 判断数据json文件是否存在
        if not os.path.exists(data_json):
            logging.info(f"Data json file not found, creating...")
            with open(data_json, 'w') as f:
                f.write("[]")
        with open(data_json, 'r') as f:
            data_json_list = f.read()
            history_data = json.loads(data_json_list)
        # 从history_data找到data_name对应的数据
        history_data_item = None
        for history_data_item in history_data:
            if history_data_item["data_name"] == itme["data_name"]:
                break

        # 如果history_data_item不存在
        if history_data_item == None:
            logging.info(f"Data file {itme['data_name']} not found in history data")
            source_dirs.append({
                "data_dir": data_dir,
                "replace_dir": source_dir,
                "target_data": target_data,
            })
            # 添加到history_data
            history_data_item = {
                "data_name": itme["data_name"],
                "update_time": time_str,
                "replace_dir_mtime": os.path.getmtime(source_dir),
            }
            history_data.append(history_data_item)
            # 写入数据json文件
            logging.info(f"Writing data json file...")
            with open(data_json, 'w') as f:
                f.write(json.dumps(history_data))
        if os.path.getsize(os.path.join(data_dir, "__data")) != data_size:
            logging.info(f"Data file {itme['data_name']} is outdated")
            source_dirs.append({
                "data_dir": data_dir,
                "replace_dir": source_dir,
                "target_data": target_data,
            })
            # 更新history_data
            history_data_item["update_time"] = time_str
            # 写入数据json文件
            with open(data_json, 'w') as f:
                f.write(json.dumps(history_data))

        # 判断replace_dir_mtime是否有变化
        if os.path.getmtime(source_dir) != history_data_item["replace_dir_mtime"]:
            logging.info(f"Replace dir {source_dir} has been modified")
            source_dirs.append({
                "data_dir": data_dir,
                "replace_dir": source_dir,
                "target_data": os.path.join(target_data_dir, time_str, itme["data_name"], "__data"),
            })
            # 更新history_data
            history_data_item["replace_dir_mtime"] = os.path.getmtime(source_dir)
            # 写入数据json文件
            with open(data_json, 'w') as f:
                f.write(json.dumps(history_data))

    if not source_dirs:
        logging.info("No data files need to be update...")
        return
    # 遍历source_dirs
    for source_dir in source_dirs:
        logging.info(f"---------------------------------------------")
        logging.info(
            f"replace {source_dir['data_dir']} with {source_dir['replace_dir']} to {source_dir['target_data']}")
        # 执行替换资源文件
        replace_spine_files(source_dir["data_dir"], source_dir["replace_dir"], source_dir["target_data"])


# 定义入口函数`
if __name__ == "__main__":
    run()
