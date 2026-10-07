"""Quotation ledger check (re-audit ST-26): research/quotations.csv lists every quotation from an external source that
the manuscript, the research notes or the code reuse, with the exact text as printed, the original wording, the source,
access date, how it was retrieved, a SHA-256 of the original wording and any correction applied in release 2.1.

Checks: (1) each printed text occurs in every file named in its used_in column (files that are not in this copy of the
package, such as the unreleased manuscript, are skipped and listed); (2) the stored hash matches the original wording.
The ledger cannot prove that a source said what it records: pages were read with a tool that passes page text through
a summarising model and no raw snapshots are archived, so 'V-tool' rows should be spot-checked against the source
before they are quoted in print ('P' rows were supplied by the study's author; 'R' rows are review statements).
Exit status 0 if every check on the available files passes."""
import sys, os, re, csv, hashlib
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
norm = lambda x: re.sub(r'\s+', ' ', x)                        # line wrapping is not a difference
rows = list(csv.DictReader(open(os.path.join(root, 'research', 'quotations.csv'), encoding='utf-8')))
bad, skipped, ok = [], set(), 0
for r in rows:
    if hashlib.sha256(r['original_text'].encode('utf-8')).hexdigest() != r['original_sha256']:
        bad.append(f"{r['id']}: stored hash does not match the original wording")
    for f in (x.strip() for x in r['used_in'].split(';') if x.strip()):
        p = os.path.join(root, f)
        if not os.path.exists(p):
            skipped.add(f); continue
        if norm(r['printed_text']) in norm(open(p, encoding='utf-8', errors='ignore').read()):
            ok += 1
        else:
            bad.append(f"{r['id']}: '{r['printed_text'][:60]}' not found in {f}")
print(f'{len(rows)} ledger rows; {ok} file occurrences confirmed')
if skipped:
    print('skipped (not in this copy):', ', '.join(sorted(skipped)))
for b in bad:
    print('MISMATCH', b)
print('quotation ledger: ' + ('OK' if not bad else f'{len(bad)} problem(s)'))
sys.exit(1 if bad else 0)
