import os
import datetime as dt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Workout Tracker", page_icon="💪", layout="centered")

PRESETS = {
    "A: Upper1 (Klatka+Biceps)": [
        "Wyciskanie sztangi na ławce płaskiej",
        "Wyciskanie hantli na ławce skośnej",
        "Rozpiętki z hantlami",
        "Uginanie ze sztangą stojąc",
        "Uginanie hantli naprzemienne",
        "Hammer curls",
    ],
    "B: Lower": [
        "Przysiad ze sztangą na barkach",
        "Martwy ciąg rumuński",
        "Prostowanie nóg na maszynie",
        "Uginanie nóg na maszynie",
        "Wspięcia na palce stojąc",
    ],
    "C: Upper2 (Klatka+Biceps)": [
        "Wyciskanie sztangi na ławce skośnej",
        "Dips (poręcze)",
        "Rozpiętki na wyciągu (góra-dół)",
        "Uginanie na modlitewniku",
        "Hammer curls",
        "Koncentryczne uginania",
    ],
    "D: Pull/Core": [
        "Podciąganie na drążku",
        "Wiosłowanie sztangą w opadzie",
        "Ściąganie drążka do klatki",
        "Wznosy ramion w opadzie tułowia",
        "Szrugsy z hantlami",
        "Russian Twist",
        "Wznosy tułowia z piłką medyczną",
    ],
}

CSV_PATH = "workouts.csv"

@st.cache_data
def load_data(path=CSV_PATH):
    if os.path.exists(path):
        df = pd.read_csv(path)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.date
        return df
    return pd.DataFrame(columns=["date","week","day","workout","exercise","weight_kg","reps","rir","notes"])

def save_row(row, path=CSV_PATH):
    df = load_data(path).copy()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(path, index=False)
    load_data.clear()

st.title("Workout Tracker 💪")
with st.sidebar:
    st.header("Preset treningu")
    preset_name = st.selectbox("Wybierz preset", list(PRESETS.keys()))
    st.caption("Zmiana presetu aktualizuje listę ćwiczeń w formularzu poniżej")

with st.form("add_set"):
    today = dt.date.today()
    c1, c2 = st.columns(2)
    date = c1.date_input("Data", today)
    week = c2.text_input("Tydzień (np. 1A/1B)", "1A")

    c3, c4, c5 = st.columns(3)
    day = c3.selectbox("Dzień", ["Pon","Wt","Śr","Czw","Pt","Sob","Nd"])
    workout = c4.text_input("Nazwa sesji", value=preset_name.split(':'))

    ex_choices = PRESETS.get(preset_name, sum(PRESETS.values(), []))
    exercise = c5.selectbox("Ćwiczenie", ex_choices)

    c6, c7, c8 = st.columns(3)
    weight = c6.number_input("Ciężar (kg)", min_value=0.0, step=0.5, value=40.0)
    reps = c7.number_input("Powtórzenia", min_value=1, step=1, value=8)
    rir = c8.number_input("RIR (zapas powt.)", min_value=0, max_value=5, step=1, value=2)
    notes = st.text_input("Notatki", "")

    c9, c10 = st.columns(2)
    submit = c9.form_submit_button("Dodaj serię")
    submit_keep = c10.form_submit_button("Dodaj i zostaw formularz")

    if submit or submit_keep:
        row = {
            "date": date, "week": week, "day": day, "workout": workout,
            "exercise": exercise, "weight_kg": weight, "reps": reps, "rir": rir, "notes": notes
        }
        save_row(row)
        st.success("Zapisano serię ✅")

# --- HISTORIA I ZARZĄDZANIE DANYMI ---
st.subheader("Historia")
df = load_data()

# pomocnicza funkcja zapisu całego df
def save_df(_df, path=CSV_PATH):
    _df.to_csv(path, index=False)
    load_data.clear()

if df.empty:
    st.info("Brak danych — dodaj pierwszą serię powyżej.")
else:
    # Filtry widoku
    c1, c2, c3 = st.columns(3)
    ex_filter = c1.selectbox("Filtr ćwiczenia", ["Wszystkie"] + sorted(df['exercise'].dropna().unique().tolist()))
    from_date = c2.date_input("Od", df['date'].min())
    to_date = c3.date_input("Do", df['date'].max())

    view = df.copy()
    view = view[(view['date'] >= from_date) & (view['date'] <= to_date)]
    if ex_filter != "Wszystkie":
        view = view[view['exercise'] == ex_filter]

    st.dataframe(view.sort_values('date', ascending=False), use_container_width=True)

    # Zarządzanie historią
    with st.expander("Zarządzanie historią"):
        st.caption("Wybierz wiersze do usunięcia lub wyczyść całą historię.")

        # etykiety do wyboru (na pełnym df, nie tylko przefiltrowanym widoku)
        labels = {
            i: f"{i} | {row['date']} | {row['exercise']} | {row['weight_kg']} kg × {row['reps']} | RIR {row['rir']}"
            for i, row in df.reset_index().rename(columns={'index':'_idx'}).iterrows()
        }
        # multiselect po indeksach oryginalnego df
        idx_options = list(range(len(df)))
        selected_idx = st.multiselect(
            "Zaznacz wiersze do usunięcia",
            options=idx_options,
            format_func=lambda i: labels.get(i, str(i))
        )

        cdel, cclear = st.columns(2)
        if cdel.button("Usuń zaznaczone wiersze 🗑️"):
            base = load_data().copy()
            base = base.drop(index=selected_idx, errors="ignore").reset_index(drop=True)
            save_df(base)
            st.success(f"Usunięto {len(selected_idx)} wierszy.")
            st.rerun()  # natychmiastowe odświeżenie widoku
        if cclear.button("Wyczyść wszystko ❌", type="primary"):
            # zostaw nagłówki, wyczyść zawartość
            empty = pd.DataFrame(columns=["date","week","day","workout","exercise","weight_kg","reps","rir","notes"])
            save_df(empty)
            st.success("Historia została wyczyszczona.")
            st.rerun()
            
