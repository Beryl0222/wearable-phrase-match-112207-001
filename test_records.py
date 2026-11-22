"""核对本地设备资料的关联。"""
import unittest
from pathlib import Path
from records import load


class DeviceRecordsTest(unittest.TestCase):
    def test_设备资料关联(self):
        data = load(Path(__file__).with_name("device_records.json"))
        assert all([p[0] for p in v] == data['axes'] for v in data['vectors'].values())
        assert all(len(data['vectors'][k.split('/')[0]][int(k.endswith('/3'))][1]) == len(v['values']) for k,v in data['patches'].items())

    def test_设备页格式和补件地址(self):
        from tempfile import TemporaryDirectory
        from generate_replay import HEADER, generate

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = generate(root, phrases=33, width=65, queries=4)
            self.assertEqual(manifest['sections'], [0, 64])
            for filename in manifest['libraries'].values():
                packed = (root / filename).read_bytes()
                stride = HEADER.size * 2 + 65
                self.assertEqual(len(packed), 33 * stride)
                self.assertEqual(HEADER.unpack_from(packed, 32 * stride + HEADER.size + 64)[:2], (32, 1))
            pages = [load(root / item['file']) for item in manifest['pages']]
            self.assertEqual(len({(page['library'], page['address']) for page in pages}), 12)
            self.assertEqual(manifest['pages'][1]['status'], 'failed')
            self.assertFalse(pages[1]['values'])
            self.assertNotEqual(pages[0]['values'][0][2], pages[3]['values'][0][2])
