### 简单的使用说明
###### 1.安装依赖
```shell
pip install -r requirements.txt
```
###### 2.修改**source_data_list.py**配置文件
这个文件中包含需要mod的资源文件列表，DB2中经常改动的_data已默认已写入（其他需要mod资源请自行对照资源表填入），格式如下:
```python
data = [
    {
        "data_name": "common-skeleton-data_assets_all.bundle",  # __data对应的资源名称
        "replace_data": ""  # 替换资源存放的目录，相对于项目根目录/replace目录的路径,不填默认为: 项目根目录{data_name}
    }
]
```

###### 3.将需要替换的资源放入**replace**目录

例如: 项目根目录/replace/common-skeleton-data_assets_all.bundle(不指定replace_data默认子目录为data_name)

如果common-skeleton-data_assets_all.bundle中包含多个需要替换资源的文件时如果需区分不同的资源，可用分别放入不同的子目录中

###### 4.运行
```shell
python main.py
```

###### 5.生成的AB资源文件在targetdata目录下
###### 6.定时运行脚本
定时运行脚本时需要自行实现定时方式，当检测到游戏服务器资源文件更新时会自动下载资源文件并替换，生成新的MOD文件，新的文件按照生成时间命名

如果需要添加新的资源文件，只需在source_data_list.py中新增即可，如果replace文件夹中文件有变化，在定时运行时同样会生成新的AB资源文件

###### 提示
如果所需问金价没有建立，可用运行一次脚本，会自动按照source_data_list.py中的配置生成对应replace目录、sourcedata目录以及下载对应__data资源文件