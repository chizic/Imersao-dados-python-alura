import streamlit as st
import pandas as pd
import plotly.express as px

# Set the page configuration
st.set_page_config(
    page_title='Dashboard de Salários na Área de dados',
    page_icon='🎲',
    layout='wide',
)

# Load the dataset
df = pd.read_csv('https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv')

#--- Sidebar configuration(Filters) ---
st.sidebar.header('🔍 Filtros')

# Filter by Year
available_years = sorted(df['ano'].unique())
selected_years = st.sidebar.multiselect('Ano', available_years, default=available_years)

# Filter bt Experience level
available_level = sorted(df['senioridade'].unique())
selected_level = st.sidebar.multiselect('Nível de Experiência', available_level, default=available_level)

#Filter by Contract type
available_contract = sorted(df['contrato'].unique())
selected_contract = st.sidebar.multiselect('Tipo de Contrato', available_contract, default=available_contract)

# Filter by Company Size
available_size = sorted(df['tamanho_empresa'].unique())
selected_size = st.sidebar.multiselect('Tamanho da Empresa', available_size, default=available_size)

#Apply filters to dataframe
filtered_df = df[
                 (df['ano'].isin(selected_years)) &
                 (df['senioridade'].isin(selected_level)) &
                 (df['contrato'].isin(selected_contract))&
                 (df['tamanho_empresa'].isin(selected_size))
                ]

#--- Main content ---
st.write('😀 Bem-vindo ao dashboard!')
st.title('🎲Dashboard de Salários na Área de dados')
st.markdown('Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros na barra lateral para refinar a sua análise.')

#principal metrics (KPIs)
st.subheader('📈 Métricas gerais(Salário anual em USD)')

if not filtered_df.empty:
    avg_salary = filtered_df['usd'].mean()
    max_salary = filtered_df['usd'].max()
    min_salary = filtered_df['usd'].min()
    total_entries = filtered_df.shape[0]
    most_frequent_position = filtered_df['cargo'].mode()[0]
else:
    avg_salary, median_salary, max_salary, total_entries, most_frequent_position = 0, 0, 0, 0, ''

col1, col2, col3, col4, = st.columns(4)
col1.metric('Salário médio', f'${avg_salary:,.0f}')
col2.metric('Salário máximo', f'${max_salary:,.0f}')
col3.metric('Total de entradas', f'{total_entries:,}')
col4.metric('Cargo mais frequente', most_frequent_position)

st.markdown('---')

#--- Visualizations with Plotly ---
st.subheader('📊 Gráficos')

graph_col1, graph_col2 = st.columns(2)

with graph_col1:
    if not filtered_df.empty:
        top_positions = filtered_df.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        positions_graph = px.bar(
            top_positions,
            x='usd',
            y='cargo',
            orientation='h',
            title='Top 10 Cargos por salário médio',
            labels={'usd': 'Média Salarial Anual (USD)', 'cargo':'Cargo'}
        )
        positions_graph.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(positions_graph, use_container_width=True)
    else:
        st.warning('Nenhum dado disponível para exibir o gráfico de cargos.')

with graph_col2:
    if not filtered_df.empty:
        hist_graph = px.histogram(
            filtered_df,
            x='usd',
            nbins=30,
            title='Distribuição salarial anual',
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}   
        )
        hist_graph.update_layout(title_x=0.1)
        st.plotly_chart(hist_graph, use_container_width=True)
    else:
        st.warning('Nenhum dado para exibir o gráfico de distribuição salarial.')

graph_col3, graph_col4 = st.columns(2)
with graph_col3:
    if not filtered_df.empty:
        remote_count = filtered_df['remoto'].value_counts().reset_index()
        remote_count.columns = ['tipo_trabalho', 'quantidade']
        remote_graph = px.pie(
            remote_count,
            names='tipo_trabalho',
            values='quantidade',
            title='proporção dos tipos de trabalho',
            hole=0.5
        )
        remote_graph.update_traces(textinfo='percent+label')
        remote_graph.update_layout(title_x=0.1)
        st.plotly_chart(remote_graph, use_container_width=True)
    
    else: 
        st.warning('Nenhum dado disponível para exibir o gráfico de tipos de trabalho.')

with graph_col4: 
    if not filtered_df.empty:
        df_ds = filtered_df[filtered_df['cargo']=='Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        country_graph = px.choropleth(media_ds_pais,
                            locations = 'residencia_iso3',
                            color='usd',
                            color_continuous_scale='rdylgn',
                            title='Média salarial para Cientista de dados por País',
                            labels= {'usd': 'Média Salarial Anual (USD)', 'residencia_iso3': 'País'}
        )
        country_graph.update_layout(title_x=0.1)
        st.plotly_chart(country_graph, use_container_width=True)

    else:
        st.warning('Nenhum dado para exibir no gráfico de Países.')

#---Tabela de dados detalhados ---
st.subheader('📋 Tabela de Dados Detalhados')
st.dataframe(filtered_df)
