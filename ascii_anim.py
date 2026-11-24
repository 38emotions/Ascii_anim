#!/usr/bin/env python3
"""이미지/GIF -> 터미널 ASCII 아트 (Pillow만 사용).

사용법:
  python3 ascii_anim.py                     # 입력 없으면 데모 캐릭터 애니메이션
  python3 ascii_anim.py cat.png -w 80       # 정지 이미지
  python3 ascii_anim.py cat.gif -w 80 -c    # GIF 재생 (-c: 컬러)
  python3 ascii_anim.py cat.gif --invert    # 명암 반전
  python3 ascii_anim.py cat.gif --line -w 50 # 흰 몸통+검은 외곽선 선화 GIF 추천
  python3 ascii_anim.py cat.gif --loops 3   # 3번 반복 (0 = 무한)
  python3 ascii_anim.py cat.gif -o out.txt  # 첫 프레임을 텍스트로 저장
Ctrl+C 로 종료.
"""
import argparse
import sys
import time

from PIL import Image, ImageOps, ImageSequence

# 어두움 -> 밝음 순 (어두운 터미널 기준: 밝은 픽셀일수록 빽빽한 글자)
RAMP = " .:-=+*#%@"

DEMO_FRAMES = [
r"""
      .-~~~-.        .-~~~-.
     (  o o  )      (       )
      \  ^  /  ~~~   \  -  /
   .--'`---'`--.  .--'`---'`--.
  /   (  ~~~  ) \/   ( zzz )   \
  \___|_______|_/\___|_______|__/
      |_|   |_|      |_|   |_|
""",
r"""
      .-~~~-.        .-~~~-.
     (  ^ ^  )      (  o o  )
      \  v  /  ~~~   \  o  /
   .--'`---'`--.  .--'`---'`--.
  / \ (  ~~~  ) /\ / ( !!! ) / \
  \___|_______|_/\___|_______|__/
      |_|   |_|      |_|   |_|
""",
]


def frame_to_ascii(img, width, color, invert, aspect, crop=None):
    img = img.convert("RGBA")
    if crop:
        img = img.crop(crop)
    # 투명 배경은 검정(또는 반전 시 흰색)으로 합성
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255) if invert else (0, 0, 0, 255))
    img = Image.alpha_composite(bg, img).convert("RGB")
    w, h = img.size
    height = max(1, int(h / w * width * aspect))  # 글자는 세로로 길어서 aspect(~0.5)로 보정
    img = img.resize((width, height), Image.LANCZOS)
    gray = ImageOps.grayscale(img)
    if invert:
        gray = ImageOps.invert(gray)
    gp, cp = gray.load(), img.load()
    n = len(RAMP) - 1
    lines = []
    for y in range(height):
        row = []
        for x in range(width):
            ch = RAMP[gp[x, y] * n // 255]
            if color and ch != " ":
                r, g, b = cp[x, y]
                row.append(f"\x1b[38;2;{r};{g};{b}m{ch}")
            else:
                row.append(ch)
        lines.append("".join(row) + ("\x1b[0m" if color else ""))
    return "\n".join(lines)


def play(frames, durations, loops):
    sys.stdout.write("\x1b[2J\x1b[?25l")  # 화면 지우기, 커서 숨김
    try:
        i = 0
        while loops == 0 or i < loops:
            for f, d in zip(frames, durations):
                sys.stdout.write("\x1b[H" + f + "\n")
                sys.stdout.flush()
                time.sleep(d)
            i += 1
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\x1b[0m\x1b[?25h\n")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("path", nargs="?", help="이미지 또는 GIF 경로 (없으면 데모)")
    p.add_argument("-w", "--width", type=int, default=80, help="가로 글자 수")
    p.add_argument("-c", "--color", action="store_true", help="24bit 컬러 출력")
    p.add_argument("--invert", action="store_true", help="명암 반전 (선화: 검은 외곽선을 글자로)")
    p.add_argument("--line", action="store_true", help="선화 모드 = --invert + 여백 자동 크롭")
    p.add_argument("--aspect", type=float, default=0.5, help="글자 세로/가로 비율 보정")
    p.add_argument("--loops", type=int, default=0, help="GIF 반복 횟수 (0=무한)")
    p.add_argument("-o", "--out", help="첫 프레임을 텍스트 파일로 저장하고 종료")
    a = p.parse_args()

    if a.path is None:
        play(DEMO_FRAMES, [0.6, 0.6], a.loops)
        return

    im = Image.open(a.path)
    if a.line:
        a.invert = True
    crop = None
    if a.line:  # 모든 프레임의 불투명 영역을 합친 bbox로 크롭 (애니메이션이 흔들리지 않게)
        boxes = [fr.convert("RGBA").getchannel("A").getbbox() for fr in ImageSequence.Iterator(im)]
        boxes = [b for b in boxes if b]
        if boxes:
            pad = 4
            crop = (max(min(b[0] for b in boxes) - pad, 0), max(min(b[1] for b in boxes) - pad, 0),
                    min(max(b[2] for b in boxes) + pad, im.width), min(max(b[3] for b in boxes) + pad, im.height))
        im.seek(0)
    frames, durations = [], []
    for fr in ImageSequence.Iterator(im):
        frames.append(frame_to_ascii(fr.copy(), a.width, a.color, a.invert, a.aspect, crop))
        durations.append(max(fr.info.get("duration", 100), 20) / 1000)

    if a.out:
        with open(a.out, "w") as f:
            f.write(frames[0] + "\n")
        print(f"saved: {a.out}")
    elif len(frames) == 1:
        print(frames[0] + ("\x1b[0m" if a.color else ""))
    else:
        play(frames, durations, a.loops)


if __name__ == "__main__":
    main()
