# GAP script: verify sharp bounds W >= W_min(m,d) for small defect
# Uses the official numericalsgps package
# Cross-validates our Python/C Kunz enumeration results

LoadPackage("numericalsgps");;

# Unified conjecture formula
# L(d) = floor((sqrt(8d+1)-1)/2) + 2
# Computed via triangular number lookup (avoids floating point)
LofD := function(d)
    local p;
    p := 0;
    while p*(p+1)/2 < d do
        p := p + 1;
    od;
    return p + 2;
end;;

WminFormula := function(m, d)
    return (m - d) * LofD(d) - 2 * m;
end;;

# Verify sharp bounds by enumerating all numerical semigroups up to a given genus
VerifyByGenus := function(max_genus)
    local g, sgs, s, m, e, d, c, L, W, violations, total, min_W_by_d,
          d_range, wmin_pred, key;

    violations := 0;
    total := 0;
    min_W_by_d := rec();  # track observed minimum W for each (m, d)

    for g in [1..max_genus] do
        sgs := NumericalSemigroupsWithGenus(g);
        for s in sgs do
            m := MultiplicityOfNumericalSemigroup(s);
            e := EmbeddingDimensionOfNumericalSemigroup(s);
            d := m - e;
            if d < 0 or d > 20 then continue; fi;

            c := ConductorOfNumericalSemigroup(s);
            L := Length(Filtered(SmallElementsOfNumericalSemigroup(s), x -> x < c));
            # SmallElements includes 0, and all elements < conductor
            W := e * L - c;

            total := total + 1;

            wmin_pred := WminFormula(m, d);

            # Only check when the predicted bound is positive (m large enough)
            if wmin_pred > 0 and W < wmin_pred then
                violations := violations + 1;
                Print("VIOLATION: m=", m, " e=", e, " d=", d,
                      " c=", c, " L=", L, " W=", W,
                      " W_min=", wmin_pred, "\n");
            fi;

            # Track minimum W for each (m, d) pair
            key := Concatenation(String(m), ",", String(d));
            if not IsBound(min_W_by_d.(key)) or W < min_W_by_d.(key)[1] then
                min_W_by_d.(key) := [W, m, e, d, c, L];
            fi;
        od;
    od;

    Print("\n========================================\n");
    Print("GAP VERIFICATION RESULTS (genus <= ", max_genus, ")\n");
    Print("========================================\n");
    Print("Total semigroups checked: ", total, "\n");
    Print("Violations of unified conjecture: ", violations, "\n\n");

    # Report minimum W for small defects
    Print("Observed minimum W by defect (for m where W_min > 0):\n");
    Print("d | m | e | W_obs | W_pred | match?\n");
    Print("--+---+---+-------+--------+-------\n");

    for d_range in [0..5] do
        for m in [3..30] do
            e := m - d_range;
            if e < 2 then continue; fi;
            key := Concatenation(String(m), ",", String(d_range));
            if IsBound(min_W_by_d.(key)) then
                wmin_pred := WminFormula(m, d_range);
                if wmin_pred > 0 then
                    Print(d_range, " | ", m, " | ", e, " | ",
                          min_W_by_d.(key)[1], " | ", wmin_pred, " | ");
                    if min_W_by_d.(key)[1] = wmin_pred then
                        Print("SHARP\n");
                    elif min_W_by_d.(key)[1] > wmin_pred then
                        Print("ok (above)\n");
                    else
                        Print("FAIL\n");
                    fi;
                fi;
            fi;
        od;
    od;

    Print("\n========================================\n");
    if violations = 0 then
        Print("VERIFICATION PASSED\n");
    else
        Print("*** VERIFICATION FAILED ***\n");
    fi;
    Print("========================================\n");
end;;

# Run verification up to genus 30 first (fast)
Print("Starting GAP verification with numericalsgps...\n\n");
VerifyByGenus(30);

QUIT;
