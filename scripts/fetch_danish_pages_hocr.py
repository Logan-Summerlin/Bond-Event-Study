"""Re-crop missed issues by locating the 'Danish' table row via hOCR bboxes."""
import gzip, io, json, os, re
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen, Request
from PIL import Image

S = 'data/raw/economist_scans'
OUT = f'{S}/danish_fix'
os.makedirs(OUT, exist_ok=True)
MARKERS = ['Uribarren', 'Equador', 'Ecuador', 'Moorish', 'Maremmana',
           'Land Warrant', 'Hectares', 'Danubian']

MISSED = """1862-09-27 1862-11-29 1863-02-28 1863-03-28 1863-04-25 1863-07-25
1863-08-29 1863-09-26 1863-10-31 1863-11-07 1863-11-14 1863-11-21 1863-11-28
1863-12-05 1863-12-12 1863-12-19 1863-12-26 1864-07-02 1864-07-09 1864-07-23
1864-08-06 1864-08-27 1864-09-17 1864-09-24 1864-10-15 1864-10-22 1864-12-31
1865-04-29 1865-06-24 1865-07-29 1865-09-30 1865-10-28""".split()

ids = {l.split('_')[2]: l.strip() for l in open(f'{S}/econ_ids.txt') if l.strip()}

def fetch(url, timeout=180):
    return urlopen(Request(url, headers={'User-Agent': 'curl/8'}),
                   timeout=timeout).read()

def locate_leaf(iid):
    pi = json.loads(gzip.decompress(fetch(
        f'https://archive.org/download/{iid}/{iid}_hocr_pageindex.json.gz')))
    st = gzip.decompress(fetch(
        f'https://archive.org/download/{iid}/{iid}_hocr_searchtext.txt.gz')
        ).decode('utf-8', 'ignore')
    votes = {}
    for pat in MARKERS:
        for m in re.finditer(pat, st, re.I):
            for i, span in enumerate(pi):
                if span[0] <= m.start() < span[1]:
                    votes[i] = votes.get(i, 0) + 1
    return max(votes, key=votes.get) if votes else None

def word_re(leaf):
    return re.compile(
        r'<span class="ocrx_word" id="word_0*%d_\d+" '
        r'title="bbox (\d+) (\d+) (\d+) (\d+)[^"]*"[^>]*>([^<]*)</span>' % leaf)

def process(d):
    iid = ids[d]
    try:
        leaf = locate_leaf(iid)
        if leaf is None:
            return f'{d} NOLEAF'
        hocr = fetch(f'https://archive.org/download/{iid}/{iid}_hocr.html'
                     ).decode('utf-8', 'ignore')
        cands = [(int(m.group(1)), int(m.group(2)))
                 for m in word_re(leaf).finditer(hocr)
                 if re.match(r'^Dani[s3]h[,.]?$', m.group(5).strip())]
        if not cands:
            return f'{d} NODANISH leaf={leaf}'
        jp2 = fetch(f'https://archive.org/download/{iid}/{iid}_jp2.zip/'
                    f'{iid}_jp2%2F{iid}_{leaf:04d}.jp2')
        im = Image.open(io.BytesIO(jp2))
        W, H = im.size
        for k, (x, y) in enumerate(cands[:3]):
            box = (max(0, x - 70), max(0, y - 100),
                   min(W, x + 1500), min(H, y + 420))
            im.crop(box).save(f'{OUT}/{d}_{k}.png')
        return f'{d} leaf={leaf} n={len(cands)}'
    except Exception as e:
        return f'{d} ERROR {type(e).__name__}: {e}'

with ThreadPoolExecutor(max_workers=5) as ex:
    for r in ex.map(process, MISSED):
        print(r, flush=True)
print('DONE')
