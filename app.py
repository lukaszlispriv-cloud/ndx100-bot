# -*- coding: utf-8 -*-
"""
BASKET BOT v1.8.1 — PEŁNY AUTOMAT (uniwersum z mapy epics: WIG20 / Nasdaq-100 / dowolne) (hedge indeksowy dla kont LONG_ONLY) (DEMO/LIVE z bezpiecznikiem) (eksperyment naukowy, konto DEMO)
=======================================================================
Nowość vs v1.0: bot sam generuje rekomendacje i raporty (API Anthropic
z wyszukiwaniem internetowym), sam commit'uje signals.json + raport HTML
do GitHuba i sam zapisuje podsumowanie biegu w logu. Człowiek nic nie
podmienia.

OBIEG DOBOWY (sterowany z cron-job.org):
  pn–pt 8:10  -> /generate?mode=daily   (puls: status + ew. wykluczenia,
                                         raport HTML ~8:30)
  pn–pt 9:15  -> /run                   (synchronizacja pozycji na demo)
  pn–pt 13:05 -> /run                   (bieg doganiający, opcjonalny)
  sobota 8:30 -> /generate?mode=weekly  (rozliczenie tygodnia + nowe koszyki)
  poniedziałek 9:15 -> /run             (rotacja koszyków)

PROTOKÓŁ DECYZJI DZIENNYCH (co puls może zrobić z pozycjami):
  * status NIEAKTUALNA        -> /run zamyka WSZYSTKO i czeka płasko;
  * exclude action=CLOSE      -> /run zamyka pozycję (twarde wyzwalacze:
                                  wezwanie, zawieszenie, szok wynikowy,
                                  ruch >8% przeciw tezie, upadek filaru tezy);
  * exclude action=REDUCE     -> /run tnie pozycję do połowy (miękkie
                                  wyzwalacze: ruch 4-8% przeciw tezie,
                                  rekomendacja przeciw tezie, short KNF
                                  +0,3 p.p.); raz zredukowana zostaje
                                  zredukowana do soboty (bez podnoszenia),
                                  a po sobotniej rotacji — gdy wpis exclude
                                  znika — wielkość wraca do pełnej wagi;
  * koszyków puls nie zmienia i kierunków nie odwraca — rotacje robi
    wyłącznie raport sobotni (falsyfikowalność deklaracji tygodniowych
    zostaje nienaruszona; wykluczenia są logowane w commitach);
  * MODUŁ TAKTYCZNY (v1.2): puls może otworzyć maks. TACTICAL_MAX
    dodatkowych pozycji (połowa wielkości) na TWARDE świeże wyzwalacze
    spółek SPOZA koszyków (np. wynik mocno powyżej konsensusu, przełomowy
    kontrakt, wezwanie) — rozliczane OSOBNO od koszyków i kasowane przy
    sobotniej rotacji; zwykle lista jest pusta.

NOWE W v1.8.0 (po rozliczeniu okresu 27.08-18.09.2026, gdzie cztery
reakcje cenowe kosztowały 17,43 USD, a REDUCE dla MU po cichu się nie
wykonał):
  * BRAMKA WYZWALACZY CENOWYCH — wpis exclude o podstawie cenowej jest
    sprawdzany wobec FAKTYCZNEJ ceny wejścia u brokera, nie wobec kursu
    odniesienia D0 z raportu. Bramka wyłącznie łagodzi (CLOSE -> REDUCE
    -> brak) i nigdy nie dokłada reakcji. Wpisy reżimowe i te o podstawie
    "news"/"rekom"/"short" przechodzą bez sprawdzania. REACT_GATE=false
    przywraca stare zachowanie.
  * CENY WEJŚCIA w signals.json (pole "fills") — bot po każdym biegu
    zapisuje, po ile naprawdę wszedł; to źródło prawdy dla bramki i dla
    raportu dziennego.
  * KONTROLA KAPITAŁU — equity z API (balance + profitLoss) jest
    porównywane z sumą upl pozycji, które bot zna. Rozjazd albo pozycja
    spoza książki oznacza alert i zejście z ALLOC_PCT na ALLOC_PCT_SAFE.
  * TWARDY STOP od ceny wejścia (STOP_LOSS_PCT) — siatka niezależna od
    logiki tygodniowej; wcześniej STX spadł o 13% w cztery sesje i żaden
    wyzwalacz nie zadziałał, bo progi mierzono od D0.
  * KILL SWITCH od KROCZĄCEGO SZCZYTU kapitału (KILL_TRAILING), a nie od
    stałej START_EQUITY, która rozluźniała próg z każdym zarobkiem.
  * RYNEK ZAMKNIĘTY TO NIE BŁĄD — weekend i przerwa w notowaniach idą do
    "pominiete"; w "błędach" zostają tylko awarie wymagające reakcji.
  * CICHE POMINIĘCIA ZNIKAJĄ — gdy minimalna wielkość transakcji nie
    pozwala zejść do celu po redukcji, bieg to raportuje (REDUCE_FALLBACK
    decyduje: zostawić pełną pozycję czy zamknąć całość).
  * POZYCJA TAKTYCZNA MOŻE MIEĆ WŁASNY EPIC spoza uniwersum koszyków.
  * CACHE MIGAWEK RYNKU na czas jednego biegu.

NOWE W v1.8.1: usunięta nieużywana integracja z Telegramem — powiadomienia
idą wyłącznie do logu usługi (linie "NOTIFY:") i do odpowiedzi endpointu.

BEZPIECZNIKI: DRY_RUN (handel), commit=false (generator), walidacja JSON
z modelu (błędny wynik => zostaje stary plik + alert, bot nie gra na
śmieciach), kill switch kapitału, tylko instrumenty z mapy "epics".
Wielkości pozycji liczone w WALUCIE RACHUNKU (PLN lub USD) — konto demo
może być prowadzone w PLN; kurs USD/PLN używany tylko przy różnych walutach.
Materiał badawczo-edukacyjny. Nie jest poradą inwestycyjną.
"""

import os
import re
import json
import math
import time
import base64
import logging
from datetime import datetime, timezone, date

import requests
from flask import Flask, request, jsonify

# ----------------------------------------------------------------------------
# KONFIGURACJA
# ----------------------------------------------------------------------------
CAPITAL_API_KEY  = os.environ.get("CAPITAL_API_KEY", "")
CAPITAL_IDENT    = os.environ.get("CAPITAL_IDENTIFIER", "")
CAPITAL_PASSWORD = os.environ.get("CAPITAL_PASSWORD", "")
CAPITAL_DEMO     = os.environ.get("CAPITAL_DEMO", "true").lower() == "true"
# Bezpiecznik LIVE (Etap 13): na rachunku rzeczywistym handel rusza wyłącznie
# po ustawieniu LIVE_POTWIERDZENIE=ROZUMIEM-RYZYKO. Chroni przed przypadkowym
# uzbrojeniem po samej zmianie CAPITAL_DEMO/kluczy.
LIVE_POTWIERDZENIE = os.environ.get("LIVE_POTWIERDZENIE", "").strip().upper()
LIVE_ODBLOKOWANY   = CAPITAL_DEMO or LIVE_POTWIERDZENIE == "ROZUMIEM-RYZYKO"
ACCOUNT_ID       = os.environ.get("CAPITAL_ACCOUNT_ID", "")

RUN_TOKEN        = os.environ.get("RUN_TOKEN", "zmien-ten-token")
DRY_RUN          = os.environ.get("DRY_RUN", "true").lower() == "true"
ALLOC_PCT        = float(os.environ.get("ALLOC_PCT", "0.13"))
# Wielkość awaryjna: używana, gdy KONTROLA KAPITAŁU nie przechodzi (na
# rachunku są pozycje spoza książki albo equity nie zgadza się z sumą upl).
# Nie skalujemy pozycji na portfelu, którego nie potrafimy odtworzyć.
ALLOC_PCT_SAFE   = float(os.environ.get("ALLOC_PCT_SAFE", "0.10"))
MAX_OVERSHOOT    = float(os.environ.get("MAX_OVERSHOOT", "1.6"))
START_EQUITY     = float(os.environ.get("START_EQUITY", "1000"))
KILL_LEVEL       = float(os.environ.get("KILL_LEVEL", "0.75"))
# Kill switch liczony od KROCZĄCEGO SZCZYTU kapitału (zapisywanego w
# signals.json), a nie od stałej START_EQUITY. Przy stałej próg rozluźniał
# się z każdym zarobionym dolarem: po wzroście kapitału do 1100 USD próg
# 0,75 x 1000 = 750 oznaczał dopuszczalne obsunięcie -32%, nie -25%.
KILL_TRAILING    = os.environ.get("KILL_TRAILING", "true").lower() == "true"
# Tolerancja KONTROLI KAPITAŁU: dopuszczalna różnica między profitLoss
# z rachunku a sumą upl pozycji zarządzanych, jako ułamek kapitału.
EQUITY_TOL       = float(os.environ.get("EQUITY_TOL", "0.02"))
FX_EPIC          = os.environ.get("FX_EPIC", "USDPLN")
FX_FALLBACK      = float(os.environ.get("FX_FALLBACK", "3.68"))

# --- GitHub jako "pamięć" systemu (sygnały + raporty + dziennik commitów)
GITHUB_TOKEN     = os.environ.get("GITHUB_TOKEN", "")       # fine-grained PAT
GITHUB_REPO      = os.environ.get("GITHUB_REPO", "")        # np. "lukasz/wig20-bot"
GITHUB_BRANCH    = os.environ.get("GITHUB_BRANCH", "main")
SIGNALS_PATH     = os.environ.get("SIGNALS_PATH", "signals.json")
REPORTS_DIR      = os.environ.get("REPORTS_DIR", "reports")
PAGES_BASE       = os.environ.get("PAGES_BASE", "")         # np. https://lukasz.github.io/wig20-bot

# --- Mózg: API Anthropic (puls i raport mogą używać RÓŻNYCH modeli)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
_MODEL_FALLBACK   = os.environ.get("ANTHROPIC_MODEL", "")
ANTHROPIC_MODEL_DAILY  = os.environ.get("ANTHROPIC_MODEL_DAILY",
                                        _MODEL_FALLBACK or "claude-sonnet-4-6")
ANTHROPIC_MODEL_WEEKLY = os.environ.get("ANTHROPIC_MODEL_WEEKLY",
                                        _MODEL_FALLBACK or "claude-fable-5")
WEB_MAX_DAILY     = int(os.environ.get("WEB_MAX_DAILY", "8"))
WEB_MAX_WEEKLY    = int(os.environ.get("WEB_MAX_WEEKLY", "30"))

