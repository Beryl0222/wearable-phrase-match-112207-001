"""核对本地设备资料的关联。"""
import unittest
from pathlib import Path
from records import load


class DeviceRecordsTest(unittest.TestCase):
    def test_设备资料关联(self):
        data = load(Path(__file__).with_name("device_records.json"))
        assert all([p[0] for p in v] == data['axes'] for v in data['vectors'].values())
        assert all(len(data['vectors'][k.split('/')[0]][int(k.endswith('/3'))][1]) == len(v['values']) for k,v in data['patches'].items())
