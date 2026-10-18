"""(e) Koszty CFD przy gross 240% (10 nóg × 24%) — roczny drag. ZAŁOŻENIA (typowe stawki Capital.com dla CFD na akcje USA,
podane jako parametry; właściciel może je podmienić):
 - spread: zmierzony w audycie 28.09 (eksport brokera, 63 pary zamknij/otwórz w tej samej sekundzie):
   AVGO 0,088%, SBUX 0,328%, CMCSA 0,312% na parę; średnia ważona ok. 0,19% na parę (= pełny round-trip);
   tu: SPREAD_RT = 0,19% (środek), wariant 0,10% / 0,30%.
 - finansowanie overnight: Capital.com liczy dziennie od wartości pozycji: long ≈ (stopa referencyjna USD + marża),
   short ≈ (marża − stopa referencyjna) — przy stopie ref. ~4,0% i marży ~2,5–3,0%: long 6,5–7,0%/rok, short ≈ 0…−1,5%/rok
   (short może być kosztem, jeśli marża > stopa ref.). Przyjęto: LONG_FIN = 7,0%, SHORT_FIN = 1,0% (koszt), warianty.
   Capital.com nalicza 1 dzień pn–czw i 3 dni w piątek (weekend) → 365 dni/rok kalendarzowych na pozycję trzymaną ciągle.
 - dywidendy: short CFD płaci 100% dywidendy brutto (korekta gotówkowa w ex-date), long otrzymuje ok. 70% (podatek u źródła
   dla nierezydenta 30%; na DEMO brak podatku) — tu: long dostaje 100% (demo) / 70% (live).
   Stopa dywidendy shortów defensywnych (PEP ~4,3%, CMCSA ~5,9% przy kursie 21, SBUX ~2,6%, TMUS ~2,3%, APP 0, NFLX 0, PAYX ~3,0%)
   — średnia koszyka short W5–W7 ≈ 2,8%/rok; longi (MU 0,07%, CSCO ~3%, inne ~0) ≈ 0,4%.
 - rotacja: udział nóg wymienianych co tydzień: W5 7/10, W6 6/10, W7 5/10, W8 9/10 → śr. ~0,68 → 6,8 nóg × round-trip tygodniowo;
   stopy + ponowne otwarcia: W7 4 stopy i 3 reopen = +3,5 round-tripów; wyrównania 17:05: audyt 28.09 → 1,1% kapitału/mies.
   przy gross ~90% (przed podwojeniem); po REBALANCE_HOURS=17 i MIN_REBALANCE_ACC=25 przyjęto połowę: 0,55%/mies. przy gross 90%,
   skalowane do gross 240% → ~1,5%/mies. (górne), 0,5%/mies. (dolne, bo pasmo 0,30 rzadziej wyzwala przy większych pozycjach).
"""
GROSS = 2.40; LONG_EXP = 1.20; SHORT_EXP = 1.20

def drag(spread_rt=0.0019, long_fin=0.070, short_fin=0.010, div_short=0.028, div_long=0.004, long_div_keep=1.0,
         rot_legs=6.8, extra_rt_per_week=0.7, rebal_month=0.010, weeks=52):
    leg = 0.24
    spread_rot = rot_legs * leg * spread_rt * weeks            # rotacje: nowa noga wchodzi i stara wychodzi = 1 RT na wymianę
    spread_stop = extra_rt_per_week * leg * spread_rt * weeks  # stopy/reopen (W7: 3,5 RT; średnio mniej)
    rebal = rebal_month * 12
    fin = LONG_EXP * long_fin + SHORT_EXP * short_fin
    div = SHORT_EXP * div_short - LONG_EXP * div_long * long_div_keep
    return dict(spread_rotacje=spread_rot, spread_stopy=spread_stop, wyrownania=rebal, finansowanie=fin, dywidendy_netto=div,
                razem=spread_rot + spread_stop + rebal + fin + div)

for name, kw in [("środek", {}),
                 ("dolne (spread 0,10%, long fin 6%, short fin 0, rebal 0,5%/m, stopy 0,3 RT/tyg)",
                  dict(spread_rt=0.0010, long_fin=0.06, short_fin=0.0, rebal_month=0.005, extra_rt_per_week=0.3)),
                 ("górne (spread 0,30%, long fin 7,5%, short fin 2%, rebal 1,5%/m, stopy 1,5 RT/tyg, live 70% dyw.)",
                  dict(spread_rt=0.0030, long_fin=0.075, short_fin=0.02, rebal_month=0.015, extra_rt_per_week=1.5, long_div_keep=0.7)),
                 ("środek przy ALLOC 0,12 (gross 120%)", dict())]:
    if "0,12" in name:
        LONG_EXP = SHORT_EXP = 0.60
        d = drag(**kw); d = {k: v / 2 if k.startswith("spread") or k == "wyrownania" else v for k, v in d.items()}
        d["razem"] = sum(v for k, v in d.items() if k != "razem")
        LONG_EXP = SHORT_EXP = 1.20
    else:
        d = drag(**kw)
    print(f"--- {name} ---")
    for k, v in d.items():
        print(f"  {k:18}{100*v:7.2f} % kapitału / rok  ({100*v/52:5.3f} %/tydz.)")
d0 = drag()
print(f"\nPorównanie: 1 p.p. spread_pp (= śr. long − śr. short, 5+5 nóg po 24%) = 5×0,24 = 1,2% kapitału. Drag 'środek' "
      f"{100*d0['razem']/52:.2f}%/tydz. kapitału = {100*d0['razem']/52/1.2:.2f} p.p. spreadu tygodniowo; skumulowany spread W1–W7 = −3,67 p.p. "
      f"na 7 tyg. (−0,52 p.p./tydz.). Przy sd spreadu ~7 p.p./tydz. wykrycie przewagi {100*d0['razem']/52/1.2:.2f} p.p. wymaga ~{(1.96*7/(d0['razem']/52*100/1.2))**2:.0f} tygodni.")
