# Workout Tracker — Presety Klatka/Biceps

Lekka aplikacja Streamlit do logowania serii (ciężar, powtórzenia, RIR), z presetami dni i listami ćwiczeń pod Twój plan (klatka + biceps priorytet), historią, wykresami objętości i estymowanym 1RM (Epley).

## Szybki start (lokalnie)
1. `pip install -r requirements.txt`
2. `streamlit run app.py`

## Wdrożenie w Streamlit Community Cloud
1. Utwórz repozytorium na GitHub i wgraj pliki: `app.py`, `requirements.txt`, `README.md`.
2. W Streamlit Cloud wybierz „Create app”, wskaż repo, branch `main` i plik startowy `app.py`, a następnie `Deploy`.
3. Otwórz adres w domenie `streamlit.app` na telefonie i dodaj skrót do ekranu głównego.

## Użycie
- Wybierz preset dnia (Upper1 / Lower / Upper2 / Pull/Core), a lista ćwiczeń w formularzu zaktualizuje się pod dany dzień.
- Loguj każdą serię (kg, powtórzenia, RIR, notatki).
- W „Historia” filtruj zakres dat/ćwiczenie, pobierz CSV, sprawdź wykres tygodniowej objętości oraz trend 1RM.

## Plik danych
Aplikacja zapisuje log do `workouts.csv` w katalogu roboczym. Możesz go wyczyścić/usunąć lub edytować w Excelu.
