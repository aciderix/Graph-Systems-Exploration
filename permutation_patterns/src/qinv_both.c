/*
 * qinv_both.c - count Av_n(1342) using BOTH generic and specialized methods
 * at a given n. Reports both counts for cross-validation.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

#define MAXN 13

static int generic_contains_1342(const int *p, int n) {
    const int pat[4] = {1,3,4,2};
    for (int a = 0; a < n - 3; a++)
    for (int b = a + 1; b < n - 2; b++)
    for (int c = b + 1; c < n - 1; c++)
    for (int d = c + 1; d < n; d++) {
        int r[4] = {p[a], p[b], p[c], p[d]};
        int rank[4];
        for (int i = 0; i < 4; i++) {
            int cnt = 1;
            for (int j = 0; j < 4; j++) if (r[j] < r[i]) cnt++;
            rank[i] = cnt;
        }
        if (rank[0]==pat[0]&&rank[1]==pat[1]&&rank[2]==pat[2]&&rank[3]==pat[3])
            return 1;
    }
    return 0;
}

static int fast_contains_1342(const int *p, int n) {
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

static uint64_t gen_count = 0, fast_count = 0;

static void enumerate(int *p, int n, int depth, int used_mask) {
    if (depth == n) {
        if (!generic_contains_1342(p, n)) gen_count++;
        if (!fast_contains_1342(p, n))    fast_count++;
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
    int n = argc >= 2 ? atoi(argv[1]) : 11;
    int p[MAXN];
    clock_t t0 = clock();
    enumerate(p, n, 0, 0);
    clock_t t1 = clock();
    printf("n=%d  generic=%llu  fast=%llu  equal=%s  time=%.2fs\n",
           n,
           (unsigned long long)gen_count,
           (unsigned long long)fast_count,
           gen_count == fast_count ? "YES" : "NO",
           (double)(t1-t0)/CLOCKS_PER_SEC);
    return 0;
}
