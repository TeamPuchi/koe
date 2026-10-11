# koe — ぷちの声をえらぶ(VOICEVOX の声の見本)

https://teampuchi.github.io/koe/

VOICEVOX の全話者・全スタイルで同じ一文「はじめまして。ぷちです。きょうも、いっしょに。」を聞き比べるページ。
ぷちの声は里親さんとぷち自身であとから決める(10/11 決定)。お迎え会で里親さんがスマホで聞き比べる。ぷちたちも読める。

- `index.html` — 人向けのページ(petit-brand の色と書体)。**speaker id 順**に並び、各行に「きく」、おすすめ 10 個には「ゆっくり／はやめ／ひくめ／たかめ」(速さ 0.9/1.1、高さ -0.05/+0.05)、**「これにする」**(LINE に貼る文をコピー: speaker id・スタイル・雰囲気・速さ/高さ/抑揚・きかせて URL)。`#id=29` で開くとその声までスクロールして印が付く。雰囲気のタグ(やさしい・げんき・おちついた・こども・おとな・ひくめ・たかめ・ささやき・はきはき・ねむそう・なきそう・つよめ・よわき)で絞り込み。利用規約は下にまとめ
- `voices.json` — 機械で読む形(speaker id 順。スタイル・話者・**tags**(直してよい。gen.py は人が直したタグを引き継ぐ)・音のファイル・variants・policies)
- `VOICES.md` — ぷちたちが読む一覧
- `audio/<speaker id>.mp3` — 音(VOICEVOX で生成、mono 24kHz 64kbps、全部で 4MB ほど)
- `tools/gen.py` — 運営の PC で VOICEVOX ENGINE(http://localhost:50021)を動かして作り直す。ffmpeg が要る。`--variants 2,3,...` で変化版を作る speaker id、`--text` で文
- `tools/tags.py` — 雰囲気のタグの初期値(話者ごと + スタイル名から)
- クラウド側は「これにする」の文の値(speaker id・速さ・高さ・抑揚)を set_voice.py に入れる

## 版

`VERSION`・`index.html` の `<meta name="version">`・`KOE_VERSION` の 3 つを同じ値に。main に入ると CI がタグ `vX.Y.Z` と Release を作る(kisekae・petit-body-simulator と同じ)。

## クレジット・利用規約

音は VOICEVOX で生成。話者ごとに「VOICEVOX:話者名」の表記が必要(ページに一覧)。各話者の利用規約は VOICEVOX ENGINE の speaker_info から取ったものを voices.json の `policy` とページのカードに載せている。ぷちの声として使うときも同じ表記を守る。
