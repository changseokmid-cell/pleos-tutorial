"""Extract real frames from the five selected videos; never modify the MP4s.

By default sources are resolved against the parent project workspace.
For a separate clone, download the Release MP4 assets and pass --video-dir.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video-dir', type=Path)
    args = parser.parse_args()
    manifest = ROOT / 'demos/media-manifest.json'
    data = json.loads(manifest.read_text(encoding='utf8'))
    for item in data['items']:
        source = (args.video_dir / item['releaseAssetName']) if args.video_dir else (
            ROOT.parent / item['workspaceSource']
        )
        if sha256(source) != item['sha256']:
            raise ValueError(f'Selected video hash does not match: {source}')
        thumb = ROOT / item['thumbnail']['path']
        thumb.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
            '-ss', str(item['thumbnail']['timeSeconds']), '-i', str(source),
            '-frames:v', '1', '-vf', 'scale=960:540', '-q:v', '2', str(thumb),
        ], check=True, timeout=60)
        item['thumbnail'].update(
            sha256=sha256(thumb), width=960, height=540,
            method='FFmpeg frame extraction; no generated artwork or added overlay',
        )
        print(item['feature'], thumb.name, flush=True)
    manifest.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n',
        encoding='utf8', newline='\n',
    )


if __name__ == '__main__':
    main()
