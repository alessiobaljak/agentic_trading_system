"""Controlla quali librerie servono agli strumenti e quali mancano nella macchina della sessione."""
import importlib
import sys

print("python", sys.version.split()[0], sys.executable)
for nome in ["numpy", "scipy", "yaml", "pandas", "pytest", "requests"]:
    try:
        modulo = importlib.import_module(nome)
        print(nome, "presente", getattr(modulo, "__version__", "?"))
    except Exception as errore:  # noqa: BLE001
        print(nome, "MANCA", type(errore).__name__, errore)
