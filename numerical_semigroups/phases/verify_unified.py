"""
Compare a kunz_fast.py JSON output (single (m, K_max) run) against the
unified Wilf bound predicted by the conjecture in section 6 of the preprint:

    W_min(m, d) = (m - d) * L(d) - 2*m
    L(d)        = ceil((sqrt(8*d+1) - 1) / 2) + 2

For each defect d found in the run:
    - print observed W_min, predicted W_min, slack, status (sharp/slack/below)
    - flag any "below" (W_obs < W_pred) — would be a falsification

Usage:
    python phases/kunz_fast.py 22 3 --backend c > /tmp/m22k3.json
    python phases/verify_unified.py /tmp/m22k3.json
"""

import json
import math
import sys


def L_of_d(d: int) -> int:
    if d == 0:
        return 2
    p = math.ceil((math.sqrt(8 * d + 1) - 1) / 2)
    return p + 2


def W_pred(m: int, d: int) -> int:
    return (m - d) * L_of_d(d) - 2 * m


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: verify_unified.py <kunz_fast_output.json>", file=sys.stderr)
        return 2
    with open(sys.argv[1]) as f:
        data = json.load(f)
    m = data["m"]
    K = data["K_max"]
    print(f"# m={m}  K_max={K}  leaves_valid={data['leaves_valid']}  "
          f"elapsed={data['elapsed_sec']}s  backend={data.get('backend','?')}")
    print(f"{'d':>3} {'count':>12} {'W_obs':>8} {'W_pred':>8} {'slack':>8}  status")
    falsified = 0
    sharp = 0
    above = 0
    for d_str, slot in sorted(data["per_defect"].items(), key=lambda x: int(x[0])):
        d = int(d_str)
        if d == 0:
            continue
        w_obs = slot["W_min"]
        w_pred = W_pred(m, d)
        slack = w_obs - w_pred
        if slack < 0:
            status = "*** FALSIFIED ***"
            falsified += 1
        elif slack == 0:
            status = "sharp"
            sharp += 1
        else:
            status = f"+{slack} (above stabilization)"
            above += 1
        print(f"{d:>3} {slot['count']:>12} {w_obs:>8} {w_pred:>8} {slack:>8}  {status}")
    print()
    print(f"Summary: sharp={sharp}  above={above}  falsified={falsified}")
    return 1 if falsified else 0


if __name__ == "__main__":
    sys.exit(main())
