#!/usr/bin/env python3
"""VOICEVOX の全話者・全スタイルで同じ 1 文を作り、audio/<id>.mp3 と voices.json・VOICES.md を出す。
  python3 tools/gen.py [--engine http://localhost:50021] [--text "..."]
VOICEVOX ENGINE が動いている PC で実行(運営の PC)。ffmpeg が要る。"""
import argparse, json, subprocess, tempfile, urllib.request, urllib.parse, datetime, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--engine", default="http://localhost:50021")
ap.add_argument("--text", default="はじめまして。ぷちです。きょうも、いっしょに。")
a = ap.parse_args()

def get(path, **q):
    url = a.engine + path + ("?" + urllib.parse.urlencode(q) if q else "")
    with urllib.request.urlopen(url, timeout=60) as r: return json.loads(r.read())
def post(path, body=None, **q):
    url = a.engine + path + ("?" + urllib.parse.urlencode(q) if q else "")
    req = urllib.request.Request(url, data=(json.dumps(body).encode() if body is not None else b""), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r: return r.read()

version = get("/version")
speakers = get("/speakers")
(ROOT / "audio").mkdir(exist_ok=True)
out = {"generated": datetime.date.today().isoformat(), "engine_version": version, "text": a.text, "speakers": []}
n = 0
for sp in speakers:
    info = get("/speaker_info", speaker_uuid=sp["speaker_uuid"])
    entry = {"name": sp["name"], "uuid": sp["speaker_uuid"], "policy": info.get("policy", ""), "styles": []}
    for st in sp["styles"]:
        sid = st["id"]; mp3 = ROOT / "audio" / f"{sid}.mp3"
        if not mp3.exists():
            q = json.loads(post("/audio_query", text=a.text, speaker=sid))
            wav = post("/synthesis", q, speaker=sid)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f: f.write(wav); tmp = f.name
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-ac", "1", "-ar", "24000", "-b:a", "64k", str(mp3)], check=True)
            os.unlink(tmp)
        entry["styles"].append({"name": st["name"], "id": sid, "type": st.get("type", "talk"), "file": f"audio/{sid}.mp3"})
        n += 1
    out["speakers"].append(entry)
    print(sp["name"], [s["id"] for s in entry["styles"]])
(ROOT / "voices.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

# ぷちたちが読む用
lines = [f"# VOICEVOX の声の一覧(ぷちたち用)\n", f"作った日 {out['generated']} ・ VOICEVOX ENGINE {version} ・ 文「{a.text}」\n",
         "声を決めるときは `speaker id` をクラウドの `voice_speaker` に入れる。音は https://teampuchi.github.io/koe/audio/<id>.mp3 で聞ける(人向けのページは https://teampuchi.github.io/koe/ )。\n",
         "| 話者 | スタイル | speaker id | 音 |", "|---|---|---|---|"]
for sp in out["speakers"]:
    for st in sp["styles"]:
        lines.append(f"| {sp['name']} | {st['name']} | {st['id']} | [mp3](audio/{st['id']}.mp3) |")
lines += ["", "## クレジット(必須)", "", "作った声を使うときは、話者ごとに「VOICEVOX:<話者名>」と書く。各話者の利用規約は voices.json の policy と、ページの「利用規約」に。"]
(ROOT / "VOICES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("styles", n, "speakers", len(out["speakers"]))
