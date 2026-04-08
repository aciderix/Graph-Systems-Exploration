# GAP quick verification: sharp bounds for defect d=1,2,3
# Genus <= 15 for speed (~12K semigroups)
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

for g in [1..15] do
    for s in NumericalSemigroupsWithGenus(g) do
        m := MultiplicityOfNumericalSemigroup(s);
        e := EmbeddingDimensionOfNumericalSemigroup(s);
        d := m - e;
        if d < 0 or d > 10 then continue; fi;
        c := ConductorOfNumericalSemigroup(s);
        L := Length(Filtered(SmallElementsOfNumericalSemigroup(s), x -> x < c));
        W := e * L - c;
        total := total + 1;
        wmp := WminFormula(m, d);
        if wmp > 0 and W < wmp then
            violations := violations + 1;
            Print("VIOLATION: m=",m," d=",d," W=",W," Wpred=",wmp,"\n");
        fi;
        key := Concatenation(String(m),",",String(d));
        if not IsBound(min_by_md.(key)) or W < min_by_md.(key) then
            min_by_md.(key) := W;
        fi;
    od;
    Print("genus ", g, " done (", total, " so far)\n");
od;

Print("\n=== RESULTS (genus <= 15) ===\n");
Print("Total: ", total, ", Violations: ", violations, "\n\n");
Print("Min W observed for d=1:\n");
for m in [3..16] do
    key := Concatenation(String(m),",1");
    if IsBound(min_by_md.(key)) then
        Print("  m=",m," W_min_obs=",min_by_md.(key),
              " W_pred=",WminFormula(m,1),"\n");
    fi;
od;
Print("\nMin W observed for d=2:\n");
for m in [4..16] do
    key := Concatenation(String(m),",2");
    if IsBound(min_by_md.(key)) then
        Print("  m=",m," W_min_obs=",min_by_md.(key),
              " W_pred=",WminFormula(m,2),"\n");
    fi;
od;
Print("\nMin W observed for d=3:\n");
for m in [5..16] do
    key := Concatenation(String(m),",3");
    if IsBound(min_by_md.(key)) then
        Print("  m=",m," W_min_obs=",min_by_md.(key),
              " W_pred=",WminFormula(m,3),"\n");
    fi;
od;

if violations = 0 then Print("\nVERIFICATION PASSED\n");
else Print("\n*** FAILED ***\n"); fi;
QUIT;
