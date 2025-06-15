import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="Simple Finance App", page_icon="💰", layout="wide")

category_file = "categories.json"

# Inicialização de categorias
if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": [],
    }

if os.path.exists(category_file):
    with open(category_file, "r") as f:
        st.session_state.categories = json.load(f)

def save_categories():
    with open(category_file, "w") as f:
        json.dump(st.session_state.categories, f)

def categorize_transactions(df):
    df["Category"] = "Uncategorized"
    for category, keywords in st.session_state.categories.items():
        if category == "Uncategorized" or not keywords:
            continue

        lowered_keywords = [keyword.lower().strip() for keyword in keywords]

        for idx, row in df.iterrows():
            details = row["Details"].lower().strip()
            if any(keyword in details for keyword in lowered_keywords):
                df.at[idx, "Category"] = category

    return df

@st.cache_data
def load_transactions(file):
    try:
        df = pd.read_csv(file)
        df.columns = [col.strip() for col in df.columns]
        df["Amount"] = df["Amount"].str.replace(",", "").astype(float)
        df["Date"] = pd.to_datetime(df["Date"], format="%d %b %Y")
        return df
    except Exception as e:
        st.error(f"Erro ao processar arquivo: {str(e)}")
        return None

def add_keyword_to_category(category, keyword):
    keyword = keyword.strip()
    if keyword and keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        save_categories()
        return True
    return False

def main():
    st.title("💰 Simple Finance Dashboard")

    uploaded_file = st.file_uploader("📤 Upload seu arquivo CSV de transações", type=["csv"])

    if uploaded_file is not None:
        df = load_transactions(uploaded_file)

        if df is not None:
            df = categorize_transactions(df)
            debits_df = df[df["Debit/Credit"] == "Debit"].copy()
            credits_df = df[df["Debit/Credit"] == "Credit"].copy()
            st.session_state.debits_df = debits_df.copy()

            tab1, tab2 = st.tabs(["💸 Despesas (Débitos)", "💳 Recebimentos (Créditos)"])

            with tab1:
                new_category = st.text_input("📌 Nome da nova categoria")
                add_button = st.button("➕ Adicionar Categoria")

                if add_button and new_category:
                    if new_category not in st.session_state.categories:
                        st.session_state.categories[new_category] = []
                        save_categories()
                        st.rerun()

                st.subheader("🧾 Suas Despesas")
                edited_df = st.data_editor(
                    st.session_state.debits_df[["Date", "Details", "Amount", "Category"]],
                    column_config={
                        "Date": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                        "Amount": st.column_config.NumberColumn("Valor", format="%.2f AED"),
                        "Category": st.column_config.SelectboxColumn(
                            "Categoria",
                            options=list(st.session_state.categories.keys())
                        )
                    },
                    hide_index=True,
                    use_container_width=True,
                    key="category_editor"
                )

                save_button = st.button("✅ Aplicar Alterações", type="primary")
                if save_button:
                    for idx, row in edited_df.iterrows():
                        new_category = row["Category"]
                        if new_category != st.session_state.debits_df.at[idx, "Category"]:
                            st.session_state.debits_df.at[idx, "Category"] = new_category
                            details = row["Details"]
                            add_keyword_to_category(new_category, details)
                    st.success("Categorias atualizadas com sucesso!")

                with st.expander("🔍 Filtros"):
                    categorias = st.multiselect("Filtrar por categoria", st.session_state.debits_df["Category"].unique())
                    datas = st.date_input("Período", [st.session_state.debits_df["Date"].min(), st.session_state.debits_df["Date"].max()])

                    df_filtrado = st.session_state.debits_df.copy()
                    if categorias:
                        df_filtrado = df_filtrado[df_filtrado["Category"].isin(categorias)]
                    if datas:
                        df_filtrado = df_filtrado[
                            (df_filtrado["Date"] >= pd.to_datetime(datas[0])) &
                            (df_filtrado["Date"] <= pd.to_datetime(datas[1]))
                        ]

                    st.dataframe(df_filtrado)

                st.subheader("📊 Resumo por Categoria")
                category_totals = st.session_state.debits_df.groupby("Category")["Amount"].sum().reset_index()
                category_totals = category_totals.sort_values("Amount", ascending=False)

                st.dataframe(
                    category_totals,
                    column_config={
                        "Amount": st.column_config.NumberColumn("Valor Total", format="%.2f AED")
                    },
                    use_container_width=True,
                    hide_index=True
                )

                fig = px.pie(
                    category_totals,
                    values="Amount",
                    names="Category",
                    title="Distribuição de Despesas por Categoria"
                )
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("📈 Evolução dos Gastos por Data")
                line_df = st.session_state.debits_df.groupby(["Date", "Category"])["Amount"].sum().reset_index()
                fig_line = px.line(line_df, x="Date", y="Amount", color="Category", title="Gastos ao Longo do Tempo")
                st.plotly_chart(fig_line, use_container_width=True)

                st.download_button(
                    label="📥 Baixar gastos categorizados (CSV)",
                    data=st.session_state.debits_df.to_csv(index=False).encode("utf-8"),
                    file_name="gastos_categorizados.csv",
                    mime="text/csv"
                )

            with tab2:
                st.subheader("📋 Resumo de Recebimentos")
                total_payments = credits_df["Amount"].sum()
                st.metric("Total Recebido", f"{total_payments:,.2f} AED")
                st.dataframe(credits_df, use_container_width=True)
                
                
                _
main()

