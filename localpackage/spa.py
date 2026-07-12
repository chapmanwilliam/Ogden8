"""
State Pension Age calculator.

Faithful Python port of the VBA `ModuleSPA.bas` (Ogden Tables VBA project), implementing the
UK State Pension age rules per:
  - Pensions Act 1995  (women's equalisation 60 -> 65)
  - Pensions Act 2011  (accelerated equalisation)
  - Pensions Act 2014 s.26 (increase to 66, 67, 68)

Source of truth: gov.uk State Pension age timetable (VBA last verified Feb 2026).
This module is a pure, offline computation — it replaces the previous live gov.uk HTTP lookup,
so process()/getStateRetirementAge no longer has any network dependency.

`StatePensionAge(dob, sex)` returns the SPA in years as a float (whole for most people:
60/65/66/67/68; fractional during transitional periods, e.g. 66.25 = 66yr 3mo), or -1 for
invalid input — matching the VBA return contract exactly.
"""

import calendar
from datetime import datetime


# --- VBA date-primitive equivalents (preserve VBA semantics exactly) ---

def _dateserial(year, month, day):
    # VBA DateSerial allows month overflow (e.g. month 15 -> +1 year, month 3). Replicate it.
    m = month - 1
    y = year + m // 12
    mo = m % 12 + 1
    day = min(day, calendar.monthrange(y, mo)[1])
    return datetime(y, mo, day)


def _add_months(d, n):
    # VBA DateAdd("m", n, d): shift by n whole months, keeping the day (clamped to month length).
    m = d.month - 1 + n
    y = d.year + m // 12
    mo = m % 12 + 1
    day = min(d.day, calendar.monthrange(y, mo)[1])
    return datetime(y, mo, day)


def _months_between(start, end):
    # VBA DateDiff("m", start, end): count of month boundaries crossed (day-of-month ignored).
    return (end.year - start.year) * 12 + (end.month - start.month)


def _datediff_years(startDate, endDate):
    # VBA DateDiffYears: whole completed months / 12 (a Double).
    totalMonths = _months_between(startDate, endDate)
    if _add_months(startDate, totalMonths) > endDate:  # final month not yet reached
        totalMonths = totalMonths - 1
    return totalMonths / 12


# --- Public API ---

def StatePensionAge(dob, sSex):
    """State Pension age in years (float). Returns -1 for invalid input (as the VBA does)."""
    if not isinstance(dob, datetime):
        return -1
    sSex = str(sSex)[:1].upper() if sSex else ''
    if sSex != 'M' and sSex != 'F':
        return -1

    # Men born before 6 Dec 1953: SPA = 65
    if sSex == 'M' and dob < _dateserial(1953, 12, 6):
        return 65

    # Women born before 6 Apr 1950: SPA = 60
    if sSex == 'F' and dob < _dateserial(1950, 4, 6):
        return 60

    # Table 1: Women born 6 Apr 1950 - 5 Apr 1953 (Pensions Act 1995)
    if sSex == 'F' and dob >= _dateserial(1950, 4, 6) and dob < _dateserial(1953, 4, 6):
        return _spa_women_table1(dob)

    # Table 2: Women born 6 Apr 1953 - 5 Dec 1953 (Pensions Act 2011)
    if sSex == 'F' and dob >= _dateserial(1953, 4, 6) and dob < _dateserial(1953, 12, 6):
        return _spa_women_table2(dob)

    # From here on the rules are the same for men and women.

    # Table 3: Born 6 Dec 1953 - 5 Oct 1954 (increase 65 -> 66)
    if dob >= _dateserial(1953, 12, 6) and dob < _dateserial(1954, 10, 6):
        return _spa_table3(dob)

    # Born 6 Oct 1954 - 5 Apr 1960: SPA = 66
    if dob >= _dateserial(1954, 10, 6) and dob < _dateserial(1960, 4, 6):
        return 66

    # Table 4: Born 6 Apr 1960 - 5 Mar 1961 (increase 66 -> 67)
    if dob >= _dateserial(1960, 4, 6) and dob < _dateserial(1961, 3, 6):
        return _spa_table4(dob)

    # Born 6 Mar 1961 - 5 Apr 1977: SPA = 67
    if dob >= _dateserial(1961, 3, 6) and dob < _dateserial(1977, 4, 6):
        return 67

    # Table 5: Born 6 Apr 1977 - 5 Apr 1978 (increase 67 -> 68)
    if dob >= _dateserial(1977, 4, 6) and dob < _dateserial(1978, 4, 6):
        return _spa_table5(dob)

    # Born 6 Apr 1978 onwards: SPA = 68
    if dob >= _dateserial(1978, 4, 6):
        return 68

    return -1  # shouldn't reach here


