/* kunz_core.c — fast invariants computation for the Kunz enumerator.
 *
 * Compiled on first import by kunz_fast.py via gcc -O3.
 *
 * Convention: k[0]=k_1, k[1]=k_2, ..., k[m-2]=k_{m-1}.
 *
 * Output buffer (8 ints):
 *   out[0] = d         (defect)
 *   out[1] = e         (m - d, embedding dimension)
 *   out[2] = k_star    (max k_i)
 *   out[3] = r_star    (largest residue achieving k_star, in [1, m-1])
 *   out[4] = L         (left elements)
 *   out[5] = F         (Frobenius number)
 *   out[6] = c         (conductor)
 *   out[7] = W         (Wilf number = e*L - c)
 */

void invariants(const int *k, int m, int *out) {
    int n = m - 1;
    int k_star = 0, r_star = 0;
    for (int i = 0; i < n; i++) {
        if (k[i] >= k_star) { k_star = k[i]; r_star = i + 1; }
    }

    /* L = k_star + sum delta_i */
    long L = k_star;
    for (int i = 0; i < n; i++) {
        int res = i + 1;
        if (res <= r_star) {
            L += (k_star - k[i]);
        } else {
            int dlt = k_star - 1 - k[i];
            if (dlt > 0) L += dlt;
        }
    }

    int F = (k_star - 1) * m + r_star;
    int c = F + 1;

    /* Defect: count residues r in [1, m-1] with some pair (a,b) such that
     * a+b ≡ r (mod m) and k_a + k_b + eps <= k_r. */
    int d = 0;
    for (int r = 1; r <= n; r++) {
        int kr = k[r - 1];
        int decomposable = 0;
        for (int a = 1; a <= n; a++) {
            int ka = k[a - 1];
            int b_nc = r - a;
            if (b_nc >= 1 && b_nc <= n) {
                if (ka + k[b_nc - 1] <= kr) { decomposable = 1; break; }
            }
            int b_c = r + m - a;
            if (b_c >= 1 && b_c <= n) {
                if (ka + k[b_c - 1] + 1 <= kr) { decomposable = 1; break; }
            }
        }
        if (decomposable) d++;
    }

    int e = m - d;
    long W = (long)e * L - c;

    out[0] = d;
    out[1] = e;
    out[2] = k_star;
    out[3] = r_star;
    out[4] = (int)L;
    out[5] = F;
    out[6] = c;
    out[7] = (int)W;
}
