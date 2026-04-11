/*
 * qstats_enum.c
 *
 * Enumerates permutations of S_n and accumulates multiple statistic
 * polynomials on each of the four classes Av_n(1234), Av_n(1342),
 * Av_n(1324), Av_n(4321):
 *
 *   - inv: number of inversions (Mahonian)
 *   - maj: major index (Mahonian)
 *   - des: number of descents (Eulerian)
 *   - peak: number of peaks (p_i > p_{i-1} and p_i > p_{i+1}, interior)
 *   - lis: length of longest increasing subsequence
 *
 * Output: JSON on stdout.
 *
 * Compile: cc -O3 -march=native -o qstats_enum qstats_enum.c
 * Run:     ./qstats_enum 11
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define MAXN 13
#define MAX_INV ((MAXN * (MAXN - 1)) / 2 + 1)

#define NPAT 4
static const char *PAT_NAME[NPAT] = {"1234", "1342", "1324", "4321"};
#define I_1234 0
#define I_1342 1
#define I_1324 2
#define I_4321 3

/* Specialized contains-tests as in qinv_enum.c. */

static inline int contains_1234(const int *p, int n) {
    for (int a = 0; a < n - 3; a++) {
        int pa = p[a];
        for (int b = a + 1; b < n - 2; b++) {
            int pb = p[b];
            if (pa >= pb) continue;
            for (int c = b + 1; c < n - 1; c++) {
                int pc = p[c];
                if (pb >= pc) continue;
                for (int d = c + 1; d < n; d++) if (pc < p[d]) return 1;
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
                for (int d = c + 1; d < n; d++) if (pc > p[d]) return 1;
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
            for (int c = b + 1; c < n - 1; c++) {
                int pc = p[c];
                if (!(pa < pc && pc < pb)) continue;
                for (int d = c + 1; d < n; d++) if (p[d] > pb) return 1;
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
                for (int d = c + 1; d < n; d++) {
                    int pd = p[d];
                    if (pa < pd && pd < pb) return 1;
                }
            }
        }
    }
    return 0;
}

/* Statistics computed on each permutation. */
static inline int stat_inv(const int *p, int n) {
    int inv = 0;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++)
            if (p[i] > p[j]) inv++;
    return inv;
}
static inline int stat_maj(const int *p, int n) {
    int maj = 0;
    for (int i = 0; i < n - 1; i++) if (p[i] > p[i+1]) maj += (i + 1);
    return maj;
}
static inline int stat_des(const int *p, int n) {
    int d = 0;
    for (int i = 0; i < n - 1; i++) if (p[i] > p[i+1]) d++;
    return d;
}
static inline int stat_peak(const int *p, int n) {
    int pk = 0;
    for (int i = 1; i < n - 1; i++) if (p[i-1] < p[i] && p[i] > p[i+1]) pk++;
    return pk;
}
static inline int stat_lis(const int *p, int n) {
    /* Patience sorting, O(n log n); here n <= 13, so O(n^2) is fine. */
    int dp[MAXN], max_lis = 0;
    for (int i = 0; i < n; i++) {
        dp[i] = 1;
        for (int j = 0; j < i; j++)
            if (p[j] < p[i] && dp[j] + 1 > dp[i]) dp[i] = dp[j] + 1;
        if (dp[i] > max_lis) max_lis = dp[i];
    }
    return max_lis;
}

/* Accumulators.
 * coeffs_inv[c][k] = number of perms in Av_n(c-th pattern) with inv=k.
 * Similarly for maj, des, peak, lis.
 */
static uint64_t coeffs_inv[NPAT][MAX_INV];
static uint64_t coeffs_maj[NPAT][MAX_INV];
static uint64_t coeffs_des[NPAT][MAXN];
static uint64_t coeffs_peak[NPAT][MAXN];
static uint64_t coeffs_lis[NPAT][MAXN + 1];
static uint64_t av_count[NPAT];

static void enumerate(int *p, int n, int depth, int used_mask) {
    if (depth == n) {
        int inv  = stat_inv(p, n);
        int maj  = stat_maj(p, n);
        int des  = stat_des(p, n);
        int peak = stat_peak(p, n);
        int lis  = stat_lis(p, n);
        int av[NPAT];
        av[I_1234] = !contains_1234(p, n);
        av[I_1342] = !contains_1342(p, n);
        av[I_1324] = !contains_1324(p, n);
        av[I_4321] = !contains_4321(p, n);
        for (int c = 0; c < NPAT; c++) {
            if (av[c]) {
                av_count[c]++;
                coeffs_inv[c][inv]++;
                coeffs_maj[c][maj]++;
                coeffs_des[c][des]++;
                coeffs_peak[c][peak]++;
                coeffs_lis[c][lis]++;
            }
        }
        return;
    }
    for (int v = 1; v <= n; v++) {
        if (!(used_mask & (1 << v))) {
            p[depth] = v;
            enumerate(p, n, depth + 1, used_mask | (1 << v));
        }
    }
}

static void print_arr(const char *name, uint64_t *arr, int len, int trailing_comma) {
    printf("        \"%s\": [", name);
    for (int k = 0; k < len; k++)
        printf("%llu%s", (unsigned long long)arr[k], k == len - 1 ? "" : ", ");
    printf("]%s\n", trailing_comma ? "," : "");
}

int main(int argc, char **argv) {
    int n = 8;
    if (argc >= 2) n = atoi(argv[1]);
    if (n < 1 || n > MAXN) { fprintf(stderr, "n in [1,%d]\n", MAXN); return 1; }

    memset(coeffs_inv, 0, sizeof(coeffs_inv));
    memset(coeffs_maj, 0, sizeof(coeffs_maj));
    memset(coeffs_des, 0, sizeof(coeffs_des));
    memset(coeffs_peak, 0, sizeof(coeffs_peak));
    memset(coeffs_lis, 0, sizeof(coeffs_lis));
    memset(av_count, 0, sizeof(av_count));

    int p[MAXN];
    clock_t t0 = clock();
    enumerate(p, n, 0, 0);
    clock_t t1 = clock();

    int max_inv = n * (n - 1) / 2;
    int max_des = n - 1;
    int max_peak = (n <= 2) ? 0 : (n - 1) / 2;
    int max_lis = n;

    printf("{\n");
    printf("  \"n\": %d,\n", n);
    printf("  \"max_inv\": %d,\n", max_inv);
    printf("  \"max_maj\": %d,\n", max_inv);
    printf("  \"max_des\": %d,\n", max_des);
    printf("  \"max_peak\": %d,\n", max_peak);
    printf("  \"max_lis\": %d,\n", max_lis);
    printf("  \"seconds\": %.3f,\n", (double)(t1-t0)/CLOCKS_PER_SEC);
    printf("  \"classes\": {\n");
    for (int c = 0; c < NPAT; c++) {
        printf("    \"%s\": {\n", PAT_NAME[c]);
        printf("      \"count\": %llu,\n", (unsigned long long)av_count[c]);
        print_arr("inv",  coeffs_inv[c],  max_inv + 1, 1);
        print_arr("maj",  coeffs_maj[c],  max_inv + 1, 1);
        print_arr("des",  coeffs_des[c],  max_des + 1, 1);
        print_arr("peak", coeffs_peak[c], max_peak + 1, 1);
        print_arr("lis",  coeffs_lis[c],  max_lis + 1, 0);
        printf("    }%s\n", c == NPAT - 1 ? "" : ",");
    }
    printf("  }\n");
    printf("}\n");
    return 0;
}
