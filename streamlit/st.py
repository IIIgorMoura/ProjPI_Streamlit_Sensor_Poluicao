import streamlit as st
from streamlit_option_menu import option_menu
import plotly_express as px
import pandas as pd
from query import get_connection



engine = get_connection()

query = "SELECT * FROM tb_sensor"


with engine.connect() as conn:
    df1 = pd.read_sql(query, conn)
    df2 = pd.read_sql(query, conn)
    df3 = pd.read_sql(query, conn)

if st.sidebar.button('Atualizar Dados'):
    with engine.connect() as conn:
        df1 = pd.read_sql(query, conn)
        df2 = pd.read_sql(query, conn)
        df3 = pd.read_sql(query, conn)


# ---------------- Filtros ------------------
df1['data'] = df1['data_hora'].dt.date
df2['data'] = df2['data_hora'].dt.date
df3['data'] = df3['data_hora'].dt.date

df1['local'] = 'df1'
df2['local'] = 'df2'
df3['local'] = 'df3'

data = st.sidebar.slider(
    'Faixa de Tempo',
    min_value=df1['data'].min(),
    max_value=df1['data'].max(),
    value=(df1['data'].min(), df1['data'].max())
)

# ---------------- Aplicação Filtros --------

df1_selecionado = df1[
    (df1['data'] >= data[0]) &
    (df1['data'] <= data[1])
]

df2_selecionado = df2[
    (df2['data'] >= data[0]) &
    (df2['data'] <= data[1])
]

df3_selecionado = df3[
    (df3['data'] >= data[0]) &
    (df3['data'] <= data[1])
]

# ---------------- Dashboard ----------------

def dashboard():

    def tabela():   
        # Dicionário mapeando nomes para DataFrames
        tabelas = {
            "df1": df1_selecionado,
            "df2": df2_selecionado,
            "df3": df3_selecionado
        }

        with st.expander('Tabela dos registros'):
            # Seleção pelo nome
            tabela_selecionada = st.selectbox(
                'Escolha a tabela',
                options=list(tabelas.keys()),
                key='filtro_tabela'
            )

            # Pega o DataFrame correspondente
            df_x = tabelas[tabela_selecionada]

            # Seleção de colunas
            exibicao = st.multiselect(
                "Filtro",
                df_x.columns,
                default=[],
                key="filtro_exibicao"
            )

            if exibicao:
                st.write(df_x[exibicao])

    def cards(coluna, df_x, simbolo=False):
        if not df_x[coluna].dropna().empty:
            # Encontrar os valores
            maior_coluna = df_x[coluna].max()
            menor_coluna = df_x[coluna].min()
            media_coluna = df_x[coluna].mean()

            # Encontrar as datas correspondentes
            data_maior = df_x.loc[df_x[coluna] == maior_coluna, 'data_hora'].iloc[0]
            data_menor = df_x.loc[df_x[coluna] == menor_coluna, 'data_hora'].iloc[0]

            # Criar os cards
            card1, card2, card3 = st.columns(3, gap="large")

            with card1:
                if simbolo:
                    st.metric(
                        "Menor Temperatura Registrada:", 
                        value=f'{menor_coluna:,.1f} {simbolo}',
                        delta=f'{data_menor}'
                    )
                else:
                    st.metric(
                        "Menor Temperatura Registrada:", 
                        value=f'{menor_coluna:,.1f}',
                        delta=f'{data_menor}'
                    )

            with card2:
                if simbolo:
                    st.metric(
                        "Média da Temperatura:", 
                        value=f'{media_coluna:,.1f} {simbolo}',
                    )
                else:
                    st.metric(
                        "Média da Temperatura:", 
                        value=f'{media_coluna:,.1f}',
                    )

            with card3:
                if simbolo:
                    st.metric(
                        "Maior Temperatura Registrada:", 
                        value=f'{maior_coluna:,.1f} {simbolo}',
                        delta=f'{data_maior}'
                    )
                else:
                    st.metric(
                        "Maior Temperatura Registrada:", 
                        value=f'{maior_coluna:,.1f}',
                        delta=f'{data_maior}'
                    )
            st.markdown("""-----""")

    def grafico_linha():

        df_geral = pd.concat([df1_selecionado, df2_selecionado, df3_selecionado])

        colunas_disponiveis = {
            'Temperatura': 'temperatura',
            'Umidade': 'umidade',
            'CO2': 'co2',
            'Pressão': 'pressao'
        }

        coluna_chave = st.selectbox(
            'Filtro:',
            options=list(colunas_disponiveis.keys())
        )

        coluna_selecionada = colunas_disponiveis[coluna_chave]


        if not df_geral[coluna_selecionada].dropna().empty: 

            medida = st.selectbox(
                'Filtro:',
                ['Máximo', 'Média', 'Menor']
            )

            if medida == 'Máximo':
                linhas_valores = df_geral.loc[df_geral.groupby('data')[coluna_selecionada].idxmax()] 

            elif medida == 'Média':
                linhas_valores = df_geral.groupby(['local', 'data'], as_index=False)[coluna_selecionada].mean()

            elif medida == 'Menor':
                linhas_valores = df_geral.loc[df_geral.groupby('data')[coluna_selecionada].idxmin()]

            fig_linhas = px.line(
                linhas_valores,
                x='data',
                y=coluna_selecionada,
                title='Um grafico ai?',
                color='local'
            )

            st.plotly_chart(fig_linhas, use_container_width=True)
    
    def grafico_barra():

        tabelas = {
            "df1": df1_selecionado,
            "df2": df2_selecionado,
            "df3": df3_selecionado
        }

        tabela_selecionada = st.selectbox(
                'Escolha a tabela',
                options=list(tabelas.keys()),
                key='filtro_tabela'
            )

            # Pega o DataFrame correspondente
        df_x = tabelas[tabela_selecionada]

        colunas_disponiveis = {
            'Temperatura': 'temperatura',
            'Umidade': 'umidade',
            'CO2': 'co2',
            'Pressão': 'pressao'
        }

        coluna_chave = st.selectbox(
            'Filtro:',
            options=list(colunas_disponiveis.keys())
        )

        coluna_selecionada = colunas_disponiveis[coluna_chave]

        if not df_x[coluna_selecionada].dropna().empty: 
        
            valores_barra = df_x.groupby(['local', 'data'], as_index=False).agg(
                max=(coluna_selecionada, 'max'),
                min=(coluna_selecionada, 'min'),
                media=(coluna_selecionada, 'mean')
            )

            st.write(valores_barra)


    grafico_barra()
# ---------------- Páginas ------------------

def paginas():
    with st.sidebar:
        selecionado = option_menu(
            menu_title="Menu",
            options=['Dashboard', 'Relatórios'],
            icons=['house', 'bar-chart'],
            default_index=0
        )

    if selecionado == 'Dashboard':
        dashboard()

    elif selecionado == 'Relatórios':
        st.write('relatorio')

paginas()

# python -m streamlit run .\streamlit\st.py