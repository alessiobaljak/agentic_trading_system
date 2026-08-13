"""QUANTI WORKER REGGE DAVVERO LA MACCHINA.

Ogni worker carica quattro anni di candele piu' il frame degli indicatori per un
simbolo: circa un giga e mezzo. Chiederne piu' di quanti la RAM ne regga non li
rende piu' veloci — li fa uccidere dal kernel a meta' validazione. Il servizio
risulta `failed` dopo ore di calcolo, e nel log dell'applicazione non c'e' niente
che lo spieghi: e' il tipo di guasto che si paga due volte, in tempo perso e in
tempo speso a capire.

Il tetto vale anche su un valore impostato a mano, ed e' voluto: un 8 esplicito che
finisce in OOM e' peggio di un 6 automatico che arriva in fondo.
"""
from backtesting.parallel import workers_for


def test_plenty_of_memory_grants_what_was_asked():
    assert workers_for(8, avail_gb=32.0, per_worker_gb=1.5) == 8


def test_little_memory_caps_the_request():
    """16 GB con 10 liberi: (10 - 1) / 1.5 = 6 worker, non 8."""
    assert workers_for(8, avail_gb=10.0, per_worker_gb=1.5) == 6


def test_a_gigabyte_stays_for_the_system_and_the_bot():
    """Il bot gira sulla stessa macchina ed e' lui che sorveglia le posizioni: la
    validazione non puo' mangiarsi l'ultima briciola di memoria."""
    assert workers_for(8, avail_gb=4.0, per_worker_gb=1.5) == 2   # (4-1)/1.5


def test_there_is_always_at_least_one_worker():
    """Meglio lento che fermo: con un solo processo la validazione finisce comunque."""
    assert workers_for(8, avail_gb=0.5, per_worker_gb=1.5) == 1
    assert workers_for(8, avail_gb=1.0, per_worker_gb=1.5) == 1


def test_an_unreadable_memory_is_not_a_limit():
    """Fuori da Linux (o se /proc non e' leggibile) non si inventa un tetto: si
    rispetta cio' che e' stato chiesto, come prima."""
    assert workers_for(8, avail_gb=0.0, per_worker_gb=1.5) == 8


def test_the_cap_never_raises_the_request():
    """Con molta RAM il tetto non deve AUMENTARE i worker: chi ne ha chiesti 2 ne
    vuole 2, magari perche' sta facendo altro sulla macchina."""
    assert workers_for(2, avail_gb=64.0, per_worker_gb=1.5) == 2


def test_a_bigger_estimate_per_worker_means_fewer_workers():
    assert workers_for(8, avail_gb=13.0, per_worker_gb=3.0) == 4
