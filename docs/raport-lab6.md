# Raport z etapu 1 (Lab 6)

Anastasiia Knyha, nr albumu 106230
16 listopada 2026

Repozytorium https://github.com/AnastasiiaKnyha/studio-danych

## Co zrobiłam

W tym etapie zrobiłam podstawę projektu Studio jakości danych. Program wczytuje plik CSV, robi profil danych, wykrywa problemy, czyści dane i zapisuje raport przed i po czyszczeniu oraz plik cleaned.csv.

Program sam rozpoznaje separator, czyli przecinek albo średnik. Przy złym kodowaniu, pustym pliku albo wadliwym wierszu pokazuje zrozumiały komunikat zamiast się wyłączać.

Każda operacja czyszczenia jest zapisana w dzienniku zmian razem z parametrami, czasem i liczbą rekordów przed i po. Dane surowe nigdy się nie zmieniają, program pracuje na kopii i w każdej chwili może do nich wrócić.

## Dane

Użyłam publicznej wersji zbioru California Housing. Ma 20640 rekordów i 10 kolumn. Są w niej braki w kolumnie total_bedrooms i wartości odstające, ale nie ma duplikatów ani wartości spoza zakresu.

Dlatego wszystkie rodzaje problemów pokazuje też mały plik testowy samples/braki.csv. Celowo umieściłam w nim brak liczby, brak tekstu, parę duplikatów, wartość spoza zakresu i wartość odstającą.

## Jak zbudowany jest kod

Podzieliłam kod na małe pliki, żeby każdy robił jedną rzecz. Logika jest oddzielona od przyszłego okienka, więc w kolejnych etapach okienko będzie tylko wywoływać gotowe funkcje.

| Plik | Co robi |
|---|---|
| studio/loading.py | wczytuje CSV i rozpoznaje separator |
| studio/profile.py | liczy profil danych, czyli rozmiar, typy, statystyki, braki, duplikaty i wartości unikalne |
| studio/rules.py | wykrywa wartości spoza zakresu i wartości odstające metodą IQR, niczego nie zmienia |
| studio/cleaning.py | operacje czyszczenia, każda pracuje na kopii danych |
| studio/session.py | sesja z danymi surowymi, danymi bieżącymi, dziennikiem zmian i powrotem do danych surowych |
| studio/report.py | tworzy raport przed i po czyszczeniu |
| studio/errors.py | własny błąd DataError z komunikatem po polsku |
| run_lab6.py | uruchamia całe czyszczenie i zapisuje wyniki |

## Jak działa czyszczenie i dlaczego

| Krok | Co robi | Dlaczego |
|---|---|---|
| 1 | usuwa pełne duplikaty | ten sam rekord dwa razy zawyża statystyki |
| 2 | tekst w kolumnie liczbowej zmienia na brak | to błąd wpisu, nie da się go użyć jako liczby |
| 3 | wartość spoza zakresu zmienia na brak | jedna zła komórka nie powinna usuwać całego rekordu |
| 4 | braki w liczbach uzupełnia medianą | mediana jest odporna na wartości odstające |
| 4 | rekordy z brakiem w tekście usuwa | położenia nie da się zgadnąć, a takich rekordów jest bardzo mało |
| 5 | wartości odstające oznacza w nowej kolumnie | drogie albo bardzo duże okręgi naprawdę istnieją, to nie są błędy |

Wartości odstające wykrywam metodą IQR. Wartość jest odstająca, gdy jest mniejsza niż Q1 minus 1,5 razy IQR albo większa niż Q3 plus 1,5 razy IQR. Nie usuwam ich automatycznie, tylko dodaję kolumnę z końcówką _outlier.

## Wyniki na danych referencyjnych

| Co sprawdzam | Przed | Po |
|---|---|---|
| rekordy | 20640 | 20640 |
| kolumny | 10 | 13, doszły 3 kolumny z oznaczeniem wartości odstających |
| pełne duplikaty | 0 | 0 |
| braki w total_bedrooms | 207, czyli 1% | 0, uzupełnione medianą 435 |
| wartości spoza zakresu | 0 | 0 |
| wartości odstające w median_income | 681 | oznaczone |
| wartości odstające w total_rooms | 1287 | oznaczone |
| wartości odstające w population | 1196 | oznaczone |

