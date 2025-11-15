import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

ruta = 'https://github.com/juliandariogiraldoocampo/analisis_taltech/raw/refs/heads/main/explorador/Estado_de_la_prestaci%C3%B3n_del_servicio_de_energ%C3%ADa_en_Zonas_No_Interconectadas_20251021.csv'
df = pd.read_csv(ruta)

df['ENERGÍA REACTIVA'] = df['ENERGÍA REACTIVA'].str.replace(',', '').astype(float).astype(int)
df['ENERGÍA ACTIVA'] = df['ENERGÍA ACTIVA'].str.replace(',', '').astype(float).astype(int)
df['POTENCIA MÁXIMA'] = df['POTENCIA MÁXIMA'].str.replace(',', '').astype(float)

lst_cambio = [['Á','A'],['É','E'], ['Í','I'], ['Ó','O'], ['Ú','U']]

# Realizar los reemplazos en las columnas 'DEPARTAMENTO' y 'MUNICIPIO'
for i in range(5):
    df['DEPARTAMENTO'] = df['DEPARTAMENTO'].str.replace(lst_cambio[i][0],lst_cambio[i][1])
    df['MUNICIPIO'] = df['MUNICIPIO'].str.replace(lst_cambio[i][0],lst_cambio[i][1])

# Crear una condición negativa para filtrar los departamentos no deseados
condicion_filtro = ~df['DEPARTAMENTO'].isin([
'ARCHIPIELAGO DE SAN ANDRES',
'ARCHIPIELAGO DE SAN ANDRES y PROVIDENCIA',
'ARCHIPIELAGO DE SAN ANDRES, PROVIDENCIA Y SANTA CATALINA'
])
df_colombia_continental = df[condicion_filtro]

df_agrupado = df_colombia_continental.groupby(['DEPARTAMENTO', 'MUNICIPIO'])[['ENERGÍA ACTIVA', 'ENERGÍA REACTIVA']].sum().reset_index()

df_pivote = df_colombia_continental.pivot_table(
    index = 'DEPARTAMENTO',
    columns = 'AÑO SERVICIO',
    values = ['ENERGÍA ACTIVA'],
    aggfunc = 'sum'
)

# Cálculo de Total por Año de Energía Activa
df_activa = df_colombia_continental.pivot_table(
    columns = 'AÑO SERVICIO',
    values = ['ENERGÍA ACTIVA'],
    aggfunc = 'sum'
).reset_index(drop=True)

filas = df.shape[0]
variables = df.shape[1]
num_deptos = df['DEPARTAMENTO'].nunique()
num_mpios = df['MUNICIPIO'].nunique()

# Cálculo de Totales y Deltas
tot_ac_25 = df_activa[2025].tolist()[0]
tot_ac_24 = df_activa[2024].tolist()[0]
tot_ac_23 = df_activa[2023].tolist()[0]
tot_ac_22 = df_activa[2022].tolist()[0]
tot_ac_21 = df_activa[2021].tolist()[0]
delta_25 = (tot_ac_25 - tot_ac_24)/tot_ac_24*100
delta_24 = (tot_ac_24 - tot_ac_23)/tot_ac_23*100
delta_23 = (tot_ac_23 - tot_ac_22)/tot_ac_22*100
delta_22 = (tot_ac_22 - tot_ac_21)/tot_ac_21*100


# Ordenar departamentos por el año 2020 de mayor a menor
df_depto_anios = df_colombia_continental.groupby(['DEPARTAMENTO', 'AÑO SERVICIO'])['ENERGÍA ACTIVA'].sum().reset_index()
departamentos = df_depto_anios['DEPARTAMENTO'].unique().tolist()



###############################################################################
#                            VISUALIZACIÓN EN STREAMLIT                       #
###############################################################################
st.set_page_config(
    page_title='⚡Zonas No Interconectadas',
    layout='centered')
st.markdown(
    '''
    <style>
        .block-container {
        max-width: 1200px;
        }

    ''',
    unsafe_allow_html=True
)


# st.title('Dashboard Zonas No Interconectadas')
# st.header('Análisis de datos')
# st.subheader('Bootcamp Talento Tech')
st.markdown('<a id="inicio"></a><br><br>', unsafe_allow_html=True)
st.image('img/encabezado.png')
st.markdown('<a id="inicio"></a>', unsafe_allow_html=True)

###############################################################################
#                        TAMAÑO DEL CONJUNTO DE DATOS                         #
###############################################################################

