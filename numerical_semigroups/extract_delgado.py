"""
Extract readable text from the pdf2tex dump 'Delgado survey.tex'.

The file contains thousands of \put(x, y){...\selectfont\color{...}TEXT}
commands. We pull every (x, y, text) tuple, group by y (line), sort by x,
join with smart spacing, and emit a flat .txt that is grep-friendly.

Output: numerical_semigroups/Delgado_survey_extracted.txt
"""

import re
from collections import defaultdict

INPUT = 'numerical_semigroups/Delgado survey.tex'
OUTPUT = 'numerical_semigroups/Delgado_survey_extracted.txt'

# \put(X, Y){\fontsize{a}{b}\usefont{c}{d}{e}{f}\selectfont\color{g}TEXT}
# We just need (X, Y) and the TEXT after \selectfont\color{...}.
PUT_HEAD_RE = re.compile(r'\\put\(\s*(-?[\d.]+)(?:pt)?\s*,\s*(-?[\d.]+)(?:pt)?\s*\)')
SELECTFONT_RE = re.compile(r'\\selectfont\\color\{[^}]*\}(.*?)\}\s*$')

def clean_text(t):
    # The dump escapes some chars; rebuild minimal substitutions
    t = t.replace('\\textendash', '-')
    t = t.replace('\\textemdash', '-')
    t = t.replace('\\textperiodcentered', '.')
    t = t.replace('\\textquoteleft', "'")
    t = t.replace('\\textquoteright', "'")
    t = t.replace('\\textquotedblleft', '"')
    t = t.replace('\\textquotedblright', '"')
    t = t.replace('\\textbar', '|')
    t = t.replace('\\textless', '<')
    t = t.replace('\\textgreater', '>')
    t = t.replace('\\colon', ':')
    t = t.replace('$\\rightarrow$', '->')
    t = t.replace('$\\times$', 'x')
    t = t.replace('$\\cap$', '∩')
    t = t.replace('$\\cup$', '∪')
    t = t.replace('$\\leq$', '<=')
    t = t.replace('$\\geq$', '>=')
    t = t.replace('$\\prec$', '<')
    t = t.replace('$\\rho$', 'rho')
    t = t.replace('$\\varphi$', 'phi')
    t = t.replace('$\\chi$', 'chi')
    t = t.replace('$\\gamma$', 'gamma')
    t = t.replace('$\\in$', 'in')
    t = t.replace('$\\subseteq$', 'sub')
    t = t.replace('$\\infty$', 'inf')
    return t


def main():
    # Parse by picture block. Each block has its own (y, x) coordinate frame.
    blocks = []  # list of [(y, x, text), ...]
    cur = None
    with open(INPUT, 'r', errors='replace') as f:
        for raw in f:
            line = raw.rstrip('\n')
            if line.startswith('\\begin{picture}'):
                cur = []
                continue
            if line.startswith('\\end{picture}'):
                if cur is not None:
                    blocks.append(cur)
                cur = None
                continue
            if cur is None:
                continue
            head = PUT_HEAD_RE.match(line)
            if not head:
                continue
            x = float(head.group(1))
            y = float(head.group(2))
            tail = SELECTFONT_RE.search(line)
            if not tail:
                continue
            text = clean_text(tail.group(1))
            cur.append((y, x, text))

    items = []
    for blk_idx, blk in enumerate(blocks):
        # Sort within block: y descending (top to bottom in PDF coords),
        # x ascending. Tag with blk_idx so we never cross blocks.
        blk.sort(key=lambda t: (-t[0], t[1]))
        for (y, x, text) in blk:
            items.append((blk_idx, y, x, text))

    print(f"extracted {len(items)} text fragments in {len(blocks)} blocks")

    # Group fragments at the same y (within tolerance) into one logical line
    out_lines = []
    cur_blk = None
    cur_y = None
    cur_pieces = []

    def flush():
        nonlocal cur_pieces
        if cur_pieces:
            line = ' '.join(p for p in cur_pieces if p)
            out_lines.append(line.strip())
            cur_pieces = []

    for (blk_idx, y, x, text) in items:
        if blk_idx != cur_blk:
            flush()
            out_lines.append(f"=== BLOCK {blk_idx} ===")
            cur_blk = blk_idx
            cur_y = y
            cur_pieces = [text]
            continue
        # Same line if y within 1.0 pt
        if cur_y is not None and abs(cur_y - y) < 1.0:
            cur_pieces.append(text)
        else:
            flush()
            cur_y = y
            cur_pieces = [text]
    flush()

    with open(OUTPUT, 'w') as f:
        for line in out_lines:
            f.write(line.rstrip() + '\n')

    print(f"wrote {len(out_lines)} logical lines to {OUTPUT}")


if __name__ == '__main__':
    main()
