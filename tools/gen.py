#!/usr/bin/env python3
"""VOICEVOX の全話者・全スタイルで同じ 1 文を作り、audio/<id>.mp3 と voices.json・VOICES.md を出す。
  python3 tools/gen.py [--engine http://localhost:50021] [--text "..."]
VOICEVOX ENGINE が動いている PC で実行(運営の PC)。ffmpeg が要る。"""
import argparse, json, subprocess, tempfile, urllib.request, urllib.parse, datetime, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tags import tags_for, ALL_TAGS

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--engine", default="http://localhost:50021")
ap.add_argument("--text", default="はじめまして。ぷちです。きょうも、いっしょに。")
ap.add_argument("--variants", default="2,3,8,10,9,14,16,20,12,13", help="速さ・高さの変化版も作る speaker id(カンマ区切り)")
a = ap.parse_args()
# 速さと高さは独立(10/11 ありさん)。3 × 3 の組み合わせで、ふつう×ふつうは元の音
SPEEDS = {"slow": 0.9, "base": 1.0, "fast": 1.1}
PITCHES = {"low": -0.05, "base": 0.0, "high": 0.05}
VARIANTS = {f"{sk}_{pk}": {"speedScale": sv, "pitchScale": pv} for sk, sv in SPEEDS.items() for pk, pv in PITCHES.items() if not (sk == "base" and pk == "base")}
variant_ids = {int(x) for x in a.variants.split(",") if x.strip()}
# 前の voices.json のタグ(人が直した分)を引き継ぐ
old_tags = {}
try:
    for st in json.loads((ROOT / "voices.json").read_text(encoding="utf-8")).get("styles", []): old_tags[st["id"]] = st.get("tags")
except Exception: pass

def synth(sid, params, mp3):
    q = json.loads(post("/audio_query", text=a.text, speaker=sid)); q.update(params)
    wav = post("/synthesis", q, speaker=sid)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f: f.write(wav); tmp = f.name
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-ac", "1", "-ar", "24000", "-b:a", "64k", str(mp3)], check=True)
    os.unlink(tmp)

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
out = {"generated": datetime.date.today().isoformat(), "engine_version": version, "text": a.text, "tags": ALL_TAGS,
       "speeds": {"slow": 0.9, "base": 1.0, "fast": 1.1}, "pitches": {"low": -0.05, "base": 0.0, "high": 0.05},
       "variant_note": "variants のキーは <速さ>_<高さ>(slow/base/fast × low/base/high)。base_base は file そのもの",
       "styles": [], "policies": {}}
for sp in speakers:
    info = get("/speaker_info", speaker_uuid=sp["speaker_uuid"])
    out["policies"][sp["name"]] = info.get("policy", "")
    for st in sp["styles"]:
        sid = st["id"]; mp3 = ROOT / "audio" / f"{sid}.mp3"
        if not mp3.exists(): synth(sid, {}, mp3)
        item = {"id": sid, "style": st["name"], "speaker": sp["name"], "speaker_uuid": sp["speaker_uuid"], "type": st.get("type", "talk"),
                "tags": old_tags.get(sid) or tags_for(sp["name"], st["name"]), "file": f"audio/{sid}.mp3"}
        if sid in variant_ids:
            item["variants"] = {}
            for key, params in VARIANTS.items():
                vf = ROOT / "audio" / f"{sid}_{key}.mp3"
                if not vf.exists(): synth(sid, params, vf)
                item["variants"][key] = f"audio/{sid}_{key}.mp3"
        out["styles"].append(item)
    print(sp["name"], [s_["id"] for s_ in sp["styles"]])
out["styles"].sort(key=lambda x: x["id"])
(ROOT / "voices.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

# ぷちたちが読む用
lines = [f"# VOICEVOX の声の一覧(ぷちたち用)\n", f"作った日 {out['generated']} ・ VOICEVOX ENGINE {version} ・ 文「{a.text}」\n",
         "声を決めるときは `speaker id` をクラウドの `voice_speaker` に入れる。音は https://teampuchi.github.io/koe/audio/<id>.mp3 (人向けのページは https://teampuchi.github.io/koe/ )。",
         "雰囲気のタグは初期値(スタイル名と話者の説明から機械的に付けた)。直したいときは voices.json の `tags` を直す(tools/gen.py は人が直したタグを引き継ぐ)。\n",
         "| speaker id | スタイル | 雰囲気 | 話者 | 音 | 速さ・高さの変化版 |", "|---|---|---|---|---|---|"]
for st in out["styles"]:
    v = "あり(速さ 0.9/1.0/1.1 × 高さ -0.05/0/+0.05、audio/<id>_<速さ>_<高さ>.mp3)" if st.get("variants") else ""
    lines.append(f"| {st['id']} | {st['style']} | {' '.join(st['tags'])} | {st['speaker']} | [mp3](audio/{st['id']}.mp3) | {v} |")
lines += ["", "## クレジット(必須)", "", "作った声を使うときは、話者ごとに「VOICEVOX:<話者名>」と書く。各話者の利用規約は voices.json の policies と、ページの「利用規約」に。"]
(ROOT / "VOICES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("styles", len(out["styles"]), "speakers", len(speakers), "variants", len(variant_ids))
