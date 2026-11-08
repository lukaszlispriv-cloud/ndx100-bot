# Godzina wejścia — wpisy fills (historia gita) vs zamknięcia (08.11.2026)

Wpisy fills z kursami: 126 (unikalne ticker/data/kierunek/cena; wyrównania wielkości tego samego dnia liczone osobno). Zakres: 2026-08-27 … 2026-11-02.

Obserwacje odstające (|koszt| > 8 %, prawdopodobnie korekta kursu/split w źródle — wyłączone z wariantu „bez odstających”): FER 2026-10-19 (+11.7 %)

| próba | koszt wejścia vs zamknięcie dnia (>0 = gorzej) | vs poprzednie zamknięcie (opóźnienie D0 → wejście) |
|---|---|---|
| wszystkie | śr +0.22 % · med +0.10 % · σ 1.64 · t 1.54 · n = 126 · gorsze niż odniesienie: 69/126 | śr +0.30 % · med +0.24 % · σ 2.42 · t 1.37 · n = 126 · gorsze niż odniesienie: 72/126 |
| bez odstających | śr +0.13 % · med +0.08 % · σ 1.28 · t 1.16 · n = 125 · gorsze niż odniesienie: 68/125 | śr +0.20 % · med +0.24 % · σ 2.19 · t 1.03 · n = 125 · gorsze niż odniesienie: 71/125 |
| poniedziałki (rotacja), bez odst. | śr +0.27 % · med +0.10 % · σ 1.53 · t 1.34 · n = 56 · gorsze niż odniesienie: 29/56 | śr +0.05 % · med +0.02 % · σ 2.19 · t 0.18 · n = 56 · gorsze niż odniesienie: 28/56 |
| pozostałe dni (wyrównania/dopełnienia), bez odst. | śr +0.02 % · med +0.08 % · σ 1.03 · t 0.14 · n = 69 · gorsze niż odniesienie: 39/69 | śr +0.32 % · med +0.51 % · σ 2.20 · t 1.22 · n = 69 · gorsze niż odniesienie: 43/69 |
| BUY, bez odst. | śr -0.02 % · med -0.06 % · σ 1.43 · t -0.09 · n = 55 · gorsze niż odniesienie: 26/55 | śr -0.15 % · med -0.03 % · σ 2.59 · t -0.43 · n = 55 · gorsze niż odniesienie: 26/55 |
| SELL, bez odst. | śr +0.25 % · med +0.17 % · σ 1.14 · t 1.82 · n = 70 · gorsze niż odniesienie: 42/70 | śr +0.48 % · med +0.54 % · σ 1.78 · t 2.25 · n = 70 · gorsze niż odniesienie: 45/70 |

Przełożenie na koszyk: +0.13 % na nogę × gross 0,8 kapitału ≈ +0.11 % kapitału na rotację, czyli ok. +0.26 pp spreadu (gross 2) — rząd kosztów transakcyjnych przyjętych w analizie 18.10 (0,27 pp/tydz.), nie rząd luki wykonania z W10 (ok. 2 pp kapitału, stopy + wyłącznik P2).

Uwaga: zamknięcie dnia nie jest ceną osiągalną (bot nie handluje na zamknięciu); test mierzy tylko, czy pierwszy kwadrans sesji jest systematycznie drogi. Kurs otwarcia nie jest dostępny w closes_5y.csv.
