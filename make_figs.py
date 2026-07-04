#!/usr/bin/env python3
"""Generate two SVG figures matching the site's fig-cossin.svg visual style.
   Colours are hardcoded (figures load via <img>, so cannot inherit page CSS)."""
import math

# --- shared palette (from fig-cossin.svg / styles.css) ---
PAPER  = "#FBFAF5"
GRID   = "#ECE8DD"
AXIS   = "#23282E"
LABEL  = "#5A6068"
NAVY   = "#13294B"   # increasing side / side b
RUST   = "#B7410E"   # decreasing side / side a (triangle 2)
GREEN  = "#3E7164"   # annotations / overlap / side a (triangle 1)
GREENF = "rgba(62,113,100,0.16)"  # translucent overlap fill

def esc(s): return s

# =====================================================================
# FIGURE 1 — increasing meets decreasing, ranges overlap -> one crossing
# =====================================================================
def fig_monotonic():
    W, H = 660, 380
    X0, X1 = 170.0, 590.0          # data x = 0 .. 2
    sx = (X1 - X0) / 2.0
    PYb, PYt = 320.0, 45.0         # data y = 0 .. 5.5
    sy = (PYb - PYt) / 5.5
    def X(x): return X0 + sx * x
    def Y(y): return PYb - sy * y

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Georgia,serif">']
    s.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>')

    # light gridlines
    for gx in [0.5, 1.0, 1.5, 2.0]:
        s.append(f'<line x1="{X(gx):.1f}" y1="{PYt}" x2="{X(gx):.1f}" y2="{PYb}" stroke="{GRID}" stroke-width="1"/>')
    for gy in range(1, 6):
        s.append(f'<line x1="{X0}" y1="{Y(gy):.1f}" x2="{X1}" y2="{Y(gy):.1f}" stroke="{GRID}" stroke-width="1"/>')

    # overlap band [3,4] across the plot
    s.append(f'<rect x="{X0}" y="{Y(4):.1f}" width="{X1-X0:.1f}" height="{Y(3)-Y(4):.1f}" fill="{GREENF}"/>')

    # axes
    s.append(f'<line x1="{X0}" y1="{PYb}" x2="{X1+22}" y2="{PYb}" stroke="{AXIS}" stroke-width="1.3"/>')
    s.append(f'<line x1="{X0}" y1="{PYb}" x2="{X0}" y2="{PYt-6}" stroke="{AXIS}" stroke-width="1.3"/>')
    # x ticks
    for xt in [0, 1, 2]:
        s.append(f'<line x1="{X(xt):.1f}" y1="{PYb}" x2="{X(xt):.1f}" y2="{PYb+5}" stroke="{AXIS}" stroke-width="1"/>')
        s.append(f'<text x="{X(xt):.1f}" y="{PYb+18}" font-size="11" fill="{LABEL}" text-anchor="middle" font-family="sans-serif">{xt}</text>')
    s.append(f'<text x="{X1+22}" y="{PYb+18}" font-size="12" fill="{LABEL}" text-anchor="middle" font-family="sans-serif">x</text>')
    # y ticks
    for yt in range(1, 6):
        s.append(f'<line x1="{X0-5}" y1="{Y(yt):.1f}" x2="{X0}" y2="{Y(yt):.1f}" stroke="{AXIS}" stroke-width="1"/>')
        s.append(f'<text x="{X0-9}" y="{Y(yt)+3.5:.1f}" font-size="10" fill="{LABEL}" text-anchor="end" font-family="sans-serif">{yt}</text>')

    # coloured range bars just inside the axis: f=[1,4] navy, g=[3,5] rust
    s.append(f'<line x1="{X0+7}" y1="{Y(1):.1f}" x2="{X0+7}" y2="{Y(4):.1f}" stroke="{NAVY}" stroke-width="4" stroke-linecap="round" opacity="0.9"/>')
    s.append(f'<line x1="{X0+15}" y1="{Y(3):.1f}" x2="{X0+15}" y2="{Y(5):.1f}" stroke="{RUST}" stroke-width="4" stroke-linecap="round" opacity="0.9"/>')
    s.append(f'<text x="{X0+2:.1f}" y="{Y(4)-5:.1f}" font-size="9.5" fill="{NAVY}" font-family="sans-serif">[1,4]</text>')
    s.append(f'<text x="{X0+20:.1f}" y="{Y(5)+1:.1f}" font-size="9.5" fill="{RUST}" font-family="sans-serif">[3,5]</text>')

    # increasing f(x)=2^x
    pts = " ".join(f"{X(x):.1f},{Y(2**x):.1f}" for x in [i/60*2 for i in range(61)])
    s.append(f'<polyline points="{pts}" fill="none" stroke="{NAVY}" stroke-width="2.6"/>')
    # decreasing g(x)=5-x
    s.append(f'<line x1="{X(0):.1f}" y1="{Y(5):.1f}" x2="{X(2):.1f}" y2="{Y(3):.1f}" stroke="{RUST}" stroke-width="2.6"/>')

    # endpoint markers
    for (x, fy, gy) in [(0, 1, 5), (2, 4, 3)]:
        s.append(f'<line x1="{X(x):.1f}" y1="{Y(fy):.1f}" x2="{X(x):.1f}" y2="{Y(gy):.1f}" stroke="{LABEL}" stroke-width="1" stroke-dasharray="3 3"/>')
        s.append(f'<circle cx="{X(x):.1f}" cy="{Y(fy):.1f}" r="3" fill="{NAVY}"/>')
        s.append(f'<circle cx="{X(x):.1f}" cy="{Y(gy):.1f}" r="3" fill="{RUST}"/>')
    # crossing point
    cx = 1.7156; cy = 5 - cx
    s.append(f'<line x1="{X(cx):.1f}" y1="{PYb}" x2="{X(cx):.1f}" y2="{Y(cy):.1f}" stroke="{GREEN}" stroke-width="1" stroke-dasharray="3 3"/>')
    s.append(f'<line x1="{X0}" y1="{Y(cy):.1f}" x2="{X(cx):.1f}" y2="{Y(cy):.1f}" stroke="{GREEN}" stroke-width="1" stroke-dasharray="3 3"/>')
    s.append(f'<circle cx="{X(cx):.1f}" cy="{Y(cy):.1f}" r="4.2" fill="none" stroke="{GREEN}" stroke-width="2"/>')
    s.append(f'<line x1="{X(cx)+4:.1f}" y1="{Y(cy)-3:.1f}" x2="{W-22}" y2="124" stroke="{GREEN}" stroke-width="0.9"/>')
    s.append(f'<text x="{W-15}" y="120" font-size="11" fill="{GREEN}" text-anchor="end" font-family="sans-serif">exactly one solution (x ≈ 1.72)</text>')

    # overlap annotation (empty left portion of the green band)
    s.append(f'<text x="{X(0.30):.1f}" y="{Y(3.5)+4:.1f}" font-size="11" fill="{GREEN}" font-family="sans-serif">ranges overlap on [3, 4] → curves must cross</text>')

    # legend (top-left inside plot)
    lx, ly = X0 + 40, PYt + 8
    s.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+26}" y2="{ly}" stroke="{NAVY}" stroke-width="2.8"/>')
    s.append(f'<text x="{lx+32}" y="{ly+4}" font-size="12" fill="{NAVY}" font-family="sans-serif">y = 2ˣ  (increasing)</text>')
    s.append(f'<line x1="{lx+170}" y1="{ly}" x2="{lx+196}" y2="{ly}" stroke="{RUST}" stroke-width="2.8"/>')
    s.append(f'<text x="{lx+202}" y="{ly+4}" font-size="12" fill="{RUST}" font-family="sans-serif">y = 5 − x  (decreasing)</text>')

    s.append('</svg>')
    return "\n".join(s)

