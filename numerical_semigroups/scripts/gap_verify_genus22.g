# GAP verification: sharp bounds, genus <= 22
# Extended version for cross-validation report
LoadPackage("numericalsgps");;

LofD := function(d)
    local p;
    p := 0;
    while p*(p+1)/2 < d do p := p + 1; od;
    return p + 2;
end;;

WminFormula := function(m, d)
    return (m - d) * LofD(d) - 2 * m;
end;;

total := 0;; violations := 0;; min_by_md := rec();;
output := OutputTextFile("/home/user/Graph-Systems-Exploration/numerical_semigroups/results/gap_genus22_results.txt", false);;

PrintBoth := function(str)
    Print(str);
    WriteAll(output, str);
end;;

for g in [1..22] do
    for s in NumericalSemigroupsWithGenus(g) do
        m := MultiplicityOfNumericalSemigroup(s);
        e := EmbeddingDimensionOfNumericalSemigroup(s);
        d := m - e;
        if d < 0 or d > 15 then continue; fi;
        c := ConductorOfNumericalSemigroup(s);
        L := Length(Filtered(SmallElementsOfNumericalSemigroup(s), x -> x < c));
        W := e * L - c;
        total := total + 1;
        wmp := WminFormula(m, d);
        if wmp > 0 and W < wmp then
            violations := violations + 1;
            PrintBoth(Concatenation("VIOLATION: m=", String(m), " d=", String(d),
                      " W=", String(W), " Wpred=", String(wmp), "\n"));
        fi;
        key := Concatenation(String(m), ",", String(d));
        if not IsBound(min_by_md.(key)) or W < min_by_md.(key) then
            min_by_md.(key) := W;
        fi;
    od;
    PrintBoth(Concatenation("genus ", String(g), " done (", String(total), " total)\n"));
od;

PrintBoth(Concatenation("\n=== GAP RESULTS (genus <= 22) ===\n"));
PrintBoth(Concatenation("Total: ", String(total), ", Violations: ", String(violations), "\n\n"));

for dd in [0..10] do
    PrintBoth(Concatenation("--- Defaut d=", String(dd), " ---\n"));
    for m in [dd+2..25] do
        key := Concatenation(String(m), ",", String(dd));
        if IsBound(min_by_md.(key)) then
            wmp := WminFormula(m, dd);
            if min_by_md.(key) = wmp then tag := "SHARP";
            elif min_by_md.(key) > wmp then tag := "above";
            else tag := "FAIL"; fi;
            PrintBoth(Concatenation("  m=", String(m), " Wobs=", String(min_by_md.(key)),
                      " Wpred=", String(wmp), " ", tag, "\n"));
        fi;
    od;
od;

if violations = 0 then PrintBoth("\nVERIFICATION PASSED\n");
else PrintBoth("\n*** FAILED ***\n"); fi;

CloseStream(output);
QUIT;
