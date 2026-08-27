'''
cd "__DIR__" && oj t -c "uv run --with sortedcontainers --with 'git+https://github.com/not522/ac-library-python' python main.py" -d ./tests/
zsh "$HOME/Library/Preferences/atcoder-cli-nodejs/python/addtest.sh" "__DIR__"
'''

import math
from collections import deque, defaultdict, Counter
from heapq import heappop, heappush, heapify
from bisect import bisect_left, bisect_right, insort
import sys
from itertools import permutations, combinations, product, accumulate

sys.setrecursionlimit(1 << 20)   # 再帰を書くなら。基本は反復推奨（PyPyは深い再帰に弱い）
INF = 1 << 60
DIJ4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIJ8 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]


# ===== ACL（AtCoderジャッジ標準装備。ローカルは main.py 冒頭の --with 付きコマンドで実行）=====
# ⚠ ACL は 0-indexed！（自前クラス Graph/WGraph は 1-indexed のまま）
try:
    from atcoder.dsu import DSU                  # DSU(n); merge/same/size/leader/groups
    from atcoder.fenwicktree import FenwickTree  # FenwickTree(n); add(i,x) / sum(l,r)=[l,r)半開
    from atcoder.segtree import SegTree          # SegTree(op, e, v); set/get/prod(l,r)=[l,r)/all_prod
    from atcoder.lazysegtree import LazySegTree  # LazySegTree(op, e, mapping, composition, id_, v) 区間更新
except ImportError:                              # --with 無しのローカル実行では未定義（使う時に気づける）
    pass
# 必要になったらコメント解除:
# from atcoder.scc import SCCGraph               # 強連結成分
# from atcoder.maxflow import MFGraph            # 最大流
# from atcoder.string import suffix_array, z_algorithm, lcp_array
# from atcoder.math import crt, floor_sum, inv_mod, pow_mod
# 多重集合（削除できる集合）は from sortedcontainers import SortedList


class BinarySearch:
    @staticmethod
    def meguru(ng, ok, check):
        """整数のめぐる式二分探索。check(x)==True となる境界(ok側)を返す。
        単調に False -> True なら ok>ng、True -> False なら ok<ng で呼ぶ。
        例) 「条件を満たす最小の x」「条件を満たす最大の x」など。"""
        while abs(ok - ng) > 1:
            mid = (ok + ng) // 2
            if check(mid):
                ok = mid
            else:
                ng = mid
        return ok

    @staticmethod
    def real(ng, ok, check, loop=100):
        """実数版。回数固定で回す（誤差問題向け）。"""
        for _ in range(loop):
            mid = (ok + ng) / 2
            if check(mid):
                ok = mid
            else:
                ng = mid
        return ok

    @staticmethod
    def count_in(a, left, right):
        """ソート済み a で left<=x<=right の個数"""
        return bisect_right(a, right) - bisect_left(a, left)

