# Studio jakości danych

Projekt 2 na Programowanie V.
Autorka Anastasiia Knyha, nr albumu 106230. Projekt zrobiłam samodzielnie.

## Cel

Aplikacja prowadzi od wczytania pliku CSV przez sprawdzenie i czyszczenie danych do wykresów i eksportu wyników. Każda zmiana w danych jest zapisana w dzienniku, więc widać, co i dlaczego się zmieniło.

## Etapy

| Etap | Zakres | Status |
|---|---|---|
| Lab 6 | profil danych, reguły jakości, czyszczenie, raport przed i po | gotowe |
| Lab 7 | wykresy w Matplotlib i Seaborn, korelacja | gotowe |
| Lab 8 | okienko w Tkinterze | w planach |
| Lab 9 | wykres w okienku, eksport, dokumentacja | w planach |

## Wymagania

- Python 3.10 lub nowszy
- biblioteki pandas, matplotlib, seaborn i pytest, są w pliku requirements.txt

## Instalacja

```
git clone https://github.com/AnastasiiaKnyha/studio-danych.git
cd studio-danych
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Dane

Dane referencyjne to publiczna wersja zbioru California Housing, zapisana w pliku `dane/housing.csv`. Są w niej braki w kolumnie total_bedrooms i wartości odstające, ale nie ma duplikatów ani wartości spoza zakresu. Dlatego wszystkie rodzaje problemów pokazuje też mały plik testowy `samples/braki.csv`.

## Uruchomienie

Czyszczenie danych referencyjnych

```
python3 run_lab6.py
```

Program zapisuje w folderze `wyniki` plik `cleaned.csv` oraz raport `raport.txt`.

Czyszczenie pliku testowego ze wszystkimi rodzajami problemów

```
python3 run_lab6.py samples/braki.csv wyniki/braki
```

Pierwszy argument to plik CSV, a drugi to folder na wyniki. Można tak podać dowolny poprawny plik CSV.

## Wykresy

Wykresy dla danych przed i po czyszczeniu

```
python3 run_lab7.py
```

Najpierw trzeba uruchomić `run_lab6.py`, bo wykresy korzystają z pliku `wyniki/cleaned.csv`. Wykresy zapisują się w folderze `wyniki/wykresy` jako PNG, a macierz korelacji także jako SVG.

| Wykres | Jakie kolumny przyjmuje |
|---|---|
| histogram | jedna kolumna liczbowa |
| punktowy | dwie różne kolumny liczbowe, w tytule jest współczynnik korelacji |
| pudełkowy | kolumna liczbowa i opcjonalnie kolumna z kategoriami jako grupy |
| słupkowy | kolumna z najwyżej 20 kategoriami |

Program blokuje wykres z komunikatem, gdy kolumna ma zły typ, ma tylko jedną wartość albo ma za dużo kategorii. Kolumny z wartościami True i False są traktowane jak kategorie.

## Wnioski z wykresów

- Dochód i wartość domu mają korelację 0,69. W okręgach z wyższym dochodem domy są zwykle droższe. To tylko korelacja, a nie dowód, że dochód powoduje wyższą cenę. Oba mogą zależeć od położenia okręgu.
- Na wykresie punktowym widać poziomą linię przy wartości 500001. To górny limit w danych, a nie prawdziwa cena domów.
- Liczba pokoi, sypialni, mieszkańców i gospodarstw ma korelacje od 0,86 do 0,97. Wszystkie te kolumny rosną razem z wielkością okręgu, więc jedna nie powoduje drugiej.
- Długość i szerokość geograficzna mają korelację minus 0,92. To wynika z kształtu Kalifornii, której wybrzeże biegnie ukośnie.
- Domy w głębi lądu (INLAND) mają medianę wartości około 108500, a przy oceanie około 215000 do 234000. Kategoria ISLAND ma tylko 5 rekordów, więc wniosek dla niej jest niepewny.
- Po uzupełnieniu braków medianą 207 wartości total_bedrooms trafiło do jednego przedziału przy 435. Kształt rozkładu się nie zmienił, ale to jest skutek uboczny imputacji.
- Rozkład dochodu jest prawostronnie skośny. 681 okręgów ma dochód powyżej 8,01 i są oznaczone jako odstające. To prawdziwe zamożne okręgi, dlatego ich nie usuwam.

## Jak działa czyszczenie

Kroki są wykonywane zawsze w tej samej kolejności, więc wynik jest powtarzalny. Dane surowe nigdy się nie zmieniają, program pracuje na kopii i w każdej chwili może do nich wrócić.

| Krok | Co robi | Dlaczego |
|---|---|---|
| 1 | usuwa pełne duplikaty | ten sam rekord dwa razy zawyża statystyki |
| 2 | tekst w kolumnie liczbowej zmienia na brak | to błąd wpisu, nie da się go użyć jako liczby |
| 3 | wartość spoza zakresu zmienia na brak | jedna zła komórka nie powinna usuwać całego rekordu |
| 4 | braki w liczbach uzupełnia medianą | mediana jest odporna na wartości odstające |
| 4 | rekordy z brakiem w tekście usuwa | położenia nie da się zgadnąć, a takich rekordów jest bardzo mało |
| 5 | wartości odstające oznacza w nowej kolumnie | drogie albo bardzo duże okręgi naprawdę istnieją, to nie są błędy |

Wartości odstające są wykrywane metodą IQR. Wartość jest odstająca, gdy jest mniejsza niż Q1 minus 1,5 razy IQR albo większa niż Q3 plus 1,5 razy IQR. Program ich nie usuwa, tylko dodaje kolumnę z końcówką `_outlier`.

## Zakresy poprawnych wartości

| Kolumna | Min | Max | Dlaczego |
|---|---|---|---|
| longitude | -125 | -114 | granice Kalifornii |
| latitude | 32 | 42 | granice Kalifornii |
| housing_median_age | 1 | 100 | wiek budynku nie może być ujemny ani bardzo duży |
| total_rooms, population, households | 1 | brak | okręg musi mieć co najmniej jeden pokój, mieszkańca i gospodarstwo |
| total_bedrooms | 0 | brak | liczba sypialni nie może być ujemna |
| median_income | 0 | brak | dochód nie może być ujemny |
| median_house_value | 0 | 500001 | w danych wartość domu jest ograniczona do 500001 |
| wiek (plik testowy) | 0 | 120 | wiek człowieka |

## Dane testowe

| Plik | Co zawiera | Oczekiwany wynik |
|---|---|---|
| `samples/przecinek.csv` | 4 rekordy z przecinkiem | 4 rekordy i 4 kolumny |
| `samples/srednik.csv` | te same dane ze średnikiem | 4 rekordy i 4 kolumny, tak samo jak z przecinkiem |
| `samples/zly_wiersz.csv` | wiersz z dodatkowym polem | komunikat o wadliwym wierszu |
| `samples/braki.csv` | brak liczby i tekstu, para duplikatów, wiek 150, dochód 99000 | z 9 rekordów zostaje 7, braki w wieku uzupełnione medianą, dochód 99000 oznaczony jako odstający |

## Testy

```
pytest -v
```

Jest 36 testów. Sprawdzają wczytywanie z różnymi separatorami, błędne pliki, wszystkie operacje czyszczenia, to, że operacje nie zmieniają innych kolumn, dziennik zmian, powrót do danych surowych oraz wykresy, czyli tytuły i opisy osi, blokowanie złych kolumn i zapis do PNG i SVG.

## Wykorzystanie AI

Przy pracy korzystałam z pomocy AI (Claude). Pomógł mi zrobić plan realizacji projektu i rozpisać zadania na każdy etap. Przygotowywał też szkice i szablony funkcji, które potem poprawiałam i dostosowywałam do mojego projektu. Szczegóły są w raportach w folderze docs.

## Źródła

- pandas.read_csv https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
- Pandas User Guide https://pandas.pydata.org/docs/user_guide/index.html
- zbiór California Housing https://github.com/ageron/handson-ml/tree/master/datasets/housing
- Matplotlib https://matplotlib.org/stable/users/index.html
- Seaborn https://seaborn.pydata.org/tutorial.html