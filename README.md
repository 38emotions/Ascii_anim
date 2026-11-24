# ascii_anim

이미지/GIF를 터미널 ASCII 아트로 변환·재생합니다.

```bash
pip install Pillow
```

## 폴더 구조

```
ascii_anim/
├── ascii_anim.py
├── README.md
└── anim.gif        ← 변환할 이미지/GIF를 여기에 넣기
```

다른 위치의 파일은 경로를 그대로 넘기면 됩니다: `python3 ascii_anim.py ~/Downloads/anim.gif`

## 사용법

```bash
python3 ascii_anim.py                          # 데모
python3 ascii_anim.py image.png -w 60          # 정지 이미지
python3 ascii_anim.py anim.gif -w 80           # GIF 재생
python3 ascii_anim.py anim.gif -w 80 -c        # 컬러
python3 ascii_anim.py anim.gif --line -w 50    # 선화 (흰 바탕 + 검은 외곽선)
python3 ascii_anim.py anim.gif --invert        # 명암 반전
python3 ascii_anim.py anim.gif --loops 3       # 반복 횟수 (0 = 무한)
python3 ascii_anim.py anim.gif -o out.txt      # 첫 프레임을 텍스트로 저장
```

| 옵션 | 설명 |
|---|---|
| `-w` | 가로 글자 수 (기본 80) |
| `-c` | 24bit 컬러 |
| `--line` | 명암 반전 + 여백 자동 크롭 |
| `--invert` | 명암 반전 |
| `--aspect` | 세로 비율 보정 (기본 0.5) |
| `--loops` | GIF 반복 횟수 |
| `-o` | 텍스트 파일로 저장 |

종료: `Ctrl+C`
