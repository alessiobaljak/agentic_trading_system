import sys, json
sys.path.insert(0, '/home/user/agentic_trading_system')
from research.programma7 import quarantunesima as lv
from research.programma7 import quarantacinquesima as q
for i in sys.argv[1:]:
    t = lv.frammenti(json.loads((q.DATI / f"{i}.json").read_text())["body"])
    print("=====", i)
    print("\n".join(t)[:int(3500)])
