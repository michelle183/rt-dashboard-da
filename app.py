
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

st.set_page_config(layout="wide")

st.title("Eine Analyse von Artikeln von RT")

# Datensatz laden
dataset_url = "https://github.com/polcomm-passau/computational_methods_python/raw/refs/heads/main/RT_D_Small.xlsx"
df = pd.read_excel(dataset_url)

# 'date' Spalte in Datumsformat umwandeln
df['date'] = pd.to_datetime(df['date'])

# Spalten f&#252;r Reaktionen, Shares und Kommentare definieren
reaction_columns = ['haha', 'like', 'wow', 'angry', 'sad', 'love', 'hug']
engagement_columns = ['shares', 'comments_num']
all_metrics_columns = reaction_columns + engagement_columns

# Bestimme minimale und maximale Daten f&#252;r die Datumsauswahl
min_date_df = df['date'].min().date()
max_date_df = df['date'].max().date()

# Datumsbereichsfelder
st.sidebar.header("Filteroptionen")
start_date = st.sidebar.date_input(
    "Startdatum:",
    value=min_date_df,
    min_value=min_date_df,
    max_value=max_date_df
)
end_date = st.sidebar.date_input(
    "Enddatum:",
    value=max_date_df,
    min_value=min_date_df,
    max_value=max_date_df
)

# Eingabefeld f&#252;r den Suchbegriff
search_term = st.sidebar.text_input("Bitte gib deinen Suchbegriff ein:", "gr&#252;n")

# Filterung des DataFrames nach Datum
df_filtered_date = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]

# Filterbedingung f&#252;r den Suchbegriff
search_condition = pd.Series([False] * len(df_filtered_date)) # Standardm&#228;&#223;ig False
if search_term:
    search_condition = df_filtered_date['text'].fillna('').str.contains(search_term, case=False, na=False) | \
                       df_filtered_date['fulltext'].fillna('').str.contains(search_term, case=False, na=False)

# Filterung der DataFrames
filtered_df_with_term = df_filtered_date[search_condition]
filtered_df_without_term = df_filtered_date[~search_condition]

# --- Liniendiagramm (Prozentualer Anteil) ---
if search_term:
    total_posts_per_day = df_filtered_date['date'].value_counts().sort_index()

    if not filtered_df_with_term.empty:
        filtered_posts_per_day = filtered_df_with_term['date'].value_counts().sort_index()

        percentage_per_day = (filtered_posts_per_day / total_posts_per_day) * 100
        percentage_per_day = percentage_per_day.fillna(0) # F&#252;lle NaN, falls an einem Tag keine Posts sind

        st.subheader(f"Prozentualer Anteil der Artikel mit '{search_term}' im Zeitverlauf")

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(percentage_per_day.index, percentage_per_day.values, marker='o', linestyle='-', color='skyblue')
        ax.set_title(f'Prozentualer Anteil der Posts pro Tag mit "{search_term}"')
        ax.set_xlabel('Datum')
        ax.set_ylabel('Prozentualer Anteil (%)')
        ax.grid(True)
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

    else:
        st.warning(f"Keine Artikel gefunden, die '{search_term}' im Text oder Fulltext im ausgew&#228;hlten Zeitraum enthalten.")
else:
    st.info("Bitte gib einen Suchbegriff ein, um die Analyse anzuzeigen.")

# --- Vergleich der durchschnittlichen Metriken ---
st.subheader("Vergleich der durchschnittlichen Metriken")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"### Artikel mit '{search_term}'")
    if not filtered_df_with_term.empty:
        st.metric(label="Gesamtzahl der Treffer", value=len(filtered_df_with_term))
        mean_metrics_with_term = filtered_df_with_term[all_metrics_columns].mean().round(2)
        st.dataframe(mean_metrics_with_term)
    else:
        st.info("Keine passenden Artikel gefunden.")

with col2:
    st.markdown(f"### Artikel ohne '{search_term}'")
    if not filtered_df_without_term.empty:
        st.metric(label="Gesamtzahl der Treffer", value=len(filtered_df_without_term))
        mean_metrics_without_term = filtered_df_without_term[all_metrics_columns].mean().round(2)
        st.dataframe(mean_metrics_without_term)
    else:
        st.info("Alle Artikel enthalten den Suchbegriff oder es wurde kein Suchbegriff eingegeben.")

with col3:
    st.markdown("### Unterschied (mit - ohne Suchbegriff)")
    if search_term and not filtered_df_with_term.empty and not filtered_df_without_term.empty:
        differences = mean_metrics_with_term - mean_metrics_without_term

        # Farben basierend auf dem Vorzeichen der Differenz zuweisen
        colors = ['red' if x > 0 else 'green' for x in differences.values]

        fig_diff, ax_diff = plt.subplots(figsize=(10, 6))
        sns.barplot(x=differences.values, y=differences.index, ax=ax_diff, palette=colors)
        ax_diff.set_title('Unterschiede der durchschnittlichen Metriken')
        ax_diff.set_xlabel('Differenz')
        ax_diff.set_ylabel('Metrik')
        ax_diff.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig_diff)
    else:
        st.info("Geben Sie einen Suchbegriff und einen g&#252;ltigen Zeitraum ein, um die Unterschiede anzuzeigen.")

# --- &#220;bung 2: Top Posts nach Reaktion ---
st.subheader("Top Posts nach Reaktion (mit Suchbegriff)")

selected_reaction = st.selectbox(
    "W&#228;hlen Sie eine Reaktion aus, um Top-Posts anzuzeigen:",
    options=reaction_columns
)

if search_term and not filtered_df_with_term.empty:
    top_posts_by_reaction = filtered_df_with_term.sort_values(by=selected_reaction, ascending=False).head(10)
    if not top_posts_by_reaction.empty:
        st.dataframe(top_posts_by_reaction[['text', selected_reaction]])
    else:
        st.info(f"Keine Posts mit '{search_term}' gefunden, die '{selected_reaction}' Reaktionen haben.")
else:
    st.info("Bitte geben Sie einen Suchbegriff ein, um die Top-Posts anzuzeigen.")

st.subheader("Originale Daten (Auszug)")
st.dataframe(df.head())