# --- Moduł taktyczny: dokładki w środku tygodnia (rozliczane OSOBNO)
TACTICAL_ENABLED   = os.environ.get("TACTICAL_ENABLED", "true").lower() == "true"
TACTICAL_ALLOC_PCT = float(os.environ.get("TACTICAL_ALLOC_PCT", "0.05"))
TACTICAL_MAX       = int(os.environ.get("TACTICAL_MAX", "2"))
REDUCE_FACTOR      = float(os.environ.get("REDUCE_FACTOR", "0.5"))
# --- Bramka wyzwalaczy cenowych --------------------------------------------
# Puls liczy ruch "od D0", czyli od kursu odniesienia z raportu tygodniowego.
# Portfel bywa składany 1-3 sesje po D0, więc cena wejścia potrafi się od D0
# różnić o kilka procent (15.09.2026: LITE wszedł po 842,25 przy D0 927,03 —
# wpis CLOSE za "ruch -9,92% od D0" zamknął pozycję, która wobec własnego
# wypełnienia była NA PLUSIE). Bramka weryfikuje każdy wyzwalacz CENOWY
# wobec faktycznej ceny otwarcia pozycji u brokera i przepuszcza go tylko
# wtedy, gdy próg jest przekroczony także tam.
REACT_GATE       = os.environ.get("REACT_GATE", "true").lower() == "true"
REACT_REDUCE_PCT = float(os.environ.get("REACT_REDUCE_PCT", "0.04"))
REACT_CLOSE_PCT  = float(os.environ.get("REACT_CLOSE_PCT", "0.08"))
# Co zrobić, gdy minimalna wielkość transakcji przekracza cel po redukcji
# (np. MU: cel 55 USD, minimum 0,1 akcji = 98 USD): "keep" zostawia pełną
# pozycję i zgłasza to w "pominiete", "close" zamyka ją w całości.
REDUCE_FALLBACK  = os.environ.get("REDUCE_FALLBACK", "keep").lower()
# Twardy stop bezpieczeństwa liczony od ceny wejścia, niezależny od logiki
# tygodniowej (STX: -13% w cztery sesje bez żadnej reakcji, bo próg 4-8%
# mierzono od D0, a pozycja weszła już po D0). 0 = wyłączony.
STOP_LOSS_PCT    = float(os.environ.get("STOP_LOSS_PCT", "0.10"))
# Zapis faktycznych cen wejścia do signals.json (pole "fills") — źródło
# prawdy dla bramki wyzwalaczy i dla raportu dziennego.
WRITE_FILLS      = os.environ.get("WRITE_FILLS", "true").lower() == "true"
# Pasmo tolerancji wyrównywania wielkości pozycji już otwartych. Poza pasmem
# pozycja jest docinana/dokładana do celu; w paśmie zostawiamy ją w spokoju,
# bo każde wyrównanie kosztuje drugi spread, a przy grubym kroku wielkości
# (0,1 akcji przy kursie 1000 USD) części odchyłek i tak nie da się usunąć.
REBALANCE_TOL      = float(os.environ.get("REBALANCE_TOL", "0.35"))
# OGRANICZNIK TEMPA: o ile najwyżej może urosnąć łączna ekspozycja brutto
# w jednym biegu. Bez niego podniesienie ALLOC_PCT albo zdjęcie kilku
# redukcji naraz potrafi podwoić książkę w ciągu jednej minuty (symulacja
# z 18.09.2026: 709 -> 1440 USD w jednym biegu). Z ogranicznikiem ta sama
# zmiana rozkłada się na kilka biegów i jest odwracalna.
MAX_EXPOSURE_STEP  = float(os.environ.get("MAX_EXPOSURE_STEP", "0.25"))

# Nazwa w powiadomieniach — bliźniacze boty (WIG20 / NDX100) piszą na ten sam
# czat, więc etykieta musi mówić, KTÓRY bot zadziałał.
BOT_NAME           = os.environ.get("BOT_NAME", "NDX100 BOT")

# --- Tryb shortów (konta LONG_ONLY): "" = klasyczne SELL na akcjach;
#     epic indeksu (np. z /search?q=wig20) = syntetyczny short przez indeks;
#     "OFF" = czysty long-only (świadoma ekspozycja kierunkowa).
HEDGE_EPIC  = os.environ.get("HEDGE_EPIC", "").strip()
HEDGE_RATIO = float(os.environ.get("HEDGE_RATIO", "1.0"))
HEDGE_TOL   = float(os.environ.get("HEDGE_TOL", "0.30"))
HEDGE_MODE  = ("classic" if not HEDGE_EPIC
               else ("off" if HEDGE_EPIC.upper() == "OFF" else "index"))

BASE_URL = ("https://demo-api-capital.backend-capital.com" if CAPITAL_DEMO
            else "https://api-capital.backend-capital.com")

WIG20 = ["ALIOR", "ALLEGRO", "BUDIMEX", "CDPROJEKT", "DINOPL", "ERSTEPL",
         "KETY", "KGHM", "KRUK", "LPP", "MBANK", "MODIVO", "PEKAO", "PEPCO",
         "PGE", "PKNORLEN", "PKOBP", "PZU", "TAURONPE", "ZABKA"]

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("wig20bot")
app = Flask(__name__)


def notify(text: str):
    """Jedyny kanał powiadomień to log usługi (Render -> Logs).

    Integracja z Telegramem została usunięta w v1.8.1 — nie była używana,
    a jej obecność sugerowała, że alert dociera gdzieś poza log. Dociera
    do logu i tylko do logu: szukaj linii zaczynających się od "NOTIFY:".
    Pełną treść ostatniego biegu zwraca też endpoint /run w polu JSON.
    """
    log.info("NOTIFY: %s", text)


# ----------------------------------------------------------------------------
# GITHUB — odczyt/zapis plików (pamięć trwała i dziennik naukowy)
# ----------------------------------------------------------------------------
GH_API = "https://api.github.com"


def gh_headers():
    return {"Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f"Bearer {GITHUB_TOKEN}"}


def gh_get_file(path):
    """Zwraca (treść, sha) albo (None, None) gdy plik nie istnieje."""
    r = requests.get(f"{GH_API}/repos/{GITHUB_REPO}/contents/{path}",
                     params={"ref": GITHUB_BRANCH}, headers=gh_headers(),
                     timeout=20)
    if r.status_code == 404:
        return None, None
    r.raise_for_status()
    j = r.json()
    return base64.b64decode(j["content"]).decode("utf-8"), j["sha"]


def gh_put_file(path, content_str, message, sha=None):
    body = {"message": message, "branch": GITHUB_BRANCH,
            "content": base64.b64encode(content_str.encode("utf-8")).decode()}
    if sha:
        body["sha"] = sha
    r = requests.put(f"{GH_API}/repos/{GITHUB_REPO}/contents/{path}",
                     headers=gh_headers(), json=body, timeout=30)
    r.raise_for_status()
    return r.json().get("commit", {}).get("sha", "")[:7]


def load_signals():
    raw, sha = gh_get_file(SIGNALS_PATH)
    if raw is None:
        raise RuntimeError(f"Brak pliku {SIGNALS_PATH} w repo {GITHUB_REPO}")
    sig = json.loads(raw)
    for k in ("version", "status", "long", "short", "epics"):
        if k not in sig:
            raise ValueError(f"signals.json: brak pola '{k}'")
    sig.setdefault("exclude", [])
    sig.setdefault("tactical", [])
    _sanity(sig)
    return sig, sha


def _sanity(sig):
    """Kontrola spójności — bot ODMAWIA handlu na zepsutym pliku (ważne,
    gdy signals.json pisze zadanie Cowork, a nie walidowany generator)."""
    L, S = list(sig["long"]), list(sig["short"])
    problemy = []
    if len(L) != 5 or len(S) != 5:
        problemy.append("koszyki muszą mieć po 5 spółek")
    if set(L) & set(S):
        problemy.append("long i short się pokrywają")
    for t in L + S:
        if t not in sig["epics"]:
            problemy.append(f"ticker spoza uniwersum (mapy epics): {t}")
    if sig["status"].upper()[:6] not in ("AKTUAL", "NIEAKT"):
        problemy.append(f"nieznany status: {sig['status']}")
    if not isinstance(sig.get("epics"), dict):
        problemy.append("brak mapy epics")
    for e in sig.get("exclude", []):
        if e.get("action", "CLOSE") not in ("CLOSE", "REDUCE"):
            problemy.append(f"złe action w exclude: {e}")
        podstawa = e.get("basis")
        if podstawa is not None and str(podstawa).lower() not in (
                "cena", "price", "news", "rekom", "short", "rezim", "reżim"):
            problemy.append(f"nieznane basis w exclude: {e}")
    for t in sig.get("tactical", []):
        # Pozycja taktyczna może mieć własny epic spoza mapy koszykowej —
        # wtedy ticker nie musi należeć do uniwersum indeksu.
        wlasny = bool((t.get("epic") or "").strip())
        if not wlasny and t.get("ticker") not in sig["epics"]:
            problemy.append(f"taktyczna spoza uniwersum bez epic: {t}")
        if t.get("direction") not in ("BUY", "SELL"):
            problemy.append(f"zły kierunek pozycji taktycznej: {t}")
    for t, f in (sig.get("fills") or {}).items():
        try:
            if float((f or {}).get("cena")) <= 0:
                raise ValueError
        except (TypeError, ValueError):
            problemy.append(f"zła cena wejścia w fills: {t}={f}")
    if problemy:
        raise ValueError("signals.json nie przechodzi kontroli spójności — "
                         "handel wstrzymany: " + "; ".join(problemy))


def save_signals(sig, sha, message):
    return gh_put_file(SIGNALS_PATH,
                       json.dumps(sig, ensure_ascii=False, indent=2),
                       message, sha)


# ----------------------------------------------------------------------------
# MÓZG — wywołanie modelu Claude z wyszukiwaniem internetowym
# ----------------------------------------------------------------------------
def ask_claude(prompt, max_tokens, web_uses, model):
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": ANTHROPIC_API_KEY,
                 "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
        json={"model": model, "max_tokens": max_tokens,
              "tools": [{"type": "web_search_20250305", "name": "web_search",
                         "max_uses": web_uses}],
              "messages": [{"role": "user", "content": prompt}]},
        timeout=900)
    r.raise_for_status()
    data = r.json()
    text = "".join(b.get("text", "") for b in data.get("content", [])
                   if b.get("type") == "text")
    return text, data.get("stop_reason"), data.get("usage", {})


def extract_block(text, tag):
    m = re.search(rf"<{tag}>\s*(.*?)\s*</{tag}>", text, re.S)
    return m.group(1) if m else None


HTML_SPEC = (
    "Samowystarczalny HTML (bez zewnętrznych fontów/skryptów), mobile-first, "
    "elegancki: tło #F6F7F4, granatowy nagłówek #10243E z dużym kursem WIG20, "
    "'pieczątka' statusu (ramka 3px, zielona/bursztynowa/czerwona, wersaliki, "
    "obrót -2.5deg), sekcja 'Najważniejsze zmiany' z kolorowymi etykietami "
    "(ESPI/SHORT/REKOM./MAKRO), tabele koszyków TOP5 i BOTTOM5 (zieleń #0E7C4A "
    "/ czerwień #C4372E, liczby mono), pasek 'Spread', kalendarz dnia, stopka "
    "z zastrzeżeniem 'materiał analityczno-edukacyjny, nie stanowi rekomendacji "
    "inwestycyjnej' i autorstwem AI. Wszystko po polsku, liczby z datą i źródłem."
)


