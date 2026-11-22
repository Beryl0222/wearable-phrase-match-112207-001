"""读取本地设备记录，便于在开发环境中核对原始资料。"""
import argparse
import json
from pathlib import Path


def load(path):
    """读取 UTF-8 记录，返回字段与原始内容。"""
    with Path(path).open(encoding="utf8") as records:
        value = json.load(records)
    if not isinstance(value, dict):
        raise ValueError("根记录必须为 JSON 对象")
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="查看设备资料的字段和记录数")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    for key, value in load(args.path).items():
        size = len(value) if isinstance(value, (list, dict)) else 1
        print(f"{key} {size}")