class BFS:
    """幅優先探索。グリッド(平坦化)と隣接リストの両対応。
    あなたの abc460/d スタイル: H=h+2,W=w+2 の番兵パディングで1次元化し、
    境界判定なし・多点スタート・未訪問は INF 番兵で判定する。
    print は使わず、結果は距離配列で返す（出力は呼び出し側の output() で）。"""
    INF = 1 << 60

    @staticmethod
    def grid(a, starts, h, w, diag=False, wall=ord("#")):
        """h*w グリッドを番兵パディングして多点BFS。
        a      : 各行の bytes（data[...] をそのまま渡す。a[i][j] が ord 値）
        starts : スタート (i, j) の列挙（0-indexed・元グリッド基準）
        diag   : True で8方向、False で4方向
        wall   : 壁とみなす ord 値（既定 '#'）。壁と番兵枠には入らない。
        戻り値 : (D, W)。元の (i, j) の距離は D[(i + 1) * W + (j + 1)]、未到達は INF。"""
        INF = BFS.INF
        H, W = h + 2, w + 2
        size = H * W
        D = [INF] * size
        block = bytearray(size)                 # 1 なら侵入禁止（壁 or 番兵枠）
        for i in range(W):                      # 上下の番兵枠
            block[i] = 1
            block[(H - 1) * W + i] = 1
        for i in range(H):                      # 左右の番兵枠
            block[i * W] = 1
            block[i * W + W - 1] = 1
        for i in range(h):                      # 壁
            base = (i + 1) * W + 1
            row = a[i]
            for j in range(w):
                if row[j] == wall:
                    block[base + j] = 1
        flat_dirs = [-1, -W - 1, -W, -W + 1, 1, W + 1, W, W - 1] if diag else [-1, -W, 1, W]
        Q = deque()
        for i, j in starts:
            pos = (i + 1) * W + (j + 1)
            if not block[pos]:
                D[pos] = 0
                Q.append(pos)
        while Q:
            pos = Q.popleft()
            d = D[pos] + 1
            for fd in flat_dirs:
                npos = pos + fd
                if D[npos] == INF and not block[npos]:
                    D[npos] = d
                    Q.append(npos)
        return D, W

    @staticmethod
    def graph(adj, starts, n):
        """隣接リスト adj（adj[v] が v の隣接頂点 list）で多点BFS。0-indexed。
        starts : スタート頂点の列挙
        戻り値 : 距離 list D（未到達は INF）。連結成分のサイズは D[v] != INF の個数。"""
        INF = BFS.INF
        D = [INF] * n
        Q = deque()
        for s in starts:
            if D[s] == INF:
                D[s] = 0
                Q.append(s)
        while Q:
            v = Q.popleft()
            d = D[v] + 1
            for u in adj[v]:
                if D[u] == INF:
                    D[u] = d
                    Q.append(u)
        return D

class Graph:
    """無向グラフ。AtCoderの1-indexed入力をそのまま add(u, v) に渡す（内部で0-indexed化）。
    g = Graph(N) → ループで g.add(u, v) → g.bfs(1) / g.dfs(1)"""

    def __init__(self, n):
        self.n = n
        self.adj = [[] for _ in range(n)]

    def add(self, u, v):
        """辺 (u, v) を両方向に張る。u, v は1-indexed"""
        u -= 1
        v -= 1
        self.adj[u].append(v)
        self.adj[v].append(u)

    def bfs(self, *starts):
        """多点BFS。starts はスタート頂点の番号（1-indexed）。
        g.bfs(1) → 頂点1から各頂点への最短距離。g.bfs(1, 3) → 頂点1と3の多点スタート。
        戻り値 D は0-indexed（頂点vの距離は D[v-1]、未到達は BFS.INF）"""
        return BFS.graph(self.adj, [s - 1 for s in starts], self.n)

    def dfs(self, start):
        """反復DFS（行きがけ順）。start は1-indexed。
        戻り値 (order, par): order は訪問順の頂点番号(1-indexed)リスト、
        par は0-indexedの親配列（根と未到達は -1）"""
        s = start - 1
        par = [-1] * self.n
        visited = [False] * self.n
        visited[s] = True
        order = []
        stack = [s]
        while stack:
            v = stack.pop()
            order.append(v + 1)
            for u in self.adj[v]:
                if not visited[u]:
                    visited[u] = True
                    par[u] = v
                    stack.append(u)
        return order, par

class WGraph:
    """重み付きグラフ（1-indexed）。g = WGraph(N); g.add(u, v, w)（無向。有向は directed=True）。
    g.dijkstra(s) → 距離list D（0-indexed: 頂点vの距離は D[v-1]、未到達は INF）。負辺は不可。"""

    def __init__(self, n):
        self.n = n
        self.adj = [[] for _ in range(n)]

    def add(self, u, v, w, directed=False):
        u -= 1
        v -= 1
        self.adj[u].append((v, w))
        if not directed:
            self.adj[v].append((u, w))

    def dijkstra(self, start):
        D = [INF] * self.n
        s = start - 1
        D[s] = 0
        q = [(0, s)]
        while q:
            d, v = heappop(q)
            if d > D[v]:
                continue
            for u, w in self.adj[v]:
                nd = d + w
                if nd < D[u]:
                    D[u] = nd
                    heappush(q, (nd, u))
        return D


