/*───────────────────────────────────────────────────────────────────────────
  EXPLAIN.gs  —  Google Sheets client scaffold for the Ogden8 =EXPLAIN() UDF
  ---------------------------------------------------------------------------
  CLIENT-SIDE, **UNTESTED**.  This file runs in the Google Sheet's Apps Script
  project, not in the Python package. It is the analogue of the VBA
  ModuleEXPLAIN_DISPATCHER (DispatchCoreExplainFromSourceCell / ParseFunctionCall):
  it reads the FORMULA of a referenced cell, extracts the Ogden function name and
  its argument cell-references, resolves those refs to values, POSTs them to the
  Python Cloud Function's /Explain/ endpoint (which returns {result, explanation}),
  and renders a human-readable audit trail (header + optional per-age table).

  It could not be run/verified here (no Sheet available). Wiring marked TODO must
  be completed against the actual workbook layout before use. Scope mirrors the
  Python engine: single-life MULTIPLIER only (JMULTIPLIER / AGGINT are future work).
───────────────────────────────────────────────────────────────────────────*/

// TODO: point this at your deployed Cloud Function base (see the other endpoints,
// e.g. https://europe-west2-<project>.cloudfunctions.net/<fn>). Must expose /Explain/.
var OGDEN_ENDPOINT_BASE = 'https://europe-west2-ogden8.cloudfunctions.net/ogden';

/**
 * =EXPLAIN(cellRef, [showTable])
 *
 * Custom function. Point it at a cell that CONTAINS a MULTIPLIER formula, e.g.
 *   A5 =  =MULTIPLIER(Claimants!B2, 40, 125, "Y", "AMI")
 *   B5 =  =EXPLAIN("A5", TRUE)
 *
 * @param {string} cellRef   A1-style reference (as text) of the cell whose formula to explain.
 * @param {boolean} showTable When TRUE, spill the full per-age breakdown table below the header.
 * @return {string|Array} Header text, or a 2-D array (header + table) that spills into the grid.
 * @customfunction
 */
function EXPLAIN(cellRef, showTable) {
  try {
    if (!cellRef) return 'EXPLAIN: supply the A1 reference (as text) of a MULTIPLIER cell.';
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var srcCell = sheet.getRange(cellRef);
    var formula = srcCell.getFormula(); // e.g. '=MULTIPLIER(Claimants!B2, 40, 125, "Y", "AMI")'
    if (!formula) return 'EXPLAIN: cell ' + cellRef + ' has no formula.';

    var parsed = parseFunctionCall_(formula);        // {funcName, args:[...]}
    if (!parsed) return 'EXPLAIN: cannot parse formula in ' + cellRef + '.';
    if (parsed.funcName.toUpperCase() !== 'MULTIPLIER') {
      return 'EXPLAIN: only MULTIPLIER is supported so far (got ' + parsed.funcName + ').';
    }

    // Resolve each argument: a cell-ref argument -> its value; a literal -> itself.
    var args = parsed.args.map(function (a) { return resolveArg_(sheet, a); });
    // MULTIPLIER(name, from, to, freq, discounts, [discountRate])
    var row = {
      name:            args[0],
      fromAge:         args.length > 1 ? args[1] : 'TRIAL',
      toAge:           args.length > 2 ? args[2] : 'LIFE',
      freq:            args.length > 3 ? args[3] : 'Y',
      options:         args.length > 4 ? args[4] : 'AMI',
      discountRate:    args.length > 5 ? args[5] : null,
      DRMethodOverride: null,
      overrides:       null
    };

    // TODO: build the 'game' block (trialDate, discountRate, claimants[...] with sex/dob/dataSet)
    // from the workbook. The Python engine needs the claimant's full context, not just the name.
    // A real implementation would look these up from a claimants config sheet/range keyed by name.
    var attributes = {
      function: 'MULTIPLIER',
      explain: true,
      explainTable: showTable === true,
      rows: [row],
      game: buildGameContext_(row.name) // TODO: implement against your workbook layout
    };

    var resp = UrlFetchApp.fetch(OGDEN_ENDPOINT_BASE + '/Explain/', {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify(attributes),
      muteHttpExceptions: true
    });
    var body = JSON.parse(resp.getContentText());
    if (body && body.error) return 'EXPLAIN error: ' + body.error;

    var cell = body[0];                // { result:[...], explanation:{...} }
    var ex = cell.explanation;
    var headerLines = formatHeader_(cell.result, ex);

    if (showTable === true && ex.table && ex.table.rows) {
      return headerAndTableGrid_(headerLines, ex.table);
    }
    return headerLines.join('\n');
  } catch (e) {
    return 'EXPLAIN exception: ' + e;
  }
}