def prompt_daily(sig):
    dzis = date.today().isoformat()
    takt = json.dumps(sig.get("tactical", []), ensure_ascii=False)
    czesc_takt, schema_takt = "", ""
    if TACTICAL_ENABLED:
        wolne = max(0, TACTICAL_MAX - len(sig.get("tactical", [])))
        czesc_takt = (
            f"\n4) MODUŁ TAKTYCZNY (dokładki w środku tygodnia, rozliczane "
            f"OSOBNO od koszyków): przeskanuj WSZYSTKIE spółki WIG20 spoza "
            f"koszyków i spoza listy taktycznej pod kątem TWARDYCH świeżych "
            f"wyzwalaczy z ostatnich 24h: wynik wyraźnie powyżej konsensusu "
            f"z pozytywną reakcją kursu, przełomowy kontrakt/komunikat ESPI, "
            f"wezwanie (=BUY), szokowo złe wyniki/komunikat (=SELL). Możesz "
            f"dodać maks. 1 pozycję dziennie i tylko gdy otwartych "
            f"taktycznych < {TACTICAL_MAX} (teraz wolnych miejsc: {wolne}). "
            f"Możesz usunąć istniejącą taktyczną, gdy jej teza upadła. "
            f"Oczekuj, że zwykle obie listy są PUSTE — to wyjątek, nie reguła.")
        schema_takt = (',"tactical_add":[{"ticker":"...","direction":'
                       '"BUY|SELL","reason":"..."}],"tactical_remove":'
                       '["ticker"]')
    return f"""Jesteś automatem 'Puls WIG20'. Dziś {dzis}. Odpowiadasz DOKŁADNIE dwoma blokami: <signals>JSON</signals> oraz <html_report>HTML</html_report>. Zero tekstu poza blokami.

AKTUALNE SYGNAŁY (tydzień {sig['version']}): LONG {sig['long']}, SHORT {sig['short']}, status {sig['status']}, reakcje {json.dumps(sig.get('exclude', []), ensure_ascii=False)}, taktyczne {takt}. D0: {json.dumps(sig.get('d0'), ensure_ascii=False)}.

ZADANIE (dane tylko z internetu, każda liczba z datą i źródłem, braki='b.d.'):
1) Kursy zamknięcia WIG20, spółek koszykowych i taktycznych z ostatniej sesji GPW; zwroty od D0 (taktyczne: od entry_date) i relatywne; spread koszyków.
2) ESPI/newsy 24h dla spółek koszykowych, zmiany w rejestrze KNF, nowe rekomendacje, status wyzwalaczy tez (m.in. projekt CIT dla energetyki/paliw), kalendarz na dziś.
3) WERDYKT wg protokołu: status='AKTUALNA' lub 'NIEAKTUALNA' (NIEAKTUALNA tylko przy zdarzeniu unieważniającym całą prognozę). Osobno 'exclude' — reakcje per spółka koszykowa, DWA szczeble: action='CLOSE' (zamknięcie) WYŁĄCZNIE przy twardych wyzwalaczach: wezwanie/delisting, zawieszenie notowań, szokowy raport/komunikat, ruch >8% od D0 PRZECIW tezie, upadek filaru tezy tej spółki; action='REDUCE' (cięcie pozycji do połowy) przy miękkich: ruch 4–8% od D0 przeciw tezie, świeża rekomendacja przeciw tezie od liczącego się DM, zmiana pozycji krótkich KNF ≥0,3 p.p. przeciw tezie, istotny negatywny news poniżej rangi szoku. Zwracasz PEŁNĄ listę reakcji (wczorajsze wpisy + ewentualne nowe; maks. 2 NOWE dziennie); REDUCE może awansować do CLOSE, nigdy odwrotnie; raz zredukowana spółka zostaje zredukowana do soboty. Oczekuj, że zwykle lista jest PUSTA. Koszyków nie zmieniasz i kierunków nie odwracasz.{czesc_takt}

<signals> ma zawierać dokładnie: {{"date":"{dzis}","status":"AKTUALNA|NIEAKTUALNA","exclude":[{{"ticker":"...","action":"CLOSE|REDUCE","reason":"..."}}]{schema_takt},"headline":"1 zdanie po polsku"}}.

<html_report>: {HTML_SPEC} Tytuł 'Puls WIG20', data {dzis}, wynik koszyków od D0, sekcja pozycji taktycznych (jeśli są), zmiany, werdykt-pieczątka."""


def prompt_weekly(sig):
    dzis = date.today().isoformat()
    return f"""Jesteś automatem 'Ranking WIG20 — raport tygodniowy'. Dziś {dzis} (sobota). Odpowiadasz DOKŁADNIE dwoma blokami: <signals>JSON</signals> i <html_report>HTML</html_report>. Zero tekstu poza blokami.

POPRZEDNI TYDZIEŃ (do rozliczenia): wersja {sig['version']}, LONG {sig['long']}, SHORT {sig['short']}, D0 {json.dumps(sig.get('d0'), ensure_ascii=False)}, wykluczenia {json.dumps(sig.get('exclude', []), ensure_ascii=False)}, pozycje taktyczne {json.dumps(sig.get('tactical', []), ensure_ascii=False)}. Historia rozliczeń: {json.dumps(sig.get('history', []), ensure_ascii=False)}.

ZADANIE (dane tylko z internetu, z datami i źródłami, braki='b.d.'):
A) ROZLICZENIE: kursy zamknięcia z wczorajszego piątku (D+5) dla spółek koszykowych i WIG20; zwroty relatywne wg [D+5/D0−1] spółki minus WIG20 (korekta o dywidendę jeśli była); hit rate TOP5 i BOTTOM5, spread L/S; ODDZIELNIE rozlicz pozycje taktyczne (zwrot od entry_date do piątku vs WIG20, suma w p.p.). Policz też wariant ZARZĄDZANY tych samych koszyków z uwzględnieniem faktycznych reakcji dziennych: CLOSE = pozycja liczona tylko do dnia reakcji (kurs zamknięcia tego dnia), REDUCE = od dnia reakcji waga 50%; managed_pp = spread zarządzany, reaction_pp = managed_pp − spread_pp (to rozstrzyga, czy reakcje dzienne pomogły). Pokaż skumulowane reaction_pp i tactical_pp z całej history. Uczciwie: 5-sesyjne zwroty są w dużej mierze losowe, cel długoterminowy 55–60%.
B) NOWY RANKING 20 spółek WIG20 wg metody: wagi Momentum25/Katalizatory20/Makro15/DM15(bazowo 7,5, ±3 tylko za udokumentowane sygnały)/Rewizje10/Przepływy10/Wycena5; p=50%+0,5×(wynik−50) obcięte do 38–62%; zweryfikuj skład WIG20; kursy z piątku; katalizatory 10 sesji; ESPI 7 dni; rekomendacje 30 dni; rejestr KNF; sektorówka (miedź/srebro, ropa, stopy, FX); status projektu CIT. Przy porównywalnych argumentach preferuj spółki o mniejszej wadze w indeksie.
C) NOWE KOSZYKI: TOP5 (long) i BOTTOM5 (short).

<signals> dokładnie: {{"version":"RRRR-Wn (kolejny numer po {sig['version']})","status":"AKTUALNA","long":["5 tickerów"],"short":["5 tickerów"],"d0":{{"date":"data piątku","wig20":liczba,"prices":{{"TICKER":kurs_zamknięcia — dla wszystkich 10 spółek koszykowych}}}},"settlement":{{"week":"{sig['version']}","spread_pp":liczba,"hit_top":"x/5","hit_bottom":"x/5","tactical_pp":liczba_lub_null,"managed_pp":liczba,"reaction_pp":liczba}},"headline":"1 zdanie"}}. Tickery WYŁĄCZNIE z: {WIG20}. long i short rozłączne, po 5.

<html_report>: {HTML_SPEC} Tytuł 'Raport tygodniowy WIG20', sekcje: rozliczenie z wyróżnionym paskiem NAJWAŻNIEJSZE ZMIANY TYGODNIA (kto wypadł/wszedł i dlaczego), pełny ranking 20 spółek (pozycja|ticker|wynik|p|teza|ryzyko), TOP5 i BOTTOM5 rozszerzone, trzy falsyfikowalne deklaracje na nowe okno."""


def validate_daily(j, sig):
    assert j.get("status") in ("AKTUALNA", "NIEAKTUALNA"), "status spoza słownika"
    basket = set(sig["long"]) | set(sig["short"])
    ex = j.get("exclude", [])
    assert isinstance(ex, list), "exclude musi być listą"
    for e in ex:
        assert e.get("ticker") in basket, f"exclude spoza koszyków: {e}"
        assert e.get("action", "CLOSE") in ("CLOSE", "REDUCE"), f"złe action: {e}"
    # Scalanie: wczorajsze reakcje są trwałe do soboty; REDUCE może awansować
    # do CLOSE, nigdy odwrotnie; maks. 2 NOWE spółki dziennie.
    merged = {e["ticker"]: dict(e) for e in sig.get("exclude", [])}
    nowe = 0  # "basis" (cena/news/rekom/short/rezim) przenosi się razem z wpisem
    for e in ex:
        t, a = e["ticker"], e.get("action", "CLOSE")
        if t in merged:
            if merged[t].get("action", "CLOSE") == "REDUCE" and a == "CLOSE":
                merged[t] = {"ticker": t, "action": "CLOSE",
                             "reason": str(e.get("reason", ""))[:200]}
        elif nowe < 2:
            merged[t] = {"ticker": t, "action": a,
                         "reason": str(e.get("reason", ""))[:200]}
            nowe += 1
    ex_final = list(merged.values())
    add, rem = [], []
    if TACTICAL_ENABLED:
        cur = {t.get("ticker") for t in sig.get("tactical", [])}
        rem = [t for t in j.get("tactical_remove", []) if t in cur]
        for a in j.get("tactical_add", [])[:1]:          # maks. 1 nowa dziennie
            t = a.get("ticker")
            assert t in sig["epics"], f"taktyczna spoza uniwersum: {t}"
            assert t not in basket, f"taktyczna nie może dublować koszyka: {t}"
            assert t not in cur, f"taktyczna już otwarta: {t}"
            assert a.get("direction") in ("BUY", "SELL"), "zły kierunek taktycznej"
            if len(cur) - len(rem) < TACTICAL_MAX:
                add.append({"ticker": t, "direction": a["direction"],
                            "reason": str(a.get("reason", ""))[:200],
                            "entry_date": date.today().isoformat()})
    return {"status": j["status"], "exclude": ex_final,
            "tactical_add": add, "tactical_remove": rem,
            "headline": str(j.get("headline", ""))[:300],
            "date": j.get("date", date.today().isoformat())}


