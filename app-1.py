import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Dashboard UBS", layout="wide")

st.title("🏥 Dashboard de Unidades Básicas de Saúde")
st.write(
    "Este dashboard apresenta uma análise das Unidades Básicas de Saúde "
    "(UBS) cadastradas na base do Cadastro Nacional de Estabelecimentos "
    "de Saúde (CNES), do Ministério da Saúde."
)

# Procura automaticamente um CSV na mesma pasta do app
pasta = Path(__file__).parent
csvs = list(pasta.glob("*.csv"))

arquivo = st.file_uploader("Ou envie outro arquivo CSV", type=["csv"])

try:
    if arquivo is not None:
        try:
            df = pd.read_csv(arquivo, sep=None, engine="python", encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(arquivo, sep=None, engine="python", encoding="latin1")
    elif csvs:
        try:
            df = pd.read_csv(csvs[0], sep=None, engine="python", encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(csvs[0], sep=None, engine="python", encoding="latin1")
    else:
        st.info("Coloque o arquivo CSV das UBS na mesma pasta do app.py.")
        st.stop()

    # Tratamento básico
    df.columns = df.columns.astype(str).str.strip()

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    duplicados = int(df.duplicated().sum())
    if duplicados:
        df = df.drop_duplicates()

    st.success("Base carregada com sucesso!")

    # Identificação da coluna de UF/estado
    possiveis_uf = [
        c for c in df.columns
        if any(p in c.lower() for p in ["uf", "estado", "sigla_uf"])
    ]

    st.subheader("📊 Indicadores")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de registros", f"{len(df):,}".replace(",", "."))
    c2.metric("Quantidade de colunas", len(df.columns))
    c3.metric("Duplicados removidos", duplicados)

    st.subheader("📋 Visualização dos dados")
    st.dataframe(df.head(10), use_container_width=True)

    st.subheader("❓ Perguntas da análise")
    st.write("**1. Qual estado possui a maior quantidade de Unidades Básicas de Saúde?**")
    st.write("**2. Como as Unidades Básicas de Saúde estão distribuídas entre os estados brasileiros?**")

    if possiveis_uf:
        col_uf = possiveis_uf[0]

        dados_uf = (
            df[col_uf]
            .replace(["nan", "None", ""], pd.NA)
            .dropna()
            .value_counts()
            .reset_index()
        )
        dados_uf.columns = ["Estado", "Quantidade"]

        # Filtro
        estados = ["Todos"] + sorted(dados_uf["Estado"].astype(str).unique().tolist())
        escolhido = st.selectbox("🔎 Filtre por estado", estados)

        if escolhido != "Todos":
            df_filtrado = df[df[col_uf].astype(str) == escolhido]
        else:
            df_filtrado = df

        st.subheader("📈 Gráfico 1 — Quantidade de UBS por estado")
        fig1 = px.bar(
            dados_uf,
            x="Estado",
            y="Quantidade",
            title="Quantidade de Unidades Básicas de Saúde por estado",
            labels={"Estado": "Estado", "Quantidade": "Quantidade de UBS"},
        )
        st.plotly_chart(fig1, use_container_width=True)

        maior = dados_uf.iloc[0]
        st.markdown(
            f"""
            ### O que podemos observar?
            O gráfico compara a quantidade de registros de UBS entre os estados.
            O estado com maior quantidade de registros na base é **{maior['Estado']}**,
            com **{int(maior['Quantidade']):,} registros**.
            """.replace(",", ".")
        )

        st.subheader("📊 Gráfico 2 — Distribuição das UBS")
        fig2 = px.pie(
            dados_uf,
            names="Estado",
            values="Quantidade",
            title="Distribuição das UBS por estado",
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown(
            """
            ### O que podemos observar?
            Este gráfico apresenta a participação de cada estado no total de
            registros da base, permitindo visualizar como as UBS estão
            distribuídas entre os estados.
            """
        )

        st.subheader("🔍 Dados do filtro")
        st.metric("Registros no filtro selecionado", len(df_filtrado))

    else:
        st.warning(
            "Não foi encontrada automaticamente uma coluna de UF/estado. "
            "As colunas disponíveis estão abaixo:"
        )
        st.write(list(df.columns))

    st.subheader("🧹 Verificação dos dados")
    faltantes = df.isnull().sum().reset_index()
    faltantes.columns = ["Coluna", "Valores ausentes"]
    st.dataframe(faltantes, use_container_width=True)

    st.subheader("🤖 Exemplo de uso da Inteligência Artificial")
    st.write(
        "A IA foi utilizada para auxiliar na escolha dos gráficos, na organização "
        "do código e na identificação de possíveis tratamentos necessários. "
        "As sugestões foram verificadas comparando os resultados do dashboard "
        "com os dados da base."
    )

    st.caption(
        "Fonte: Ministério da Saúde — Cadastro Nacional de Estabelecimentos de Saúde (CNES)."
    )

except Exception as erro:
    st.error("Não foi possível carregar a base.")
    st.write("Erro:", erro)
