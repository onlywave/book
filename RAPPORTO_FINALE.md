# 🏛️ RAPPORTO FINALE & HANDOFF DEFINITIVO — Book 4·Sleeve
**Data:** 2026-07-04 · **Stato:** sistema LIVE, operatività manuale, monitoraggio web + email.
**Questo documento è la fonte di verità unica.** Se riparti da zero o da un altro PC, leggi solo questo.

---

## 1. COS'È, IN UNA PAGINA
Un sistema di trading **quantitativo, semplice e onesto** su 4 asset (Bitcoin, Ethereum, S&P 500, Oro).
Non prevede la direzione dei prezzi (impossibile sui mercati liquidi, dimostrato): **segue il trend dove esiste
e diversifica dove non esiste**. Esecuzione **manuale** (~1,8 operazioni a settimana), monitorata da una
dashboard web pubblica e da alert via email.

- **Numeri (walk-forward, tutti i costi, 7,7 anni):** CAGR **+20,8%** · Sharpe **1,52** · perdita max **−18%**.
- **Dashboard live (da ovunque, senza login):** **https://onlywave.github.io/book/**
- **Repository:** https://github.com/onlywave/book (pubblico; contiene solo la logica, nessuna credenziale).

---

## 2. LA STRATEGIA — 3 livelli
```
L1 DIREZIONE   BTC, ETH → media mobile ADATTIVA (long/flat): prezzo sopra = dentro, sotto = fuori.
               SPX, XAU → DETENUTI sempre (lì il timing distrugge valore: meglio possederli).
L2 QUANTO      size = min(1, 30% / volatilità): più un asset balla, meno se ne mette. Mai leva.
L3 SICUREZZA   se il portafoglio perde 15% dal massimo → chiude tutto; rientra sopra −9%.
               (Isteresi su equity "ombra": 1 solo evento in 7,7 anni.)
PESI           25% ciascuno dei 4 sleeve.
```
**La media NON è fissa:** viene ricalcolata ogni settimana (regola minimax-plateau, isteresi ±20) scegliendo
la zona più robusta. Oggi: **BTC = 43 giorni · ETH = 58 giorni**. Non è "la 200": è adattiva e per-asset.

**Perché questi 4:** BTC/ETH hanno un trend vero e sfruttabile; SPX/Oro danno diversificazione (correlazione ~0
con le cripto) → è il mix che alza lo Sharpe a parità di rischio. Bond e valute esclusi (nessun vantaggio).

---

## 3. LA STORIA (come ci siamo arrivati, onestamente)
1. **Motore 8 LLM** (`~/financial_ai_simulator`) per prevedere la direzione → **refutato** (bootstrap/OOS/Bonferroni): niente edge direzionale sui mercati liquidi.
2. **App intraday MT5** (`~/operativita_real_time`) con ponte MT5 collaudato → in demo reale ha perso −4.641€. **Post-mortem:** uscite di sistema +256€, uscite MANUALI di panico −4.897€. Lezione: mai chiusure emotive.
3. **PIVOT (27/06):** l'alpha è nel layer regime/rischio, non nei forecaster. Edge veri solo su BTC/ETH via media.
4. **God-mode (1-4 luglio):** verifica indipendente (BTC edge confermato su yahoo+TradingView; ETH è L/F non L/S), book 4-sleeve, stress-test 54 configurazioni (plateau, non picco), 48.000 forecast LLM (direzione morta, ma lo **spread** dei quantili prevede la **volatilità** → gli LLM utili solo in L2, opzionale).
5. **Produttivizzazione:** L3 corretto (shadow+isteresi), cadenza esecuzione validata (~92 ops/anno), dashboard web, alert email, automazione cloud.

**Cosa NON rifare (già pagato):** direzione dagli LLM · short su ETH · leva · timing su SPX/XAU/bond/FX · trailing stretti (overfit) · FERMA TUTTO di pancia · micro-ottimizzazioni.

---

## 4. TRACK RECORD (2018→2026)
| | Valore |
|---|---|
| Rendimento medio annuo (CAGR) | +20,8% |
| Sharpe (rendimento/rischio) | 1,52 |
| Perdita massima (drawdown) | −18% |
| Mesi positivi | 56% (52/93) |
| Anni in utile | 6 su 9 (unico anno pieno negativo: 2022, −9,6%) |
| Crescita totale | ×4,2 (€100k → €420k) |

Rischio da accettare: una discesa del ~18% dal picco è normale e va **attraversata senza vendere** — è quando L3 protegge.

---

