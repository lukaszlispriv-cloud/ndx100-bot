## A. P(kill) dla B_cap05 i B — dodatkowe polityki (bootstrap blokowy, 4000 ścieżek, koszty wliczone)

| konstrukcja | skład | polityka | alfa | P(kill 12) | P(kill 26) | P(kill 52) |
|---|---|---|---|---|---|---|
| B_cap05 | PIT | fix:0.10 | 0 | 0.1% | 3.1% | 19.1% |
| B_cap05 | PIT | fix:0.10 | in-sample | 0.0% | 0.7% | 7.5% |
| B_cap05 | PIT | fix:0.10 + soft −10% | 0 | 0.0% | 0.1% | 2.1% |
| B_cap05 | PIT | fix:0.10 + soft −10% | in-sample | 0.0% | 0.0% | 0.3% |
| B_cap05 | PIT | fix:0.08 + soft −10% | 0 | 0.0% | 0.0% | 0.2% |
| B_cap05 | PIT | fix:0.08 + soft −10% | in-sample | 0.0% | 0.0% | 0.0% |
| B_cap05 | PIT | vt (cel 1.0%/d) | 0 | 0.0% | 2.5% | 21.8% |
| B_cap05 | PIT | vt (cel 1.0%/d) | in-sample | 0.0% | 1.2% | 8.2% |
| B_cap05 | PIT | vt (cel 1.0%/d) + soft −10% | 0 | 0.0% | 0.0% | 2.3% |
| B_cap05 | PIT | vt (cel 1.0%/d) + soft −10% | in-sample | 0.0% | 0.0% | 0.4% |
| B_cap05 | dzis | fix:0.10 | 0 | 0.0% | 3.5% | 23.1% |
| B_cap05 | dzis | fix:0.10 | in-sample | 0.0% | 0.3% | 3.1% |
| B_cap05 | dzis | fix:0.10 + soft −10% | 0 | 0.0% | 0.0% | 2.1% |
| B_cap05 | dzis | fix:0.10 + soft −10% | in-sample | 0.0% | 0.0% | 0.1% |
| B_cap05 | dzis | fix:0.08 + soft −10% | 0 | 0.0% | 0.0% | 0.2% |
| B_cap05 | dzis | fix:0.08 + soft −10% | in-sample | 0.0% | 0.0% | 0.0% |
| B_cap05 | dzis | vt (cel 1.0%/d) | 0 | 0.1% | 4.2% | 25.8% |
| B_cap05 | dzis | vt (cel 1.0%/d) | in-sample | 0.0% | 0.4% | 2.7% |
| B_cap05 | dzis | vt (cel 1.0%/d) + soft −10% | 0 | 0.0% | 0.0% | 3.4% |
| B_cap05 | dzis | vt (cel 1.0%/d) + soft −10% | in-sample | 0.0% | 0.0% | 0.0% |
| B | PIT | fix:0.10 | 0 | 0.2% | 4.9% | 23.4% |
| B | PIT | fix:0.10 | in-sample | 0.2% | 2.2% | 12.4% |
| B | PIT | fix:0.10 + soft −10% | 0 | 0.0% | 0.1% | 3.5% |
| B | PIT | fix:0.10 + soft −10% | in-sample | 0.0% | 0.1% | 1.5% |
| B | PIT | fix:0.08 + soft −10% | 0 | 0.0% | 0.0% | 0.8% |
| B | PIT | fix:0.08 + soft −10% | in-sample | 0.0% | 0.0% | 0.1% |
| B | PIT | vt (cel 1.0%/d) | 0 | 0.0% | 1.6% | 17.2% |
| B | PIT | vt (cel 1.0%/d) | in-sample | 0.0% | 0.5% | 6.5% |
| B | PIT | vt (cel 1.0%/d) + soft −10% | 0 | 0.0% | 0.0% | 1.3% |
| B | PIT | vt (cel 1.0%/d) + soft −10% | in-sample | 0.0% | 0.0% | 0.4% |
| B | dzis | fix:0.10 | 0 | 0.4% | 6.0% | 28.0% |
| B | dzis | fix:0.10 | in-sample | 0.1% | 0.8% | 4.2% |
| B | dzis | fix:0.10 + soft −10% | 0 | 0.0% | 0.1% | 4.7% |
| B | dzis | fix:0.10 + soft −10% | in-sample | 0.0% | 0.0% | 0.2% |
| B | dzis | fix:0.08 + soft −10% | 0 | 0.0% | 0.0% | 0.8% |
| B | dzis | fix:0.08 + soft −10% | in-sample | 0.0% | 0.0% | 0.1% |
| B | dzis | vt (cel 1.0%/d) | 0 | 0.1% | 4.0% | 25.7% |
| B | dzis | vt (cel 1.0%/d) | in-sample | 0.0% | 0.4% | 1.8% |
| B | dzis | vt (cel 1.0%/d) + soft −10% | 0 | 0.0% | 0.1% | 3.2% |
| B | dzis | vt (cel 1.0%/d) + soft −10% | in-sample | 0.0% | 0.0% | 0.1% |

