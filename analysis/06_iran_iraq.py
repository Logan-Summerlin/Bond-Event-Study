"""Iran-Iraq War (1980-88): documented negative result.

Neither belligerent had traded sovereign debt during the war, so no
market-implied victory probability can be constructed. Sources:
Hinrichsen (2019), LSE Economic History WP 304, reconstructs Iraq's debt
build-up: from net creditor in 1979 to ~$86-130bn owed by 1990, almost
all in *untraded* form (Gulf-state deposits and loans, export credits,
military credits). Iran, after the 1979 revolution, largely repudiated
foreign borrowing on ideological grounds and financed the war from oil
revenue. The secondary market for LDC bank loans that emerged after 1982
carried no regular Iran/Iraq quotations during the war.
"""

import pandas as pd

from common import OUT

rows = [
    ("Iraq",
     "Net creditor in 1979; war financed by Gulf-state 'deposits'/loans "
     "(~$40bn, arguably grants), official export credits, and military "
     "credits from the USSR and France. None traded on an exchange. First "
     "defaults occurred in the late 1980s on trade credits; market "
     "quotations for Iraqi claims only appear after the 1990 Kuwait "
     "invasion, at cents on the dollar.",
     "Hinrichsen (2019) LSE WP 304"),
    ("Iran",
     "Post-revolution government repudiated most foreign borrowing; war "
     "financed from oil exports and money creation. No traded external "
     "debt 1980-88.",
     "Hinrichsen (2019); IMF Article IV histories"),
    ("Indirect instruments",
     "War-risk shipping insurance premia for Gulf tankers and the "
     "Kuwaiti/Gulf equity markets moved with the tanker war, and oil "
     "futures priced supply risk - but none maps to a *victory "
     "probability* for either side via the default-risk channel.",
     "tanker-war literature"),
]
df = pd.DataFrame(rows, columns=["issuer", "situation", "source"])
df.to_csv(OUT / "iran_iraq_data_availability.csv", index=False)
print(df.to_string())
print("\nConclusion: the mechanism requires marketable debt whose repayment "
      "hinges on the war's outcome; 1980s war finance ran through states "
      "and banks, not markets, so no such instrument exists for this war.")
