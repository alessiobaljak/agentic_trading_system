"""I giorni dei comunicati delle riunioni PROGRAMMATE della banca centrale americana (FOMC), 2016-2024.

Fonte: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm (2021-2024) e
https://www.federalreserve.gov/monetarypolicy/fomchistorical{anno}.htm (2016-2020), letti il 24 ottobre 2026. Il
comunicato esce alle 14:00 di New York del secondo giorno della riunione. Fuori: le riunioni straordinarie (3 e 15 marzo
2020); la riunione programmata del 17-18 marzo 2020 non si è tenuta (sostituita da quella del 15).
"""
from datetime import date

COMUNICATI = [date(*x) for x in [
    (2016, 1, 27), (2016, 3, 16), (2016, 4, 27), (2016, 6, 15), (2016, 7, 27), (2016, 9, 21), (2016, 11, 2), (2016, 12, 14),
    (2017, 2, 1), (2017, 3, 15), (2017, 5, 3), (2017, 6, 14), (2017, 7, 26), (2017, 9, 20), (2017, 11, 1), (2017, 12, 13),
    (2018, 1, 31), (2018, 3, 21), (2018, 5, 2), (2018, 6, 13), (2018, 8, 1), (2018, 9, 26), (2018, 11, 8), (2018, 12, 19),
    (2019, 1, 30), (2019, 3, 20), (2019, 5, 1), (2019, 6, 19), (2019, 7, 31), (2019, 9, 18), (2019, 10, 30), (2019, 12, 11),
    (2020, 1, 29), (2020, 4, 29), (2020, 6, 10), (2020, 7, 29), (2020, 9, 16), (2020, 11, 5), (2020, 12, 16),
    (2021, 1, 27), (2021, 3, 17), (2021, 4, 28), (2021, 6, 16), (2021, 7, 28), (2021, 9, 22), (2021, 11, 3), (2021, 12, 15),
    (2022, 1, 26), (2022, 3, 16), (2022, 5, 4), (2022, 6, 15), (2022, 7, 27), (2022, 9, 21), (2022, 11, 2), (2022, 12, 14),
    (2023, 2, 1), (2023, 3, 22), (2023, 5, 3), (2023, 6, 14), (2023, 7, 26), (2023, 9, 20), (2023, 11, 1), (2023, 12, 13),
    (2024, 1, 31), (2024, 3, 20), (2024, 5, 1), (2024, 6, 12), (2024, 7, 31), (2024, 9, 18), (2024, 11, 7), (2024, 12, 18),
]]

# Il periodo chiuso (2 gennaio 2025 → 30 settembre 2026), dalla stessa pagina letta il 24 ottobre 2026
# (https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm); nessuna riunione straordinaria nel periodo.
COMUNICATI_CHIUSO = [date(*x) for x in [
    (2025, 1, 29), (2025, 3, 19), (2025, 5, 7), (2025, 6, 18), (2025, 7, 30), (2025, 9, 17), (2025, 10, 29), (2025, 12, 10),
    (2026, 1, 28), (2026, 3, 18), (2026, 4, 29), (2026, 6, 17), (2026, 7, 29), (2026, 9, 16),
]]


# Dopo il periodo chiuso, per la misura in avanti della miscela (stock/avanti/MISCELA.md): secondo giorno di ogni riunione programmata,
# dalla pagina https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm letta l'11 novembre 2026.
COMUNICATI_AVANTI = [date(*x) for x in [
    (2026, 10, 28), (2026, 12, 9),
    (2027, 1, 27), (2027, 3, 17), (2027, 4, 28), (2027, 6, 9), (2027, 7, 28), (2027, 9, 15), (2027, 10, 27), (2027, 12, 8),
]]


