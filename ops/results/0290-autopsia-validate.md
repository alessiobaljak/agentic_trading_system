# 0290-autopsia-validate.req

_eseguito: 2026-09-27 06:12 UTC_

**richiesta:** `autopsia-validate`
**eseguito:** `.venv/bin/python -m scripts.autopsia_validate`
**esito:** codice 0 in 782.5s

```
[firebase] connesso (Firestore + RTDB)
[autopsia] 212 validate · 212 coppie su 68 coin da valutare a 15m · dati 2022-01-01->2026-09-27
[paper] 30 verdetti trailing (11 prematuri, 19 protetti) -> keep candidato dal vissuto: 0.75 (si aggiunge ai 3 fissi, non li sostituisce: sceglie il gate)
[paper] 111 trade chiusi -> scala candidata dal vissuto: [0.75, 1.25, 2.0] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
[parallel] worker ridotti da 8 a 6: 14.4 GB disponibili, ~2 GB per worker (alza BACKTEST_MEM_PER_WORKER_GB se la stima e' pessimistica)
[autopsia] 6 worker · configurazione globale 1.5/3/5 BE keep0.5 · deadline 720s
[backtest] dati da cache: 165985 candele (BTCUSDT 15m)
[backtest] dati da cache: 165985 candele (BTCUSDT 15m)
[backtest] dati da cache: 165985 candele (BTCUSDT 15m)
[backtest] dati da cache: 165985 candele (BTCUSDT 15m)
[backtest] dati da cache: 165985 candele (BTCUSDT 15m)
[backtest] dati da cache: 165985 candele (BTCUSDT 15m)
[backtest] dati da cache: 37711 candele (HEMIUSDT 15m)
[backtest] dati da cache: 46797 candele (HUMAUSDT 15m)
[backtest] dati da cache: 48058 candele (SKYAIUSDT 15m)
[backtest] dati da cache: 63205 candele (ORCAUSDT 15m)
[backtest] dati da cache: 165985 candele (DOTUSDT 15m)
[backtest] dati da cache: 39024 candele (USELESSUSDT 15m)
[autopsia] 20/212 coppie valutate · 148s
[autopsia] 40/212 coppie valutate · 155s
[autopsia] HEMIUSDT: 11 coppie in 48s
[backtest] dati da cache: 53514 candele (MUBARAKUSDT 15m)
[autopsia] USELESSUSDT: 8 coppie in 46s
[backtest] dati da cache: 43069 candele (BULLAUSDT 15m)
[autopsia] HUMAUSDT: 10 coppie in 71s
[backtest] dati da cache: 37411 candele (QUSDT 15m)
[autopsia] ORCAUSDT: 15 coppie in 74s
[autopsia] SKYAIUSDT: 8 coppie in 75s
[backtest] dati da cache: 126087 candele (STXUSDT 15m)
[autopsia] 60/212 coppie valutate · 202s
[backtest] dati da cache: 59085 candele (TRUMPUSDT 15m)
[autopsia] 80/212 coppie valutate · 228s
[autopsia] BULLAUSDT: 6 coppie in 57s
[backtest] dati da cache: 165985 candele (VETUSDT 15m)
[autopsia] MUBARAKUSDT: 7 coppie in 68s
[backtest] dati da cache: 38363 candele (XPLUSDT 15m)
[autopsia] QUSDT: 6 coppie in 53s
[backtest] dati da cache: 56189 candele (GPSUSDT 15m)
[autopsia] 100/212 coppie valutate · 259s
[autopsia] TRUMPUSDT: 6 coppie in 72s
[backtest] dati da cache: 62830 candele (SPXUSDT 15m)
[autopsia] XPLUSDT: 6 coppie in 43s
[backtest] dati da cache: 48639 candele (SYRUPUSDT 15m)
[autopsia] 120/212 coppie valutate · 301s
[autopsia] GPSUSDT: 5 coppie in 60s
[backtest] dati da cache: 61491 candele (DEXEUSDT 15m)
[autopsia] SPXUSDT: 5 coppie in 62s
[backtest] dati da cache: 70995 candele (NEIROUSDT 15m)
[autopsia] DOTUSDT: 18 coppie in 221s
[backtest] dati da cache: 59180 candele (AVAAIUSDT 15m)
[autopsia] STXUSDT: 6 coppie in 147s
[autopsia] SYRUPUSDT: 5 coppie in 62s
[backtest] dati da cache: 36742 candele (FLOCKUSDT 15m)
[backtest] dati da cache: 104975 candele (BICOUSDT 15m)
[autopsia] DEXEUSDT: 4 coppie in 59s
[backtest] dati da cache: 56701 candele (HEIUSDT 15m)
[autopsia] 140/212 coppie valutate · 377s
[autopsia] FLOCKUSDT: 3 coppie in 39s
[backtest] dati da cache: 98169 candele (JTOUSDT 15m)
[autopsia] VETUSDT: 6 coppie in 167s
[backtest] dati da cache: 75993 candele (RENDERUSDT 15m)
[autopsia] AVAAIUSDT: 3 coppie in 65s
[backtest] dati da cache: 43825 candele (SAHARAUSDT 15m)
[autopsia] NEIROUSDT: 4 coppie in 80s
[backtest] dati da cache: 52643 candele (WALUSDT 15m)
[autopsia] HEIUSDT: 3 coppie in 64s
[backtest] dati da cache: 50423 candele (BANKUSDT 15m)
[autopsia] 160/212 coppie valutate · 444s
[autopsia] BICOUSDT: 3 coppie in 105s
[backtest] dati da cache: 87023 candele (ENAUSDT 15m)
[autopsia] SAHARAUSDT: 3 coppie in 49s
[backtest] dati da cache: 45363 candele (HOMEUSDT 15m)
[autopsia] WALUSDT: 3 coppie in 55s
[autopsia] RENDERUSDT: 3 coppie in 73s
[backtest] dati da cache: 53133 candele (PLUMEUSDT 15m)
[backtest] dati da cache: 36813 candele (OPENUSDT 15m)
[autopsia] BANKUSDT: 2 coppie in 45s
[backtest] dati da cache: 59375 candele (PROMUSDT 15m)
[autopsia] JTOUSDT: 3 coppie in 106s
[backtest] dati da cache: 67641 candele (SCRUSDT 15m)
[autopsia] HOMEUSDT: 2 coppie in 42s
[backtest] dati da cache: 119169 candele (SUIUSDT 15m)
[autopsia] OPENUSDT: 2 coppie in 40s
[backtest] dati da cache: 41539 candele (TAUSDT 15m)
[autopsia] PLUMEUSDT: 2 coppie in 57s
[backtest] dati da cache: 79733 candele (ZKUSDT 15m)
[autopsia] ENAUSDT: 2 coppie in 84s
[autopsia] PROMUSDT: 2 coppie in 57s
[backtest] dati da cache: 59277 candele (ARCUSDT 15m)
[backtest] dati da cache: 165985 candele (ATOMUSDT 15m)
[autopsia] TAUSDT: 2 coppie in 39s
[backtest] dati da cache: 166081 candele (AXSUSDT 15m)
[autopsia] 180/212 coppie valutate · 566s
[autopsia] SCRUSDT: 2 coppie in 76s
[backtest] dati da cache: 48811 candele (B2USDT 15m)
[autopsia] ARCUSDT: 1 coppie in 56s
[backtest] dati da cache: 37879 candele (BTRUSDT 15m)
[autopsia] ZKUSDT: 2 coppie in 79s
[backtest] dati da cache: 42583 candele (CROSSUSDT 15m)
[autopsia] B2USDT: 1 coppie in 45s
[backtest] dati da cache: 166081 candele (EGLDUSDT 15m)
[autopsia] SUIUSDT: 2 coppie in 120s
[backtest] dati da cache: 54017 candele (EPICUSDT 15m)
[autopsia] BTRUSDT: 1 coppie in 35s
[backtest] dati da cache: 53345 candele (FORMUSDT 15m)
[autopsia] CROSSUSDT: 1 coppie in 37s
[backtest] dati da cache: 165985 candele (GALAUSDT 15m)
[autopsia] EPICUSDT: 1 coppie in 48s
[backtest] dati da cache: 60619 candele (GRIFFAINUSDT 15m)
[autopsia] FORMUSDT: 1 coppie in 48s
[backtest] dati da cache: 155507 candele (JASMYUSDT 15m)
[autopsia] ATOMUSDT: 1 coppie in 160s
[backtest] dati da cache: 92951 candele (JUPUSDT 15m)
[autopsia] AXSUSDT: 1 coppie in 157s
[backtest] dati da cache: 37855 candele (MITOUSDT 15m)
[autopsia] GALAUSDT: 1 coppie in 74s
[autopsia] MITOUSDT: 1 coppie in 13s
[autopsia] GRIFFAINUSDT: 1 coppie in 55s
[autopsia] JUPUSDT: 1 coppie in 42s
[autopsia] JASMYUSDT: 1 coppie in 63s
[autopsia] EGLDUSDT: 1 coppie in 156s

COPPIA                               CONFIG OPERATA         (A) gate oggi    (B) config op.   CLASSE       PF(trade) ultimi 45g / 120g / 180g
FLOCKUSDT|gen_f3124a14               1/2/3 BE keep0.75      NO:recovery      PASSA            artefatto    2.227(14) / 1.663(29) / 1.888(46)
GPSUSDT|gen_871647b8                 2/4/6 BE keep0.5       NO:consistency   PASSA            artefatto    1.737(7) / 1.518(29) / 1.74(47)
HUMAUSDT|gen_da39a23a                1/1.5/2.5 BE keep0.75  NO:regime        PASSA            artefatto    1.302(7) / 2.548(23) / 2.774(36)
MUBARAKUSDT|gen_1e2af031             2/4/6 BE keep0.35      NO:recovery      PASSA            artefatto    11.873(6) / 6.569(12) / 5.217(15)
SAHARAUSDT|gen_6b94025f              2/4/6 BE keep0.35      NO:regime        PASSA            artefatto    3.44(12) / 1.798(31) / 1.938(49)
XPLUSDT|gen_d32ec7de                 2/4/6 BE keep0.5       NO:recovery      PASSA            artefatto    0.629(17) / 0.902(39) / 1.075(63)
ARCUSDT|gen_96c1ed1b                 2/4/6 BE keep0.5       NO:total_return  NO:total_return  bocciata     5.673(4) / 1.648(24) / 1.395(31)
ATOMUSDT|gen_eaa569ba                1/2/3 BE keep0.5       NO:regime        NO:regime        bocciata     2.659(5) / 0.833(14) / 0.624(15)
AVAAIUSDT|gen_14e1775b               1.5/3/5 BE keep0.5     NO:holdout       = A              bocciata     0.415(5) / 1.14(16) / 1.354(24)
AVAAIUSDT|gen_68ebd3b9               1.5/3/5 BE keep0.5     NO:holdout       = A              bocciata     0.415(5) / 1.14(16) / 1.354(24)
AVAAIUSDT|gen_e50a9211               1.5/3/5 BE keep0.5     NO:regime        = A              bocciata     3.755(8) / 1.264(24) / 1.404(32)
AXSUSDT|gen_b922252e                 1.5/3/5 BE keep0.5     NO:consistency   = A              bocciata     999(2) / 2.601(7) / 3.354(8)
B2USDT|gen_ddb3def9                  2/4/6 BE keep0.5       NO:recovery      NO:consistency   bocciata     2.694(8) / 1.685(26) / 1.615(46)
BANKUSDT|gen_1efbb088                1.5/3/5 BE keep0.5     NO:recovery      = A              bocciata     999(4) / 1.295(7) / 0.963(14)
BANKUSDT|gen_fb3d971f                2/4/6 BE keep0.5       NO:recovery      NO:consistency   bocciata     999(4) / 1.571(8) / 0.988(17)
BICOUSDT|gen_2e6776ad                1.5/3/5 BE keep0.5     NO:consistency   = A              bocciata     999(5) / 3.853(11) / 2.337(24)
BICOUSDT|gen_35632db9                1.5/3/5 BE keep0.5     NO:consistency   = A              bocciata     999(5) / 3.853(11) / 2.337(24)
BICOUSDT|gen_f238d283                2/4/6 BE keep0.5       NO:total_return  NO:total_return  bocciata     1.894(8) / 1.833(25) / 1.655(39)
BTRUSDT|gen_8981d5f2                 1.5/3/5 BE keep0.5     NO:consistency   = A              bocciata     0.973(13) / 0.866(38) / 0.797(55)
BULLAUSDT|gen_2e8fb80a               2/4/6 BE keep0.5       NO:holdout       NO:holdout       bocciata     2.876(4) / 1.563(15) / 2.563(19)
BULLAUSDT|gen_3f1b628b               2/4/6 BE keep0.5       NO:consistency   NO:consistency   bocciata     9.399(7) / 7.903(14) / 3.656(20)
BULLAUSDT|gen_6df6961d               2/4/6 BE keep0.5       NO:holdout       NO:holdout       bocciata     2.876(4) / 1.563(15) / 2.563(19)
BULLAUSDT|gen_7ac562e3               1.5/3/5 BE keep0.5     NO:holdout       = A              bocciata     999(4) / 2.945(15) / 4.089(19)
BULLAUSDT|gen_99c9c036               1/1.75/3 BE keep0.5    NO:recovery      NO:regime        bocciata     999(8) / 999(15) / 18.254(17)
BULLAUSDT|gen_c8aa0d13               2/4/6 BE keep0.5       NO:holdout       NO:holdout       bocciata     2.876(4) / 1.563(15) / 2.563(19)
CROSSUSDT|gen_d606fde3               2/4/6 BE keep0.5       NO:regime        NO:regime        bocciata     1.257(9) / 1.454(29) / 1.609(40)
DEXEUSDT|gen_887d87df                1.5/3/5 BE keep0.5     NO:consistency   = A              bocciata     5.175(10) / 1.963(46) / 1.482(69)
DEXEUSDT|gen_b31d8b93                2/4/6 BE keep0.5       NO:consistency   NO:consistency   bocciata     999(6) / 2.946(25

[... 15773 caratteri omessi (testa e coda conservate) ...]

/3/5 BE keep0.5     NO:total_return  = A              bocciata     3.319(7) / 1.775(18) / 1.745(25)
SYRUPUSDT|gen_af734c68               1.5/3/5 BE keep0.5     NO:recovery      = A              bocciata     1.492(21) / 2.048(30) / 1.595(51)
SYRUPUSDT|gen_b7d57ce7               2/4/6 BE keep0.5       NO:holdout       NO:holdout       bocciata     1.222(20) / 1.411(30) / 1.378(51)
SYRUPUSDT|gen_f3b97917               1/1.5/2.5 BE keep0.5   NO:consistency   NO:consistency   bocciata     999(7) / 4.237(16) / 2.546(26)
TAUSDT|gen_b028553e                  1.5/3/5 BE keep0.5     NO:consistency   = A              bocciata     999(5) / 1.881(17) / 1.466(25)
TAUSDT|gen_bf2be656                  1.5/3/5 BE keep0.5     NO:recovery      = A              bocciata     1.44(16) / 1.59(37) / 1.579(46)
TRUMPUSDT|gen_0e000630               2/4/6 BE keep0.75      NO:total_return  NO:total_return  bocciata     2.452(7) / 1.489(22) / 1.058(34)
TRUMPUSDT|gen_108c996b               2/4/6 BE keep0.5       NO:total_return  NO:total_return  bocciata     1.976(8) / 1.68(19) / 1.445(27)
TRUMPUSDT|gen_452d4511               2/4/6 BE keep0.5       NO:consistency   NO:consistency   bocciata     1.375(9) / 1.36(30) / 1.392(42)
TRUMPUSDT|gen_8c450b67               2/4/6 BE keep0.5       NO:holdout       NO:holdout       bocciata     0.996(24) / 1.139(59) / 1.171(88)
TRUMPUSDT|gen_93131ef1               2/4/6 BE keep0.5       NO:total_return  NO:total_return  bocciata     1.976(8) / 1.68(19) / 1.445(27)
TRUMPUSDT|gen_f156ca1b               2/4/6 BE keep0.5       NO:total_return  NO:total_return  bocciata     1.976(8) / 1.68(19) / 1.445(27)
USELESSUSDT|gen_1623b4cb             1.5/3/5 BE keep0.5     NO:holdout       = A              bocciata     1.85(3) / 1.08(9) / 1.667(17)
USELESSUSDT|gen_194e2514             2/4/6 BE keep0.5       NO:recovery      NO:recovery      bocciata     6.814(5) / 2.874(25) / 1.904(39)
USELESSUSDT|gen_1bb04e1a             2/4/6 BE keep0.5       NO:recovery      NO:recovery      bocciata     6.814(5) / 2.874(25) / 1.904(39)
USELESSUSDT|gen_2031005e             2/4/6 BE keep0.5       NO:total_return  NO:total_return  bocciata     0.918(41) / 1.148(84) / 0.885(136)
USELESSUSDT|gen_68a8a9c7             2/4/6 BE keep0.5       NO:recovery      NO:recovery      bocciata     999(4) / 3.175(23) / 1.983(37)
USELESSUSDT|gen_acea368d             2/4/6 BE keep0.5       NO:consistency   NO:recovery      bocciata     2.475(5) / 1.207(25) / 0.947(41)
USELESSUSDT|gen_c0fd1d91             1.5/3/5 BE keep0.5     NO:total_return  = A              bocciata     1.397(17) / 1.39(52) / 0.913(80)
USELESSUSDT|gen_fa5179ea             2/4/6 BE keep0.5       NO:recovery      NO:recovery      bocciata     1.632(8) / 1.858(33) / 1.468(49)
VETUSDT|gen_6d06dca0                 2/4/6 BE keep0.5       NO:total_return  NO:total_return  bocciata     0.386(31) / 0.494(57) / 0.573(85)
VETUSDT|gen_b2f350ff                 2/4/6 BE keep0.5       NO:consistency   NO:recovery      bocciata     1.345(6) / 2.355(17) / 1.501(28)
VETUSDT|gen_b9c251a1                 1/1.5/2.5 BE keep0.5   NO:consistency   NO:consistency   bocciata     999(5) / 999(13) / 5.572(24)
VETUSDT|gen_f3124a14                 1.5/3/5 BE keep0.5     NO:regime        = A              bocciata     0.237(9) / 0.504(20) / 0.677(33)
VETUSDT|gen_fb3d971f                 2/4/6 BE keep0.5       NO:consistency   NO:consistency   bocciata     0.866(5) / 2.238(16) / 1.576(25)
VETUSDT|gen_fca11c08                 1.5/3/5 BE keep0.5     NO:consistency   = A              bocciata     999(5) / 10.309(14) / 2.659(25)
WALUSDT|gen_2b41880d                 2/4/6 BE keep0.5       NO:regime        NO:regime        bocciata     2.219(5) / 1.319(18) / 2.01(29)
WALUSDT|gen_cee79cdd                 2/4/6 BE keep0.5       NO:holdout       NO:holdout       bocciata     1.811(4) / 1.452(13) / 1.943(24)
WALUSDT|gen_f238d283                 2/4/6 BE keep0.5       NO:total_return  NO:total_return  bocciata     1.344(13) / 1.228(38) / 0.929(58)
XPLUSDT|gen_0a991220                 1.5/3/5 BE keep0.5     NO:regime        = A              bocciata     0.683(4) / 0.671(15) / 1.013(27)
XPLUSDT|gen_2f405402                 1.5/3/5 BE keep0.5     NO:total_return  = A              bocciata     1.284(7) / 0.663(27) / 0.486(45)
XPLUSDT|gen_a220b439                 1.5/3/5 BE keep0.5     NO:holdout       = A              bocciata     0.193(9) / 0.844(18) / 0.959(28)
XPLUSDT|gen_b437a671                 2/4/6 BE keep0.5       NO:recovery      NO:pf_ex_top     bocciata     0.557(19) / 0.903(48) / 1.06(78)
XPLUSDT|gen_e59ad90b                 1.5/3/5 BE keep0.5     NO:consistency   = A              bocciata     0.726(32) / 1.002(97) / 0.986(159)
ZKUSDT|gen_98837ec2                  2/4/6 BE keep0.5       NO:regime        NO:regime        bocciata     1.063(7) / 0.953(13) / 0.961(25)
ZKUSDT|gen_c61d9322                  2/4/6 BE keep0.5       NO:regime        NO:regime        bocciata     0.915(8) / 1.491(16) / 1.193(30)
JTOUSDT|gen_35632db9                 1.5/3/5 BE keep0.35    PASSA            PASSA            passa        3.317(10) / 1.41(17) / 1.365(30)
JUPUSDT|gen_bb762669                 1.5/3/5 BE keep0.35    PASSA            PASSA            passa        - / - / -
MUBARAKUSDT|gen_2053cba6             2/4/6 BE keep0.75      PASSA            PASSA            passa        1.815(7) / 2.712(13) / 2.795(19)
MUBARAKUSDT|gen_49c2f657             1.5/3/5 BE keep0.75    PASSA            PASSA            passa        1.987(8) / 3.359(18) / 3.323(24)
OPENUSDT|gen_2bb283ca                1.5/3/5 BE keep0.35    PASSA            PASSA            passa        3.189(10) / 2.179(20) / 2.432(34)
PLUMEUSDT|gen_e94b056d               2/4/6 BE keep0.75      PASSA            PASSA            passa        6.134(8) / 3.818(13) / 3.181(21)
QUSDT|gen_0ada82e9                   1.5/3/5 BE keep0.75    PASSA            PASSA            passa        3.524(14) / 4.307(30) / 4.893(36)
QUSDT|gen_18c839a0                   1.5/3/5 BE keep0.75    PASSA            PASSA            passa        2.275(15) / 3.708(31) / 4.785(38)
QUSDT|gen_7f8adcde                   1.5/3/5 BE keep0.75    PASSA            PASSA            passa        3.524(14) / 4.307(30) / 4.893(36)
QUSDT|gen_a12226f7                   1.5/3/5 BE keep0.75    PASSA            PASSA            passa        2.275(15) / 3.708(31) / 4.785(38)
SAHARAUSDT|gen_60d64cfd              2/4/6 BE keep0.35      PASSA            PASSA            passa        5.143(5) / 0.988(19) / 2.239(32)
SAHARAUSDT|gen_95aff747              1.5/3/5 BE keep0.5     PASSA            = A              passa        2.51(11) / 2.029(25) / 1.422(38)
SCRUSDT|gen_63712f8e                 2/4/6 BE keep0.75      PASSA            PASSA            passa        1.463(10) / 1.154(16) / 1.349(24)
SKYAIUSDT|gen_6191df86               2/4/6 BE keep0.65      PASSA            PASSA            passa        2.473(8) / 3.354(13) / 3.231(24)
SKYAIUSDT|gen_eb2ece0c               1.5/3/5 BE keep0.35    PASSA            PASSA            passa        10.108(6) / 2.01(9) / 3.878(14)
SKYAIUSDT|gen_f68b811d               2/4/6 BE keep0.35      PASSA            PASSA            passa        8.536(8) / 2.687(15) / 2.606(24)
SYRUPUSDT|gen_4c6df481               2/4/6 BE keep0.75      PASSA            PASSA            passa        1.876(35) / 1.754(92) / 1.468(130)
MTLUSDT|gen_4b4f7174                 1.5/3/5 BE keep0.5     TEMPO            
ONGUSDT|gen_73ae3696                 1.5/3/5 BE keep0.5     TEMPO            
PENGUUSDT|gen_a32bee42               2/4/6 BE keep0.5       TEMPO            
PHAUSDT|gen_fa304106                 1.5/3/5 BE keep0.5     TEMPO            
PNUTUSDT|gen_4810faab                2/4/6 BE keep0.5       TEMPO            
PUNDIXUSDT|gen_96c1ed1b              2/4/6 BE keep0.5       TEMPO            
RAYSOLUSDT|gen_fa304106              2/4/6 BE keep0.5       TEMPO            
RSRUSDT|gen_b2f350ff                 2/4/6 BE keep0.5       TEMPO            
SEIUSDT|gen_4f890271                 2/4/6 BE keep0.5       TEMPO            
SOLUSDT|gen_f3124a14                 2/4/6 BE keep0.5       TEMPO            
SOPHUSDT|gen_42acf37e                1.5/3/5 BE keep0.5     TEMPO            
SUPERUSDT|gen_0eb999b7               1.5/3/5 BE keep0.5     TEMPO            
THEUSDT|gen_658b2edb                 2/4/6 BE keep0.5       TEMPO            
TSTUSDT|gen_a640dfa5                 2/4/6 BE keep0.5       TEMPO            
TUTUSDT|gen_4465723e                 1.5/3/5 BE keep0.5     TEMPO            
XMRUSDT|gen_35632db9                 1.5/3/5 BE keep0.5     TEMPO            
XRPUSDT|gen_a22411e3                 1.5/3/5 BE keep0.5     TEMPO            
ZORAUSDT|gen_2c248ee9                1.5/3/5 BE keep0.5     TEMPO            

RIASSUNTO · 212 validate · 194 valutate · tempo 18
  (A) passano col gate di oggi (passo 1 = configurazione globale 1.5/3/5 BE keep0.5): 17 su 194
  (B) passano col passo 1 sulla configurazione operata: 23 su 194 (68 operano gia' la configurazione globale: A = B)
  bocciate in (A) e passate in (B) = ARTEFATTO della configurazione globale: 6 su 177 bocciate
  passate in (A) ma bocciate in (B): 0 (il gate conferma una configurazione che il bot non opera)
  bocciate in entrambe: 171 · criterio binding (B): recovery 37 · consistency 33 · total_return 32 · holdout 30 · regime 28 · pf_ex_top 11 · (A): recovery 38 · total_return 34 · consistency 33 · regime 29 · holdout 29 · pf_ex_top 8
  PF < 1 negli ultimi 120 giorni (configurazione operata, serie intera): 24 su 190 con trade
  LETTURA: solo una parte delle bocciature (6 su 177) e' un artefatto del passo 1: la maggior parte regge anche sulla configurazione operata, quindi correggere il gate recupera poco e il problema principale e' altrove (mercato recente o soglie). Sugli ultimi 120 giorni 24 su 190 con trade hanno PF < 1 con la configurazione operata.
  18 coppie NON valutate per tempo (budget 720s): --budget 0 da tmux, oppure OPS_TIMEOUT_S piu' alto
[autopsia] finito in 781s
```
