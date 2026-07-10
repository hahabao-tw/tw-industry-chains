#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — 櫃買中心「產業價值鏈資訊平台」爬蟲
輸出 data/chains.js（window.CHAIN_DATA = {...}），供 index.html 使用。

架構原則（與 tw-margin-table / tw-market-dashboard 一致）：
- 純 Python 標準庫，無第三方依賴
- 增量更新：僅覆寫本次成功解析的產業，失敗者保留舊資料
- domain 快取（data/domains.json）：台灣公司官網域名只抓一次，可手動修正

用法：
  python build.py                 # 更新 TARGET_INDUSTRIES（預設 4100 太空衛星科技）
  python build.py --all           # 自動探索並更新全部產業鏈（首次約 40+ 次請求）
  python build.py --ic 4100 D000  # 指定 ic 代碼
  python build.py --dump          # 另存原始 HTML 至 debug/ 供除錯
  python build.py --no-domains    # 跳過台灣公司官網域名抓取
"""
import json
import os
import re
import ssl
import sys
import time
from html.parser import HTMLParser
from urllib.request import Request, urlopen

BASE = "https://ic.tpex.org.tw"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": BASE + "/index.php",
}
TARGET_INDUSTRIES = ["4100"]          # 預設更新清單；--all 或 --ic 可覆蓋
MAX_DOMAIN_FETCH_PER_RUN = 60          # 每次執行最多新抓幾家公司官網域名（逐週收斂）
SLEEP = 0.8                            # 請求間隔（秒），對來源友善

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
DEBUG_DIR = os.path.join(ROOT, "debug")
CHAINS_JS = os.path.join(DATA_DIR, "chains.js")
DOMAIN_CACHE = os.path.join(DATA_DIR, "domains.json")

MARKET_HEADERS = {
    "本國上市公司": "上市",
    "本國上櫃公司": "上櫃",
    "本國興櫃公司": "興櫃",
    "知名外國企業": "外國",
}
LAYER_KEYS = ("上游", "中游", "下游")
RE_SUB = re.compile(r"^(.+?)\s*[（(](\d+)家[)）]$")
RE_MARKET = re.compile(r"^(本國上市公司|本國上櫃公司|本國興櫃公司|知名外國企業)")
RE_TOTAL = re.compile(r"^共\s*(\d+)\s*家$")
EMPTY_MARK = "尚未有公司納入此產業鏈"
IGNORE_DOMAINS = ("tpex.org.tw", "twse.com.tw", "mops.twse", "gov.tw")


# ---------------------------------------------------------------- fetch
def fetch(url, dump_name=None):
    """GET，含 SSL 降級重試（沿用既有專案模式）。"""
    req = Request(url, headers=HEADERS)
    for attempt in range(2):
        try:
            ctx = None
            if attempt == 1:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            with urlopen(req, timeout=30, context=ctx) as r:
                raw = r.read()
            text = raw.decode("utf-8", errors="replace")
            if dump_name:
                os.makedirs(DEBUG_DIR, exist_ok=True)
                with open(os.path.join(DEBUG_DIR, dump_name), "w", encoding="utf-8") as f:
                    f.write(text)
            return text
        except Exception as e:  # noqa: BLE001
            if attempt == 1:
                print(f"  [warn] fetch failed: {url} ({e})")
                return None
            time.sleep(1)
    return None


# ---------------------------------------------------------------- token stream
class TokenStream(HTMLParser):
    """
    將頁面線性化為 token 序列，降低對確切標籤結構的依賴：
      ("text", 文字)
      ("a", href, 連結文字或 title)
    """

    def __init__(self):
        super().__init__()
        self.tokens = []
        self._href = None
        self._title = None
        self._buf = []
        self._skip = 0  # script/style 深度

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
            return
        if tag == "a":
            d = dict(attrs)
            self._href = d.get("href", "")
            self._title = d.get("title", "")
            self._buf = []

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
            return
        if tag == "a" and self._href is not None:
            text = "".join(self._buf).strip() or (self._title or "").strip()
            if text:
                self.tokens.append(("a", self._href, text))
            self._href = None
            self._buf = []

    def handle_data(self, data):
        if self._skip:
            return
        if self._href is not None:
            self._buf.append(data)
            return
        t = data.strip()
        if t:
            self.tokens.append(("text", t))


def tokenize(html_text):
    p = TokenStream()
    p.feed(html_text)
    return p.tokens


# ---------------------------------------------------------------- industry list
def discover_industries(dump=False):
    """從首頁/簡介頁的下拉選單探索所有產業 ic 代碼。"""
    html_text = fetch(f"{BASE}/introduce.php?ic=4100",
                      "industry_list.html" if dump else None)
    if not html_text:
        return []
    opts = re.findall(
        r'<option[^>]+value=["\']?(\w+)["\']?[^>]*>\s*([^<]+?)\s*</option>',
        html_text)
    seen, out = set(), []
    for code, name in opts:
        name = name.strip()
        if not name or code in seen or not re.fullmatch(r"\w{2,6}", code):
            continue
        # 排除非產業選項（如年份、空值）
        if re.fullmatch(r"(19|20)\d{2}", code):
            continue
        seen.add(code)
        out.append({"ic": code, "name": name})
    print(f"[info] 探索到 {len(out)} 個產業鏈選項")
    return out


# ---------------------------------------------------------------- chain parse
def parse_chain(html_text, ind_name):
    """
    解析單一 introduce.php?ic=X 頁面 → layers 結構。

    頁面線性結構（實測 ic=4100）：
      Stage A：上游 / (層標題) / 環節名... 中游 ... 下游 ...
      Stage B：依環節順序出現：
        [細項標籤 (N家)] * n → 各細項公司表（市場別標頭 + 公司連結）→ 共N家
        無細項之環節：公司表 → 共N家
      之後為重複的明細區與簡介文字（segments 佇列耗盡後自動忽略）
    """
    tokens = tokenize(html_text)

    # ---- Stage A：層級與環節名 ----
    layers = []           # [{"name":..., "segments":[名稱...]}]
    seg_queue = []        # [(layer_idx, seg_name)]
    i = 0
    cur_layer = -1
    stage_a_started = False
    while i < len(tokens):
        tk = tokens[i]
        if tk[0] == "text":
            t = tk[1]
            if t in LAYER_KEYS:
                stage_a_started = True
                cur_layer += 1
                # 下一個文字 token 視為層標題（如「設備製造」）
                subtitle = ""
                j = i + 1
                while j < len(tokens) and tokens[j][0] != "text":
                    j += 1
                if j < len(tokens):
                    subtitle = tokens[j][1]
                    i = j
                layers.append({"name": f"{t} · {subtitle}", "segments": []})
            elif stage_a_started:
                if RE_SUB.match(t) or RE_MARKET.match(t) or t == EMPTY_MARK:
                    break  # Stage A 結束
                if len(t) <= 12 and cur_layer >= 0:
                    layers[cur_layer]["segments"].append(t)
                    seg_queue.append((cur_layer, t))
        elif tk[0] == "a" and "company_basic.php" in tk[1] and stage_a_started:
            break
        i += 1

    if not layers or not seg_queue:
        print(f"  [warn] {ind_name}: 無法解析層級/環節結構")
        return None

    # ---- Stage B：以「細項標籤家數」對齊公司表 ----
    result = {L["name"]: {s: {} for s in L["segments"]} for L in layers}
    # result[layer][segment][sub or ""] = [company...]
    qi = 0                              # seg_queue index
    pending = []                        # [(sub_name, count)]
    cur_sub, cur_count, cur_market = None, 0, None

    def cur_seg():
        return seg_queue[qi] if qi < len(seg_queue) else None

    def open_next_sub():
        nonlocal cur_sub, cur_count
        while pending:
            name, cnt = pending.pop(0)
            if cnt > 0:
                cur_sub, cur_count = name, cnt
                return
        cur_sub, cur_count = None, 0

    def add_company(co):
        nonlocal cur_count
        seg = cur_seg()
        if seg is None:
            return
        li, sname = seg
        if cur_sub is None and pending:
            open_next_sub()
        key = cur_sub or ""
        bucket = result[layers[li]["name"]][sname].setdefault(key, [])
        bucket.append(co)
        if cur_sub is not None:
            cur_count -= 1
            if cur_count <= 0:
                open_next_sub()

    while i < len(tokens) and qi < len(seg_queue):
        tk = tokens[i]
        if tk[0] == "text":
            t = tk[1]
            m = RE_SUB.match(t)
            if m and m.group(1) not in MARKET_HEADERS:
                mh = RE_MARKET.match(t)
                if mh:  # 「本國上市公司(6家)」也符合 RE_SUB，需排除
                    cur_market = MARKET_HEADERS[mh.group(1)]
                else:
                    pending.append((m.group(1), int(m.group(2))))
            else:
                mh = RE_MARKET.match(t)
                if mh:
                    cur_market = MARKET_HEADERS[mh.group(1)]
                elif t == EMPTY_MARK:
                    if cur_sub is not None:
                        open_next_sub()
                    elif pending:
                        pending.pop(0)
                elif RE_TOTAL.match(t):
                    qi += 1
                    pending, cur_sub, cur_count, cur_market = [], None, 0, None
        elif tk[0] == "a":
            href, name = tk[1], tk[2]
            m = re.search(r"company_basic\.php\?stk_code=(\d+)", href)
            if m and cur_market:
                add_company({"n": name, "c": m.group(1),
                             "m": cur_market, "d": ""})
            elif (cur_market == "外國" and href.startswith("http")
                  and not any(x in href for x in IGNORE_DOMAINS)):
                dom = re.sub(r"^www\.", "",
                             re.sub(r"^https?://", "", href).split("/")[0])
                add_company({"n": name, "d": dom})
        i += 1

    # ---- 整理輸出 ----
    out_layers = []
    total = 0
    for L in layers:
        segs = []
        for sname in L["segments"]:
            subs_map = result[L["name"]][sname]
            subs = []
            for sub_name, cos in subs_map.items():
                # 去重（如 K-SAT 全/半形括號重複）
                seen, uniq = set(), []
                for c in cos:
                    k = c.get("c") or c.get("d") or c["n"]
                    if k in seen:
                        continue
                    seen.add(k)
                    uniq.append(c)
                if uniq:
                    subs.append({"name": sub_name or None, "companies": uniq})
                    total += len(uniq)
            if subs:
                segs.append({"name": sname, "subs": subs})
        if segs:
            out_layers.append({"name": L["name"], "segments": segs})
    if total == 0:
        print(f"  [warn] {ind_name}: 解析到 0 家公司，略過")
        return None
    print(f"  [ok] {ind_name}: {len(out_layers)} 層 / 共 {total} 筆公司歸屬")
    return out_layers


# ---------------------------------------------------------------- TW domains
def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def fetch_tw_domain(code):
    """從公司基本資料頁猜官網域名：取第一個非官方網站的外部連結。"""
    html_text = fetch(f"{BASE}/company_basic.php?stk_code={code}")
    if not html_text:
        return ""
    for href in re.findall(r'href=["\'](https?://[^"\']+)["\']', html_text):
        if any(x in href for x in IGNORE_DOMAINS):
            continue
        dom = re.sub(r"^www\.", "",
                     re.sub(r"^https?://", "", href).split("/")[0])
        if "." in dom:
            return dom
    return ""


def fill_domains(industries, cache, budget):
    """回填台灣公司域名；cache 命中不重抓，未命中且有額度才抓。"""
    fetched = 0
    for ind in industries:
        for L in ind["layers"]:
            for seg in L["segments"]:
                for sub in seg["subs"]:
                    for co in sub["companies"]:
                        code = co.get("c")
                        if not code:
                            continue
                        if code in cache:
                            co["d"] = cache[code]
                        elif fetched < budget:
                            time.sleep(SLEEP)
                            dom = fetch_tw_domain(code)
                            cache[code] = dom  # 空字串也記錄，避免重抓
                            co["d"] = dom
                            fetched += 1
                            print(f"  [domain] {code} -> {dom or '(未找到)'}")
    if fetched:
        print(f"[info] 本次新抓 {fetched} 家公司域名（上限 {budget}）")
    return cache


# ---------------------------------------------------------------- chains.js IO
def load_existing():
    """讀取既有 chains.js 以支援增量更新。"""
    if not os.path.exists(CHAINS_JS):
        return {"updated": "", "industries": []}
    with open(CHAINS_JS, encoding="utf-8") as f:
        txt = f.read()
    m = re.search(r"window\.CHAIN_DATA\s*=\s*(\{.*\});?\s*$", txt, re.S)
    if not m:
        return {"updated": "", "industries": []}
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        print("[warn] 既有 chains.js 非純 JSON（種子檔），將整檔重建")
        return {"updated": "", "industries": []}


def write_chains(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CHAINS_JS, "w", encoding="utf-8") as f:
        f.write("/* 由 build.py 自動產生，請勿手動編輯 */\n")
        f.write("window.CHAIN_DATA = ")
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print(f"[done] 已寫入 {CHAINS_JS}")


# ---------------------------------------------------------------- main
def main():
    args = sys.argv[1:]
    dump = "--dump" in args
    no_domains = "--no-domains" in args
    use_all = "--all" in args
    ics = []
    if "--ic" in args:
        j = args.index("--ic") + 1
        while j < len(args) and not args[j].startswith("--"):
            ics.append(args[j])
            j += 1

    all_inds = discover_industries(dump)
    name_of = {x["ic"]: x["name"] for x in all_inds}

    if use_all:
        targets = [x["ic"] for x in all_inds]
    elif ics:
        targets = ics
    else:
        targets = TARGET_INDUSTRIES
    if not targets:
        print("[error] 無目標產業，結束")
        sys.exit(1)

    existing = load_existing()
    merged = {ind["ic"]: ind for ind in existing.get("industries", [])}

    for ic in targets:
        name = name_of.get(ic, ic)
        print(f"[fetch] {name} (ic={ic})")
        time.sleep(SLEEP)
        html_text = fetch(f"{BASE}/introduce.php?ic={ic}",
                          f"chain_{ic}.html" if dump else None)
        if not html_text:
            print(f"  [warn] 保留舊資料：{ic}")
            continue
        layers = parse_chain(html_text, name)
        if layers:
            merged[ic] = {"ic": ic, "name": name, "layers": layers}
        else:
            print(f"  [warn] 解析失敗，保留舊資料：{ic}")

    industries = sorted(merged.values(), key=lambda x: x["ic"])

    if not no_domains:
        cache = load_json(DOMAIN_CACHE, {})
        cache = fill_domains(industries, cache, MAX_DOMAIN_FETCH_PER_RUN)
        with open(DOMAIN_CACHE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=1, sort_keys=True)

    write_chains({
        "updated": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
        "industries": industries,
    })


if __name__ == "__main__":
    main()