def StatePensionDate(dob, sSex):
    """The actual date the person reaches SPA. Returns None for invalid input (VBA returns 0)."""
    sSex = str(sSex)[:1].upper() if sSex else ''
    spa = StatePensionAge(dob, sSex)
    if spa is None or spa < 0:
        return None
    wholeYears = int(spa)
    fracMonths = int(round((spa - wholeYears) * 12))
    return _dateserial(dob.year + wholeYears, dob.month + fracMonths, dob.day)


# --- Private transitional-band tables (ported verbatim from the VBA) ---

def _spa_women_table1(dob):
    # Women's equalisation 60 -> 65 (Pensions Act 1995 as amended by 2011 Act): 36 monthly bands.
    bands = [
        (_dateserial(1950, 5, 6),  _dateserial(2010, 5, 6)),
        (_dateserial(1950, 6, 6),  _dateserial(2010, 7, 6)),
        (_dateserial(1950, 7, 6),  _dateserial(2010, 9, 6)),
        (_dateserial(1950, 8, 6),  _dateserial(2010, 11, 6)),
        (_dateserial(1950, 9, 6),  _dateserial(2011, 1, 6)),
        (_dateserial(1950, 10, 6), _dateserial(2011, 3, 6)),
        (_dateserial(1950, 11, 6), _dateserial(2011, 5, 6)),
        (_dateserial(1950, 12, 6), _dateserial(2011, 7, 6)),
        (_dateserial(1951, 1, 6),  _dateserial(2011, 9, 6)),
        (_dateserial(1951, 2, 6),  _dateserial(2011, 11, 6)),
        (_dateserial(1951, 3, 6),  _dateserial(2012, 1, 6)),
        (_dateserial(1951, 4, 6),  _dateserial(2012, 3, 6)),
        (_dateserial(1951, 5, 6),  _dateserial(2012, 5, 6)),
        (_dateserial(1951, 6, 6),  _dateserial(2012, 7, 6)),
        (_dateserial(1951, 7, 6),  _dateserial(2012, 9, 6)),
        (_dateserial(1951, 8, 6),  _dateserial(2012, 11, 6)),
        (_dateserial(1951, 9, 6),  _dateserial(2013, 1, 6)),
        (_dateserial(1951, 10, 6), _dateserial(2013, 3, 6)),
        (_dateserial(1951, 11, 6), _dateserial(2013, 5, 6)),
        (_dateserial(1951, 12, 6), _dateserial(2013, 7, 6)),
        (_dateserial(1952, 1, 6),  _dateserial(2013, 9, 6)),
        (_dateserial(1952, 2, 6),  _dateserial(2013, 11, 6)),
        (_dateserial(1952, 3, 6),  _dateserial(2014, 1, 6)),
        (_dateserial(1952, 4, 6),  _dateserial(2014, 3, 6)),
        (_dateserial(1952, 5, 6),  _dateserial(2014, 5, 6)),
        (_dateserial(1952, 6, 6),  _dateserial(2014, 7, 6)),
        (_dateserial(1952, 7, 6),  _dateserial(2014, 9, 6)),
        (_dateserial(1952, 8, 6),  _dateserial(2014, 11, 6)),
        (_dateserial(1952, 9, 6),  _dateserial(2015, 1, 6)),
        (_dateserial(1952, 10, 6), _dateserial(2015, 3, 6)),
        (_dateserial(1952, 11, 6), _dateserial(2015, 5, 6)),
        (_dateserial(1952, 12, 6), _dateserial(2015, 7, 6)),
        (_dateserial(1953, 1, 6),  _dateserial(2015, 9, 6)),
        (_dateserial(1953, 2, 6),  _dateserial(2015, 11, 6)),
        (_dateserial(1953, 3, 6),  _dateserial(2016, 1, 6)),
        (_dateserial(1953, 4, 6),  _dateserial(2016, 3, 6)),
    ]
    for upper, pensionDate in bands:
        if dob < upper:
            return _datediff_years(dob, pensionDate)
    return -1


