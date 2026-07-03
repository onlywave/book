#!/bin/zsh
# ============================================================
#  DEPLOY AUTOMATICO — Book 4-Sleeve dashboard web
#  Doppio click. Fa TUTTO: crea il repo GitHub, carica i file,
#  attiva la pagina web e lancia il primo aggiornamento.
#  L'unica cosa che devi fare TU: autorizzare nel browser (1 volta).
# ============================================================
set -e
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:$PATH"
REPO="book"                       # nome del repository (cambialo qui se vuoi)
EXPECT_USER="onlywave"            # account atteso (solo per mostrare l'URL giusto)

echo "══════════════════════════════════════════════════════"
echo "  DEPLOY DASHBOARD BOOK 4-SLEEVE"
echo "══════════════════════════════════════════════════════"

command -v gh >/dev/null || { echo "❌ gh non trovato. Apri il Terminale e lancia:  brew install gh"; read "?Invio per chiudere"; exit 1; }

# 1) Autenticazione (una sola volta; se già fatto, salta)
if ! gh auth status >/dev/null 2>&1; then
  echo "▶︎ PASSO 1 — Autenticazione GitHub (si apre il browser, autorizza e torna qui)."
  gh auth login --hostname github.com --git-protocol https --web
fi
USER=$(gh api user -q .login)
echo "✓ Autenticato come: $USER"

# 2) Crea il repo (se non esiste) e fai il push
if gh repo view "$USER/$REPO" >/dev/null 2>&1; then
  echo "▶︎ Repo $USER/$REPO esiste già — aggiorno."
  git remote remove origin 2>/dev/null || true
  git remote add origin "https://github.com/$USER/$REPO.git"
  git branch -M main
  git push -u origin main --force
else
  echo "▶︎ PASSO 2 — Creo il repository pubblico e carico i file…"
  git branch -M main
  gh repo create "$REPO" --public --source=. --remote=origin --push
fi

# 3) Attiva GitHub Pages sulla cartella /docs
echo "▶︎ PASSO 3 — Attivo GitHub Pages (/docs)…"
gh api -X POST "repos/$USER/$REPO/pages" -f "source[branch]=main" -f "source[path]=/docs" >/dev/null 2>&1 \
  || gh api -X PUT "repos/$USER/$REPO/pages" -f "source[branch]=main" -f "source[path]=/docs" >/dev/null 2>&1 || true

# 4) Lancia subito il workflow di aggiornamento segnali
echo "▶︎ PASSO 4 — Primo aggiornamento segnali…"
gh workflow run update.yml 2>/dev/null || true

URL="https://$USER.github.io/$REPO/"
echo ""
echo "══════════════════════════════════════════════════════"
echo "  ✅ FATTO. La tua sala operativa sarà online tra 1-2 minuti:"
echo ""
echo "        $URL"
echo ""
echo "  (salvala sul telefono: Condividi → Aggiungi a Home)"
echo "══════════════════════════════════════════════════════"
command -v open >/dev/null && (sleep 90 && open "$URL") &
read "?Premi Invio per chiudere."
