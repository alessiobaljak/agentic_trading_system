import json, sys, time
sys.path.insert(0, "/home/user/agentic_trading_system")
import os; os.environ["TRADING_BOT_TEST_MODE"]="1"
sys.dont_write_bytecode=True
from bot.portafoglio.f5 import contratti_monete, ESCLUSI
info = json.load(open(sys.argv[1]))
c = contratti_monete(info)
print("contratti_monete:", len(c))
print("serverTime UTC:", time.strftime("%Y-%m-%d %H:%M", time.gmtime(info["serverTime"]/1000)))
for s in ("MITOUSDT","PTBUSDT"):
    x=[y for y in info["symbols"] if y["symbol"]==s]
    if x:
        x=x[0]; print(s, x["status"], x.get("contractType"), "deliveryDate", time.strftime("%Y-%m-%d %H:%M", time.gmtime(int(x["deliveryDate"])/1000)))
    else:
        print(s, "assente")
tr=[y for y in info["symbols"] if y.get("contractType")=="PERPETUAL" and y.get("quoteAsset")=="USDT" and y.get("status")=="TRADING"]
print("perpetui USDT in TRADING (tutti):", len(tr))
