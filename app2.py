import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector  # type: ignore

st.set_page_config(page_title="Visualização de Dados Hospitalares", layout="wide")
st.title(" Painel Interativo de Dados Hospitalares")

@st.cache_data
def carregar_dados_mysql():
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
            database="trabalhobd"
        )
        query = "SELECT * FROM basedados2025;"
        df = pd.read_sql(query, conexao)
        conexao.close()
        origem = "MySQL"
    except Exception as e:
        st.error(f"Erro ao conectar ao MySQL: {e}")
        return None, None
    return df, origem


# ===================== CARREGAMENTO =====================
df, origem = carregar_dados_mysql()

if df is None:
    st.stop()

st.sidebar.success(f" Dados carregados via: {origem}")

# ===================== LIMPEZA BÁSICA =====================
for col in df.columns:
    if "Data" in col:
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
        except:
            pass

if "Data de Nascimento" in df.columns:
    df["Idade"] = (pd.Timestamp.now() - df["Data de Nascimento"]).dt.days // 365


st.subheader("Visualização do Dataset")

# Mostra as 10 primeiras linhas por padrão
st.dataframe(df.head(10), use_container_width=True)

# Opção para visualizar mais linhas, se desejar
with st.expander("Ver dataset completo"):
    st.dataframe(df, use_container_width=True)

# ===================== VISÃO GERAL =====================
st.subheader("Visão Geral dos Dados")

col1, col2, col3 = st.columns(3)
col1.metric("Total de Atendimentos", len(df))
if "Sexo" in df.columns:
    col2.metric("Proporção Feminina (%)", round((df["Sexo"].str.upper().eq("F").mean())*100, 1))
if "Municício" in df.columns:
    col3.metric("Municípios Únicos", df["Municício"].nunique())

st.markdown("---")
st.write("### Análises detalhadas dos principais indicadores do dataset:")

# ===================== OUTROS GRÁFICOS =====================

# Distribuição por sexo
if "Sexo" in df.columns:
    fig1 = px.histogram(
        df,
        x="Sexo",
        color="Sexo",
        title="Distribuição por Sexo dos Pacientes",
        text_auto=True
    )
    st.plotly_chart(fig1, use_container_width=True)

# Atendimentos por Unidade
if "Descrição da Unidade" in df.columns:
    top_unidades = df["Descrição da Unidade"].value_counts().nlargest(10)
    fig2 = px.bar(
        x=top_unidades.index,
        y=top_unidades.values,
        text=top_unidades.values,
        title="Top 10 Unidades com Mais Atendimentos",
        labels={"x": "Unidade de Atendimento", "y": "Quantidade"}
    )
    st.plotly_chart(fig2, use_container_width=True)

# Faixa etária dos pacientes
if "Idade" in df.columns:
    fig3 = px.histogram(
        df,
        x="Idade",
        nbins=20,
        title="Distribuição Etária dos Pacientes",
        labels={"Idade": "Idade (anos)", "count": "Quantidade de Pacientes"}
    )
    st.plotly_chart(fig3, use_container_width=True)

# CID mais comuns (diagnósticos)
if "Descrição do CID" in df.columns:
    top_cid = df["Descrição do CID"].value_counts().nlargest(10)
    fig4 = px.bar(
        x=top_cid.values,
        y=top_cid.index,
        orientation="h",
        text=top_cid.values,
        title="Principais Diagnósticos (CID)",
        labels={"x": "Quantidade", "y": "Diagnóstico"}
    )
    st.plotly_chart(fig4, use_container_width=True)

# Encaminhamento para Especialista
if "Encaminhamento para Atendimento Especialista" in df.columns:
    encaminhamento = df["Encaminhamento para Atendimento Especialista"].value_counts()
    fig5 = px.pie(
        values=encaminhamento.values,
        names=encaminhamento.index,
        title="Encaminhamento para Especialista",
        hole=0.3
    )
    st.plotly_chart(fig5, use_container_width=True)

# Atendimentos por bairro (top 10)
if "Bairro" in df.columns:
    top_bairros = df["Bairro"].value_counts().nlargest(10)
    fig6 = px.bar(
        x=top_bairros.index,
        y=top_bairros.values,
        text=top_bairros.values,
        title="📍 Top 10 Bairros com Mais Atendimentos",
        labels={"x": "Bairro", "y": "Quantidade"}
    )
    st.plotly_chart(fig6, use_container_width=True)

# ===================== RODAPÉ =====================
st.info(" O dataset utilizado mostra dados hospitalares de um período curto e pode não ser preciso para análises extensas.")
