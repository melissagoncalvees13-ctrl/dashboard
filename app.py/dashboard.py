import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard de Saúde — Dengue", layout="wide")
st.title("Dashboard de Saúde Pública: Dengue no Brasil")
st.write(
    "Este dashboard analisa a evolução dos casos prováveis de dengue no Brasil "
    "entre 2000 e 2023, usando uma série histórica do Ministério da Saúde."
)
st.caption("Fonte: Ministério da Saúde — Série histórica de casos prováveis de dengue (2000–2023).")
arquivo = st.file_uploader("Envie o arquivo CSV de dados", type=["csv"])

if arquivo is not None:
    df = pd.read_csv(arquivo)
else:
    st.info("Para começar, use o arquivo dengue_brasil_2000_2023.csv fornecido com o projeto.")
    st.stop()

necessarias = {"ano", "casos_provaveis"}
if not necessarias.issubset(df.columns):
    st.error("O CSV precisa conter as colunas 'ano' e 'casos_provaveis'.")
    st.stop()

df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
df["casos_provaveis"] = pd.to_numeric(df["casos_provaveis"], errors="coerce")
df = df.dropna(subset=["ano", "casos_provaveis"]).copy()
df["ano"] = df["ano"].astype(int)
df = df.drop_duplicates()

if df.empty:
    st.warning("Não há linhas válidas para mostrar.")
    st.stop()

total = int(df["casos_provaveis"].sum())
ano_pico = int(df.loc[df["casos_provaveis"].idxmax(), "ano"])
maior_valor = int(df["casos_provaveis"].max())

c1, c2, c3 = st.columns(3)
c1.metric("Total somado no período", f"{total:,}".replace(",", "."))
c2.metric("Ano com mais casos", str(ano_pico))
c3.metric("Maior número anual", f"{maior_valor:,}".replace(",", "."))

st.subheader("1. Como os casos prováveis mudaram ao longo dos anos?")
fig_linha = px.line(
    df.sort_values("ano"),
    x="ano",
    y="casos_provaveis",
    markers=True,
    title="Casos prováveis de dengue por ano"
)
fig_linha.update_layout(xaxis_title="Ano", yaxis_title="Casos prováveis")
st.plotly_chart(fig_linha, use_container_width=True)

st.write(
    "O gráfico de linha permite observar os anos de aumento e diminuição. "
    "Ele mostra a evolução dos registros, mas não explica sozinho as causas dessas mudanças."
)

st.subheader("2. Quais anos tiveram os maiores números de casos?")
top_anos = df.nlargest(min(10, len(df)), "casos_provaveis").sort_values("casos_provaveis")
fig_barras = px.bar(
    top_anos,
    x="casos_provaveis",
    y="ano",
    orientation="h",
    title="Até 10 anos com mais casos prováveis"
)
fig_barras.update_layout(xaxis_title="Casos prováveis", yaxis_title="Ano")
st.plotly_chart(fig_barras, use_container_width=True)

st.write(
    f"Na base enviada, o maior valor anual é de {maior_valor:,} casos prováveis, "
    f"registrado em {ano_pico}. A comparação destaca os anos com números mais altos."
    .replace(",", ".")
)

st.subheader("Dados utilizados")
st.dataframe(df.sort_values("ano"), use_container_width=True)