/* ── ParseFunctionCall analogue: '=FUNC(arg1, arg2, ...)' -> {funcName, args[]} ── */
function parseFunctionCall_(formula) {
  var f = String(formula).trim();
  if (f.charAt(0) === '=') f = f.substring(1);
  f = f.replace(/@/g, '').trim();           // strip structured-ref implicit intersection
  var open = f.indexOf('(');
  if (open < 0 || f.charAt(f.length - 1) !== ')') return null;
  var funcName = f.substring(0, open).trim();
  var inner = f.substring(open + 1, f.length - 1);
  return { funcName: funcName, args: splitArgs_(inner) };
}

/* Split a top-level comma-separated arg list, respecting quotes and nested parens. */
function splitArgs_(s) {
  var args = [], depth = 0, inQ = false, cur = '';
  for (var i = 0; i < s.length; i++) {
    var c = s.charAt(i);
    if (c === '"') { inQ = !inQ; cur += c; }
    else if (!inQ && c === '(') { depth++; cur += c; }
    else if (!inQ && c === ')') { depth--; cur += c; }
    else if (!inQ && c === ',' && depth === 0) { args.push(cur.trim()); cur = ''; }
    else cur += c;
  }
  if (cur.trim().length) args.push(cur.trim());
  return args;
}

/* Resolve one argument token to a value: quoted literal, number, or a cell reference. */
function resolveArg_(sheet, tok) {
  if (tok === '' || tok == null) return null;
  if (tok.charAt(0) === '"' && tok.charAt(tok.length - 1) === '"') return tok.slice(1, -1);
  if (!isNaN(Number(tok))) return Number(tok);
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    return (tok.indexOf('!') >= 0 ? ss.getRange(tok) : sheet.getRange(tok)).getValue();
  } catch (e) {
    return tok; // treat as a literal string point (e.g. TRIAL, LIFE, TRIAL+3Y)
  }
}

/* TODO: return the game/claimants context for the named claimant from the workbook. */
function buildGameContext_(claimantName) {
  // Placeholder. A real implementation reads trial date, discount rate and the claimant's
  // sex/dob(or age)/dataSet from a config sheet keyed by claimantName. Returning this stub
  // will make the endpoint report a missing-claimant error until wired up.
  return {
    trialDate: null,      // TODO 'dd/mm/yyyy'
    discountRate: -0.0025, // TODO from the sheet
    useTablesEF: false,
    projection: true,
    autoYrAttained: false,
    claimants: []         // TODO [{name, sex, dob|age, dataSet:{year,region,yrAttainedIn}, cont}]
  };
}

/* Render the header of the explanation as text lines. */
function formatHeader_(result, ex) {
  var h = ex.header, lines = [];
  lines.push('MULTIPLIER for ' + h.claimant + ' (' + h.sex + '), age ' + h.ageAtTrial + ' at trial'
    + (h.revisedAge ? ' (revised age ' + h.revisedAge + ')' : ''));
  lines.push('From ' + h.fromAge + ' (' + h.fromDate + ') to ' + h.toAge + ' (' + h.toDate + '), '
    + h.frequencyText);
  lines.push('Basis: ' + h.optionsText + '; discount rate ' + (h.discountRate * 100).toFixed(2)
    + '% (' + h.discountMethod + ')');
  lines.push('Mortality: ONS ' + h.mortalityBasis.region + ' ' + h.mortalityBasis.year
    + (h.mortalityBasis.projection ? ' projected' : '') + ', year attained ' + h.mortalityBasis.yrAttainedIn);
  var d = ex.decomposition;
  lines.push('Past ' + fmt_(d.past.value) + ' + Interest ' + fmt_(d.interest.value)
    + ' + Future ' + fmt_(d.future.value) + ' = ' + fmt_(d.total.value));
  lines.push('(interest = ' + d.interest.formula + ')');
  return lines;
}

/* Build a 2-D grid: header lines, blank row, table header, then table rows (spills into the sheet). */
function headerAndTableGrid_(headerLines, table) {
  var grid = headerLines.map(function (l) { return [l]; });
  grid.push(['']);
  grid.push(table.columns);
  table.rows.forEach(function (r) {
    grid.push(table.columns.map(function (c) { return r[c]; }));
  });
  // Pad every row to the widest for a clean rectangular spill.
  var w = grid.reduce(function (m, r) { return Math.max(m, r.length); }, 0);
  return grid.map(function (r) { while (r.length < w) r.push(''); return r; });
}

function fmt_(x) { return (x == null) ? '' : Number(x).toFixed(2); }