# Prima del 2016, per il secondo campione della prova 54 (`stock/prove/P054_ciclo_banca_centrale.md`, `METODO.md` sezione 4): l'ultimo
# giorno di ogni riunione PROGRAMMATA, dalle pagine https://www.federalreserve.gov/monetarypolicy/fomchistorical{anno}.htm (1994-2015),
# lette il 28 novembre 2026. Fuori tutte le «Conference Call» (fra queste le decisioni fuori calendario del 18 aprile 1994, del 15
# ottobre 1998, del 3 gennaio, 18 aprile e 17 settembre 2001, del 22 gennaio, 10 marzo e 8 ottobre 2008) e le due riunioni segnate
# «(unscheduled)» (16 ottobre 2013 e 4 marzo 2014); fuori anche la riunione del 15 settembre 2003, senza comunicato né documenti per
# la decisione (Greenbook e Bluebook sono della riunione del 16, che resta). Fino al marzo 1999 la banca centrale non pubblicava un comunicato dopo le riunioni senza cambi (sulla pagina non ce l'hanno 28
# delle 40 riunioni del 1994-1998 e le prime due del 1999): il giorno 0 resta l'ultimo giorno della riunione programmata, come nello
# studio di Cieslak, Morse e Vissing-Jorgensen (2019). Otto riunioni ogni anno, 176 in tutto.
COMUNICATI_1994_2015 = [date(*x) for x in [
    (1994, 2, 4), (1994, 3, 22), (1994, 5, 17), (1994, 7, 6), (1994, 8, 16), (1994, 9, 27), (1994, 11, 15), (1994, 12, 20),
    (1995, 2, 1), (1995, 3, 28), (1995, 5, 23), (1995, 7, 6), (1995, 8, 22), (1995, 9, 26), (1995, 11, 15), (1995, 12, 19),
    (1996, 1, 31), (1996, 3, 26), (1996, 5, 21), (1996, 7, 3), (1996, 8, 20), (1996, 9, 24), (1996, 11, 13), (1996, 12, 17),
    (1997, 2, 5), (1997, 3, 25), (1997, 5, 20), (1997, 7, 2), (1997, 8, 19), (1997, 9, 30), (1997, 11, 12), (1997, 12, 16),
    (1998, 2, 4), (1998, 3, 31), (1998, 5, 19), (1998, 7, 1), (1998, 8, 18), (1998, 9, 29), (1998, 11, 17), (1998, 12, 22),
    (1999, 2, 3), (1999, 3, 30), (1999, 5, 18), (1999, 6, 30), (1999, 8, 24), (1999, 10, 5), (1999, 11, 16), (1999, 12, 21),
    (2000, 2, 2), (2000, 3, 21), (2000, 5, 16), (2000, 6, 28), (2000, 8, 22), (2000, 10, 3), (2000, 11, 15), (2000, 12, 19),
    (2001, 1, 31), (2001, 3, 20), (2001, 5, 15), (2001, 6, 27), (2001, 8, 21), (2001, 10, 2), (2001, 11, 6), (2001, 12, 11),
    (2002, 1, 30), (2002, 3, 19), (2002, 5, 7), (2002, 6, 26), (2002, 8, 13), (2002, 9, 24), (2002, 11, 6), (2002, 12, 10),
    (2003, 1, 29), (2003, 3, 18), (2003, 5, 6), (2003, 6, 25), (2003, 8, 12), (2003, 9, 16), (2003, 10, 28), (2003, 12, 9),
    (2004, 1, 28), (2004, 3, 16), (2004, 5, 4), (2004, 6, 30), (2004, 8, 10), (2004, 9, 21), (2004, 11, 10), (2004, 12, 14),
    (2005, 2, 2), (2005, 3, 22), (2005, 5, 3), (2005, 6, 30), (2005, 8, 9), (2005, 9, 20), (2005, 11, 1), (2005, 12, 13),
    (2006, 1, 31), (2006, 3, 28), (2006, 5, 10), (2006, 6, 29), (2006, 8, 8), (2006, 9, 20), (2006, 10, 25), (2006, 12, 12),
    (2007, 1, 31), (2007, 3, 21), (2007, 5, 9), (2007, 6, 28), (2007, 8, 7), (2007, 9, 18), (2007, 10, 31), (2007, 12, 11),
    (2008, 1, 30), (2008, 3, 18), (2008, 4, 30), (2008, 6, 25), (2008, 8, 5), (2008, 9, 16), (2008, 10, 29), (2008, 12, 16),
    (2009, 1, 28), (2009, 3, 18), (2009, 4, 29), (2009, 6, 24), (2009, 8, 12), (2009, 9, 23), (2009, 11, 4), (2009, 12, 16),
    (2010, 1, 27), (2010, 3, 16), (2010, 4, 28), (2010, 6, 23), (2010, 8, 10), (2010, 9, 21), (2010, 11, 3), (2010, 12, 14),
    (2011, 1, 26), (2011, 3, 15), (2011, 4, 27), (2011, 6, 22), (2011, 8, 9), (2011, 9, 21), (2011, 11, 2), (2011, 12, 13),
    (2012, 1, 25), (2012, 3, 13), (2012, 4, 25), (2012, 6, 20), (2012, 8, 1), (2012, 9, 13), (2012, 10, 24), (2012, 12, 12),
    (2013, 1, 30), (2013, 3, 20), (2013, 5, 1), (2013, 6, 19), (2013, 7, 31), (2013, 9, 18), (2013, 10, 30), (2013, 12, 18),
    (2014, 1, 29), (2014, 3, 19), (2014, 4, 30), (2014, 6, 18), (2014, 7, 30), (2014, 9, 17), (2014, 10, 29), (2014, 12, 17),
    (2015, 1, 28), (2015, 3, 18), (2015, 4, 29), (2015, 6, 17), (2015, 7, 29), (2015, 9, 17), (2015, 10, 28), (2015, 12, 16),
]]
