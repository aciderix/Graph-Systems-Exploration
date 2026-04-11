/*
 * qinv_verify.c
 *
 * Runs both specialized contains_1342 and generic rank-based pattern test
 * on S_n and reports permutations where they disagree. Small n only.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 11

static int generic_contains(const int *p, int n, const int pat[4]) {
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

static void enumerate(int *p, int n, int depth, int used_mask,
                      long *disagree, long *shown) {
    if (depth == n) {
        const int pat[4] = {1,3,4,2};
        int g = generic_contains(p, n, pat);
        int f = fast_contains_1342(p, n);
        if (g != f) {
            (*disagree)++;
            if (*shown < 5) {
                printf("DISAGREE: perm=[");
                for (int i = 0; i < n; i++) printf("%d%s", p[i], i==n-1?"":",");
                printf("]  generic=%d  fast=%d\n", g, f);
                (*shown)++;
            }
        }
        return;
    }
    for (int v = 1; v <= n; v++) {
        if (!(used_mask & (1 << v))) {
            p[depth] = v;
            enumerate(p, n, depth + 1, used_mask | (1 << v), disagree, shown);
        }
    }
}

int main(int argc, char **argv) {
    int n = argc >= 2 ? atoi(argv[1]) : 9;
    if (n < 4 || n > MAXN) { fprintf(stderr, "bad n\n"); return 1; }
    int p[MAXN];
    long disagree = 0, shown = 0;
    enumerate(p, n, 0, 0, &disagree, &shown);
    printf("n=%d, total disagreements: %ld\n", n, disagree);
    return 0;
}
