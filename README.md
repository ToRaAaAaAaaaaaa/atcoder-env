# atcoder-env

競プロ用の **全部入り Python テンプレート** と、問題フォルダを作るスクリプト。
Mac / Linux / WSL / Git Bash のどこでも動く（bash 3.2 以上）。

## 使い方

```sh
git clone https://github.com/ToRaAaAaAaaaaaa/atcoder-env.git
cd atcoder-env/python
bash new.sh probA          # probA/main.py と probA/tests/ ができる（注釈なし版が入る）
```

`tests/sample-1.in` / `sample-1.out` にサンプルを貼って実行:

```sh
cd probA
python3 main.py < tests/sample-1.in
```

[online-judge-tools](https://github.com/online-judge-tools/oj) があれば自動取得＆一括照合:

```sh
oj d <問題URL> -d tests/          # サンプルをダウンロード
oj t -c "python3 main.py" -d tests/
```

まとめて作成・ネストもOK:

```sh
bash new.sh arc180/a yuki/1234
```

## ファイル

| ファイル | 中身 |
|---|---|
| `python/main.py` | テンプレ本体（**説明つき**。何が使えるか調べる用） |
| `python/main_bare.py` | 同じ中身から docstring と `#` コメントを除いた版（**生成に使われる**のはこっち） |
| `python/mkbare.py` | `main.py` を編集したら `python3 mkbare.py` で `main_bare.py` を更新 |
| `python/new.sh` | 問題フォルダを作る |

## テンプレート (`python/main.py`) の中身

| 分類 | 使えるもの |
|---|---|
| 入力 | `nexts(n)`（整数n個） / `nextstr(n)`（文字列n個） / `data`（トークン配列）※1回読み |
| 出力 | `output()` `Yes()` `No()` `Print()`（`print` は使わず stdout に直接書く） |
| グラフ | `Graph`（BFS/反復DFS） / `WGraph`（ダイクストラ） / `BFS.grid`（番兵パディングの多点BFS） |
| 探索 | `BinarySearch.meguru`（めぐる式） `.real` `.count_in` |
| 数学 | `Comb`（mod nCk/nPk/nHk） `sieve` `factorize` `divisors` `is_prime`（Miller-Rabin・64bit） |
| 文字 | `char(n)`=chr（数→文字） / `code(c)`=ord（文字→数） |
| 進数 | `base_conv(a, b, c)`（b進数の a を c進数の文字列に。`base_conv("ff",16,2)`→`'11111111'`） |
| リスト | `rev(a)`（反転） / `cut(a,l,r)`（l〜r を切り出し・両端含む） / `cut_out(a,l,r)`（除いた残り） |
| その他 | `toposort` `lis` `mat_pow` / 幾何 `cross` `dot` `seg_intersect` `convex_hull` |
| 定数 | `INF` `DIJ4` `DIJ8` |

- 素の `nCk` は `math.comb(n, k)` でOK（mod を取るなら `Comb` クラス）
- **グラフの頂点は 1-indexed 統一**（AtCoder の入力をそのまま `g.add(u, v)` に渡せる）
- `from atcoder...`（ACL）は AtCoder ジャッジに標準装備されている前提。ローカルで使うなら
  `pip install git+https://github.com/not522/ac-library-python`。
  未インストールでも `try/except` で読み飛ばすのでテンプレは動く。

## 注意

- 実行は **`bash new.sh ...`**（zsh では叩かない）
- 生成される `main.py` の3行目（`addtest.sh` の行）は開発機（Mac）専用のパス。他PCでは無視してOK
