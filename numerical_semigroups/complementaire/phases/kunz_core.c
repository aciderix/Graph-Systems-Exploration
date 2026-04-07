/* kunz_core.c — fast invariants + enumeration kernel for the Kunz polyhedron.
 *
 * Compiled on first import by kunz_fast.py via gcc -O3.
 *
 * Two entry points:
 *   invariants(k, m, out)        — compute invariants of one tuple
 *   run_enum(m, K_max, ...)      — full backtracking enumeration in C
 *
 * Convention: k[0]=k_1, k[1]=k_2, ..., k[m-2]=k_{m-1}.
 */

#include <string.h>
#include <limits.h>

#define MAX_M 64

/* ----------- single-tuple invariants (kept for unit testing) ------------ */

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

/* ============================================================
 * Full backtracking enumeration in C (the real speedup).
 * ============================================================
 *
 * Layout of kunz_result_t (must match Python ctypes Structure exactly):
 *   counts    [MAX_M]               int32
 *   W_neg     [MAX_M]               int32
 *   W_min     [MAX_M]               int64
 *   argmin_k  [MAX_M][MAX_M]        int32
 *   leaves_raw                      int64
 *   leaves_valid                    int64
 *   leaves_kept                     int64
 */
typedef struct {
    int counts[MAX_M];
    int W_neg[MAX_M];
    long long W_min[MAX_M];
    int argmin_k[MAX_M][MAX_M];
    long long leaves_raw;
    long long leaves_valid;
    long long leaves_kept;
} kunz_result_t;

static int     g_M;
static int     g_KMAX;
static int     g_K[MAX_M];
static kunz_result_t *g_RES;
static int     g_DMIN, g_DMAX;
static long long g_WMAX;
static int     g_HAS_WMAX;

static void compute_and_record(void) {
    int n = g_M - 1;
    int k_star = 0, r_star = 0;
    for (int i = 0; i < n; i++) {
        if (g_K[i] >= k_star) { k_star = g_K[i]; r_star = i + 1; }
    }
    long long L = k_star;
    for (int i = 0; i < n; i++) {
        int res = i + 1;
        if (res <= r_star) L += (k_star - g_K[i]);
        else { int dlt = k_star - 1 - g_K[i]; if (dlt > 0) L += dlt; }
    }
    int F = (k_star - 1) * g_M + r_star;
    int c = F + 1;

    int d = 0;
    for (int r = 1; r <= n; r++) {
        int kr = g_K[r - 1];
        int decomposable = 0;
        for (int a = 1; a <= n; a++) {
            int ka = g_K[a - 1];
            int b_nc = r - a;
            if (b_nc >= 1 && b_nc <= n) {
                if (ka + g_K[b_nc - 1] <= kr) { decomposable = 1; break; }
            }
            int b_c = r + g_M - a;
            if (b_c >= 1 && b_c <= n) {
                if (ka + g_K[b_c - 1] + 1 <= kr) { decomposable = 1; break; }
            }
        }
        if (decomposable) d++;
    }
    int e = g_M - d;
    long long W = (long long)e * L - c;

    if (d < g_DMIN || d > g_DMAX) return;
    if (g_HAS_WMAX && W > g_WMAX) return;

    g_RES->leaves_kept++;
    g_RES->counts[d]++;
    if (W < 0) g_RES->W_neg[d]++;
    if (g_RES->counts[d] == 1 || W < g_RES->W_min[d]) {
        g_RES->W_min[d] = W;
        for (int i = 0; i < n; i++) g_RES->argmin_k[d][i] = g_K[i];
    }
}

static int verify_carry(void) {
    int n = g_M - 1;
    for (int r = 1; r <= n; r++) {
        int kr = g_K[r - 1];
        for (int a = r + 1; a <= n; a++) {
            int b = r + g_M - a;
            if (b >= 1 && b <= n) {
                if (kr > g_K[a - 1] + g_K[b - 1] + 1) return 0;
            }
        }
    }
    return 1;
}

static void rec_enum(int r) {
    if (r == g_M) {
        g_RES->leaves_raw++;
        if (verify_carry()) {
            g_RES->leaves_valid++;
            compute_and_record();
        }
        return;
    }
    int ub = g_KMAX;
    for (int a = 1; a < r; a++) {
        int b = r - a;
        int v = g_K[a - 1] + g_K[b - 1];
        if (v < ub) ub = v;
    }
    if (ub < 1) return;
    for (int val = 1; val <= ub; val++) {
        g_K[r - 1] = val;
        rec_enum(r + 1);
    }
}

void run_enum(int m, int k_max,
              int d_min, int d_max,
              long long w_max, int has_w_max,
              kunz_result_t *out) {
    if (m < 2 || m > MAX_M) return;
    g_M = m;
    g_KMAX = k_max;
    g_DMIN = d_min;
    g_DMAX = d_max;
    g_WMAX = w_max;
    g_HAS_WMAX = has_w_max;
    g_RES = out;
    memset(g_RES, 0, sizeof(*g_RES));
    /* Initialize W_min sentinel; counts==0 means "no record yet" so the
     * first hit will overwrite regardless of value. */
    rec_enum(1);
}
