# Fix di scoping `NO TRADE` — skill `bottleneck-portfolio-cio` + anti-tracimazione `emanuele-portfolio-architect`

Patch di accompagnamento all'intervento del 9 agosto 2026. Le tre scritture in memoria
(regola CAPACITÀ, memoria #8, memoria #3) sono già attive sull'account; questo patch copre
la parte che vive nei file skill, che sono montati in sola lettura nelle sessioni.

## Diagnosi (riepilogo)

`NO TRADE` era scritto come **preambolo globale** («Default operativo permanente») in testa a
`SKILL.md`, quindi agiva su ogni sessione che sfiorasse il tema, invece di valere come
**ipotesi nulla dell'esito del ciclo mensile di decisione di capitale**. Quattro occorrenze
"regola" in tre file; le occorrenze nell'enum delle decisioni CIO (`filtri_canonici.md:56`)
e nelle celle di tabella per singolo titolo (`current_state_2026-08-06.md:81/82/88`) sono
valori legittimi dell'output e restano intatte.

## Applicazione rapida

Dal root del repo che contiene le cartelle `bottleneck-portfolio-cio/` e
`emanuele-portfolio-architect/` (i path del diff sono relativi a quel root):

```bash
git checkout -b claude/no-trade-scoping-fix
git apply --check skill_fixes.patch   # verifica: nessun output = ok
git apply skill_fixes.patch
git add -A
git commit -m "Rescope NO TRADE: da preambolo globale a ipotesi nulla del ciclo di capitale"
git push -u origin claude/no-trade-scoping-fix
```

Se il layout del repo ha un prefisso diverso (es. `skills/bottleneck-portfolio-cio/`),
usare `git apply --directory=skills skill_fixes.patch`, oppure applicare a mano i cinque
blocchi qui sotto. Dopo il push, ricaricare/riabilitare le skill su claude.ai perché le
sessioni montano la copia caricata, non il repo.

## I cinque blocchi cerca/sostituisci

### 1. `bottleneck-portfolio-cio/SKILL.md` — riga 10 (preambolo)

**CERCA**

> **Default operativo permanente: NO TRADE.** Questa skill non autorizza alcuna esecuzione. Produce ricerca, classificazione, shadow target e checkpoint datati.

**SOSTITUISCI**

> **NO TRADE è l'ipotesi nulla del ciclo di decisione di capitale (§9), non una regola di sessione.** Vale come esito di default di ogni proposta di capitale finché riconciliazione ed evidenze non giustificano altro; non vieta né limita analisi, risposte o giudizi CIO conclusivi su titoli, settori o tesi. Questa skill non esegue ordini: produce ricerca, classificazione, shadow target, checkpoint datati e giudizi espliciti.

### 2. `bottleneck-portfolio-cio/SKILL.md` — riga 185 (stato datato in §10)

**CERCA**

> **Stato al 6 agosto 2026: RICERCA ATTIVA — RADAR IN ESPANSIONE — PORTAFOGLI NON RICONCILIATI — NO TRADE.**

**SOSTITUISCI**

> **Esito del ciclo al 6 agosto 2026: RICERCA ATTIVA — RADAR IN ESPANSIONE — PORTAFOGLI NON RICONCILIATI — NO TRADE.** È lo stato datato dell'ultimo checkpoint: decade al checkpoint successivo e non vincola le risposte delle sessioni correnti.

### 3. `bottleneck-portfolio-cio/references/portfolios_and_capital.md` — riga 75

**CERCA**

> Default operativo: **NO TRADE**.

**SOSTITUISCI**

> Ipotesi nulla del ciclo: **NO TRADE** finché i dieci passaggi del protocollo non sono completati con esito favorevole. È il default dell'esito di capitale, non un limite all'analisi o al giudizio.

### 4. `bottleneck-portfolio-cio/references/current_state_2026-08-06.md` — riga 149

**CERCA**

> **RICERCA ATTIVA — RADAR IN ESPANSIONE — PORTAFOGLI NON RICONCILIATI — NO TRADE.**

**SOSTITUISCI**

> **RICERCA ATTIVA — RADAR IN ESPANSIONE — PORTAFOGLI NON RICONCILIATI — esito del ciclo: NO TRADE** (checkpoint datato 2026-08-06: non è un divieto di sessione e non limita analisi o giudizi conclusivi).

### 5. `emanuele-portfolio-architect/SKILL.md` — blocco anti-tracimazione

Inserire subito dopo il paragrafo introduttivo («This skill produces educational
analysis…»), prima di `## Effort scaling`:

```markdown
## Scope isolation

This skill is independent of `bottleneck-portfolio-cio`. That skill's cycle rules — its
`NO TRADE` null hypothesis, monthly checkpoint cadence, and reconciliation gates — govern
only the GLOBAL BOTTLENECK mandates and never carry over here. Never decline, defer, or
dilute an answer within this skill's scope by citing another skill's rules.
```

## Cosa NON toccare

- `bottleneck-portfolio-cio/references/filtri_canonici.md` riga 56: `NO TRADE` nell'enum
  delle decisioni CIO è un valore legittimo dell'output — rimuoverlo amputerebbe una
  decisione possibile invece di liberarla.
- `current_state_2026-08-06.md` righe 81, 82, 88: `WATCH / NO TRADE`, `HOLD / NO TRADE`
  nelle tabelle sono decisioni datate per singolo titolo, non preamboli.

## Test funzionale di verifica

Dopo il ricaricamento delle skill, in una **nuova** sessione:

1. **Non deve più bloccare.** Chiedere: *«Che ne pensi di Schneider Electric in capacità
   propria? Dammi giudizio conclusivo, sizing e livelli.»* — Atteso: analisi conclusiva con
   giudizio esplicito compra/vendi/tieni, senza citare `NO TRADE` come motivo per non
   rispondere e senza rinvio a un consulente.
2. **Deve ancora valere dove serve.** Chiedere: *«Prepara la proposta di capitale del
   ciclo, i report riconciliati non ci sono.»* — Atteso: l'esito resta `NO TRADE` come
   ipotesi nulla del ciclo, dichiarando che mancano le riconciliazioni.
3. **Niente tracimazione.** Attivare `emanuele-portfolio-architect` su un tema Ferreri
   core-satellite — Atteso: nessuna citazione delle regole bottleneck.
