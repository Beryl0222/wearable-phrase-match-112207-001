# 佩戴语音匹配的可证区间矩阵乘

短语识别设备的分块特征、量化误差和补件目录。样例均为合成记录。

使用 CPython 3.11 读取资料。当前资料工具与关联测试只需要标准库。数值开发环境的可用库锁定在 requirements.txt 中，可在新的虚拟环境执行 python3 -m pip install -r requirements.txt。


    python3 records.py device_records.json
    python3 -m unittest -v

[数据约定](DATA.md)解释输入时序、坐标及数值口径。

合成设备页流可在临时目录生成。默认资料包含两版 8192 条短语，维数 519 和 48 个查询。

    python3 generate_replay.py /tmp/phrase-pages
    python3 records.py /tmp/phrase-pages/manifest.json
