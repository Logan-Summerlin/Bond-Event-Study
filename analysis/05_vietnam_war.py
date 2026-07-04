"""Vietnam War: documented negative result.

Neither belligerent had sovereign bonds trading on a deep, neutral
exchange during 1955-75, so the bond-implied-probability mechanism that
works for the other wars has no instrument here. This script documents
the reasoning as a machine-readable table (output/vietnam_data_availability.csv)
so the negative result is part of the reproducible pipeline.
"""

import pandas as pd

from common import OUT, load_events

rows = [
    ("South Vietnam (RVN)",
     "No external bond market. The RVN was financed by US grant aid and "
     "concessional loans (USAID/PL-480), not by marketable debt; its "
     "domestic piastre bonds had no neutral-market quotation.",
     "US aid substituted for the capital market; solvency was a function "
     "of US politics, not battlefield news."),
    ("North Vietnam (DRV)",
     "Centrally planned economy financed by Soviet and Chinese aid; no "
     "internationally traded debt.",
     "No instrument."),
    ("France (colonial predecessor)",
     "Indochinese colonial bonds traded in Paris priced the First "
     "Indochina War (to 1954), guaranteed by metropolitan France - they "
     "priced French fiscal policy, not Vietnamese war outcomes.",
     "Closest historical instrument, but for the 1946-54 war and with a "
     "French guarantee blunting outcome sensitivity."),
    ("United States",
     "US Treasuries traded deeply throughout, but US *solvency* was never "
     "at stake in Vietnam; yields moved on inflation and Fed policy.",
     "War news shows up in gold/inflation expectations, not default risk - "
     "the mechanism requires the *issuer's survival* to be in question."),
]
df = pd.DataFrame(rows, columns=["issuer", "market_situation", "implication"])
df.to_csv(OUT / "vietnam_data_availability.csv", index=False)
print(df.to_string())
print("\nEvent chronology retained at data/events/vietnam_war.csv for any "
      "future instrument (e.g. hand-collected piastre black-market rates).")
