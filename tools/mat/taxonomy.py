"""Controlled topic vocabulary for the MAT database.

The first ten topics follow the official MAT syllabus (issued January 2018);
the remainder cover the ground the long questions actually test - combinatorics,
number theory, logic and algorithmic reasoning - which the syllabus assumes
rather than lists. Every topic maps to a chapter of this site so a question can
link straight to the relevant theory.

Each entry is (id, label, chapter, {weight: [patterns]}). Weights are 3 for a
signal that all but settles the topic, 2 for a good one, 1 for corroboration.
Patterns are matched case-insensitively as regular expressions.
"""

TOPICS = [
    ("polynomials", "Polynomials &amp; quadratics", "algebra.html", {
        3: [r"\bdiscriminant\b", r"completing the square", r"factor theorem",
            r"\bquartic\b", r"remainder theorem"],
        2: [r"\bquadratics?\b", r"\bcubics?\b", r"\bpolynomials?\b",
            r"repeated root", r"\bfactorise\b"],
        1: [r"\broots?\b", r"\bdegree\b", r"\bcoefficients?\b"]}),

    ("algebra", "Algebra &amp; inequalities", "algebra.html", {
        3: [r"\binequalit(y|ies)\b", r"simultaneous equations?",
            # "how many real solutions" is an equation-solving question, not counting
            r"how many[\w\s]{0,24}\b(solutions?|roots?|values)\b"],
        2: [r"\brearrange", r"\bmodulus\b", r"\bsurds?\b", r"\bsatisfied precisely when\b",
            r"\|x\|"],
        1: [r"\bsolve the equation\b", r"\bsolutions? x\b", r"\bexpression\b"]}),

    ("binomial", "Binomial theorem", "counting.html", {
        3: [r"\bbinomial\b", r"\bpascal"],
        2: [r"coefficient of x", r"\bexpansion of\b"],
        1: [r"\bexpansion\b"]}),

    ("differentiation", "Differentiation", "differentiation.html", {
        3: [r"\bderivative\b", r"\bdifferentiat", r"turning points?",
            r"stationary points?", r"first principles"],
        2: [r"\btangent to\b", r"\bnormal to\b", r"\bd\s*y\s*/?\s*d\s*x\b",
            r"increasing and decreasing", r"second (order )?derivative"],
        1: [r"\bmaxim(um|a)\b", r"\bminim(um|a)\b", r"\bgradient\b", r"\bconcave\b"]}),

    ("integration", "Integration", "integration.html", {
        3: [r"\bintegrals?\b", r"\bintegrat(e|ing|ion)\b", r"\btrapezium\b"],
        2: [r"\bd\s*x\b(?!\s*/)", r"area (under|between|bounded|beneath)",
            r"signed area"],
        1: [r"\bareas?\b", r"\bvolumes?\b"]}),

    ("graphs", "Graphs &amp; transformations", "functions.html", {
        3: [r"\bsketch(ed|es|ing)?\b", r"\basymptot", r"\btransformation"],
        2: [r"\bgraph(s)? of\b", r"is sketched in", r"\bstretch\b",
            r"\breflect(ion|ed)\b", r"\btranslat(e|ion)\b"],
        1: [r"\bgraph\b", r"\bcurves?\b", r"\baxes\b", r"\bplot"]}),

    ("logexp", "Logarithms &amp; exponentials", "functions.html", {
        3: [r"\blogarithms?\b", r"\blog_?1?0?\b", r"\bln\b"],
        2: [r"\bexponentials?\b", r"\be\^", r"\bpowers of\b"],
        1: [r"\bexponent"]}),

    ("coordgeom", "Coordinate geometry", "geometry.html", {
        3: [r"co-?ordinate geometry", r"equation of the (straight )?line"],
        2: [r"co-?ordinates?\b", r"\bmidpoint\b", r"\bperpendicular\b",
            r"distance between"],
        1: [r"\bstraight line\b", r"\borigin\b", r"\bx-axis\b", r"\by-axis\b"]}),

    ("circles", "Circles", "geometry.html", {
        3: [r"\bcircles?\b", r"\bcircumference\b", r"\bchord\b"],
        2: [r"\bradius\b", r"\bradii\b", r"\bcentre\b", r"\barc\b", r"\bsector\b"],
        1: [r"\btangent\b"]}),

    ("trigonometry", "Trigonometry", "geometry.html", {
        3: [r"\btrigonometr", r"sine rule", r"cosine rule", r"\bsin\b", r"\bcos\b",
            r"\btan\b"],
        2: [r"\bradians?\b", r"\bdegrees\b", r"\bperiodic"],
        1: [r"\bangles?\b", r"\btriangles?\b"]}),

    ("vectors", "Vectors", "geometry.html", {
        3: [r"\bvectors?\b"],
        2: [r"position vector", r"scalar product", r"dot product"],
        1: []}),

    ("sequences", "Sequences &amp; series", "sequences.html", {
        3: [r"\bsequences?\b", r"\bseries\b", r"\brecurrence\b",
            r"(arithmetic|geometric) (progression|series|sequence)"],
        2: [r"\bfibonacci\b", r"sum to infinity", r"\bconverge", r"\bnth term\b",
            r"defined iteratively"],
        1: [r"\bterms?\b", r"\bsums?\b"]}),

    ("numbertheory", "Number theory", "numbers.html", {
        3: [r"\bprimes?\b", r"\bdivisible\b", r"\bmodulo\b", r"highest common",
            r"\bdivisors?\b", r"\b(square|cube|triangular) numbers?\b",
            r"perfect (square|cube)", r"\bfloor\b", r"largest whole number"],
        2: [r"\bmultiple of\b", r"\bremainder\b", r"\bdigits?\b",
            r"whole numbers?", r"\bintegers?\b", r"\bfactors? of\b"],
        1: [r"\bodd\b", r"\beven\b"]}),

    ("combinatorics", "Combinatorics &amp; counting", "counting.html", {
        3: [r"how many ways", r"number of ways", r"\bpermutations?\b",
            r"\bcombinations?\b", r"\barrangements?\b"],
        2: [r"\bchoose\b", r"\bdistinct\b.*\bways\b", r"\bcounting\b"],
        1: [r"\bpossibilit(y|ies)\b", r"how many\b"]}),

    ("probability", "Probability", "counting.html", {
        3: [r"\bprobabilit(y|ies)\b", r"\bexpected value\b"],
        2: [r"\brandom(ly)?\b", r"\bdice\b", r"\bdie\b", r"\bcoin\b",
            r"\bindependent events?\b"],
        1: [r"\bchance\b"]}),

    ("logic", "Logic &amp; proof", "logic.html", {
        3: [r"\binduction\b", r"\bcontradiction\b", r"if and only if",
            r"\bcounter-?example\b", r"truth table", r"logically equivalent"],
        2: [r"\bstatements?\b", r"\bimplies\b", r"\bnecessary and sufficient\b",
            r"\btrue or false\b", r"\blogic"],
        1: [r"\bprove\b", r"\bshow that\b", r"\bjustify\b"]}),

    ("algorithms", "Algorithms &amp; games", "logic.html", {
        3: [r"\balgorithms?\b", r"\bstrateg(y|ies)\b", r"\bplayers?\b",
            r"\bbinary\b", r"\bprocedure\b"],
        2: [r"\bgames?\b", r"\bwins\b", r"\bmoves?\b", r"\bgrid\b", r"\bcells?\b",
            r"\bsteps?\b", r"\bmachine\b", r"\brobot\b"],
        1: [r"\brules?\b", r"\bsequence of moves\b"]}),
]

BY_ID = {t[0]: t for t in TOPICS}
