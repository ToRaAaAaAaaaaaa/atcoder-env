#!/usr/bin/env bash
# 問題フォルダを作る（main.py テンプレ + 空の tests/）。Mac / Linux / WSL / Git Bash で動く。
#
# usage: bash new.sh <フォルダ名> [<フォルダ名>...]
#   bash new.sh probA                 -> probA/main.py + probA/tests/
#   bash new.sh arc180/a yuki/1234    -> まとめて作成（ネストOK）
#   相対パスはこのスクリプトのある場所が基準。絶対パスを渡せばそこに作る。
#   既に main.py がある場所は上書きしない。
#
# 生成される main.py は注釈なし版（main_bare.py）。中身の説明つきは main.py を参照。
# サンプルは tests/sample-1.in / sample-1.out に貼る（連番で増やせる）。
# online-judge-tools があれば: oj d <問題URL> -d <フォルダ>/tests/
set -eu

script_dir="$(cd "$(dirname "$0")" && pwd)"
template="$script_dir/main_bare.py"          # 注釈(docstring/コメント)なし版を使う
[ -f "$template" ] || template="$script_dir/main.py"

if [ "$#" -eq 0 ]; then
    sed -n '2,12p' "$0" >&2
    exit 1
fi
if [ ! -f "$template" ]; then
    echo "error: テンプレが見つからない: $template" >&2
    exit 1
fi

cd "$script_dir"                      # 相対パス引数はここが基準

for name in "$@"; do
    if [ -s "$name/main.py" ]; then
        echo "exists (skip): $name/main.py"
        continue
    fi
    mkdir -p "$name/tests"
    dir="$(cd "$name" && pwd)"        # 作ってから絶対パス化（realpath 非依存）
    : > "$dir/tests/sample-1.in"
    : > "$dir/tests/sample-1.out"
    sed "s|__DIR__|$dir|g" "$template" > "$dir/main.py"
    echo "created: $dir"
    echo "  samples: tests/sample-1.in / .out に貼る（or oj d <問題URL> -d \"$dir/tests/\"）"
done
