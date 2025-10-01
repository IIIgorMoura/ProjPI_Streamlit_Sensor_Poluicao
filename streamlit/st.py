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

df1['local'] = 'maua_interno'
df2['local'] = 'maua_externo'
df3['local'] = 'congonhas'

data = st.sidebar.slider(
    'Faixa de Tempo',
    min_value=df1['data'].min(),
    max_value=df1['data'].max(),
    value=(df1['data'].min(), df1['data'].max())
)


colunas_disponiveis = {
    'Temperatura': 'temperatura',
    'Umidade': 'umidade',
    'CO2': 'co2',
    'Pressão': 'pressao',
    'PM 2.5': 'poeira1',
    'PM 10': 'poeira2'
}

coluna_chave = st.sidebar.selectbox(
    'Filtro:',
    options=list(colunas_disponiveis.keys()),
    key='filtro_linha'
)

coluna_selecionada = colunas_disponiveis[coluna_chave]

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

# -------------------- definição graficos ----------

    tabelas = {
        "Mauá interno": df1_selecionado,
        "Mauá externo": df2_selecionado,
        "Aeroporto Congonhas": df3_selecionado
    }

    df_geral = pd.concat([df1_selecionado, df2_selecionado, df3_selecionado])

    mapa_das_cores = {
        'maua_interno': '#2761B3',   
        'maua_externo': '#7BBEE2',      
        'congonhas': '#7E6FB6',       
        'Maior_valor': '#409487', 
        'Menor_valor': '#131766', 
        'Média': '#4C8D26'       
    }
    
    def cards(coluna, simbolo=False):

        tabela_selecionada = st.selectbox(
                'Escolha a tabela',
                options=list(tabelas.keys()),
                key='filtro_tabela'
            )

        # Pega o DataFrame correspondente
        df_x = tabelas[tabela_selecionada]

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

    # Confirma se a coluna não esteja vazia
    if not df_geral[coluna_selecionada].dropna().empty: 

        if coluna_selecionada == 'temperatura':
            cards('temperatura', '°C')

        elif coluna_selecionada == 'umidade':
            cards('umidade', '%')

        elif coluna_selecionada == 'co2':
            cards('co2', 'ppm')

        elif coluna_selecionada == 'pressao':
            cards('pressao', 'hPa')

        # Separar por abas
        tab1, tab2, tab3 = st.tabs(["📈 Linhas", "📊 Barras", '⚠️ heatmap'])

        with tab1:
            # Filtro da medida
            medida = st.selectbox(
                'Medida:',
                ['Maior valor', 'Média', 'Menor valor'],
                key='filtro_medida_linha'
            )

            # Seleção dos dados conforme medida
            if medida == 'Maior valor':
                linhas_valores = df_geral.loc[
                    df_geral.groupby('data')[coluna_selecionada].idxmax()
                ]
            elif medida == 'Média':
                linhas_valores = df_geral.groupby(
                    ['local', 'data'], as_index=False
                )[coluna_selecionada].mean()
            elif medida == 'Menor valor':
                linhas_valores = df_geral.loc[
                    df_geral.groupby('data')[coluna_selecionada].idxmin()
                ]

            # Gráfico de linhas
            fig_linhas = px.line(
                linhas_valores,
                x='data',
                y=coluna_selecionada,
                title=f'{medida} de {coluna_chave} entre diferentes locais',
                color='local',
                color_discrete_map=mapa_das_cores,
                labels={
                    'data': 'Data',
                    'local': 'Local da coleta',
                    coluna_selecionada: coluna_chave
                }
            )

            st.plotly_chart(fig_linhas, use_container_width=True)

        with tab2:
            # Agregações
            valores_barra = df_geral.groupby(['local'], as_index=False).agg(
                Maior_valor=(coluna_selecionada, 'max'),
                Menor_valor=(coluna_selecionada, 'min'),
                Média=(coluna_selecionada, 'mean')
            )
            
            # Gráfico de barras
            fig_barras = px.bar(
                valores_barra,
                x='local',
                y=['Maior_valor', 'Menor_valor', 'Média'],
                barmode='group',
                title=f'Comparação da {coluna_chave} entre os locais',
                color_discrete_map=mapa_das_cores,
                labels={
                    'variable': 'Medida',
                    'value': 'Valor',
                    'local': 'Local'
                }
            )

            st.plotly_chart(fig_barras, use_container_width=True)

        with tab3:
            medida = st.selectbox(
                'Medida:',
                ['Maior valor', 'Média', 'Menor valor'],
                key='filtro_medida_heatmap'
            )

            if medida == 'Maior valor':

                heatmap_data = df_geral.pivot_table(
                    index='local',
                    columns='data',
                    values=coluna_selecionada,
                    aggfunc='max'  
                )

                if coluna_selecionada != 'CO2':
                    titulo = f'no maior valor da {coluna_selecionada}'
                else:
                    titulo = f'no maior valor do {coluna_selecionada}'

            elif medida == 'Média':

                heatmap_data = df_geral.pivot_table(
                    index='local',
                    columns='data',
                    values=coluna_selecionada,
                    aggfunc='mean'  
                )

                if coluna_selecionada != 'CO2':
                    titulo = f'na média da {coluna_selecionada}'
                else:
                    titulo = f'no Maior Valor do {coluna_selecionada}'

            elif medida == 'Menor valor':

                heatmap_data = df_geral.pivot_table(
                    index='local',
                    columns='data',
                    values=coluna_selecionada,
                    aggfunc='min'  
                )

                if coluna_selecionada != 'CO2':
                    titulo = f'no menor valor da {coluna_selecionada}'
                else:
                    titulo = f'no menor valor do {coluna_selecionada}'



            fig_heatmap = px.imshow(
                heatmap_data,
                labels=dict(x="Dias", y="Local", color=coluna_selecionada.capitalize()),
                x=heatmap_data.columns,
                y=heatmap_data.index,
                title=f'Heatmap com base {titulo}',
                color_continuous_scale="RdYlBu_r"  # escala de cores (azul=frio, vermelho=quente)
            )

            st.plotly_chart(fig_heatmap, use_container_width=True)

    else:
        st.warning('Não há dados disponiveis para os filtros selecionados', icon='🥺')

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