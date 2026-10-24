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
