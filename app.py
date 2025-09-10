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

st.subheader("Historia")
df = load_data()
if df.empty:
    st.info("Brak danych — dodaj pierwszą serię powyżej.")
else:
    c1, c2, c3 = st.columns(3)
    ex_filter = c1.selectbox("Filtr ćwiczenia", ["Wszystkie"] + sorted(df['exercise'].dropna().unique().tolist()))
    from_date = c2.date_input("Od", df['date'].min())
    to_date = c3.date_input("Do", df['date'].max())
    view = df.copy()
    view = view[(view['date'] >= from_date) & (view['date'] <= to_date)]
    if ex_filter != "Wszystkie":
        view = view[view['exercise'] == ex_filter]
    st.dataframe(view.sort_values('date', ascending=False), use_container_width=True)

    import altair as alt
    view['week_num'] = view['date'].apply(lambda d: f"{d.isocalendar().year}-W{d.isocalendar().week}")
    view['tonnage'] = view['weight_kg'] * view['reps']
    weekly = view.groupby(['week_num','exercise'], as_index=False).agg({'tonnage':'sum','reps':'sum'})

    st.subheader("Tygodniowa objętość (tonnage)")
    if not weekly.empty:
        chart = alt.Chart(weekly).mark_bar().encode(
            x='week_num:N', y='tonnage:Q', color='exercise:N', tooltip=['week_num','exercise','tonnage','reps']
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)

    st.subheader("Szacowany 1RM (Epley)")
    view['est_1rm'] = view.apply(lambda r: float(r['weight_kg']) * (1 + float(r['reps'])/30.0) if pd.notnull(r['weight_kg']) and pd.notnull(r['reps']) else None, axis=1)
    one_rm = view.dropna(subset=['est_1rm']).groupby(['date','exercise'], as_index=False)['est_1rm'].max()
    if not one_rm.empty:
        line = alt.Chart(one_rm).mark_line(point=True).encode(
            x='date:T', y='est_1rm:Q', color='exercise:N', tooltip=['date','exercise','est_1rm']
        ).properties(height=300)
        st.altair_chart(line, use_container_width=True)

if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Pobierz CSV", data=csv, file_name="workouts_export.csv", mime="text/csv")
