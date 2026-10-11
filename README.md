# koe — ぷちの声をえらぶ(VOICEVOX の声の見本)

https://teampuchi.github.io/koe/

VOICEVOX の全話者・全スタイルで同じ一文「はじめまして。ぷちです。きょうも、いっしょに。」を聞き比べるページ。
ぷちの声は里親さんとぷち自身であとから決める(10/11 決定)。お迎え会で里親さんがスマホで聞き比べる。ぷちたちも読める。

- `index.html` — 人向けのページ(petit-brand の色と書体。話者ごとのカード、スタイルごとの再生ボタン、speaker id、絞り込み、利用規約)
- `voices.json` — 機械で読む形(話者・スタイル・speaker id・音のファイル・利用規約)
- `VOICES.md` — ぷちたちが読む一覧
- `audio/<speaker id>.mp3` — 音(VOICEVOX で生成、mono 24kHz 64kbps、全部で 4MB ほど)
- `tools/gen.py` — 運営の PC で VOICEVOX ENGINE(http://localhost:50021)を動かして作り直す。ffmpeg が要る

## 版

`VERSION`・`index.html` の `<meta name="version">`・`KOE_VERSION` の 3 つを同じ値に。main に入ると CI がタグ `vX.Y.Z` と Release を作る(kisekae・petit-body-simulator と同じ)。

## クレジット・利用規約

音は VOICEVOX で生成。話者ごとに「VOICEVOX:話者名」の表記が必要(ページに一覧)。各話者の利用規約は VOICEVOX ENGINE の speaker_info から取ったものを voices.json の `policy` とページのカードに載せている。ぷちの声として使うときも同じ表記を守る。