## B. Moc testu F (σ_B/σ_A) na koszykach cieniach — bootstrap par tygodni (A, B_cap05) PIT

| tygodni | P(F-test p<0,05) | P(σ-ratio < 0,85) | mediana σ-ratio | p5–p95 σ-ratio | P(sparowany t(Δ) < −2) |
|---|---|---|---|---|---|
| 12 | 22% | 68% | 0.72 | 0.40–1.24 | 3.5% |
| 26 | 47% | 80% | 0.69 | 0.47–1.03 | 3.7% |
| 52 | 74% | 90% | 0.68 | 0.52–0.91 | 4.1% |

σ sparowanej różnicy B_cap05 − A (PIT): 5.21 p.p./tydz.; tygodni do t=2 przy prawdziwej Δ 0,3 / 0,5 / 1,0 p.p.: 1204 / 433 / 108

## C. Wrażliwość B_cap05 na definicję grupy (skład PIT i dzisiejszy)

| definicja | skład | n | śr. | σ | Sharpe | Δ vs A | t(Δ) | σ-ratio | b_SOX zreal. | najgorszy |
|---|---|---|---|---|---|---|---|---|---|---|
| base industry≥4|sector, grupa≥3 | PIT | 209 | +0.38 | 4.61 | 0.60 | -0.21 | -0.58 | 0.669 | +0.31 | -12.7 |
| base industry≥4|sector, grupa≥3 | dzis | 209 | +0.82 | 5.05 | 1.17 | -0.12 | -0.35 | 0.735 | +0.27 | -13.4 |
| industry≥2|sector | PIT | 209 | +0.27 | 4.23 | 0.46 | -0.33 | -0.86 | 0.614 | +0.20 | -14.2 |
| industry≥2|sector | dzis | 209 | +0.39 | 4.50 | 0.62 | -0.56 | -1.38 | 0.654 | +0.16 | -12.8 |
| industry≥6|sector | PIT | 209 | +0.41 | 4.67 | 0.63 | -0.19 | -0.52 | 0.679 | +0.34 | -13.3 |
| industry≥6|sector | dzis | 209 | +0.54 | 4.78 | 0.82 | -0.40 | -1.18 | 0.695 | +0.23 | -12.8 |
| grupa≥5 | PIT | 209 | +0.30 | 4.08 | 0.54 | -0.29 | -0.76 | 0.592 | +0.15 | -11.4 |
| grupa≥5 | dzis | 209 | +0.77 | 5.24 | 1.06 | -0.18 | -0.47 | 0.762 | +0.05 | -13.2 |
| sector-only | PIT | 209 | +0.23 | 4.36 | 0.37 | -0.37 | -1.03 | 0.633 | +0.23 | -10.9 |
| sector-only | dzis | 209 | +0.55 | 4.58 | 0.86 | -0.40 | -1.14 | 0.667 | +0.21 | -12.8 |
