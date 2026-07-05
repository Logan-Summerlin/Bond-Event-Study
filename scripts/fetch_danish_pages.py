"""Fetch the Bankers' Price Current page image for selected Economist issues.

Source for data/manual/danish_london_1862_1865.csv (see
data/manual/PROVENANCE.md). For each issue of The Economist 1862-65 on
archive.org (Serials in Microfilm scans): download the hOCR pageindex +
searchtext (small), locate the leaf containing the PRICES OF FOREIGN
STOCKS table via distinctive row labels, download that leaf's jp2, and
save a cropped strip covering the foreign-stocks table. The Danish quotes
were then read off the strips by eye; strips whose fixed crop window
missed the table were re-cropped with fetch_danish_pages_hocr.py, which
locates the 'Danish' row label's pixel coordinates in the full hOCR.
"""
import gzip, io, json, os, re
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen, Request

S = 'data/raw/economist_scans'
OUT = f'{S}/danish_strips'
os.makedirs(OUT, exist_ok=True)

from PIL import Image

MARKERS = ['Uribarren', 'Equador', 'Ecuador', 'Moorish', 'Maremmana',
           'Land Warrant', 'Hectares', 'Maremmani']


def fetch(url, timeout=120):
    req = Request(url, headers={'User-Agent': 'curl/8'})
    return urlopen(req, timeout=timeout).read()


IDS_FILE = f'{S}/econ_ids.txt'
if not os.path.exists(IDS_FILE):
    q = ('https://archive.org/advancedsearch.php?q=identifier%3A%28sim_'
         'economist_186*%29+AND+date%3A%5B1862-06-01+TO+1866-12-31%5D'
         '&fl%5B%5D=identifier&rows=300&output=json')
    docs = json.loads(fetch(q))['response']['docs']
    with open(IDS_FILE, 'w') as fh:
        fh.write('\n'.join(sorted(
            x['identifier'] for x in docs
            if x['identifier'] < 'sim_economist_1866')))

ids = [l.strip() for l in open(IDS_FILE) if l.strip()]
ids = [i for i in ids if 'supplement' not in i]

def date_of(iid):
    return iid.split('_')[2]

# issue selection: weekly Nov 1863 - Nov 1864, else last issue of each month
sel = []
by_month = {}
for iid in ids:
    d = date_of(iid)
    if '1863-11-01' <= d <= '1864-11-30':
        sel.append(iid)
    else:
        by_month.setdefault(d[:7], []).append(iid)
for m, lst in sorted(by_month.items()):
    sel.append(sorted(lst)[-1])
sel = sorted(set(sel), key=date_of)
print(len(sel), 'issues selected', flush=True)

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
    if not votes:
        return None
    return max(votes, key=votes.get)

def process(iid):
    d = date_of(iid)
    out = f'{OUT}/{d}.png'
    if os.path.exists(out):
        return f'{d} cached'
    try:
        leaf = locate_leaf(iid)
        if leaf is None:
            return f'{d} NOLEAF'
        n = f'{leaf:04d}'
        jp2 = fetch(f'https://archive.org/download/{iid}/{iid}_jp2.zip/'
                    f'{iid}_jp2%2F{iid}_{n}.jp2')
        im = Image.open(io.BytesIO(jp2))
        W, H = im.size
        crop = im.crop((int(0.04*W), int(0.36*H), int(0.58*W), int(0.60*H)))
        crop.save(out)
        return f'{d} leaf={leaf} {crop.size}'
    except Exception as e:
        return f'{d} ERROR {type(e).__name__}: {e}'

with ThreadPoolExecutor(max_workers=6) as ex:
    for res in ex.map(process, sel):
        print(res, flush=True)
print('DONE', flush=True)