Pełny raport jest w pliku wyniki/raport.txt, a oczyszczone dane w pliku wyniki/cleaned.csv.

## Wyniki na pliku testowym

| Operacja | Zmienione rekordy | Rekordy po |
|---|---|---|
| usunięcie pełnych duplikatów | 1, para rekordów Lublin | 8 |
| wiek spoza zakresu 0 do 120 zmieniony na brak | 1, wiek 150 | 8 |
| uzupełnienie braków w wieku medianą 40,5 | 2 | 8 |
| usunięcie rekordu z brakiem kategorii | 1, Kraków | 7 |
| oznaczenie wartości odstającej w dochodzie | 1, dochód 99000 | 7 |

Raport wykrył wszystkie przygotowane problemy. Pełny raport jest w pliku wyniki/braki/raport.txt.

## Powtarzalność

Uruchomiłam czyszczenie dwa razy i porównałam sumy kontrolne pliku cleaned.csv. Obie są takie same, czyli wynik jest powtarzalny.

## Historia w GitHub

| Data | Commit |
|---|---|
| 16.11.2026 | Initial project structure |
| 16.11.2026 | Add CSV loading with separator detection |
| 16.11.2026 | Add data profile |
| 16.11.2026 | Add range rules and IQR outlier detection |
| 16.11.2026 | Add cleaning operations |
| 16.11.2026 | Add data session with change log and reset |
| 16.11.2026 | Add cleaning pipeline and before/after report |
| 16.11.2026 | Add reference data and cleaning results |
| 16.11.2026 | Add session code (file was empty in previous commit) |
| 16.11.2026 | Add tests for loading, cleaning and session |

W commicie z sesją plik był jeszcze pusty, bo nie zapisałam go przed commitem. Poprawiłam to w osobnym commicie.

## Testy

Napisałam 20 testów automatycznych w pytest. Wszystkie przeszły. Testy działają na małych tabelach, w których znam każdy problem.

| Plik | Co sprawdza |
|---|---|
| test_loading.py | przecinek i średnik dają te same kolumny, wadliwy wiersz, brak pliku, plik z samym nagłówkiem |
| test_cleaning.py | usuwanie tylko pełnych duplikatów, uzupełnianie braków medianą i dominantą, usuwanie braków, zakresy, wartości odstające, tekst w kolumnie liczbowej, brak zmian w innych kolumnach |
| test_session.py | dziennik zmian, powrót do danych surowych, dane surowe się nie zmieniają, sprawdzanie nie zmienia danych, powtarzalność |

## Dlaczego takie testy

Testy wczytywania sprawdzają, czy program działa z przecinkiem i średnikiem i czy zły plik daje komunikat zamiast błędu.

Testy czyszczenia sprawdzają każdą operację osobno. Kilka testów porównuje całą tabelę przed i po operacji bez zmienianej kolumny. To pokazuje, że operacje nie zmieniają innych kolumn.

Testy sesji sprawdzają, czy dane surowe zostają bez zmian, czy można do nich wrócić i czy te same kroki dają ten sam wynik.

## Źródła i narzędzia

Użyłam biblioteki pandas do danych i pytest do testów. Z Pythona użyłam modułów dataclasses, datetime, pathlib i sys.

Korzystałam z dokumentacji
https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
https://pandas.pydata.org/docs/user_guide/index.html
https://docs.pytest.org/

Dane California Housing pobrałam z repozytorium
https://github.com/ageron/handson-ml/tree/master/datasets/housing

Korzystałam z pomocy AI (Claude). Claude pomógł mi zrobić plan realizacji etapu i rozpisać zadania. Przygotowywał szkice i szablony funkcji, które potem poprawiałam i dostosowywałam do mojego projektu. Pomagał mi też szukać przyczyn błędów i napisać testy automatyczne.
