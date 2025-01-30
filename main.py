import pandas as pd
import time
import streamlit as st # type: ignore
import market_api as mapi

def fetch_data():
    df = pd.DataFrame(columns=[
        "set_url",
        "set_max_buy",
        "set_min_sell",
        "items_max_buy_sum",
        "items_min_sell_sum",
        "number_of_items",
        "instant_profit",
        "listed_profit",
    ])
    prime_sets = mapi.fetch_items_list()
    for item_set in prime_sets["url_name"]:
        time.sleep(mapi.TIME_TO_WAIT)  # API limitáció miatt
        try:
            df = pd.concat([df, pd.DataFrame(mapi.fetch_set_info(item_set), index=[0])], ignore_index=True)
        except Exception as e:
            pass
    return df
def main():
    # Adatok inicializálása (ha még nincsenek betöltve)
    if "data" not in st.session_state:
        with st.spinner("Loading data..."):  # Spinner a betöltéshez
            st.session_state["data"] = fetch_data()

    st.title("Warframe market analyzer")

    # Frissítési gomb
    if st.button("Refresh data"):
        st.write("Refreshing data...")
        st.session_state["data"] = fetch_data()
        st.success("Data refreshed successfully!")

    # DataFrame megjelenítése
    df = st.session_state["data"]

    # Rendezési opciók
    sort_column = st.selectbox(
        "Sort columns:",
        options=["instant_profit", "listed_profit"],
        index=0
    )
    sort_order = st.radio(
        "Sort order:",
        options=["decreasing", "ascending"],
        index=0
    )
    ascending = sort_order == "ascending"

    # Adatok rendezése
    df_sorted = df.sort_values(by=sort_column, ascending=ascending)
    st.write("Sorted Datatable:")
    st.dataframe(df_sorted)

if __name__ == "__main__":
    main()