def _spa_women_table2(dob):
    # Women born 6 Apr 1953 - 5 Dec 1953 (Pensions Act 2011): 8 bands jumping by 4 months.
    bands = [
        (_dateserial(1953, 5, 6),  _dateserial(2016, 7, 6)),
        (_dateserial(1953, 6, 6),  _dateserial(2016, 11, 6)),
        (_dateserial(1953, 7, 6),  _dateserial(2017, 3, 6)),
        (_dateserial(1953, 8, 6),  _dateserial(2017, 7, 6)),
        (_dateserial(1953, 9, 6),  _dateserial(2017, 11, 6)),
        (_dateserial(1953, 10, 6), _dateserial(2018, 3, 6)),
        (_dateserial(1953, 11, 6), _dateserial(2018, 7, 6)),
        (_dateserial(1953, 12, 6), _dateserial(2018, 11, 6)),
    ]
    for upper, pensionDate in bands:
        if dob < upper:
            return _datediff_years(dob, pensionDate)
    return -1


def _spa_table3(dob):
    # Everyone born 6 Dec 1953 - 5 Oct 1954 (increase 65 -> 66): 10 monthly bands.
    bands = [
        (_dateserial(1954, 1, 6),  _dateserial(2019, 3, 6)),
        (_dateserial(1954, 2, 6),  _dateserial(2019, 5, 6)),
        (_dateserial(1954, 3, 6),  _dateserial(2019, 7, 6)),
        (_dateserial(1954, 4, 6),  _dateserial(2019, 9, 6)),
        (_dateserial(1954, 5, 6),  _dateserial(2019, 11, 6)),
        (_dateserial(1954, 6, 6),  _dateserial(2020, 1, 6)),
        (_dateserial(1954, 7, 6),  _dateserial(2020, 3, 6)),
        (_dateserial(1954, 8, 6),  _dateserial(2020, 5, 6)),
        (_dateserial(1954, 9, 6),  _dateserial(2020, 7, 6)),
        (_dateserial(1954, 10, 6), _dateserial(2020, 9, 6)),
    ]
    for upper, pensionDate in bands:
        if dob < upper:
            return _datediff_years(dob, pensionDate)
    return -1


def _spa_table4(dob):
    # Everyone born 6 Apr 1960 - 5 Mar 1961 (increase 66 -> 67): SPA = 66 years + N months,
    # where band N covers DOBs [6 (3+N) 1960 .. 6 (4+N) 1960).
    months = 0
    for i in range(1, 12):
        bandEnd = _dateserial(1960, 4 + i, 6)
        if dob < bandEnd:
            months = i
            break
    return 66 + months / 12


def _spa_table5(dob):
    # Everyone born 6 Apr 1977 - 5 Apr 1978 (increase 67 -> 68): monthly bands.
    bands = [
        (_dateserial(1977, 5, 6),  _dateserial(2044, 5, 6)),
        (_dateserial(1977, 6, 6),  _dateserial(2044, 7, 6)),
        (_dateserial(1977, 7, 6),  _dateserial(2044, 9, 6)),
        (_dateserial(1977, 8, 6),  _dateserial(2044, 11, 6)),
        (_dateserial(1977, 9, 6),  _dateserial(2045, 1, 6)),
        (_dateserial(1977, 10, 6), _dateserial(2045, 3, 6)),
        (_dateserial(1977, 11, 6), _dateserial(2045, 5, 6)),
        (_dateserial(1977, 12, 6), _dateserial(2045, 7, 6)),
        (_dateserial(1978, 1, 6),  _dateserial(2045, 9, 6)),
        (_dateserial(1978, 2, 6),  _dateserial(2045, 11, 6)),
        (_dateserial(1978, 3, 6),  _dateserial(2046, 1, 6)),
        (_dateserial(1978, 4, 6),  _dateserial(2046, 3, 6)),
    ]
    for upper, pensionDate in bands:
        if dob < upper:
            return _datediff_years(dob, pensionDate)
    return -1
