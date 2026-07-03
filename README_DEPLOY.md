# 📖 Book 4-Sleeve — Dashboard Web (deploy in 5 minuti, gratis per sempre)

App web statica + GitHub Actions: i segnali si ricalcolano da soli ogni mattina,
la pagina è raggiungibile da qualunque dispositivo, i prezzi crypto sono live (Binance).
Nessun server, nessun costo, nessuna credenziale di trading.

## Deploy (una volta sola, dal browser)

1. **Crea il repository**: vai su https://github.com/new
   - Nome: `book` (o quello che vuoi) · **Public** · crea.

2. **Carica questi file** (pulsante *uploading an existing file*, trascina TUTTO il
   contenuto della cartella `book_web/` — comprese le sottocartelle):
   ```
   compute_signals_web.py
   README_DEPLOY.md
   .github/workflows/update.yml
   docs/index.html
   docs/signal.json            (già calcolato, così la pagina è viva da subito)
   docs/window_history.json
   ```
   ⚠️ Se il drag&drop non prende `.github/`, creala a mano: *Add file → Create new file* →
   scrivi come nome `.github/workflows/update.yml` e incolla il contenuto.

3. **Attiva la pagina web**: Settings → Pages → Source: *Deploy from a branch* →
   Branch `main`, cartella `/docs` → Save.

4. **Attiva l'aggiornamento automatico**: tab *Actions* → abilita i workflow →
   apri "Aggiorna segnali book" → *Run workflow* (prima esecuzione manuale di prova).

5. Dopo ~1 minuto la tua sala operativa è su:
   **`https://TUONOME.github.io/book/`**  ← salvala sul telefono (Aggiungi a Home)

## Cosa mostra
- Segnale per sleeve (🟢 LONG / ⚪ FLAT / 🔵 HOLD) con **media adattiva in uso** (es. MA43)
- **Prezzi live** BTC/ETH (Binance, refresh 30s) e distanza % dalla media
- **⚡ FLIP imminente** lampeggiante se il prezzo live attraversa la media (conferma alla chiusura daily)
- Stato **L3** (ON / VETO), drawdown ombra, equity backtest, storia delle finestre
- Target in € sul TUO capitale (lo inserisci nella pagina, resta solo sul tuo dispositivo)
- Box **"Cosa fare"**: prossimo allineamento settimanale o azione immediata

## Sicurezza & privacy
- Il repo contiene SOLO la logica dei segnali: niente capitale, niente broker, niente chiavi.
- Il capitale lo digiti nel browser e resta in localStorage del dispositivo.
- Esecuzione: MANUALE sul tuo broker (~92 operazioni/anno, 1 allineamento a settimana).

## Aggiornare la logica in futuro
Modifica `compute_signals_web.py` nel repo (o ricaricalo) — al run successivo delle
Actions i segnali si rigenerano con la nuova logica.
