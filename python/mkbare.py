#!/usr/bin/env python3
"""main.py から docstring と # コメントを取り除いた main_bare.py を作る。
usage: python3 mkbare.py
先頭の実行コマンド（__DIR__ を含むヘッダ）は残す。main.py を編集したらこれを実行して更新する。"""
import ast
import io
import os
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))


def strip_source(src):
    tree = ast.parse(src)
    drop = set()                       # 削除する行番号（docstring）
    for node in ast.walk(tree):        # Module は対象外＝先頭ヘッダは残す
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        body = node.body
        if len(body) > 1 and isinstance(body[0], ast.Expr) \
                and isinstance(body[0].value, ast.Constant) \
                and isinstance(body[0].value.value, str):
            drop.update(range(body[0].lineno, body[0].end_lineno + 1))

    cuts = {}                          # 行番号 -> コメント開始桁（文字列中の # は誤爆しない）
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT:
            ln, col = tok.start
            cuts[ln] = min(cuts.get(ln, 1 << 30), col)

    kept = []
    for i, line in enumerate(src.splitlines(), 1):
        if i in drop:
            continue
        if i in cuts:
            line = line[:cuts[i]].rstrip()
            if not line:
                continue               # コメントだけの行は落とす
        kept.append(line)

    out, blank = [], 0                 # 連続する空行は1行に圧縮
    for line in kept:
        if line.strip():
            blank = 0
        else:
            blank += 1
            if blank > 1:
                continue
        out.append(line)
    return "\n".join(out).rstrip() + "\n"


def main():
    src = open(os.path.join(HERE, "main.py"), encoding="utf-8").read()
    bare = strip_source(src)
    compile(bare, "main_bare.py", "exec")          # 壊れていないか検査
    with open(os.path.join(HERE, "main_bare.py"), "w", encoding="utf-8") as f:
        f.write(bare)
    print("main_bare.py を更新: {} 行 -> {} 行".format(
        len(src.splitlines()), len(bare.splitlines())))


if __name__ == "__main__":
    main()
