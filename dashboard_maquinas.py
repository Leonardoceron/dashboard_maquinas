
# dashboard_maquinas.py
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from io import BytesIO

# Gerando dataset simulado
def gerar_dados():
    np.random.seed(42)
    n = 200
    dados = pd.DataFrame({
        'ID_Maquina': np.random.choice([f'Maq_{i}' for i in range(1, 21)], n),
        'Status': np.random.choice(['Funcionando', 'Parada', 'Falha'], n, p=[0.6, 0.25, 0.15]),
        'Sensor1': np.random.normal(50, 10, n),
        'Sensor2': np.random.normal(75, 15, n),
        'Sensor3': np.random.normal(100, 20, n),
        'Tempo_Operacao': np.random.uniform(100, 500, n),
        'Data': pd.date_range(start='2024-01-01', periods=n, freq='D'),
    })
    dados['Necessita_Manutencao'] = np.where((dados['Sensor1'] > 70) | (dados['Status'] == 'Falha'), 'Sim', 'Não')
    return dados

# Função para download do dataset
def gerar_download(df):
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer

# Dados
df = gerar_dados()
st.set_page_config(layout="wide", page_title="Dashboard de Máquinas")
st.title("📊 Dashboard de Monitoramento de Máquinas")

# Abas
aba1, aba2, aba3, aba4 = st.tabs(["Visão Geral", "Análises Detalhadas", "Correlação e Insights", "Download dos Dados"])

# Filtros gerais com sidebar
st.sidebar.header("Filtros")
status_filtrado = st.sidebar.multiselect("Status da Máquina", df['Status'].unique(), default=df['Status'].unique())
data_filtrada = st.sidebar.date_input("Intervalo de Data", [df['Data'].min(), df['Data'].max()])
id_filtrado = st.sidebar.multiselect("ID da Máquina", df['ID_Maquina'].unique(), default=df['ID_Maquina'].unique())

# Aplicando filtros
df_filtrado = df[(df['Status'].isin(status_filtrado)) &
                 (df['ID_Maquina'].isin(id_filtrado)) &
                 (df['Data'] >= pd.to_datetime(data_filtrada[0])) &
                 (df['Data'] <= pd.to_datetime(data_filtrada[1]))]

# ===== ABA 1 - Visão Geral =====
with aba1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Máquinas", df_filtrado['ID_Maquina'].nunique())
    col2.metric("Máquinas que precisam de manutenção", df_filtrado[df_filtrado['Necessita_Manutencao'] == 'Sim'].shape[0])
    col3.metric("Período Analisado", f"{data_filtrada[0]} a {data_filtrada[1]}")

    st.subheader("Média dos Sensores por Máquina")
    media_por_maquina = df_filtrado.groupby('ID_Maquina')[['Sensor1', 'Sensor2', 'Sensor3']].mean().reset_index()
    st.dataframe(media_por_maquina)
    fig = px.bar(media_por_maquina, x='ID_Maquina', y=['Sensor1', 'Sensor2', 'Sensor3'], barmode='group')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Percentual de Status das Máquinas")
    status_percentual = df_filtrado['Status'].value_counts(normalize=True)*100
    fig = px.pie(values=status_percentual.values, names=status_percentual.index, title="Distribuição de Status")
    st.plotly_chart(fig, use_container_width=True)

# ===== ABA 2 - Análises Detalhadas =====
with aba2:
    st.subheader("Máquinas que Precisam de Manutenção")
    manutencao_df = df_filtrado[df_filtrado['Necessita_Manutencao'] == 'Sim']
    st.dataframe(manutencao_df)

    st.subheader("Distribuição Sensor 1")
    fig, ax = plt.subplots()
    sns.histplot(df_filtrado['Sensor1'], kde=True, bins=30, ax=ax)
    st.pyplot(fig)

    st.subheader("Tempo médio de operação por Status")
    fig = px.box(df_filtrado, x='Status', y='Tempo_Operacao', color='Status')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Relação Sensor1 vs Sensor2")
    fig = px.scatter(df_filtrado, x='Sensor1', y='Sensor2', color='Status', hover_data=['ID_Maquina'])
    st.plotly_chart(fig, use_container_width=True)

# ===== ABA 3 - Correlação e Insights =====
with aba3:
    st.subheader("Correlação entre Variáveis")
    corr = df_filtrado[['Sensor1', 'Sensor2', 'Sensor3', 'Tempo_Operacao']].corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)

    st.subheader("Insight Adicional")
    tendencia = df_filtrado.groupby('Data')[['Sensor1', 'Sensor2']].mean().reset_index()
    fig = px.line(tendencia, x='Data', y=['Sensor1', 'Sensor2'], title="Tendência dos Sensores ao Longo do Tempo")
    st.plotly_chart(fig, use_container_width=True)

# ===== ABA 4 - Download dos Dados =====
with aba4:
    st.subheader("Visualização dos Dados Filtrados")
    st.dataframe(df_filtrado)

    st.download_button(
        label="Baixar dados como CSV",
        data=gerar_download(df_filtrado),
        file_name='dados_maquinas_filtrado.csv',
        mime='text/csv'
    )