class Comb:
    """mod 組合せ（階乗前計算）。c = Comb(2 * 10**5)（既定mod=998244353。1e9+7なら mod=10**9+7）。
    c.C(n, k)=nCk, c.P(n, k)=nPk, c.H(n, k)=重複組合せ nHk"""

    def __init__(self, n, mod=998244353):
        self.mod = mod
        f = [1] * (n + 1)
        for i in range(1, n + 1):
            f[i] = f[i - 1] * i % mod
        inv = [1] * (n + 1)
        inv[n] = pow(f[n], -1, mod)
        for i in range(n, 0, -1):
            inv[i - 1] = inv[i] * i % mod
        self.f = f
        self.finv = inv

    def C(self, n, k):
        if k < 0 or k > n:
            return 0
        return self.f[n] * self.finv[k] % self.mod * self.finv[n - k] % self.mod

    def P(self, n, k):
        if k < 0 or k > n:
            return 0
        return self.f[n] * self.finv[n - k] % self.mod

    def H(self, n, k):
        if n == 0 and k == 0:
            return 1
        return self.C(n + k - 1, k)


# ---------- 数論 ----------
def sieve(n):
    """n 以下の素数 list（エラトステネス）"""
    if n < 2:
        return []
    is_p = bytearray([1]) * (n + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if is_p[i]:
            is_p[i * i::i] = bytearray(len(is_p[i * i::i]))
    return [i for i in range(n + 1) if is_p[i]]


def factorize(x):
    """素因数分解。dict {素数: 指数}（試し割り、x <= 1e12 目安）"""
    res = {}
    d = 2
    while d * d <= x:
        while x % d == 0:
            res[d] = res.get(d, 0) + 1
            x //= d
        d += 1 if d == 2 else 2
    if x > 1:
        res[x] = res.get(x, 0) + 1
    return res


def divisors(x):
    """約数の昇順 list"""
    small = []
    large = []
    d = 1
    while d * d <= x:
        if x % d == 0:
            small.append(d)
            if d * d != x:
                large.append(x // d)
        d += 1
    return small + large[::-1]


def is_prime(n):
    """決定的 Miller-Rabin（64bit まで正確）"""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


# ---------- その他アルゴリズム ----------
def toposort(n, edges):
    """トポロジカルソート（Kahn法）。edges は 1-indexed の (u, v)=u→v のlist。
    戻り値: 頂点番号(1-indexed)の順序list。閉路があれば None"""
    adj = [[] for _ in range(n + 1)]
    deg = [0] * (n + 1)
    for u, v in edges:
        adj[u].append(v)
        deg[v] += 1
    Q = deque(v for v in range(1, n + 1) if deg[v] == 0)
    order = []
    while Q:
        v = Q.popleft()
        order.append(v)
        for u in adj[v]:
            deg[u] -= 1
            if deg[u] == 0:
                Q.append(u)
    return order if len(order) == n else None


def lis(a, strict=True):
    """最長増加部分列の長さ。strict=False で広義単調増加"""
    b = bisect_left if strict else bisect_right
    tails = []
    for x in a:
        i = b(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


def mat_mul(A, B, mod=0):
    """行列積（mod=0 なら剰余なし）"""
    n, m, l = len(A), len(B[0]), len(B)
    C = [[0] * m for _ in range(n)]
    for i in range(n):
        Ai = A[i]
        Ci = C[i]
        for k in range(l):
            a = Ai[k]
            if a:
                Bk = B[k]
                for j in range(m):
                    Ci[j] += a * Bk[j]
        if mod:
            for j in range(m):
                Ci[j] %= mod
    return C


def mat_pow(A, k, mod=0):
    """行列累乗 A^k（フィボナッチ・遷移DPの高速化）"""
    n = len(A)
    R = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    while k:
        if k & 1:
            R = mat_mul(R, A, mod)
        A = mat_mul(A, A, mod)
        k >>= 1
    return R


# ---------- 幾何（整数座標推奨） ----------
def cross(o, a, b):
    """外積 (a-o)×(b-o)。>0: oから見て a→b は左折（反時計回り）"""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def dot(o, a, b):
    """内積 (a-o)・(b-o)"""
    return (a[0] - o[0]) * (b[0] - o[0]) + (a[1] - o[1]) * (b[1] - o[1])


def seg_intersect(p1, p2, p3, p4):
    """線分 p1p2 と p3p4 が交わるか（端点接触も True。整数座標なら誤差なし）"""
    d1 = cross(p3, p4, p1)
    d2 = cross(p3, p4, p2)
    d3 = cross(p1, p2, p3)
    d4 = cross(p1, p2, p4)
    if ((d1 > 0 > d2) or (d1 < 0 < d2)) and ((d3 > 0 > d4) or (d3 < 0 < d4)):
        return True

    def on(p, q, r):  # q が線分 pr 上か（一直線前提）
        return min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and min(p[1], r[1]) <= q[1] <= max(p[1], r[1])
    if d1 == 0 and on(p3, p1, p4):
        return True
    if d2 == 0 and on(p3, p2, p4):
        return True
    if d3 == 0 and on(p1, p3, p2):
        return True
    if d4 == 0 and on(p1, p4, p2):
        return True
    return False


def convex_hull(pts):
    """凸包（Andrew's monotone chain）。反時計回りの頂点list（一直線上の点は含めない）"""
    pts = sorted(set(map(tuple, pts)))
    if len(pts) <= 2:
        return pts
    lo = []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    hi = []
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def output(a):
    return sys.stdout.write(a)
def Yes():
    return output("".join("Yes") + "\n")
def No():
    return output("".join("No") + "\n")
def Print(a):
    return output("".join(a) + "\n")
def OR(a, b):
    return a | b
def AND(a, b):
    return a & b
def XOR(a, b):
    return a ^ b
def to_bin(x, w=0):
    """整数を2進文字列に変換（'0b' なし）。w を指定するとその桁数まで0埋め。
    例) to_bin(10) -> '1010' / to_bin(10, 8) -> '00001010'"""
    return format(x, "0" + str(w) + "b") if w else format(x, "b")
def from_bin(s):
    """2進文字列を整数に戻す。例) from_bin('1010') -> 10"""
    return int(s, 2)
def popcount(x):
    """立っているビットの個数。例) popcount(10) -> 2"""
    return bin(x).count("1")
def two_pointers(l, r, A):
    return A[r+1] - A[l]
def haepque(a):
    return heapify(a)
def rev(a):
    """反転した新しい list を返す（元の a は変更しない）。文字列にも使える。
    例) rev([1, 2, 3]) -> [3, 2, 1] / rev("abc") -> "cba" """
    return a[::-1]
def cut(a, l, r):
    """a の l 番目〜 r 番目（0-indexed・両端含む）を切り抜いて返す。文字列にも使える。
    例) cut([0, 1, 2, 3, 4], 1, 3) -> [1, 2, 3]"""
    return a[l:r + 1]
def cut_out(a, l, r):
    """a から l 番目〜 r 番目（0-indexed・両端含む）を取り除いた残りを返す。
    例) cut_out([0, 1, 2, 3, 4], 1, 3) -> [0, 4]"""
    return a[:l] + a[r + 1:]

# --- 文字と数（chr / ord を忘れる用）---
def char(n):
    """数 -> 文字。char(97) -> 'a'   ※中身は chr(n)"""
    return chr(n)
def code(c):
    """文字 -> 数。code('a') -> 97   ※中身は ord(c)"""
    return ord(c)

# --- 進数変換 ---
def base_conv(a, b, c):
    """b進数の a を c進数の文字列にして返す（2<=b,c<=36）。a は文字列でも整数でもOK。
    10以上の桁は A,B,C... で表す。負数・0 も可。
    例) base_conv("ff", 16, 2) -> '11111111' / base_conv(255, 10, 16) -> 'FF'
        base_conv(6, 10, 2) -> '110' / base_conv("110", 2, 10) -> '6'
    ※ 数として使いたいときは int(base_conv(...), c) か、b進数->10進数だけなら int(str(a), b)"""
    n = int(str(a), b)
    if n == 0:
        return "0"
    sign = "-" if n < 0 else ""
    n = abs(n)
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    res = []
    while n:
        n, r = divmod(n, c)
        res.append(digits[r])
    res.reverse()
    return sign + "".join(res)

data = sys.stdin.buffer.read().split()
_it = iter(data)
def nx():
    """整数を1個読む。読むと自動で進むので num += の進め忘れが構造的に起きない"""
    return int(next(_it))
def nxs():
    """文字列を1個読む"""
    return next(_it).decode()
def nexts(n):
    """整数を n 個読んで list で返す。例) A = nexts(N)"""
    return [int(next(_it)) for _ in range(n)]
def nextstr(n):
    """文字列を n 個読んで list で返す"""
    return [next(_it).decode() for _ in range(n)]


