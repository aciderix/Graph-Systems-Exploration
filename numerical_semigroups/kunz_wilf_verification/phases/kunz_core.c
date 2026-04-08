/* kunz_core.c — fast invariants + enumeration kernel for the Kunz polyhedron.
 *
 * Compiled on first import by kunz_fast.py via gcc -O3 (-fopenmp when
 * available). Two enumeration entry points:
 *
 *   run_enum      — single-threaded backtracking (reference)
 *   run_enum_omp  — OpenMP-parallel backtracking (split over k_1)
 *
 * Both write into the same kunz_result_t layout (see below); a reduce step
 * merges per-thread partial results into the caller's struct.
 *
 * Convention: k[0]=k_1, k[1]=k_2, ..., k[m-2]=k_{m-1}.
 */

#include <string.h>
#include <limits.h>
#ifdef _OPENMP
#include <omp.h>
#endif

#define MAX_M 64

/* ----------- single-tuple invariants (kept for unit testing) ------------ */

void invariants(const int *k, int m, int *out) {
    int n = m - 1;
    int k_star = 0, r_star = 0;
    for (int i = 0; i < n; i++) {
        if (k[i] >= k_star) { k_star = k[i]; r_star = i + 1; }
    }

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
 * Enumeration kernel (reentrant, used by both serial and OMP).
 * ============================================================
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

typedef struct {
    int m;
    int k_max;
    int d_min, d_max;
    long long w_max;
    int has_w_max;
    int K[MAX_M];
    kunz_result_t res;
} kunz_ctx_t;

static void ctx_compute_and_record(kunz_ctx_t *c) {
    int m = c->m;
    int n = m - 1;
    int *K = c->K;

    int k_star = 0, r_star = 0;
    for (int i = 0; i < n; i++) {
        if (K[i] >= k_star) { k_star = K[i]; r_star = i + 1; }
    }
    long long L = k_star;
    for (int i = 0; i < n; i++) {
        int res = i + 1;
        if (res <= r_star) L += (k_star - K[i]);
        else { int dlt = k_star - 1 - K[i]; if (dlt > 0) L += dlt; }
    }
    int F = (k_star - 1) * m + r_star;
    int cc = F + 1;

    int d = 0;
    for (int r = 1; r <= n; r++) {
        int kr = K[r - 1];
        int decomposable = 0;
        for (int a = 1; a <= n; a++) {
            int ka = K[a - 1];
            int b_nc = r - a;
            if (b_nc >= 1 && b_nc <= n) {
                if (ka + K[b_nc - 1] <= kr) { decomposable = 1; break; }
            }
            int b_c = r + m - a;
            if (b_c >= 1 && b_c <= n) {
                if (ka + K[b_c - 1] + 1 <= kr) { decomposable = 1; break; }
            }
        }
        if (decomposable) d++;
    }
    int e = m - d;
    long long W = (long long)e * L - cc;

    if (d < c->d_min || d > c->d_max) return;
    if (c->has_w_max && W > c->w_max) return;

    kunz_result_t *R = &c->res;
    R->leaves_kept++;
    R->counts[d]++;
    if (W < 0) R->W_neg[d]++;
    if (R->counts[d] == 1 || W < R->W_min[d]) {
        R->W_min[d] = W;
        for (int i = 0; i < n; i++) R->argmin_k[d][i] = K[i];
    }
}

static int ctx_verify_carry(kunz_ctx_t *c) {
    int m = c->m;
    int n = m - 1;
    int *K = c->K;
    for (int r = 1; r <= n; r++) {
        int kr = K[r - 1];
        for (int a = r + 1; a <= n; a++) {
            int b = r + m - a;
            if (b >= 1 && b <= n) {
                if (kr > K[a - 1] + K[b - 1] + 1) return 0;
            }
        }
    }
    return 1;
}

static void ctx_rec(kunz_ctx_t *c, int r) {
    if (r == c->m) {
        c->res.leaves_raw++;
        if (ctx_verify_carry(c)) {
            c->res.leaves_valid++;
            ctx_compute_and_record(c);
        }
        return;
    }
    int ub = c->k_max;
    for (int a = 1; a < r; a++) {
        int b = r - a;
        int v = c->K[a - 1] + c->K[b - 1];
        if (v < ub) ub = v;
    }
    if (ub < 1) return;
    for (int val = 1; val <= ub; val++) {
        c->K[r - 1] = val;
        ctx_rec(c, r + 1);
    }
}

/* ------------------------- reduction helper --------------------------- */

static void reduce_into(kunz_result_t *dst, const kunz_result_t *src, int m) {
    dst->leaves_raw   += src->leaves_raw;
    dst->leaves_valid += src->leaves_valid;
    dst->leaves_kept  += src->leaves_kept;
    for (int d = 0; d < MAX_M; d++) {
        if (src->counts[d] == 0) continue;
        int had = dst->counts[d];
        dst->counts[d] += src->counts[d];
        dst->W_neg[d]  += src->W_neg[d];
        if (had == 0 || src->W_min[d] < dst->W_min[d]) {
            dst->W_min[d] = src->W_min[d];
            for (int i = 0; i < m - 1; i++)
                dst->argmin_k[d][i] = src->argmin_k[d][i];
        }
    }
}

/* ------------------------- public entry points ------------------------ */

void run_enum(int m, int k_max,
              int d_min, int d_max,
              long long w_max, int has_w_max,
              kunz_result_t *out) {
    if (m < 2 || m > MAX_M) return;
    memset(out, 0, sizeof(*out));

    kunz_ctx_t ctx;
    memset(&ctx, 0, sizeof(ctx));
    ctx.m = m;
    ctx.k_max = k_max;
    ctx.d_min = d_min;
    ctx.d_max = d_max;
    ctx.w_max = w_max;
    ctx.has_w_max = has_w_max;

    ctx_rec(&ctx, 1);
    reduce_into(out, &ctx.res, m);
}

/* Enumerate only the subtree where (k_1, ..., k_{plen}) is fixed to the
 * given prefix. Used for chunking long enumerations into independent jobs:
 * the union of all valid prefix-restricted runs reproduces run_enum exactly.
 *
 * The prefix must already satisfy the no-carry constraints internally
 * (k_r <= k_a + k_b for a+b=r within the prefix). Invalid prefixes simply
 * yield zero leaves.
 */
void run_enum_prefix(int m, int k_max,
                     int d_min, int d_max,
                     long long w_max, int has_w_max,
                     const int *prefix, int plen,
                     kunz_result_t *out) {
    if (m < 2 || m > MAX_M) return;
    if (plen < 0 || plen >= m) return;
    memset(out, 0, sizeof(*out));

    kunz_ctx_t ctx;
    memset(&ctx, 0, sizeof(ctx));
    ctx.m = m;
    ctx.k_max = k_max;
    ctx.d_min = d_min;
    ctx.d_max = d_max;
    ctx.w_max = w_max;
    ctx.has_w_max = has_w_max;

    /* Validate prefix against the no-carry forward constraints. */
    for (int r = 1; r <= plen; r++) {
        int v = prefix[r - 1];
        if (v < 1 || v > k_max) return;
        for (int a = 1; a < r; a++) {
            int b = r - a;
            if (v > prefix[a - 1] + prefix[b - 1]) return;
        }
        ctx.K[r - 1] = v;
    }

    if (plen == m - 1) {
        /* Whole tuple fixed: just verify carry and record. */
        ctx.res.leaves_raw++;
        if (ctx_verify_carry(&ctx)) {
            ctx.res.leaves_valid++;
            ctx_compute_and_record(&ctx);
        }
    } else {
        ctx_rec(&ctx, plen + 1);
    }
    reduce_into(out, &ctx.res, m);
}

/* OpenMP parallel variant. Splits the outer loop over k_1 across threads
 * (each value of k_1 is an independent subtree). Falls back to serial when
 * compiled without -fopenmp. */
void run_enum_omp(int m, int k_max,
                  int d_min, int d_max,
                  long long w_max, int has_w_max,
                  int n_threads,
                  kunz_result_t *out) {
    if (m < 2 || m > MAX_M) return;
    memset(out, 0, sizeof(*out));

#ifdef _OPENMP
    if (n_threads > 0) omp_set_num_threads(n_threads);
#else
    (void)n_threads;
#endif

    /* Precompute all valid (k_1, k_2) pairs (k_2 <= 2 k_1 by forward check)
     * so we have many more tasks than threads even when k_max is tiny. */
    int pairs1[MAX_M * MAX_M], pairs2[MAX_M * MAX_M];
    int npairs = 0;
    if (m == 2) {
        for (int v1 = 1; v1 <= k_max; v1++) {
            pairs1[npairs] = v1; pairs2[npairs] = 0; npairs++;
        }
    } else {
        for (int v1 = 1; v1 <= k_max; v1++) {
            int ub2 = 2 * v1; if (ub2 > k_max) ub2 = k_max;
            for (int v2 = 1; v2 <= ub2; v2++) {
                pairs1[npairs] = v1; pairs2[npairs] = v2; npairs++;
            }
        }
    }

#pragma omp parallel
    {
        kunz_ctx_t ctx;
        memset(&ctx, 0, sizeof(ctx));
        ctx.m = m;
        ctx.k_max = k_max;
        ctx.d_min = d_min;
        ctx.d_max = d_max;
        ctx.w_max = w_max;
        ctx.has_w_max = has_w_max;

#pragma omp for schedule(dynamic, 1)
        for (int idx = 0; idx < npairs; idx++) {
            ctx.K[0] = pairs1[idx];
            if (m == 2) {
                ctx.res.leaves_raw++;
                ctx.res.leaves_valid++;
                ctx_compute_and_record(&ctx);
            } else if (m == 3) {
                ctx.K[1] = pairs2[idx];
                ctx.res.leaves_raw++;
                if (ctx_verify_carry(&ctx)) {
                    ctx.res.leaves_valid++;
                    ctx_compute_and_record(&ctx);
                }
            } else {
                ctx.K[1] = pairs2[idx];
                ctx_rec(&ctx, 3);
            }
        }

#pragma omp critical
        {
            reduce_into(out, &ctx.res, m);
        }
    }
}