## 5. COME SI OPERA (manuale, ~5 min/settimana)
1. **Una volta a settimana** (es. lunedì): apri la dashboard o guarda l'email di recap.
2. Porta il conto alle **percentuali indicate** (banda ±5%): ETF per S&P 500 e Oro, exchange/ETF per cripto, il resto liquido.
3. **Subito** se arriva l'email `***ALLERTA SEGNALE***` o vedi il badge ⚡CAMBIO: un asset ha attraversato la media → agisci a fine giornata.
4. **Mai** trade di impulso. Nient'altro.

Gli ordini restano **decisione umana**: nessun sistema invia ordini con soldi reali al posto tuo.

---

## 6. INFRASTRUTTURA LIVE (cosa gira, dove)
| Componente | Dove | Ruolo |
|---|---|---|
| **Dashboard web** | https://onlywave.github.io/book/ (GitHub Pages) | monitor pubblico, prezzi live Binance, track record, medie |
| **Repo** | github.com/onlywave/book | codice: `docs/index.html`, `compute_signals_web.py`, `notify.py`, `.github/workflows/update.yml` |
| **Automazione** | GitHub Actions (cron 06:40 UTC) | ricalcola segnali · email su cambio · recap lunedì · si aggiorna anche a Mac spento |
| **Email** | SMTP Gmail (secret) | alert + recap a ebferreri@egonon.ch e ebferreri@gmail.com |
| **Sorgente locale** | `~/operativita_real_time/book_web/` | copia di lavoro; `.venv_book` per rigenerare in locale |

**"Live per sempre":** sì, perché il calcolo e le email girano su GitHub (cloud), non sul tuo Mac. Il Mac serve solo se vuoi rigenerare a mano o lavorare su L2b.

---

## 7. MANUTENZIONE
- **Automatica (cloud):** il workflow gira ogni giorno; se fallisce, GitHub ti manda un'email di errore. Il recap del lunedì è anche la conferma "tutto ok".
- **Controllo del decadimento:** guarda il grafico "evoluzione della media" in dashboard. Se BTC esce stabilmente dalla zona ~35-50 o ETH da ~120-140 → l'edge su quell'asset sta decadendo: riducilo.
- **Quando rigirare L2 (pesi/LLM):** L2b (spread LLM → volatilità) richiede il motore 8-modelli (~6GB, solo in locale). **Non urgente** (migliora solo il drawdown di BTC di pochi punti). Consiglio: **ri-valutarlo ogni 3 mesi** o quando il grafico delle medie mostra decadimento. Comando locale: `~/financial_ai_simulator/.venv/bin/python l2b_today.py`.

---

## 8. COSA MANCA (azioni una-tantum, solo tue — riguardano credenziali)
1. **Autorizzare lo scope `workflow`** su GitHub (device code) → per attivare l'automazione. *(fatto una volta)*
2. **Creare una Gmail App Password** (myaccount.google.com → Sicurezza → Password per le app) e aggiungerla come **GitHub Secret** `MAIL_PASSWORD`, con `MAIL_USERNAME=ebferreri@gmail.com`. *(io non posso vedere password: le inserisci tu nei Secret del repo)*
3. Poi: tab **Actions → Run workflow** con "test_email" = true → arriva la prima email vera.

Finché il punto 2 non è fatto, il sistema **calcola e pubblica** i segnali ma **non invia** email (li vedi comunque in dashboard). La bozza di test è già nella tua Gmail → Bozze.

---

## 9. FILE E AMBIENTE
- **Web/automazione:** `~/operativita_real_time/book_web/` (= repo onlywave/book).
- **Motore book locale:** `~/operativita_real_time/` — `book_daily.py`, `_book_lib.py`, `align_book.py` (executor demo MT5), `dashboard_book.py` (sala operativa locale :8503).
- **Venv:** `~/operativita_real_time/.venv_book` (leggero: numpy/pandas/yfinance/streamlit). Motore 8-LLM: `~/financial_ai_simulator/.venv` (pesante, opzionale).
- **Export completo precedente:** `~/Desktop/EXPORT_OPERATIVITA_RT_20260703/`.
- **Vincoli:** Python 3.12; cartelle locali (mai iCloud/OneDrive per i venv). Ordini reali solo su demo, cutover sempre umano.

---

## 10. PROSSIMI SVILUPPI (facoltativi)
- 5° sleeve scorrelato (il vero upgrade di Sharpe: aggiungere edge indipendenti).
- L2b in produzione se il motore viene messo su un server.
- App mobile/PWA (la dashboard è già usabile "Aggiungi a Home").

*Fine rapporto. Il sistema è vivo, semplice, onesto e documentato. Sopravvivere prima di guadagnare.*
