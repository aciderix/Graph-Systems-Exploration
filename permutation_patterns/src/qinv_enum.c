/*
 * qinv_enum.c
 *
 * Brute-force exhaustive enumerator for permutations of S_n,
 * counting the q-inversion polynomial f_n^pi(q) = sum_{sigma in Av_n(pi)} q^{inv(sigma)}
 * for patterns pi in {1234, 1342, 1324, 4321}, simultaneously in one pass.
 *
 * Also tracks the full S_n q-factorial [n]_q! as baseline (unrestricted sum of q^inv).
 *
 * Size: n <= 12 feasible in brute force (479M perms at n=12).
 *       n <= 11 recommended for the first pass (39.9M perms).
 *
 * Output: stdout, one JSON-ish block per n.
 *
 * Compile: cc -O3 -march=native -o qinv_enum qinv_enum.c
 * Run:     ./qinv_enum 11
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define MAXN 14
#define MAX_INV ((MAXN * (MAXN - 1)) / 2 + 1)

/* We test 4 patterns in parallel. Indices:
 *   0: 1234
 *   1: 1342
 *   2: 1324
 *   3: 4321
 */
#define NPAT 4
static const int PAT[NPAT][4] = {
    {1, 2, 3, 4},
    {1, 3, 4, 2},
    {1, 3, 2, 4},
    {4, 3, 2, 1}
};
static const char *PAT_NAME[NPAT] = {"1234", "1342", "1324", "4321"};

/* Accumulators: coeffs[pat][k] = number of perms in Av_n(pat) with inv = k.
 * Also: all_coeffs[k] = number of perms of S_n with inv = k = Mahonian numbers.
 */
static uint64_t coeffs[NPAT][MAX_INV];
static uint64_t all_coeffs[MAX_INV];
static uint64_t av_count[NPAT];   /* |Av_n(pat)| */

/* Specialized containment tests. For each of the 4 target patterns we write
 * an inlined scan with prefix pruning: as soon as an (a), (a,b), (a,b,c)
 * prefix can't complete, we skip the corresponding inner loops.
 *
 * 1234: p[a] < p[b] < p[c] < p[d]
 * 1342: p[a] < p[d] < p[b] < p[c]
 * 1324: p[a] < p[c] < p[b] < p[d]
 * 4321: p[a] > p[b] > p[c] > p[d]
 */

static inline int contains_1234(const int *p, int n) {
    for (int a = 0; a < n - 3; a++) {
        int pa = p[a];
        for (int b = a + 1; b < n - 2; b++) {
            int pb = p[b];
            if (pa >= pb) continue;
            for (int c = b + 1; c < n - 1; c++) {
                int pc = p[c];
                if (pb >= pc) continue;
                for (int d = c + 1; d < n; d++) {
                    if (pc < p[d]) return 1;
                }
            }
        }
    }
    return 0;
}

static inline int contains_4321(const int *p, int n) {
    for (int a = 0; a < n - 3; a++) {
        int pa = p[a];
        for (int b = a + 1; b < n - 2; b++) {
            int pb = p[b];
            if (pa <= pb) continue;
            for (int c = b + 1; c < n - 1; c++) {
                int pc = p[c];
                if (pb <= pc) continue;
                for (int d = c + 1; d < n; d++) {
                    if (pc > p[d]) return 1;
                }
            }
        }
    }
    return 0;
}

static inline int contains_1324(const int *p, int n) {
    for (int a = 0; a < n - 3; a++) {
        int pa = p[a];
        for (int b = a + 1; b < n - 2; b++) {
            int pb = p[b];
            if (pa >= pb) continue;
            /* Need c with a<b<c<n-1, p[a]<p[c]<p[b], and then some d>c with p[d]>p[b]. */
            for (int c = b + 1; c < n - 1; c++) {
                int pc = p[c];
                if (!(pa < pc && pc < pb)) continue;
                for (int d = c + 1; d < n; d++) {
                    if (p[d] > pb) return 1;
                }
            }
        }
    }
    return 0;
}

static inline int contains_1342(const int *p, int n) {
    for (int a = 0; a < n - 3; a++) {
        int pa = p[a];
        for (int b = a + 1; b < n - 2; b++) {
            int pb = p[b];
            if (pa >= pb) continue;
            for (int c = b + 1; c < n - 1; c++) {
                int pc = p[c];
                if (pb >= pc) continue;
                /* Need d with c<d<n and pa<p[d]<pb. */
                for (int d = c + 1; d < n; d++) {
                    int pd = p[d];
                    if (pa < pd && pd < pb) return 1;
                }
            }
        }
    }
    return 0;
}

/* Count inversions of p[0..n-1]. O(n^2). */
static inline int inv_count(const int *p, int n) {
    int inv = 0;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++)
            if (p[i] > p[j]) inv++;
    return inv;
}

/* Recursive lexicographic enumeration of all permutations of [1..n]. */
static void enumerate(int *p, int n, int depth, int used_mask) {
    if (depth == n) {
        int inv = inv_count(p, n);
        all_coeffs[inv]++;
        if (!contains_1234(p, n)) { coeffs[0][inv]++; av_count[0]++; }
        if (!contains_1342(p, n)) { coeffs[1][inv]++; av_count[1]++; }
        if (!contains_1324(p, n)) { coeffs[2][inv]++; av_count[2]++; }
        if (!contains_4321(p, n)) { coeffs[3][inv]++; av_count[3]++; }
        return;
    }
    for (int v = 1; v <= n; v++) {
        if (!(used_mask & (1 << v))) {
            p[depth] = v;
            enumerate(p, n, depth + 1, used_mask | (1 << v));
        }
    }
}

int main(int argc, char **argv) {
    int n = 8;
    if (argc >= 2) n = atoi(argv[1]);
    if (n < 1 || n > MAXN) {
        fprintf(stderr, "n must be in [1, %d]\n", MAXN);
        return 1;
    }

    memset(coeffs, 0, sizeof(coeffs));
    memset(all_coeffs, 0, sizeof(all_coeffs));
    memset(av_count, 0, sizeof(av_count));

    int p[MAXN];
    clock_t t0 = clock();
    enumerate(p, n, 0, 0);
    clock_t t1 = clock();
    double secs = (double)(t1 - t0) / CLOCKS_PER_SEC;

    int max_inv = n * (n - 1) / 2;

    /* Emit JSON-ish block to stdout. */
    printf("{\n");
    printf("  \"n\": %d,\n", n);
    printf("  \"max_inv\": %d,\n", max_inv);
    printf("  \"seconds\": %.3f,\n", secs);
    printf("  \"mahonian\": [");
    for (int k = 0; k <= max_inv; k++) {
        printf("%llu%s", (unsigned long long)all_coeffs[k],
               k == max_inv ? "" : ", ");
    }
    printf("],\n");
    printf("  \"classes\": {\n");
    for (int c = 0; c < NPAT; c++) {
        printf("    \"%s\": {\n", PAT_NAME[c]);
        printf("      \"count\": %llu,\n", (unsigned long long)av_count[c]);
        printf("      \"f\": [");
        for (int k = 0; k <= max_inv; k++) {
            printf("%llu%s", (unsigned long long)coeffs[c][k],
                   k == max_inv ? "" : ", ");
        }
        printf("]\n");
        printf("    }%s\n", c == NPAT - 1 ? "" : ",");
    }
    printf("  }\n");
    printf("}\n");

    return 0;
}
