#!/usr/bin/env bash
# Download the raw data sources into data/raw. See data/raw/SOURCES.md.
set -euo pipefail
cd "$(dirname "$0")/../data/raw"

echo "== NBER Macrohistory chapter 13 yield series =="
for s in m13041b m13041c m13028a m13033a; do
  [ -f "nber_$s.dat" ] || curl -sfL \
    "https://data.nber.org/databases/macrohistory/rectdata/13/$s.dat" \
    -o "nber_$s.dat"
done

echo "== Frey & Waldenstrom WW2 bond prices (author-posted) =="
[ -f frey_waldenstrom_fhr2004.xls ] || curl -sL \
  "https://www.dropbox.com/s/evvn09s732tn6q5/Data_Frey_Waldenstrom_Market_Work_in_Wars_FHR_2004.xls?dl=1" \
  -o frey_waldenstrom_fhr2004.xls
[ -f frey_waldenstrom_hsr2008.xls ] || curl -sL \
  "https://www.dropbox.com/s/pas1ts497uhpadw/Data_Frey_Waldenstrom_Using_FM_to_Analyze_History_HSR_2008.xls?dl=1" \
  -o frey_waldenstrom_hsr2008.xls

echo "== Yale ICF Investor's Monthly Manual (large; not committed) =="
if [ ! -f Stocks_new.csv ]; then
  curl -sL "https://som.yale.edu/sites/default/files/2021-12/Stocks_new.csv.zip" \
    -o imm_stocks.csv.zip
  unzip -o imm_stocks.csv.zip
fi

echo "== Mitchell (1908) OCR excerpt (public domain, archive.org) =="
if [ ! -f mitchell1908_table2_excerpt.txt ]; then
  curl -sL "https://archive.org/download/goldpricesandwa00mitcgoog/goldpricesandwa00mitcgoog_djvu.txt" \
    -o mitchell1908_full.txt
  sed -n '400,2400p' mitchell1908_full.txt > mitchell1908_table2_excerpt.txt
  rm mitchell1908_full.txt
fi

echo "done."
