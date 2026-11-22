"""为短语匹配设备生成两版量化库和精度页的合成记录。"""
import argparse
import json
from pathlib import Path
import random
import struct


HEADER = struct.Struct('<HHbfff')


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def generate(root, phrases=8192, width=519, queries=48):
    """生成尺寸可调的设备输入，不计算匹配结果。"""
    if not (32 <= phrases <= 65535 and 65 <= width <= 2048 and 4 <= queries <= 256):
        raise ValueError('词表、维数或询问数量超出回放格式范围')
    root.mkdir(parents=True, exist_ok=True)
    rng = random.Random(220701)
    starts = list(range(0, width, 64))
    capacities = [min(64, width - start) for start in starts]
    manifest = {
        'sections': starts, 'width': width, 'phrases': phrases,
        'libraries': {'r1': 'r1.bin', 'r2': 'r2.bin'}, 'retained': [['r1'], ['r1', 'r2'], ['r2']],
        'requests': [], 'pages': [], 'rounds': 3,
        'limits': {'working_elements': 16384, 'library_passes_per_round': 3, 'precision_bytes_per_round': 1080},
    }
    for version, filename in manifest['libraries'].items():
        saved = {}
        with (root / filename).open('wb') as stream:
            for phrase in range(phrases):
                for segment, span in enumerate(capacities):
                    zero = (phrase + segment) % 7 - 3
                    scale = (2 + phrase % 9) / 256
                    codes = [rng.randrange(-24, 25) for _ in range(span)]
                    if phrase in (3, 4, 5):
                        scale, zero = 0.03125, 0
                        direction = 1 if version == 'r1' else -1
                        codes = [9 + direction * (phrase - 3) * (j % 2) for j in range(span)]
                        saved[phrase, segment] = codes
                    stream.write(HEADER.pack(phrase, segment, zero, scale, -0.00390625, 0.0078125))
                    stream.write(struct.pack(f'<{span}b', *codes))
        for address, (phrase, segments, available, status) in enumerate([
            (3, [0, 1], 0, 'ok'), (4, [0], 0, 'failed'), (5, [0], 1, 'ok'),
            (3, [0], 1, 'ok'), (4, [1], 2, 'ok'), (5, [1], 2, 'ok'),
        ]):
            name = f'{version}-p{address}.json'
            values = []
            if status == 'ok':
                correction = -0.001953125 if address == 3 else 0.001953125
                for segment in segments:
                    original = [x / 32 + correction for x in saved[phrase, segment]]
                    values.append([phrase, segment, original])
            write_json(root / name, {'library': version, 'address': address, 'values': values})
            manifest['pages'].append({'file': name, 'library': version, 'address': address, 'status': status,
                                      'available_round': available, 'transmitted_bytes': 40 + 4 * sum(capacities[i] for i in segments),
                                      'coverage': [[phrase, segment] for segment in segments]})
    for request in range(queries):
        segments = []
        for start, span in zip(starts, capacities):
            codes = [rng.randrange(-4, 8) for _ in range(span)] if request else [4] * span
            segments.append([start, codes, 0, 0.03125, [-0.0078125, 0.01171875]])
        old = request < queries // 2
        manifest['requests'].append({'query': f'q{request}', 'library': 'r1' if old else 'r2',
                                     'arrival_round': 0 if old else 1, 'min_margin': 0.08 if request % 2 else 1.35,
                                     'wake_floor': 13 + (request % 4) * 3, 'priority': request % 5,
                                     'required': request % 3 == 0, 'segments': segments})
    write_json(root / 'manifest.json', manifest)
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='生成短语库的设备页流')
    parser.add_argument('directory', type=Path)
    parser.add_argument('--phrases', type=int, default=8192)
    parser.add_argument('--width', type=int, default=519)
    parser.add_argument('--queries', type=int, default=48)
    args = parser.parse_args()
    generate(args.directory, args.phrases, args.width, args.queries)