# =====================================================================
# FIGURE 2 — the ambiguous (SSA) case: two triangles
# =====================================================================
def fig_ssa():
    W, H = 620, 340
    Ax, Ay = 70.0, 250.0
    sc = 36.0
    A_deg = 30.0
    b, a = 8.0, 5.0
    Ar = math.radians(A_deg)
    def P(x, y): return (Ax + sc*x, Ay - sc*y)  # data->screen

    Cx, Cy = P(b*math.cos(Ar), b*math.sin(Ar))       # apex C
    h = b*math.sin(Ar)                                # = 4
    root = math.sqrt(a*a - h*h)                       # = 3
    b1x = b*math.cos(Ar) - root                       # nearer foot (obtuse tri)
    b2x = b*math.cos(Ar) + root                       # farther foot (acute tri)
    B1 = P(b1x, 0); B2 = P(b2x, 0); F = P(b*math.cos(Ar), 0)

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Georgia,serif">']
    s.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>')

    # baseline (arm 2) with arrowhead
    bx_end = P(11.6, 0)[0]
    s.append(f'<line x1="{P(-0.4,0)[0]:.1f}" y1="{Ay}" x2="{bx_end:.1f}" y2="{Ay}" stroke="{AXIS}" stroke-width="1.6"/>')
    s.append(f'<polygon points="{bx_end:.1f},{Ay} {bx_end-9:.1f},{Ay-4:.1f} {bx_end-9:.1f},{Ay+4:.1f}" fill="{AXIS}"/>')

    # compass-swing arc (circle centred C, radius a), sampled a little beyond B1..B2
    r_px = a*sc
    ph1 = math.atan2(B1[1]-Cy, B1[0]-Cx)   # ~127 deg (screen, y-down)
    ph2 = math.atan2(B2[1]-Cy, B2[0]-Cx)   # ~53 deg
    a_lo, a_hi = min(ph1, ph2)-0.16, max(ph1, ph2)+0.16
    arc = []
    n = 80
    for i in range(n+1):
        t = a_lo + (a_hi-a_lo)*i/n
        arc.append(f"{Cx + r_px*math.cos(t):.1f},{Cy + r_px*math.sin(t):.1f}")
    s.append(f'<polyline points="{" ".join(arc)}" fill="none" stroke="{LABEL}" stroke-width="1.2" stroke-dasharray="4 4"/>')
    s.append(f'<text x="{Cx-150:.1f}" y="{Ay+34:.1f}" font-size="11" fill="{LABEL}" font-family="sans-serif">arc of radius a — the compass swing</text>')

    # side b (A->C), navy
    s.append(f'<line x1="{Ax:.1f}" y1="{Ay:.1f}" x2="{Cx:.1f}" y2="{Cy:.1f}" stroke="{NAVY}" stroke-width="2.6"/>')
    # side a, triangle 2 (acute) C->B2, rust
    s.append(f'<line x1="{Cx:.1f}" y1="{Cy:.1f}" x2="{B2[0]:.1f}" y2="{B2[1]:.1f}" stroke="{RUST}" stroke-width="2.6"/>')
    # side a, triangle 1 (obtuse) C->B1, green
    s.append(f'<line x1="{Cx:.1f}" y1="{Cy:.1f}" x2="{B1[0]:.1f}" y2="{B1[1]:.1f}" stroke="{GREEN}" stroke-width="2.6"/>')

    # height h (dashed) + right-angle mark
    s.append(f'<line x1="{Cx:.1f}" y1="{Cy:.1f}" x2="{F[0]:.1f}" y2="{F[1]:.1f}" stroke="{AXIS}" stroke-width="1" stroke-dasharray="3 3"/>')
    ra = 8
    s.append(f'<path d="M {F[0]-ra:.1f} {F[1]:.1f} L {F[0]-ra:.1f} {F[1]-ra:.1f} L {F[0]:.1f} {F[1]-ra:.1f}" fill="none" stroke="{AXIS}" stroke-width="1"/>')
    s.append(f'<text x="{(Cx+F[0])/2+6:.1f}" y="{(Cy+F[1])/2:.1f}" font-size="11" fill="{AXIS}" font-family="sans-serif">h = b sin A = 4</text>')

    # angle A arc + label
    ar = 30
    p_start = (Ax+ar, Ay)
    p_end = (Ax+ar*math.cos(Ar), Ay-ar*math.sin(Ar))
    s.append(f'<path d="M {p_start[0]:.1f} {p_start[1]:.1f} A {ar} {ar} 0 0 0 {p_end[0]:.1f} {p_end[1]:.1f}" fill="none" stroke="{AXIS}" stroke-width="1.2"/>')
    s.append(f'<text x="{Ax+40:.1f}" y="{Ay-14:.1f}" font-size="11.5" fill="{AXIS}" font-family="sans-serif">A = 30°</text>')

    # vertex labels & points
    s.append(f'<circle cx="{Ax:.1f}" cy="{Ay:.1f}" r="3.2" fill="{AXIS}"/>')
    s.append(f'<text x="{Ax-14:.1f}" y="{Ay+16:.1f}" font-size="13" fill="{AXIS}" font-family="sans-serif">A</text>')
    s.append(f'<circle cx="{Cx:.1f}" cy="{Cy:.1f}" r="3.2" fill="{NAVY}"/>')
    s.append(f'<text x="{Cx+7:.1f}" y="{Cy-4:.1f}" font-size="13" fill="{NAVY}" font-family="sans-serif">C</text>')
    s.append(f'<circle cx="{B1[0]:.1f}" cy="{B1[1]:.1f}" r="3.2" fill="{GREEN}"/>')
    s.append(f'<text x="{B1[0]-4:.1f}" y="{B1[1]+18:.1f}" font-size="12.5" fill="{GREEN}" font-family="sans-serif">B₁</text>')
    s.append(f'<circle cx="{B2[0]:.1f}" cy="{B2[1]:.1f}" r="3.2" fill="{RUST}"/>')
    s.append(f'<text x="{B2[0]-4:.1f}" y="{B2[1]+18:.1f}" font-size="12.5" fill="{RUST}" font-family="sans-serif">B₂</text>')

    # side labels
    s.append(f'<text x="{(Ax+Cx)/2-16:.1f}" y="{(Ay+Cy)/2-4:.1f}" font-size="12" fill="{NAVY}" font-family="sans-serif">b = 8</text>')
    s.append(f'<text x="{(Cx+B2[0])/2+4:.1f}" y="{(Cy+B2[1])/2-2:.1f}" font-size="12" fill="{RUST}" font-family="sans-serif">a = 5</text>')
    s.append(f'<text x="{(Cx+B1[0])/2-30:.1f}" y="{(Cy+B1[1])/2:.1f}" font-size="12" fill="{GREEN}" font-family="sans-serif">a = 5</text>')

    # legend of the two triangles
    lx, ly = 360, 40
    s.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+24}" y2="{ly}" stroke="{RUST}" stroke-width="2.8"/>')
    s.append(f'<text x="{lx+30}" y="{ly+4}" font-size="12" fill="{RUST}" font-family="sans-serif">triangle AB₂C  (B acute)</text>')
    s.append(f'<line x1="{lx}" y1="{ly+20}" x2="{lx+24}" y2="{ly+20}" stroke="{GREEN}" stroke-width="2.8"/>')
    s.append(f'<text x="{lx+30}" y="{ly+24}" font-size="12" fill="{GREEN}" font-family="sans-serif">triangle AB₁C  (B obtuse)</text>')

    s.append('</svg>')
    return "\n".join(s)

open("img/fig-monotonic.svg", "w").write(fig_monotonic())
open("img/fig-ssa.svg", "w").write(fig_ssa())
print("wrote img/fig-monotonic.svg and img/fig-ssa.svg")
