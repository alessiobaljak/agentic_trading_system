import re, sys
sys.path.insert(0, '/home/user/agentic_trading_system')
from research.src import registro as r
righe = open('/home/user/agentic_trading_system/research/REGISTRO.md', encoding='utf-8').read().splitlines()
ap = re.compile(r"^(\d+)\.\s+\*\*(.+?)\*\*")
ch = re.compile(r"^\d+\.\s+~~")
out = []
for i, riga in enumerate(righe, 1):
    if ch.match(riga):
        continue
    m = ap.match(riga)
    if m:
        out.append((i, int(m.group(1)), riga))
print('aperte secondo lo schema:', len(out))
with open('/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/punti_ciechi/idee_aperte.txt', 'w') as f:
    for i, n, riga in out:
        # il testo intero della voce: fino alla prossima riga numerata o vuota
        j = i
        testo = [riga]
        while j < len(righe) and righe[j].strip() and not re.match(r"^\d+\.\s", righe[j]):
            testo.append(righe[j]); j += 1
        f.write(f"### riga {i} voce {n}\n" + "\n".join(testo) + "\n\n")
print([ (i, n) for i, n, _ in out])
