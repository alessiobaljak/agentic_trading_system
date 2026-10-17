#!/usr/bin/env bash
# Passo 0 del protocollo 4, punto 10: prepara il branch research/campagna/LINK6 con una storia propria (un solo
# commit, senza i commit del branch principale), senza i file vietati della sezione 12 e con un CLAUDE.md pulito.
# Uso: bash research/passo0_4/prepara_branch.sh <cartella di lavoro temporanea fuori dal repository>
set -euo pipefail
LAVORO="$1"
RADICE="$(git rev-parse --show-toplevel)"
BASE="$(git -C "$RADICE" rev-parse HEAD)"
git -C "$RADICE" worktree add --detach "$LAVORO" "$BASE"
cd "$LAVORO"
git checkout -q --orphan research/campagna/LINK6
# fuori dal branch: documenti, canale della macchina, e in research/ tutto tranne quello che la sessione legge
git rm -r -q --cached docs ops
git rm -r -q --cached research/CHANGELOG.md research/PROTOCOLLO.md research/PROTOCOLLO_2.md research/PROTOCOLLO_3.md \
  research/protocollo_4_note.md research/altre_monete_3 research/apertura research/collaudo_3 research/collaudo_4 \
  research/confronto research/esperimenti research/lezioni research/monete_di_controllo_4 research/passo0_2 \
  research/passo0_4 research/passo4 research/prova_processo research/taratura research/universo research/vault \
  research/vault_strumenti
for c in $(git ls-files research/campagne | cut -d/ -f3 | sort -u); do
  if [ "$c" != "LINK6" ]; then git rm -r -q --cached "research/campagne/$c"; fi
done
for f in $(git ls-files research/config); do
  case "$f" in
    research/config/parametri_4.yaml|research/config/bot_4.md|research/config/guida_pratica_4.md|research/config/percorsi_vietati.txt) ;;
    *) git rm -q --cached "$f" ;;
  esac
done
git clean -fdxq -e research/data
cp "$RADICE/research/passo0_4/CLAUDE_link6.md" CLAUDE.md
git add CLAUDE.md
git commit -q -F "$RADICE/research/passo0_4/messaggio_branch_link6.txt"
git ls-files | cut -d/ -f1-2 | sort -u
echo "commit: $(git rev-parse HEAD), file: $(git ls-files | wc -l)"