st.markdown('<a id="acerca-de"></a><br><br>', unsafe_allow_html=True)
with st.container(border=True):
    st.html('<h2><font color=#3D6E85>Acerca del Conjunto de Datos</h2>')


    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric('Número de Variables', variables, border=True)

    with col2:
        st.metric('Número de Observaciones', filas, border=True)

    with col3:
        st.metric('Número de Departamentos', num_deptos, border=True)

    with col4:
        st.metric('Número de Municipios', num_mpios, border=True)

    if st.checkbox('Mostrar detalles el Dataset'):
        st.write('Conjuto de datos obtendios del Portal de Datos Abiertos del Gobierno Nacional de Colombia')
        st.write('Disponible en https://www.datos.gov.co/Minas-y-Energ-a/Estado-de-la-prestaci-n-del-servicio-de-energ-a-en/3ebi-d83g/about_data')

    with st.expander('Ver conjunto de datos completo'):
        st.dataframe(df)

    with st.expander('Ver Datos de Energía Activa por Departamento y Año'):
        st.dataframe(df_pivote)

###############################################################################
#      GRAFICO INTRACTIVO DE BARRAS HORIZONTALES POR DEPARTAMENTO Y AÑO       #
###############################################################################

st.markdown('<a id="evolucion"></a><br><br>', unsafe_allow_html=True)
with st.container(border=True):
    st.html('<font size=5><font color=#3D6E85>Evolución de Energía Activa por Departamento</font>')

    # Desplegable para seleccionar departamento
    depto_selec = st.selectbox(
        'Selecciona un departamento:',
        options=departamentos
    )
    condicion_filtro = df_depto_anios['DEPARTAMENTO'] == depto_selec
    df_departamento = df_depto_anios[condicion_filtro]

    # Crear gráfico de barras horizontales
    # 1 Crear el objeto Figure
    fig_barras = go.Figure()

    # 2 Agregar las barras a fig_barras que es el objeto Figure
    fig_barras.add_trace(go.Bar(
        x=df_departamento['ENERGÍA ACTIVA'],
        y=df_departamento['AÑO SERVICIO'].astype(str),
        orientation='h',
        marker_color='#4E7F96',
        text=df_departamento['ENERGÍA ACTIVA'],
        texttemplate='%{text:,.0f}',
        textposition='auto',
    ))

    # 3. Actualizar el objeto Figure con el diseño deseado
    fig_barras.update_layout(
        height=400,
        xaxis_title='Energía Activa (kWh)',
        yaxis_title='Año',
        showlegend=False,
        yaxis={'categoryorder': 'category ascending'}
    )

    # Mostrar
    st.plotly_chart(fig_barras, use_container_width=True)

###############################################################################
#           INDICADORES DE ENERGÍA ACTIVA POR AÑO EN MILLONES DE KWH          #
###############################################################################

st.markdown('<a id="indicadores"></a><br><br>', unsafe_allow_html=True)
with st.container(border=True):
    st.html('<h2><font color=#3D6E85>Indicadores de Energía Activa por año en Millones de kWh</h2>')
    col5, col6, col7, col8 = st.columns(4)
    col5.metric(
        label='2022',
        value= round(tot_ac_22/1000000,2),
        delta= f'{round(delta_22,2)}%',
        help='Este es un valor de ejemplo',
        border=True
    )

    col6.metric(
        label='2023',
        value= round(tot_ac_23/1000000,2),
        delta= f'{round(delta_23,2)}%',
        border=True
    )

    col7.metric(
        label='2024',
        value= round(tot_ac_24/1000000,2),
        delta= f'{round(delta_24,2)}%',
        border=True
    )

    col8.metric(
        label='2025',
        value= round(tot_ac_25/1000000,2),
        delta= f'{round(delta_25,2)}%',
        border=True
    )

    with st.container(border=True):
        df_activa = df_activa[[2022,2023,2024,2025]].T

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df_activa.index,
                y=df_activa[0],
                mode='lines+markers',
                line=dict(color="#4E7F96")
                )
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, config = {'scrollZoom': False})
        st.caption('*Fuente: Datos Abiertos del Gobierno Nacional de Colombia*')



###############################################################################
#   GRÁFICO BARRAS DE ENERGÍA ACTIVA Y REACTIVA POR AÑO EN MILLONES DE KWH    #
###############################################################################

