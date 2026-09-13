[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/chapmanwilliam/Ogden8/master?urlpath=voila%2Frender%2FOgden.ipynb)
.. image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/chapmanwilliam/Ogden8/master?urlpath=voila%2Frender%2FOgden.ipynb
## Special Account Rate

`localpackage/Data/SAR.csv` is the canonical Court Funds Office Special Account
Rate table for every Ogden product. The web page's `data/ogden/SAR.csv` is a
verbatim copy and the Excel add-in's `sar-rates.json` is generated from it.
It is kept current by [sar-watch](https://github.com/chapmanwilliam/sar-watch),
a daily job that appends each announced change to all three repos and
redeploys this function. Edit it by hand only to correct history, and then
update the copies too.

`GET https://europe-west2-ogden8.cloudfunctions.net/ogden-2/sar` returns the
table as JSON (`rates: [{date, ratePct}]`, plus `last`). The web page and the
Excel add-in read it from there at runtime, keeping their bundled copies only
as an offline fallback, and sar-watch checks it after every deploy.
