#!/usr/bin/env python3
"""Patch a captive portal ZIP setting a specific video file name in index/login pages.

Usage:
  python patch_portal_zip.py -i portal_original.zip -v Eld02.mp4 [-o portal_patched.zip]

Behavior:
  - Extracts ZIP to a temp dir.
  - Detects index.html (+ login.html/login2.html if present).
  - Rewrites first <source src="assets/videos/..."> to chosen video name (adds .mp4 if missing).
  - Updates poster attribute if a matching poster (same basename .jpg/.png) exists OR if poster references old eldNN.*.
  - Creates/updates assets/videos/selected_video.txt with the chosen video name.
  - Repackages ZIP (new file unless --in-place specified).
"""
from __future__ import annotations
import argparse, zipfile, tempfile, shutil, os, re, sys
from pathlib import Path

def patch_html(path: Path, video_name: str, posters: list[str]) -> bool:
    if not path.is_file():
        return False
    try:
        content = path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return False
    changed = False
    # Ensure source replacement
    pattern = r'(<source\b[^>]*\bsrc=["\']assets/videos/)([^"\']+)(["\'][^>]*>)'
    if f"assets/videos/{video_name}" not in content:
        new_content, n = re.subn(pattern, r'\1' + video_name + r'\3', content, count=1)
        if n == 0:
            # fallback direct replace of eld01.mp4 / eld02.mp4 etc
            new_content = re.sub(r'assets/videos/eld\d+\.mp4', f'assets/videos/{video_name}', content, count=1)
            if new_content != content:
                n = 1
        if n > 0:
            content = new_content
            changed = True
    # Poster logic
    base_no_ext = os.path.splitext(video_name)[0]
    for ext in ('.jpg', '.png'):
        cand = f'assets/videos/{base_no_ext}{ext}'
        if any(p.endswith(cand.split('/')[-1]) for p in posters):
            # Replace poster attr if not already
            if cand not in content:
                new_content, n2 = re.subn(r'(poster=["\']assets/videos/)([^"\']+)(["\'])', r'\1' + base_no_ext + ext + r'\3', content, count=1)
                if n2 == 0:
                    # fallback if poster eldNN.jpg exists
                    new_content = re.sub(r'poster=["\']assets/videos/eld\d+\.(jpg|png)["\']', f'poster="{cand}"', content, count=1)
                    if new_content != content:
                        n2 = 1
                if n2 > 0:
                    content = new_content
                    changed = True
            break
    if changed:
        try:
            path.write_text(content, encoding='utf-8')
        except Exception as e:
            print(f"Falha ao gravar {path}: {e}", file=sys.stderr)
            return False
    return changed

def main():
    ap = argparse.ArgumentParser(description='Patch portal ZIP video reference.')
    ap.add_argument('-i','--input', required=True, help='Input portal ZIP')
    ap.add_argument('-v','--video', required=True, help='Desired video filename (with or without extension .mp4)')
    ap.add_argument('-o','--output', help='Output ZIP (default: add _patched before extension)')
    ap.add_argument('--in-place', action='store_true', help='Overwrite original ZIP in place')
    args = ap.parse_args()

    zip_in = Path(args.input).resolve()
    if not zip_in.is_file():
        print('ZIP de entrada não encontrado', file=sys.stderr)
        sys.exit(1)

    video_name = args.video.strip()
    if '.' not in os.path.basename(video_name):
        video_name += '.mp4'

    if args.in_place:
        zip_out = zip_in
    else:
        if args.output:
            zip_out = Path(args.output).resolve()
        else:
            zip_out = zip_in.with_name(zip_in.stem + '_patched' + zip_in.suffix)

    with tempfile.TemporaryDirectory() as td:
        extract_dir = Path(td) / 'extracted'
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_in, 'r') as z:
            z.extractall(extract_dir)
        # Collect posters
        videos_dir = extract_dir / 'assets' / 'videos'
        posters = []
        if videos_dir.is_dir():
            for f in videos_dir.iterdir():
                if f.suffix.lower() in ('.jpg','.png'):
                    posters.append(str(f))
            # write selected_video.txt override
            try:
                (videos_dir / 'selected_video.txt').write_text(video_name + '\n', encoding='utf-8')
            except Exception as e:
                print(f'Falha ao criar selected_video.txt: {e}', file=sys.stderr)
        changed_any = False
        for name in ['index.html','login.html','login2.html']:
            p = extract_dir / name
            changed = patch_html(p, video_name, posters)
            changed_any = changed_any or changed
        # Repack
        with zipfile.ZipFile(zip_out, 'w', zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(extract_dir):
                for f in files:
                    full = Path(root)/f
                    rel = full.relative_to(extract_dir)
                    z.write(full, rel.as_posix())
    print(f'ZIP gerado: {zip_out}')

if __name__ == '__main__':
    main()
