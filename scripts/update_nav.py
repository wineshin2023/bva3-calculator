"""Fetch 超鑫動 (EOA) NAV history from Nan Shan's public fund page and embed it in index.html."""
import datetime, json, re, sys, urllib.request

TZ = datetime.timezone(datetime.timedelta(hours=8))
now = datetime.datetime.now(TZ)
url = ("https://ilp.nanshanlife.com.tw/w/bcd/BCDTFundNavList.djbcd"
       f"?a=EOA&b=1&c=2026-8-1&d={now.year}-{now.month}-{now.day}")
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
raw = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
body = raw.split("<!--")[0].strip()
dates_s, vals_s = body.split(" ", 1)
dates, vals = dates_s.split(","), vals_s.strip().split(",")
if len(dates) != len(vals) or not dates:
    sys.exit(f"Unexpected response: {raw[:200]}")
navs = []
for d, v in zip(dates, vals):
    x = float(v)
    if not (re.fullmatch(r"\d{8}", d) and 1 < x < 50):
        sys.exit(f"Bad row: {d} {v}")
    navs.append([f"{d[:4]}-{d[4:6]}-{d[6:]}", round(x, 2)])
navs.sort()

html = open("index.html", encoding="utf-8").read()
pat = re.compile(r'(<script id="nav-data" type="application/json">\s*)(.*?)(\s*</script>)', re.S)
m = pat.search(html)
old = json.loads(m.group(2))
if len(navs) < len(old["navs"]):
    sys.exit("Fewer rows than before; refusing to overwrite")
if navs == [[d, round(v, 2)] for d, v in old["navs"]]:
    print("No new NAV"); sys.exit(0)
new = json.dumps({"updated": now.strftime("%Y-%m-%d %H:%M"), "navs": navs}, ensure_ascii=False, separators=(",", ":"))
open("index.html", "w", encoding="utf-8").write(html[:m.start(2)] + new + html[m.end(2):])
print(f"Updated: latest {navs[-1][0]} {navs[-1][1]:.2f}")