def validate_weekly(j):
    for k in ("version", "status", "long", "short"):
        assert k in j, f"brak pola {k}"
    assert j["status"] == "AKTUALNA", "nowy tydzień musi startować jako AKTUALNA"
    L, S = list(j["long"]), list(j["short"])
    assert len(L) == 5 and len(S) == 5, "koszyki muszą mieć po 5 spółek"
    assert not set(L) & set(S), "long i short nie mogą się pokrywać"
    for t in L + S:
        assert t in sig["epics"], f"ticker spoza uniwersum: {t}"
    return j


def generate(mode, do_commit=True):
    out = {"tryb": mode, "commit": do_commit,
           "czas_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    sig, sha = load_signals()
    prompt = prompt_daily(sig) if mode == "daily" else prompt_weekly(sig)
    web = WEB_MAX_DAILY if mode == "daily" else WEB_MAX_WEEKLY
    maxtok = 9000 if mode == "daily" else 16000
    model = ANTHROPIC_MODEL_DAILY if mode == "daily" else ANTHROPIC_MODEL_WEEKLY
    out["model"] = model

    text, stop, usage = ask_claude(prompt, maxtok, web, model)
    out["zuzycie_tokenow"] = usage
    if stop == "max_tokens":
        raise RuntimeError("Model uciął odpowiedź (max_tokens) — bez zmian.")

    raw_sig = extract_block(text, "signals")
    raw_html = extract_block(text, "html_report")
    if not raw_sig or not raw_html:
        raise RuntimeError("Brak wymaganych bloków <signals>/<html_report>.")
    j = json.loads(re.sub(r"^```(json)?|```$", "", raw_sig.strip(), flags=re.M))

    if mode == "daily":
        v = validate_daily(j, sig)
        sig["status"] = v["status"]
        sig["exclude"] = v["exclude"]
        sig["last_daily"] = v["date"]
        sig["tactical"] = ([t for t in sig.get("tactical", [])
                            if t.get("ticker") not in v["tactical_remove"]]
                           + v["tactical_add"])
        commit_msg = (f"puls {v['date']}: {v['status']}"
                      + (f", wykluczenia: {[e['ticker'] for e in v['exclude']]}"
                         if v["exclude"] else "")
                      + (f", taktyczne +{[t['ticker'] for t in v['tactical_add']]}"
                         if v["tactical_add"] else "")
                      + (f", taktyczne -{v['tactical_remove']}"
                         if v["tactical_remove"] else ""))
        report_name = f"puls-{v['date']}.html"
        headline = v["headline"]
    else:
        v = validate_weekly(j)
        sig.setdefault("history", [])
        if j.get("settlement"):
            sig["history"] = (sig["history"] + [j["settlement"]])[-26:]
        sig.update({"version": v["version"], "status": "AKTUALNA",
                    "long": v["long"], "short": v["short"],
                    "exclude": [], "tactical": [], "d0": j.get("d0"),
                    "generated": date.today().isoformat()})
        commit_msg = (f"tydzień {v['version']}: LONG {v['long']} "
                      f"SHORT {v['short']}")
        report_name = f"raport-{v['version']}.html"
        headline = str(j.get("headline", ""))[:300]

    out["sygnaly_nowe"] = {k: sig[k] for k in
                           ("version", "status", "long", "short",
                            "exclude", "tactical")}
    out["headline"] = headline

    if do_commit:
        c1 = save_signals(sig, sha, commit_msg)
        _, rsha = gh_get_file(f"{REPORTS_DIR}/{report_name}")
        c2 = gh_put_file(f"{REPORTS_DIR}/{report_name}", raw_html,
                         f"raport: {report_name}", rsha)
        out["commity"] = [c1, c2]
        link = (f"{PAGES_BASE}/{REPORTS_DIR}/{report_name}" if PAGES_BASE else
                f"https://github.com/{GITHUB_REPO}/blob/{GITHUB_BRANCH}/"
                f"{REPORTS_DIR}/{report_name}")
        emoji = "📊" if mode == "daily" else "🗓️"
        notify(f"{emoji} {'Puls' if mode == 'daily' else 'Raport tygodniowy'} "
               f"WIG20 gotowy — {sig['status']}"
               + (f", wykluczenia: {[e['ticker'] for e in sig['exclude']]}"
                  if sig.get("exclude") else "")
               + (f", taktyczne: {[t['ticker'] for t in sig['tactical']]}"
                  if sig.get("tactical") else "")
               + f"\n{headline}\nRaport: {link}")
        out["raport_link"] = link
    return out


# ----------------------------------------------------------------------------
# KLIENT CAPITAL.COM
# ----------------------------------------------------------------------------
class Capital:
    def __init__(self):
        self.switch_error = None
        # Cache migawek rynku na czas jednego biegu: market() jest teraz
        # odpytywany z trzech miejsc (bramka reakcji, stopy, wyrównywanie
        # wielkości), a bez cache jeden bieg robiłby ~30 zapytań zamiast ~10
        # i mógłby podejmować decyzje na dwóch różnych cenach tej samej
        # spółki w odstępie sekund.
        self._rynki = {}
        self.s = requests.Session()
        self.s.headers.update({"X-CAP-API-KEY": CAPITAL_API_KEY,
                               "Content-Type": "application/json"})

    def login(self):
        r = self.s.post(f"{BASE_URL}/api/v1/session",
                        json={"identifier": CAPITAL_IDENT,
                              "password": CAPITAL_PASSWORD}, timeout=20)
        if r.status_code != 200:
            raise RuntimeError(f"Logowanie nieudane ({r.status_code}): {r.text[:200]}")
        self.s.headers.update({"CST": r.headers.get("CST"),
                               "X-SECURITY-TOKEN": r.headers.get("X-SECURITY-TOKEN")})
        if ACCOUNT_ID:
            self._switch_account(ACCOUNT_ID)

    def _switch_account(self, account_id):
        """Przełącza AKTYWNY rachunek sesji. Konieczne przy >1 rachunku:
        pozycje i zlecenia zawsze dotyczą rachunku aktywnego, nie tego,
        z którego czytamy saldo."""
        try:
            cur = self._get("/api/v1/session").get("accountId")
            if cur == account_id:
                return
        except Exception:
            pass  # kształt odpowiedzi nieistotny — spróbujemy przełączyć
        r = self.s.put(f"{BASE_URL}/api/v1/session",
                       json={"accountId": account_id}, timeout=20)
        if r.status_code == 200:
            for h in ("CST", "X-SECURITY-TOKEN"):
                if r.headers.get(h):
                    self.s.headers[h] = r.headers[h]
            log.info("Aktywny rachunek przełączony na %s.", account_id)
        elif "not-different" in r.text or "already" in r.text.lower():
            pass  # ten rachunek jest już aktywny
        else:
            self.switch_error = (f"Nie mogę przełączyć rachunku na {account_id}: "
                                 f"{r.status_code} {r.text[:150]}")
            log.error(self.switch_error)

    def _get(self, path, **kw):
        r = self.s.get(f"{BASE_URL}{path}", timeout=20, **kw)
        r.raise_for_status()
        return r.json()

    def accounts(self):
        return self._get("/api/v1/accounts").get("accounts", [])

    def account_snapshot(self):
        """Pełna migawka rachunku: kapitał, saldo i wycena pozycji OSOBNO.

        Rozbicie na balance i profitLoss jest potrzebne do KONTROLI KAPITAŁU:
        profitLoss z API musi się zgadzać z sumą upl pozycji, które bot zna.
        Gdy się nie zgadza, na rachunku dzieje się coś poza książką bota
        (ręczne pozycje, wpłata, inny instrument) i nie wolno skalować
        wielkości pozycji.
        """
        accs = self.accounts()
        pick = None
        for a in accs:
            if ACCOUNT_ID and a.get("accountId") == ACCOUNT_ID:
                pick = a
                break
            if not ACCOUNT_ID and a.get("preferred"):
                pick = a
        pick = pick or accs[0]
        b = pick.get("balance", {})
        saldo = float(b.get("balance", 0) or 0)
        wycena = float(b.get("profitLoss", 0) or 0)
        return {"equity": saldo + wycena, "saldo": saldo, "wycena": wycena,
                "ccy": pick.get("currency", "?"),
                "accountId": pick.get("accountId"),
                "dostepne": float(b.get("available", 0) or 0)}

    def equity(self):
        s = self.account_snapshot()
        return s["equity"], s["ccy"], s["accountId"]

    def positions(self):
        out = []
        for p in self._get("/api/v1/positions").get("positions", []):
            pos, mkt = p.get("position", {}), p.get("market", {})
            # "level" to cena otwarcia pozycji u brokera — jedyne źródło
            # prawdy o tym, po ile bot naprawdę wszedł. Capital.com bywa
            # niekonsekwentny w nazwie pola, więc bierzemy pierwsze sensowne.
            poziom = None
            for k in ("level", "openLevel", "price"):
                v = pos.get(k)
                if v not in (None, ""):
                    try:
                        poziom = float(v)
                        break
                    except (TypeError, ValueError):
                        pass
            upl = pos.get("upl")
            try:
                upl = float(upl) if upl not in (None, "") else None
            except (TypeError, ValueError):
                upl = None
            out.append({"dealId": pos.get("dealId"), "epic": mkt.get("epic"),
                        "name": mkt.get("instrumentName"),
                        "direction": pos.get("direction"),
                        "size": float(pos.get("size", 0)),
                        "wejscie": poziom,
                        "otwarta": (pos.get("createdDateUTC")
                                    or pos.get("createdDate")),
                        "waluta": (pos.get("currency")
                                   or mkt.get("currency") or ""),
                        "upl": upl})
        return out

    def market(self, epic, odswiez=False):
        if not odswiez and epic in self._rynki:
            return self._rynki[epic]
        d = self._get(f"/api/v1/markets/{epic}")
        snap = d.get("snapshot", {})
        rules = d.get("dealingRules", {})
        instr = d.get("instrument", {})
        bid, offer = snap.get("bid"), snap.get("offer")
        mid = (bid + offer) / 2 if bid and offer else (bid or offer)
        out = {"epic": epic, "name": instr.get("name", epic),
               "currency": instr.get("currency")
                           or (instr.get("currencies") or [{}])[0].get("code")
                           or "PLN",
               "status": snap.get("marketStatus"), "mid": mid,
               "min": float(rules.get("minDealSize", {}).get("value", 1) or 1)}
        self._rynki[epic] = out
        return out

    def search(self, term):
        d = self._get("/api/v1/markets", params={"searchTerm": term})
        return [{"epic": m.get("epic"), "name": m.get("instrumentName"),
                 "type": m.get("instrumentType"), "status": m.get("marketStatus")}
                for m in d.get("markets", [])][:15]

    def open(self, epic, direction, size):
        r = self.s.post(f"{BASE_URL}/api/v1/positions",
                        json={"epic": epic, "direction": direction,
                              "size": size, "guaranteedStop": False}, timeout=20)
        if not r.ok:
            return False, None, r.text[:200]
        ref = r.json().get("dealReference")
        if not ref:
            return False, None, "brak dealReference: " + r.text[:150]
        # POTWIERDZENIE realizacji — samo przyjęcie zlecenia to NIE otwarcie
        # pozycji: broker może je odrzucić na etapie potwierdzenia (np. SELL
        # niedostępny). Bez tej pętli /run raportowałby fikcyjne "OTWARTO".
        for _ in range(8):
            time.sleep(0.5)
            try:
                c = self._get(f"/api/v1/confirms/{ref}")
            except requests.HTTPError:
                continue
            st = str(c.get("dealStatus") or c.get("status") or "").upper()
            if st in ("ACCEPTED", "OPEN", "OPENED"):
                lvl = c.get("level") or c.get("openLevel")
                try:
                    lvl = float(lvl) if lvl not in (None, "") else None
                except (TypeError, ValueError):
                    lvl = None
                return True, ref, ("potwierdzono"
                                   + (f" @ {lvl}" if lvl is not None else ""))
            if st in ("REJECTED", "DECLINED", "DELETED"):
                powod = (c.get("rejectReason") or c.get("reason")
                         or json.dumps(c, ensure_ascii=False)[:150])
                return False, ref, f"ODRZUCONO przez brokera: {powod}"
        return False, ref, ("BRAK POTWIERDZENIA po 4 s — pozycji nie liczę "
                            "jako otwartej; zweryfikuj w aplikacji")

    def close(self, deal_id):
        r = self.s.delete(f"{BASE_URL}/api/v1/positions/{deal_id}", timeout=20)
        return r.ok, r.text[:200]

    def close_all_epics(self, positions, epics):
        """Pomocnicze zamknięcie listy pozycji — używane przez /close_all."""
        out = []
        for p in positions:
            if p["epic"] in epics:
                ok, msg = self.close(p["dealId"])
                out.append((p["epic"], ok, msg))
        return out

    def usd_pln(self):
        try:
            m = self.market(FX_EPIC)
            if m["mid"]:
                return float(m["mid"])
        except Exception as e:
            log.warning("Brak %s (%s), FX_FALLBACK=%s", FX_EPIC, e, FX_FALLBACK)
        return FX_FALLBACK

    def fx_rate(self, from_ccy, to_ccy):
        """Kurs przeliczenia from→to. Waluty zgodne = 1.0; para USD/PLN
        z rynku USDPLN; inne pary = 1.0 z ostrzeżeniem w logu."""
        if from_ccy == to_ccy:
            return 1.0
        if {from_ccy, to_ccy} == {"USD", "PLN"}:
            r = self.usd_pln()                      # PLN za 1 USD
            return r if (from_ccy, to_ccy) == ("USD", "PLN") else 1.0 / r
        log.warning("Nieobsługiwana para walut %s→%s — przyjmuję 1.0",
                    from_ccy, to_ccy)
        return 1.0


def calc_size(cap, target_acc, epic, acc_ccy):
    """target_acc w WALUCIE RACHUNKU; przeliczenie na walutę instrumentu."""
    m = cap.market(epic)
    if not m["mid"]:
        return None, m, "brak ceny"
    fx = cap.fx_rate(acc_ccy, m["currency"])   # 1.0 gdy waluty zgodne
    step = m["min"] if m["min"] > 0 else 1.0
    surowy = target_acc * fx / m["mid"]
    dol = math.floor(surowy / step) * step
    gora = dol + step
    size = dol
    # Zaokrąglanie do BLIŻSZEGO kroku (nie floor): przy grubych krokach floor
    # potrafił zaniżać pozycję o 20-30% (np. TSLA 0.2 zam. 0.3). Krok w górę
    # dopuszczamy do 125% celu — bliżej celu niż niedomiar, bez przestrzału.
    if dol >= step:
        w_dol = abs(dol * m["mid"] / fx - target_acc)
        w_gore = abs(gora * m["mid"] / fx - target_acc)
        if w_gore < w_dol and gora * m["mid"] / fx <= target_acc * 1.25:
            size = gora
    size = round(size, 4)
    if size < step:
        min_acc = step * m["mid"] / fx
        if min_acc <= target_acc * MAX_OVERSHOOT:
            return step, m, f"min. wielkość ({step})"
        return None, m, (f"min. wielkość {step} = {min_acc:.0f} {acc_ccy} "
                         f"> tolerancja — pomijam")
    return size, m, "ok"


# ----------------------------------------------------------------------------
# SYNCHRONIZACJA PORTFELA (/run)
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# STAN RACHUNKU: ceny wejścia, kontrola kapitału, bramka wyzwalaczy
# ----------------------------------------------------------------------------
RYNEK_OTWARTY = "TRADEABLE"


def rynek(cap, epic, rep, etykieta):
    """Zwraca migawkę rynku albo None, opisując powód w raporcie.

    Rozdziela DWA różne zdarzenia, które wcześniej lądowały w jednym worku
    "błędy": zamknięty rynek (weekend, święto, przerwa) to normalne
    POMINIĘCIE, a nie awaria. 12-13.09.2026 każdy weekendowy bieg raportował
    "błędy: 3", przez co prawdziwa awaria w dzień sesyjny wyglądała tak samo
    jak sobota i nie zwracała niczyjej uwagi.
    """
    try:
        m = cap.market(epic)
    except requests.RequestException as e:
        rep["błędy"].append(f"{etykieta}: rynek niedostępny ({e})")
        return None
    if not m["mid"]:
        rep["pominiete"].append(f"{etykieta}: brak ceny (rynek zamknięty?)")
        return None
    if m["status"] != RYNEK_OTWARTY:
        rep["pominiete"].append(f"{etykieta}: rynek {m['status']}")
        return None
    return m


def ceny_wejscia(sig, positions, epic2tic):
    """Mapa ticker -> cena wejścia, z pozycji brokera i z signals.json.

    Pierwszeństwo ma poziom otwarcia u brokera (to fakt), signals.json jest
    zapasem na wypadek, gdyby API nie podało pola level.
    """
    fills = {}
    for t, f in (sig.get("fills") or {}).items():
        try:
            c = float((f or {}).get("cena"))
            if c > 0:
                fills[t] = {"cena": c, "data": (f or {}).get("data"),
                            "zrodlo": "signals.json"}
        except (TypeError, ValueError):
            continue
    for p in positions:
        t = epic2tic.get(p["epic"])
        if t and p.get("wejscie"):
            fills[t] = {"cena": float(p["wejscie"]),
                        "data": (p.get("otwarta") or "")[:10] or None,
                        "kierunek": p.get("direction"),
                        "zrodlo": "broker"}
    return fills


def kontrola_kapitalu(snap, positions, managed, rep):
    """Czy kapitał z API daje się odtworzyć z pozycji, które bot zna?

    Rozliczenie okresu 27.08-18.09.2026 pokazało, że kapitał raportowany
    przez bota rósł ok. 2,5x szybciej, niż wynikało z historii transakcji
    (17.09: log +47,1 USD wobec +21,8 USD z odtworzonych pozycji). Bot
    liczył kapitał jako balance + profitLoss i nigdy nie sprawdzał, czy
    profitLoss pochodzi z jego własnej książki. Ta funkcja to sprawdza
    i przy rozjeździe blokuje skalowanie wielkości pozycji.
    """
    obce = [p for p in positions if p["epic"] not in managed]
    znane = [p for p in positions if p["epic"] in managed]
    suma_upl = sum(p["upl"] for p in znane if p.get("upl") is not None)
    braki = [p["epic"] for p in znane if p.get("upl") is None]
    roznica = snap["wycena"] - suma_upl
    prog = max(abs(snap["equity"]) * EQUITY_TOL, 1.0)
    ok = abs(roznica) <= prog and not obce and not braki
    wynik = {
        "kapital": round(snap["equity"], 2),
        "saldo": round(snap["saldo"], 2),
        "wycena_z_api": round(snap["wycena"], 2),
        "suma_upl_pozycji_bota": round(suma_upl, 2),
        "roznica": round(roznica, 2),
        "tolerancja": round(prog, 2),
        "pozycje_spoza_ksiazki": [f"{p['epic']} {p['direction']} {p['size']}"
                                  for p in obce],
        "pozycje_bez_wyceny": braki,
        "zgodne": ok}
    if not ok:
        powody = []
        if obce:
            powody.append(f"{len(obce)} pozycji spoza książki bota "
                          f"({', '.join(wynik['pozycje_spoza_ksiazki'][:5])})")
        if braki:
            powody.append(f"{len(braki)} pozycji bez wyceny z API")
        if abs(roznica) > prog:
            powody.append(f"wycena z API {snap['wycena']:.2f} vs suma upl "
                          f"{suma_upl:.2f} (różnica {roznica:+.2f} przy "
                          f"tolerancji {prog:.2f})")
        wynik["powod"] = "; ".join(powody)
        rep["błędy"].append("KONTROLA KAPITAŁU: " + wynik["powod"]
                            + " — wielkość pozycji ograniczona do "
                              f"ALLOC_PCT_SAFE={ALLOC_PCT_SAFE}")
    return wynik


def _kierunek_tickera(sig, ticker):
    if ticker in sig.get("long", []):
        return "BUY"
    if ticker in sig.get("short", []):
        return "SELL"
    for t in sig.get("tactical", []):
        if t.get("ticker") == ticker:
            return t.get("direction")
    return None


def ruch_przeciw_tezie(kierunek, wejscie, biezaca):
    """Dodatnia liczba = pozycja jest pod wodą o tyle ułamka ceny wejścia."""
    if not wejscie or not biezaca or wejscie <= 0:
        return None
    if kierunek == "BUY":
        return (wejscie - biezaca) / wejscie
    if kierunek == "SELL":
        return (biezaca - wejscie) / wejscie
    return None


def bramka_reakcji(sig, cap, fills, rep):
    """Weryfikuje wyzwalacze CENOWE wobec faktycznych cen wejścia.

    Bramka wyłącznie ŁAGODZI: może obniżyć CLOSE do REDUCE albo pominąć
    reakcję, nigdy nie zaostrza i nigdy nie dokłada nowych wpisów. Wpisy
    reżimowe (P1/P2) i wpisy o podstawie innej niż cenowa przechodzą bez
    sprawdzania — one nie mierzą ruchu kursu.
    """
    closed, reduced, slad = set(), set(), []
    for e in sig.get("exclude", []):
        ticker = e.get("ticker")
        akcja = e.get("action", "CLOSE")
        podstawa = str(e.get("basis") or "cena").lower()
        powod = str(e.get("reason") or "")
        rezim = (powod.upper().startswith("REŻIM")
                 or podstawa in ("rezim", "reżim"))
        cel = closed if akcja == "CLOSE" else reduced
        if not REACT_GATE or rezim or podstawa not in ("cena", "price"):
            cel.add(ticker)
            slad.append({"ticker": ticker, "wpis": akcja, "wykonane": akcja,
                         "podstawa": "reżim" if rezim else podstawa,
                         "uwaga": "bez bramki — wyzwalacz nie jest cenowy"})
            continue
        kierunek = _kierunek_tickera(sig, ticker)
        wejscie = (fills.get(ticker) or {}).get("cena")
        epic = sig["epics"].get(ticker, "")
        m = None
        if epic:
            try:
                m = cap.market(epic)
            except requests.RequestException:
                m = None
        biezaca = (m or {}).get("mid")
        ruch = ruch_przeciw_tezie(kierunek, wejscie, biezaca)
        if ruch is None:
            # Nie potrafimy zweryfikować (brak ceny wejścia albo rynek
            # zamknięty) — wykonujemy wpis pulsu bez zmian. Bramka ma
            # korygować pomiar, a nie wprowadzać własną uznaniowość.
            cel.add(ticker)
            slad.append({"ticker": ticker, "wpis": akcja, "wykonane": akcja,
                         "podstawa": "cena",
                         "uwaga": "brak danych do weryfikacji — wpis wykonany"})
            continue
        if ruch >= REACT_CLOSE_PCT:
            nowa = akcja                      # CLOSE zostaje, REDUCE zostaje
        elif ruch >= REACT_REDUCE_PCT:
            nowa = "REDUCE"
        else:
            nowa = "BRAK"
        if nowa == "CLOSE":
            closed.add(ticker)
        elif nowa == "REDUCE":
            reduced.add(ticker)
        wpis = {"ticker": ticker, "wpis": akcja, "wykonane": nowa,
                "podstawa": "cena", "cena_wejscia": round(wejscie, 4),
                "cena_biezaca": round(biezaca, 4),
                "ruch_przeciw_tezie": f"{ruch * 100:+.2f}%"}
        if nowa != akcja:
            opis = (f"pozycja jest NA PLUSIE o {-ruch * 100:.2f}%"
                    if ruch < 0 else
                    f"strata wynosi {ruch * 100:.2f}%")
            wpis["uwaga"] = (f"złagodzone: licząc od ceny wejścia {opis}, "
                             f"progi {REACT_REDUCE_PCT * 100:.0f}%/"
                             f"{REACT_CLOSE_PCT * 100:.0f}%")
            rep["pominiete"].append(
                f"{ticker}: wpis {akcja} złagodzony do "
                f"{'braku reakcji' if nowa == 'BRAK' else nowa} — licząc od "
                f"ceny wejścia {wejscie:.2f} {opis}")
        slad.append(wpis)
    return closed, reduced, slad


def stopy_bezpieczenstwa(positions, fills, epic2tic, cap, rep):
    """Zwraca epic-i pozycji, które przebiły twardy stop od ceny wejścia."""
    trafione = {}
    if STOP_LOSS_PCT <= 0:
        return trafione
    for p in positions:
        t = epic2tic.get(p["epic"])
        if not t:
            continue
        wejscie = p.get("wejscie") or (fills.get(t) or {}).get("cena")
        m = None
        try:
            m = cap.market(p["epic"])
        except requests.RequestException:
            continue
        if not m["mid"] or m["status"] != RYNEK_OTWARTY:
            continue
        ruch = ruch_przeciw_tezie(p["direction"], wejscie, m["mid"])
        if ruch is not None and ruch >= STOP_LOSS_PCT:
            trafione[p["epic"]] = (f"STOP {STOP_LOSS_PCT * 100:.0f}%: "
                                   f"{t} {ruch * 100:.1f}% pod ceną wejścia "
                                   f"{wejscie:.2f}")
    return trafione


def desired_book(sig, closed=None, reduced=None):
    book, skipped = {}, []
    if closed is None:
        closed = {e.get("ticker") for e in sig.get("exclude", [])
                  if e.get("action", "CLOSE") == "CLOSE"}
    if reduced is None:
        reduced = {e.get("ticker") for e in sig.get("exclude", [])
                   if e.get("action") == "REDUCE"}
    pary = [(t, "BUY") for t in sig["long"]]
    if HEDGE_MODE == "classic":
        pary += [(t, "SELL") for t in sig["short"]]
    else:
        skipped.append("koszyk SHORT (akcje): pominięty — "
                       + ("syntetyczny short przez indeks (HEDGE_EPIC)"
                          if HEDGE_MODE == "index" else "tryb long-only"))
    for ticker, direction in pary:
        if ticker in closed:
            continue
        epic = sig["epics"].get(ticker, "")
        if not epic or epic.upper().startswith("UZUP"):
            skipped.append(f"{ticker} (brak epic)")
            continue
        book[epic] = {"direction": direction, "ticker": ticker,
                      "reduced": ticker in reduced}
    if TACTICAL_ENABLED:
        for t in sig.get("tactical", []):
            ticker = t.get("ticker")
            if HEDGE_MODE != "classic" and t.get("direction") == "SELL":
                skipped.append(f"{ticker} (taktyczna SELL — rachunek LONG_ONLY)")
                continue
            # Pozycja taktyczna może mieć własny epic spoza mapy koszykowej:
            # najmocniejszym twardym wyzwalaczem 17.09.2026 był kontrakt
            # Generac z Amazonem (+21,35%), odrzucony wyłącznie dlatego, że
            # spółka nie należy do NDX-100. Uniwersum koszyków zostaje bez
            # zmian, skan taktyczny może sięgnąć szerzej.
            epic = (t.get("epic") or sig["epics"].get(ticker, "")).strip()
            if not epic or epic.upper().startswith("UZUP"):
                skipped.append(f"{ticker} (taktyczna, brak epic)")
                continue
            if epic in book:
                continue
            book[epic] = {"direction": t.get("direction"), "ticker": ticker,
                          "tactical": True}
    return book, skipped, closed


def sync():
    rep_uwaga_live = (None if LIVE_ODBLOKOWANY else
                      "TRYB LIVE NIEUZBROJONY (brak LIVE_POTWIERDZENIE) — "
                      "to wyłącznie plan na sucho; realny handel wymaga "
                      "potwierdzenia i DRY_RUN=false")
    if not LIVE_ODBLOKOWANY and not DRY_RUN:
        return {"tryb": "LIVE", "handel": "ZABLOKOWANY",
                "błąd": ("Rachunek rzeczywisty (CAPITAL_DEMO=false) bez zmiennej "
                         "LIVE_POTWIERDZENIE=ROZUMIEM-RYZYKO — handel wstrzymany. "
                         "To celowy bezpiecznik: patrz sekcja o uzbrajaniu LIVE "
                         "w INSTRUKCJI. Biegi na sucho (DRY_RUN=true) działają "
                         "bez potwierdzenia.")}
    rep = {"czas_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "dry_run": DRY_RUN, "akcje": [], "pominiete": [], "błędy": []}
    sig, sig_sha = load_signals()

    if rep_uwaga_live:
        rep["uwaga"] = rep_uwaga_live
    rep["sygnaly"] = {k: sig[k] for k in
                      ("version", "status", "long", "short",
                       "exclude", "tactical")}
    cap = Capital()
    cap.login()
    if ACCOUNT_ID and cap.switch_error:
        return {"handel": "ZABLOKOWANY",
                "błąd": (f"CAPITAL_ACCOUNT_ID='{ACCOUNT_ID}' odrzucone przez "
                         f"Capital.com ({cap.switch_error}). Handel wstrzymany, "
                         "żeby nie działać na niewłaściwym rachunku. Otwórz "
                         "/status i skopiuj poprawne pole accountId z "
                         "'konta_wszystkie' (to NIE jest numer konta z aplikacji).")}
    snap = cap.account_snapshot()
    equity, ccy, acc = snap["equity"], snap["ccy"], snap["accountId"]
    rep["konto"] = {"accountId": acc, "kapital": equity, "waluta": ccy,
                    "saldo": snap["saldo"], "wycena_pozycji": snap["wycena"]}
    managed = {e for e in sig["epics"].values()
               if e and not e.upper().startswith("UZUP")}
    if HEDGE_MODE == "index" and HEDGE_EPIC:
        managed.add(HEDGE_EPIC)
    epic2tic = {v: k for k, v in sig["epics"].items()}
    for t in sig.get("tactical", []):
        e = (t.get("epic") or "").strip()
        if e:
            managed.add(e)
            epic2tic.setdefault(e, t.get("ticker"))
    wszystkie = cap.positions()
    positions = [p for p in wszystkie if p["epic"] in managed]
    rep["pozycje_przed"] = positions

    # KONTROLA KAPITAŁU — czy equity daje się odtworzyć z książki bota.
    rep["kontrola_kapitalu"] = kontrola_kapitalu(snap, wszystkie, managed, rep)
    alloc = ALLOC_PCT if rep["kontrola_kapitalu"]["zgodne"] else ALLOC_PCT_SAFE
    rep["alloc_pct"] = alloc

    fills = ceny_wejscia(sig, positions, epic2tic)
    rep["ceny_wejscia"] = fills

    def do_close(p, powod):
        if DRY_RUN:
            rep["akcje"].append(f"[DRY] ZAMKNIJ {p['direction']} "
                                f"{epic2tic.get(p['epic'], p['epic'])} — {powod}")
            return
        ok, msg = cap.close(p["dealId"])
        if ok:
            rep["akcje"].append(
                f"ZAMKNIĘTO {epic2tic.get(p['epic'], p['epic'])} ({powod})")
            return
        # Nieudane zamknięcie przy zamkniętym rynku to nie awaria bota —
        # spróbuje w kolejnym biegu. Do "błędów" trafiają tylko odmowy,
        # których sam czas nie naprawi.
        etykieta = epic2tic.get(p["epic"], p["epic"])
        zamkniety = False
        try:
            m = cap.market(p["epic"])
            zamkniety = (not m["mid"]) or m["status"] != RYNEK_OTWARTY
        except requests.HTTPError:
            zamkniety = False
        if zamkniety:
            rep["pominiete"].append(
                f"{etykieta}: zamknięcie odłożone — rynek zamknięty ({powod})")
        else:
            rep["akcje"].append(f"BŁĄD zamykania {etykieta}: {msg}")
            rep["błędy"].append(f"{etykieta}: {msg}")

    # Kill switch od KROCZĄCEGO SZCZYTU: przy stałej START_EQUITY próg
    # rozluźniał się z każdym zarobionym dolarem (kapitał 1104 USD, próg
    # 750 USD = dopuszczalne obsunięcie -32% zamiast deklarowanych -25%).
    szczyt = float(sig.get("equity_peak") or 0) or START_EQUITY
    if KILL_TRAILING and equity > szczyt:
        szczyt = equity
    odniesienie = max(szczyt, START_EQUITY) if KILL_TRAILING else START_EQUITY
    prog_kill = odniesienie * KILL_LEVEL
    rep["kill_switch"] = {"odniesienie": round(odniesienie, 2),
                          "prog": round(prog_kill, 2),
                          "kapital": round(equity, 2),
                          "kroczacy": KILL_TRAILING}
    if equity < prog_kill:
        for p in positions:
            do_close(p, "KILL SWITCH")
        notify(f"⛔ {BOT_NAME} KILL SWITCH: kapitał {equity:.2f} {ccy} "
               f"poniżej progu {prog_kill:.2f} (szczyt {odniesienie:.2f}). "
               f"Wszystko zamknięte, handel wstrzymany.")
        rep["akcje"].append("KILL SWITCH aktywny — handel wstrzymany.")
        return rep

    if sig["status"].upper().startswith("NIEAKT"):
        for p in positions:
            do_close(p, "status NIEAKTUALNA")
        rep["akcje"].append("Status NIEAKTUALNA — portfel płasko do nowych sygnałów.")
        return rep

    # BRAMKA WYZWALACZY: wpisy cenowe pulsu liczą ruch od D0, a pozycja
    # bywa otwarta kilka sesji po D0 — sprawdzamy je wobec ceny wejścia.
    g_closed, g_reduced, slad = bramka_reakcji(sig, cap, fills, rep)
    rep["reakcje"] = slad
    book, skipped, closed = desired_book(sig, g_closed, g_reduced)
    rep["pominiete"] += skipped

    # TWARDY STOP od ceny wejścia — siatka niezależna od logiki tygodniowej.
    stopy = stopy_bezpieczenstwa(positions, fills, epic2tic, cap, rep)
    if stopy:
        rep["stopy"] = list(stopy.values())

    for p in positions:
        if p["epic"] == HEDGE_EPIC:
            continue  # pozycją hedge zarządza osobny blok niżej
        want = book.get(p["epic"])
        tic = epic2tic.get(p["epic"], p["epic"])
        if p["epic"] in stopy:
            do_close(p, stopy[p["epic"]])
            book.pop(p["epic"], None)   # nie otwieraj jej z powrotem w tym biegu
            continue
        if not want:
            do_close(p, "wykluczona przez puls" if tic in closed
                     else "poza aktualnymi sygnałami")
        elif want["direction"] != p["direction"]:
            do_close(p, f"zmiana kierunku na {want['direction']}")

    # WYRÓWNANIE WIELKOŚCI pozycji, które zostają w koszyku (w OBIE strony:
    # docięcie po action=REDUCE i dołożenie z powrotem do pełnej wagi).
    # Wcześniej dotykaliśmy tylko redukcji, więc raz zmniejszona pozycja
    # zostawała na połowie wagi także w kolejnych oknach (puls czyści exclude,
    # ale wielkości nikt nie przeliczał), a pozycje niesione tygodniami
    # rozjeżdżały się z celem wraz z kursem — koszyk L/S przestawał być
    # zbalansowany i bot łapał niezamierzoną ekspozycję kierunkową.
    # Ruszamy dopiero poza pasmem REBALANCE_TOL i tylko wtedy, gdy krok
    # wielkości pozwala faktycznie podejść bliżej celu (inaczej byłby to
    # cotygodniowy churn: zamknij i otwórz to samo, płacąc spread).
    # OGRANICZNIK TEMPA WZROSTU EKSPOZYCJI — liczony raz, przed zmianami.
    if MAX_EXPOSURE_STEP > 0:
        teraz_brutto = 0.0
        for p in positions:
            if p["epic"] not in book:
                continue
            try:
                m = cap.market(p["epic"])
            except requests.RequestException:
                continue
            if m["mid"]:
                teraz_brutto += abs(p["size"] * m["mid"]
                                    / cap.fx_rate(ccy, m["currency"]))
        cel_brutto = sum(
            equity * (TACTICAL_ALLOC_PCT if w.get("tactical")
                      else alloc * (REDUCE_FACTOR if w.get("reduced") else 1.0))
            for w in book.values())
        limit = teraz_brutto * (1 + MAX_EXPOSURE_STEP)
        if teraz_brutto > 0 and cel_brutto > limit:
            skala = limit / cel_brutto
            alloc = alloc * skala
            rep["ogranicznik_tempa"] = {
                "ekspozycja_teraz": round(teraz_brutto, 2),
                "ekspozycja_cel": round(cel_brutto, 2),
                "limit_na_bieg": round(limit, 2),
                "alloc_po_ograniczeniu": round(alloc, 4)}
            rep["pominiete"].append(
                f"ogranicznik tempa: cel {cel_brutto:.0f} {ccy} przekracza "
                f"limit {limit:.0f} {ccy} (+{MAX_EXPOSURE_STEP * 100:.0f}% "
                f"od {teraz_brutto:.0f}) — w tym biegu ALLOC_PCT "
                f"ograniczony do {alloc:.4f}")

    stracone = set()
    for p in positions:
        want = book.get(p["epic"])
        # poza koszykiem albo zmiana kierunku = zamknięta w pętli wyżej
        if not want or want["direction"] != p["direction"]:
            continue
        m = rynek(cap, p["epic"], rep, want["ticker"])
        if m is None:
            continue          # rynek zamknięty albo błąd — już opisane
        fx = cap.fx_rate(ccy, m["currency"])
        cur_acc = p["size"] * m["mid"] / fx
        cel_acc = equity * (TACTICAL_ALLOC_PCT if want.get("tactical")
                            else alloc * (REDUCE_FACTOR
                                          if want.get("reduced") else 1.0))
        if abs(cur_acc - cel_acc) <= cel_acc * REBALANCE_TOL:
            continue          # w paśmie — zostawiamy
        size, _, info = calc_size(cap, cel_acc, p["epic"], ccy)
        # Cichy brak wykonania redukcji: przy MU (kurs ~980 USD) cel po
        # redukcji to ~55 USD, a minimalna transakcja 0,1 akcji = ~98 USD,
        # więc calc_size zwracał None, pętla robiła "continue" i nikt się
        # nie dowiadywał, że signals.json mówi REDUCE, a portfel ma pełną
        # pozycję. Teraz każdy taki przypadek jest opisany, a zachowanie
        # wybiera REDUCE_FALLBACK.
        if size is None:
            if want.get("reduced") and REDUCE_FALLBACK == "close":
                do_close(p, f"REDUCE niewykonalny ({info}) — REDUCE_FALLBACK=close")
            else:
                rep["pominiete"].append(
                    f"{want['ticker']}: nie zmieniam wielkości — {info} "
                    f"(cel {cel_acc:.0f} {ccy}, obecnie {cur_acc:.0f} {ccy})")
            continue
        if size == p["size"]:
            rep["pominiete"].append(
                f"{want['ticker']}: krok wielkości nie pozwala podejść bliżej "
                f"celu {cel_acc:.0f} {ccy} (zostaje {cur_acc:.0f} {ccy})")
            continue
        if DRY_RUN:
            rep["akcje"].append(f"[DRY] WYRÓWNAJ {want['ticker']} "
                                f"z size {p['size']} (~{cur_acc:.0f} {ccy}) "
                                f"do size {size} (~{cel_acc:.0f} {ccy})")
            continue
        ok, msg = cap.close(p["dealId"])
        if not ok:
            rep["błędy"].append(f"wyrównanie {want['ticker']}: {msg}")
            continue
        ok2, ref, msg2 = cap.open(p["epic"], want["direction"], size)
        rep["akcje"].append(f"WYRÓWNANO {want['ticker']}: size {p['size']} "
                            f"-> {size}" if ok2
                            else f"BŁĄD wyrównania {want['ticker']}: {msg2}")
        if not ok2:
            # pozycja została zamknięta, a nie udało się otworzyć jej na nowo —
            # niech domknie ją blok otwarć niżej, zamiast czekać na kolejny bieg
            rep["błędy"].append(msg2)
            stracone.add(p["epic"])
        time.sleep(0.4)

    held = {p["epic"]: p["direction"] for p in positions
            if p["epic"] not in stracone}
    rep["wielkosc_docelowa"] = {
        "waluta": ccy,
        "koszyk": round(equity * alloc, 2),
        "koszyk_po_redukcji": round(equity * alloc * REDUCE_FACTOR, 2),
        "taktyczna": round(equity * TACTICAL_ALLOC_PCT, 2)}
    for epic, want in book.items():
        if held.get(epic) == want["direction"]:
            continue
        target = equity * (TACTICAL_ALLOC_PCT if want.get("tactical")
                           else alloc * (REDUCE_FACTOR
                                         if want.get("reduced") else 1.0))
        try:
            size, m, info = calc_size(cap, target, epic, ccy)
        except requests.HTTPError as e:
            rep["błędy"].append(f"{want['ticker']}: rynek niedostępny ({e})")
            continue
        if m["status"] != RYNEK_OTWARTY or not m["mid"]:
            # Rynek zamknięty (weekend, święto, przerwa) to POMINIĘCIE,
            # a nie błąd — sprawdzamy to przed brakiem wielkości, bo bez
            # ceny calc_size i tak nie ma z czego liczyć.
            rep["pominiete"].append(f"{want['ticker']}: rynek "
                                    f"{m['status'] or 'bez ceny'}")
            continue
        if size is None:
            rep["pominiete"].append(f"{want['ticker']}: {info}")
            continue
        if DRY_RUN:
            rep["akcje"].append(f"[DRY] OTWÓRZ {want['direction']} "
                                f"{want['ticker']} size {size} @ ~{m['mid']:.2f} "
                                f"{m['currency']} ({info})")
            continue
        ok, ref, msg = cap.open(epic, want["direction"], size)
        rep["akcje"].append(f"OTWARTO {want['direction']} {want['ticker']} "
                            f"size {size} (ref {ref})" if ok
                            else f"BŁĄD otwarcia {want['ticker']}: {msg}")
        if not ok:
            rep["błędy"].append(msg)
        time.sleep(0.4)

    # ZAPIS CEN WEJŚCIA do signals.json — żeby puls liczył wyzwalacze od
    # tego, po ile bot naprawdę wszedł, a nie od kursu odniesienia D0.
    if WRITE_FILLS and not DRY_RUN:
        try:
            po = [x for x in cap.positions() if x["epic"] in managed]
            nowe = {}
            for x in po:
                t = epic2tic.get(x["epic"])
                if t and x.get("wejscie"):
                    nowe[t] = {"cena": round(float(x["wejscie"]), 4),
                               "kierunek": x["direction"],
                               "wielkosc": x["size"],
                               "data": (x.get("otwarta") or "")[:10] or None}
            stare = sig.get("fills") or {}
            szczyt_stary = float(sig.get("equity_peak") or 0)
            # Próg 0,5% — inaczej każdy nowy szczyt o grosz robiłby commit.
            zmiana_szczytu = (KILL_TRAILING
                              and szczyt > max(szczyt_stary * 1.005,
                                               szczyt_stary + 0.01))
            if nowe != stare or zmiana_szczytu:
                sig["fills"] = nowe
                if KILL_TRAILING:
                    sig["equity_peak"] = round(szczyt, 2)
                save_signals(sig, sig_sha,
                             f"bot: ceny wejścia ({len(nowe)} pozycji)"
                             + (f", szczyt kapitału {szczyt:.2f}"
                                if zmiana_szczytu else ""))
                rep["zapis_fills"] = {"pozycje": len(nowe),
                                      "equity_peak": sig.get("equity_peak")}
        except Exception as e:
            # Zapis to udogodnienie, nie warunek handlu: konflikt sha
            # (puls zapisał plik w międzyczasie) nie może wywrócić biegu.
            rep["pominiete"].append(f"zapis cen wejścia pominięty: {e}")

    zam = len([a for a in rep["akcje"]
               if a.startswith(("ZAMKNIĘTO", "OTWARTO", "WYRÓWNANO", "[DRY]"))])
    # Błędy MUSZĄ być w powiadomieniu: nieudane zamknięcie (np. przy zamkniętym
    # rynku) nie trafia do licznika akcji i bez tego pola bieg wyglądałby na
    # spokojny "akcje: 0", choć portfel rozjechał się z sygnałami.
    ostrzezenia = []
    if not rep["kontrola_kapitalu"]["zgodne"]:
        ostrzezenia.append("⚠ KONTROLA KAPITAŁU")
    if rep.get("stopy"):
        ostrzezenia.append(f"⛔ STOP x{len(rep['stopy'])}")
    zlagodzone = [r for r in slad if r.get("wykonane") != r.get("wpis")]
    if zlagodzone:
        ostrzezenia.append(f"↓ bramka x{len(zlagodzone)}")
    notify(f"🤖 {BOT_NAME} /run v{sig['version']} | kapitał {equity:.2f} {ccy} | "
           f"akcje: {zam} | pominięte: {len(rep['pominiete'])} | "
           f"błędy: {len(rep['błędy'])} | "
           f"{'DRY-RUN' if DRY_RUN else 'DEMO'}"
           + (" | " + " ".join(ostrzezenia) if ostrzezenia else ""))
    if HEDGE_MODE == "index":
        long_cel = sum(equity * (TACTICAL_ALLOC_PCT if w.get("tactical")
                                 else alloc * (REDUCE_FACTOR
                                               if w.get("reduced") else 1.0))
                       for w in book.values() if w["direction"] == "BUY")
        hedge_cel = long_cel * HEDGE_RATIO
        hpos = [p for p in positions if p["epic"] == HEDGE_EPIC
                and p["direction"] == "SELL"]
        try:
            hm = cap.market(HEDGE_EPIC)
        except requests.HTTPError as e:
            hm, _ = None, rep["błędy"].append(f"hedge: brak rynku {HEDGE_EPIC}: {e}")
        if hm and hm["mid"]:
            fx = cap.fx_rate(ccy, hm["currency"])
            cur_acc = sum(p["size"] for p in hpos) * hm["mid"] / fx
            rep["hedge"] = {"epic": HEDGE_EPIC, "cel": round(hedge_cel, 2),
                            "biezacy": round(cur_acc, 2), "waluta": ccy}
            if hedge_cel <= 0 and hpos:
                for p in hpos:
                    do_close(p, "hedge zbędny — brak aktywnych longów")
            elif hedge_cel > 0 and abs(cur_acc - hedge_cel) > hedge_cel * HEDGE_TOL:
                for p in hpos:
                    do_close(p, "hedge — dopasowanie wielkości")
                step = hm["min"] if hm["min"] > 0 else 0.1
                size = round(math.floor((hedge_cel * fx / hm["mid"]) / step)
                             * step, 4)
                if size >= step:
                    if DRY_RUN:
                        rep["akcje"].append(f"[DRY] HEDGE SELL {HEDGE_EPIC} "
                                            f"size {size} (~{hedge_cel:.0f} {ccy})")
                    else:
                        ok, ref, msg = cap.open(HEDGE_EPIC, "SELL", size)
                        rep["akcje"].append(f"HEDGE SELL {HEDGE_EPIC} size {size}"
                                            f" — {msg}")
                        if not ok:
                            rep["błędy"].append(f"hedge: {msg}")
                    time.sleep(0.3)
                else:
                    rep["błędy"].append(
                        f"hedge: minimalna wielkość {step} × kurs "
                        f"{hm['mid']} ≈ {step * hm['mid'] / fx:.0f} {ccy} "
                        f"przekracza cel {hedge_cel:.0f} {ccy} — hedge "
                        f"NIEOTWARTY; rozważ inny instrument albo HEDGE_RATIO")

    return rep


# ----------------------------------------------------------------------------
# ENDPOINTY
# ----------------------------------------------------------------------------
def auth_ok():
    return request.args.get("token") == RUN_TOKEN


@app.get("/health")
def health():
    return jsonify(ok=True, wersja="1.7.2", dry_run=DRY_RUN, tryb=("DEMO" if CAPITAL_DEMO else "LIVE"), live_odblokowany=LIVE_ODBLOKOWANY)


@app.route("/generate", methods=["GET", "POST"])
def generate_ep():
    if not auth_ok():
        return jsonify(error="zły token"), 401
    mode = request.args.get("mode", "daily")
    if mode not in ("daily", "weekly"):
        return jsonify(error="mode: daily|weekly"), 400
    do_commit = request.args.get("commit", "true").lower() != "false"
    try:
        return jsonify(generate(mode, do_commit))
    except Exception as e:
        log.exception("Błąd generatora")
        notify(f"❌ {BOT_NAME} /generate {mode}: {e}. "
               f"Stare sygnały pozostają w mocy — decyzja ręczna.")
        return jsonify(error=str(e)), 500


@app.route("/run", methods=["GET", "POST"])
def run_ep():
    if not auth_ok():
        return jsonify(error="zły token"), 401
    try:
        return jsonify(sync())
    except Exception as e:
        log.exception("Błąd biegu")
        notify(f"❌ {BOT_NAME} /run: {e}")
        return jsonify(error=str(e)), 500


@app.get("/status")
def status_ep():
    if not auth_ok():
        return jsonify(error="zły token"), 401
    try:
        sig, _ = load_signals()
        cap = Capital()
        cap.login()
        snap = cap.account_snapshot()
        eq, ccy, acc = snap["equity"], snap["ccy"], snap["accountId"]
        konta = [{"accountId": a.get("accountId"),
                  "nazwa": a.get("accountName"),
                  "waluta": a.get("currency"),
                  "saldo": (a.get("balance") or {}).get("balance"),
                  "preferowane": a.get("preferred", False),
                  "aktywne_dla_bota": a.get("accountId") == acc}
                 for a in cap.accounts()]
        managed = {e for e in sig["epics"].values()
                   if e and not e.upper().startswith("UZUP")}
        if HEDGE_MODE == "index" and HEDGE_EPIC:
            managed.add(HEDGE_EPIC)
        return jsonify(blad_przelaczenia_rachunku=cap.switch_error,
                       konta_wszystkie=konta,
                       sygnaly={k: sig[k] for k in
                                ("version", "status", "long", "short",
                                 "exclude", "tactical")},
                       historia=sig.get("history", []),
                       konto={"accountId": acc, "kapital": eq, "waluta": ccy,
                              "saldo": snap["saldo"],
                              "wycena_pozycji": snap["wycena"]},
                       kontrola_kapitalu=kontrola_kapitalu(
                           snap, cap.positions(), managed,
                           {"błędy": [], "pominiete": []}),
                       ceny_wejscia=sig.get("fills", {}),
                       equity_peak=sig.get("equity_peak"),
                       ustawienia={"alloc_pct": ALLOC_PCT,
                                   "alloc_pct_safe": ALLOC_PCT_SAFE,
                                   "reduce_factor": REDUCE_FACTOR,
                                   "reduce_fallback": REDUCE_FALLBACK,
                                   "react_gate": REACT_GATE,
                                   "react_reduce_pct": REACT_REDUCE_PCT,
                                   "react_close_pct": REACT_CLOSE_PCT,
                                   "stop_loss_pct": STOP_LOSS_PCT,
                                   "kill_trailing": KILL_TRAILING,
                                   "kill_level": KILL_LEVEL,
                                   "max_exposure_step": MAX_EXPOSURE_STEP},
                       pozycje=[p for p in cap.positions()
                                if p["epic"] in managed],
                       dry_run=DRY_RUN)
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.get("/close_all")
def close_all_ep():
    if not auth_ok():
        return jsonify(error="zły token"), 401
    sig, _ = load_signals()
    cap = Capital()
    cap.login()
    if ACCOUNT_ID and cap.switch_error:
        return {"handel": "ZABLOKOWANY",
                "błąd": (f"CAPITAL_ACCOUNT_ID='{ACCOUNT_ID}' odrzucone przez "
                         f"Capital.com ({cap.switch_error}). Handel wstrzymany, "
                         "żeby nie działać na niewłaściwym rachunku. Otwórz "
                         "/status i skopiuj poprawne pole accountId z "
                         "'konta_wszystkie' (to NIE jest numer konta z aplikacji).")}
    managed = {e for e in sig["epics"].values()
               if e and not e.upper().startswith("UZUP")}
    if HEDGE_MODE == "index" and HEDGE_EPIC:
        managed.add(HEDGE_EPIC)
    managed |= {(t.get("epic") or "").strip()
                for t in sig.get("tactical", []) if (t.get("epic") or "").strip()}
    out = []
    for p in cap.positions():
        if p["epic"] in managed:
            if DRY_RUN:
                out.append(f"[DRY] zamknąłbym {p['epic']}")
            else:
                ok, msg = cap.close(p["dealId"])
                out.append(f"zamknięto {p['epic']}" if ok else f"błąd: {msg}")
    notify(f"{BOT_NAME}: ręczne CLOSE_ALL wykonane.")
    return jsonify(wynik=out)


@app.get("/search")
def search_ep():
    if not auth_ok():
        return jsonify(error="zły token"), 401
    cap = Capital()
    cap.login()
    if ACCOUNT_ID and cap.switch_error:
        return {"handel": "ZABLOKOWANY",
                "błąd": (f"CAPITAL_ACCOUNT_ID='{ACCOUNT_ID}' odrzucone przez "
                         f"Capital.com ({cap.switch_error}). Handel wstrzymany, "
                         "żeby nie działać na niewłaściwym rachunku. Otwórz "
                         "/status i skopiuj poprawne pole accountId z "
                         "'konta_wszystkie' (to NIE jest numer konta z aplikacji).")}
    return jsonify(wyniki=cap.search(request.args.get("q", "")))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