st.markdown('<a id="barras"></a><br><br>', unsafe_allow_html=True)
with st.container(border=True):
    st.html('<font size=5><font color=#3D6E85>Gráficos de Energía Activa y Reactiva por Municipio</font>')
    col9, col10 = st.columns(2)

    with col9:
        # Del df_agrupado, ordenamos por energía activa y elegimos los 5 priomeros
        df_mayores = df_agrupado.sort_values(by= 'ENERGÍA ACTIVA', ascending=False).head(5)
        
        # 1. Crear objeto y agregar gráficos
        fig = px.bar(
            df_mayores,
            x='MUNICIPIO',
            y='ENERGÍA ACTIVA',
            color = 'DEPARTAMENTO',
            title='Top 5 Municipios con Mayor Energía Activa',
            labels = {'MUNICIPIO':'Municipios', 'ENERGÍA ACTIVA':'Energía Activa (kWh)', 'DEPARTAMENTO':'Departamento'},
            color_discrete_sequence=px.colors.sequential.Tealgrn,
            height=500
        )
        
        # 2. Actualización del diseño
        fig.update_traces(
            textposition='outside', 
            texttemplate='%{y:,.0f}'
            )

        # 3. Mostrar
        st.plotly_chart(fig, use_container_width=True)

    with col10:
        # Del df_agrupado, ordenamos por energía activa y elegimos los 5 priomeros
        df_mayores = df_agrupado.sort_values(by= 'ENERGÍA REACTIVA', ascending=False).head(5)
        
        # 1. Crear objeto y agregar gráficos
        fig = px.bar(
            df_mayores,
            x='MUNICIPIO',
            y='ENERGÍA REACTIVA',
            color = 'DEPARTAMENTO',
            title='Top 5 Municipios con Mayor Energía Reactiva',
            labels = {'MUNICIPIO':'Municipios', 'ENERGÍA REACTIVA':'Energía Reactiva (kWh)', 'DEPARTAMENTO':'Departamento'},
            color_discrete_sequence=px.colors.sequential.Purpor,
            height=500
        )
        
        # 2. Actualización del diseño
        fig.update_traces(
            textposition='outside', 
            texttemplate='%{y:,.0f}'
            )

        # 3. Mostrar
        st.plotly_chart(fig, use_container_width=True)
        
###############################################################################
#   GRÁFICO BARRAS DE TORTA ACTIVA Y REACTIVA POR AÑO EN MILLONES DE KWH    #
###############################################################################

st.markdown('<a id="tortas"></a><br><br>', unsafe_allow_html=True)
with st.container(border=True):
     st.html('<font size=5><font color=#3D6E85>Gráficos de Energía Activa y Reactiva por Departamento</font>')
     col11, col12 = st.columns(2)

    
     with col11:
        df_depto_activa = df_agrupado.groupby('DEPARTAMENTO')['ENERGÍA ACTIVA'].sum().reset_index()
        df_depto_activa = df_depto_activa.sort_values(by='ENERGÍA ACTIVA', ascending=False).head(5)

        
        # 1. Crear objeto y agregar gráficos

        fig_act = px.pie(
            df_depto_activa,
            names ='DEPARTAMENTO',
            values='ENERGÍA ACTIVA',
            title='Top 5 Departamentos con Mayor Energía Activa',
            hole=0.6,
            color_discrete_sequence=px.colors.sequential.Tealgrn,

        )

        # 2. Actualización del diseño
        
            
        
        # 3. Mostrar
        st.plotly_chart(fig_act, use_container_width=True)


with col12:
    df_depto_reactiva = df_agrupado.groupby('DEPARTAMENTO')['ENERGÍA REACTIVA'].sum().reset_index()
    df_depto_reactiva = df_depto_reactiva.sort_values(by='ENERGÍA REACTIVA', ascending=False).head(5)

    
    # 1. Crear objeto y agregar gráficos

    fig_react = px.pie(
        df_depto_reactiva,
        names ='DEPARTAMENTO',
        values='ENERGÍA REACTIVA',
        title='Top 5 Departamentos con Mayor Energía Reactiva',
        hole=0.6,
        color_discrete_sequence=px.colors.sequential.Tealgrn,

    )

    # 2. Actualización del diseño
    
        
    
    # 3. Mostrar
    st.plotly_chart(fig_react, use_container_width=True)


###############################################################################
#                            MENÚ DE BARRA LATERAL                            #
###############################################################################

with st.sidebar.container():
    st.markdown('''
                <style>
                [data-testid="stSidebar"] a {
                    display: block;
                    text-decoration: none;
                    padding: 10px 5px;
                    border-radius: 6px;
                }
                [data-testid="stSidebar"] a:hover {
                    background-color: #FFFFFF;
                }
                </style>
                ''',
                unsafe_allow_html=True)
    
    st.html('<font size = 5><font color=#F4F4F4>Menú de Navegación</font>')
    st.markdown('[Inicio](#inicio)')
    st.markdown('[Acerca de los Datos](#acerca-de)')
    st.markdown('[Evolución de Energía Activa](#evolucion)')
    st.markdown('[Indicadores de Energía Activa](#indicadores)')
    st.markdown('[Gráficos por Municipio](#barras)')
    st.markdown('[Gráficos por Departamento](#tortas)')

        