import streamlit as st
import pandas as pd
import requests as rq  # (opcional) pode remover se não usar
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt  # só se quiser manter o gráfico matplotlib
import seaborn as sns           # (opcional) pode remover se não usar
import streamlit_option_menu
from streamlit_option_menu import option_menu

st.set_page_config(page_title="FIAP - Tech Challenge 1", layout="wide")
st.title('FIAP - Tech Challenge 1')

# -----------------------
# Carrega dados
# -----------------------
export = pd.read_csv('dados/exportacao_vinho_ready.csv', sep=',')
imp    = pd.read_csv('dados/importacao_vinho_ready.csv', sep=',')

# últimos 15 anos
anos_validos         = sorted(export['ano'].unique())[-15:]
anos_validos_import  = sorted(imp['ano'].unique())[-15:]
export_15anos = export[export['ano'].isin(anos_validos)].copy()
imp_15anos    = imp[imp['ano'].isin(anos_validos_import)].copy()

# -----------------------
# Agregações principais
# -----------------------
imp_grouped = (
    imp_15anos.groupby(['ano'])[['quantidade_kg', 'quantidade_dolar']]
    .sum().reset_index()
)
exp_grouped = (
    export_15anos.groupby(['ano'])[['quantidade_kg', 'quantidade_dolar']]
    .sum().reset_index()
)

# saldo (exportação - importação)
saldo = pd.merge(
    exp_grouped, imp_grouped,
    on=['ano'], how='outer', suffixes=('_exp', '_imp')
).fillna(0)
saldo['saldo_kg']    = saldo['quantidade_kg_exp']    - saldo['quantidade_kg_imp']
saldo['saldo_dolar'] = saldo['quantidade_dolar_exp'] - saldo['quantidade_dolar_imp']

# por país (para linha Top 5)
export_paises = (
    export_15anos.groupby(['ano', 'pais'])['quantidade_dolar']
    .sum().reset_index()
)
top_paises = (
    export_paises.groupby('pais')['quantidade_dolar']
    .sum().sort_values(ascending=False).head(5).index
)
df_top_export = export_paises[export_paises['pais'].isin(top_paises)]

# agregado anual (valor x quantidade) para barras
df_agg = (
    export_15anos.groupby("ano")[["quantidade_dolar", "quantidade_kg"]]
    .sum().reset_index()
)

# === (Quantidade + Crescimento %) ===
df_ano_geral = (
    export_15anos
    .groupby('ano')['quantidade_kg']
    .sum()
    .reset_index()
    .rename(columns={'ano': 'Ano', 'quantidade_kg': 'Quantidade'})
)
df_ano_geral['Crescimento_%'] = df_ano_geral['Quantidade'].pct_change() * 100

# -----------------------
# Sidebar / Navegação
# -----------------------
with st.sidebar:
    selected = option_menu(
        menu_title="Menu",
        options=["Geral", "Exportações", "Importações",
                 "Exportações x Importações", "Mercados futuros"],
        icons=["house", "arrow-bar-up", "arrow-bar-down",
               "arrows-angle-expand", "graph-up"],
        menu_icon="menu-up",
        default_index=0,
    )

# -----------------------
# Páginas
# -----------------------
if selected == "Geral":
    st.title("Panorama da Vitivinicultura Brasileira")
    
    st.markdown("""
    A vitivinicultura brasileira teve início em **1970**, no estado do **Rio Grande do Sul**, e desde então vem se consolidando como uma tradição cultural na produção de vinhos, sucos, espumantes e outros derivados. Atualmente, cerca de **90%** das uvas utilizadas na produção nacional provêm do próprio estado gaúcho, que é o principal polo do setor no país.  
    
    O mercado internacional de vinhos representa uma das maiores oportunidades de crescimento para a vitivinicultura brasileira. Nos últimos anos, o Brasil tem buscado fortalecer sua presença no comércio exterior, tanto por meio da exportação de rótulos nacionais quanto da importação estratégica de vinhos estrangeiros.  
    
    Este relatório apresenta uma análise das importações e exportações de vinhos com origem no Rio Grande do Sul, buscando identificar padrões, tendências e oportunidades. O estudo considera tanto o volume quanto o valor movimentado ao longo dos anos, oferecendo um panorama do desempenho do setor no comércio internacional.
    """)

    st.header('Visão geral dos dados')    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Exportações (amostra)**")
        st.dataframe(export_15anos.head(50), use_container_width=True)
    with c2:
        st.markdown("**Importações (amostra)**")
        st.dataframe(imp_15anos.head(50), use_container_width=True)


elif selected == "Exportações":
    st.subheader("**Exportações**")
    st.dataframe(export_15anos, use_container_width=True)


    st.markdown("""
Com base nos dados apresentados em gráficos, observa-se uma evolução significativa das exportações brasileiras de vinhos entre 2009 e 2023.
    """)

    # --- Evolução da Quantidade + Crescimento (%) (Plotly, 2 eixos) ---
    fig_q = go.Figure()
    fig_q.add_trace(go.Scatter(
        x=df_ano_geral['Ano'], y=df_ano_geral['Quantidade'],
        mode='lines+markers', name='Quantidade (kg)'
    ))
    fig_q.add_trace(go.Scatter(
        x=df_ano_geral['Ano'], y=df_ano_geral['Crescimento_%'],
        mode='lines+markers', name='Crescimento (%)', yaxis='y2',
        line=dict(dash='dash')
    ))
    fig_q.update_layout(
        title='Evolução das Exportações (Quantidade) e Crescimento (%) ano a ano',
        xaxis=dict(title='Ano', tickmode='linear'),
        yaxis=dict(title='Quantidade (kg)'),
        yaxis2=dict(title='Crescimento (%)', overlaying='y', side='right'),
        template='plotly_white', height=480
    )
    st.plotly_chart(fig_q, use_container_width=True)

    st.markdown("""
Para entender melhor os acontecimentos relevantes, neste período. Podemos relacionar a exportação por quantidade e por valor.
    """)

    # --- Barras agrupadas: Valor x Quantidade ---
    fig_b = go.Figure(data=[
        go.Bar(name='Valor (US$)',     x=df_agg['ano'], y=df_agg['quantidade_dolar']),
        go.Bar(name='Quantidade (kg)', x=df_agg['ano'], y=df_agg['quantidade_kg'])
    ])
    fig_b.update_layout(
        barmode='group', xaxis_title='Ano', yaxis_title='Valores',
        title='Exportações por Ano: Valor x Quantidade',
        legend_title='Indicador',
        xaxis=dict(type='category'),
        template='plotly_white', height=500
    )
    st.plotly_chart(fig_b, use_container_width=True)

    
    st.markdown("""
Analisando o gráfico abaixo, podemos notar duas situações que nos chamam atenção neste período.  
Dois picos se destacam: o expressivo aumento de **quantidade** em **2009** e de **valor** em **2013**.  

O pico de 2009 está diretamente relacionado à adoção do **Prêmio de Escoamento de Produção (PEP)** pelo Governo Federal.  
Com isso, o valor em dólar não cresce na mesma proporção, sendo essa desproporção agravada pela crise mundial.  

Já o pico de valor no ano de 2013 também se deve à adoção do **PEP**, mas também ao programa de exportação **Wine of Brazil**. Na tela abaixo, há possíveis acontecimentos que podem estar relacionados ao período.
""")

    st.markdown("""
| Ano(s) | Comportamento | Possíveis Eventos / Influências |
|---|---|---|
| 2009 | Quantidade exportada (kg) teve pico; valor aumentou pouco | Expansão do volume em vinhos de mesa (baixo valor agregado), impulsionada por incentivos federais como o **PEP** (Prêmio ao Escoamento de Produção). Valor monetário baixo ainda sentido pela crise mundial de 2008[1][2] |
| 2013 | Valor em US$ atingiu pico significativo, quantidade moderada | Exportação de vinhos premium com maior receita unitária[3]. Programa de exportação *Wine of Brazil* [4] |
| 2014 | Possível continuidade do pico de valor (se mantido no gráfico) | Mundial de Futebol atraiu atenção global; exportações de vinhos brasileiros cresceram ~75%, com alta visibilidade e valorização da marca país [5] |
| Pós-2014 até 2016 | Queda geral nos valores e quantidades exportadas | Crise econômica brasileira reduziu competitividade exportadora; menor demanda externa e interna afetaram o setor [6][7] |
| 2021–2022 | Recuperação gradual nos dois indicadores | O contexto global de reabertura econômica pós-pandemia elevou a demanda por vinhos, especialmente premium e espumantes. Setores de horeca cresceram, afetando exportações [8] |
""")


    # --- Linha: Top 5 países por valor ao longo do tempo ---
    fig = px.line(
        df_top_export,
        x="ano", y="quantidade_dolar", color="pais", markers=True,
        labels={"ano": "Ano", "quantidade_dolar": "Quantidade (dólar)", "pais": "País"},
        title="Exportação de Vinho por País ao Longo do Tempo (Top 5)"
    )
    fig.update_layout(xaxis=dict(tickmode='linear'),
                      legend_title="País", hovermode="x unified",
                      template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
A análise dos dados revela que o **Paraguai** se consolidou como o principal destino dos vinhos nacionais em relação a valor monetário e quantidade, especialmente a partir de 2016, com um crescimento consistente e expressivo até 2022.  
Esse avanço pode ser atribuído a fatores como a **proximidade geográfica**, **acordos comerciais regionais no âmbito do Mercosul** e **menor barreira de entrada no mercado**[9].
""")



# Top 5 países por VALOR acumulado (usando seu export_paises e top_paises já criados)
    top_paises_valor_df = (
        export_paises[export_paises['pais'].isin(top_paises)]
        .groupby('pais', as_index=False)['quantidade_dolar']
        .sum()
        .sort_values('quantidade_dolar', ascending=False)
        .head(5)
    )

    fig_top_valor = px.bar(
        top_paises_valor_df,
        x='pais',
        y='quantidade_dolar',
        title='Top 5 Países que Mais Compraram Vinho Brasileiro (Total Acumulado)',
        text='quantidade_dolar',
        color='pais'
    )

    # formatação bonita: sem legenda repetida, rótulos fora e valores com separador
    fig_top_valor.update_traces(
        texttemplate='US$ %{text:,.0f}',  # 1.234.567
        textposition='outside',
        hovertemplate='%{x}<br>US$ %{y:,.0f}'
    )
    fig_top_valor.update_layout(
        showlegend=False,
        xaxis_tickangle=-45,
        yaxis_title='Valor (US$)',
        template='plotly_white',
        height=450
    )

    st.plotly_chart(fig_top_valor, use_container_width=True)
    st.markdown("""
    Analisando o gráfico acima, por outro lado, mercados estratégicos como **Estados Unidos**, **Reino Unido** e **China** mantêm-se com valores mais discretos, mas estáveis.

    A **Rússia**, embora tenha apresentado um pico atípico de importações em 2013, possivelmente em razão de uma operação denominada *Prêmio de Escoamento de Produção (PEP)*[10], não manteve a consistência nos anos seguintes, o que indica volatilidade e dependência de fatores externos, como questões geopolíticas e econômicas.
    """)


    st.markdown("""
    **Referências:** [1](https://revistacultivar.com/artigos/atuacao-do-brasil-no-mercado-vitivinicola-mundial-n-panorama-2009), [2](https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/661539/1/VitiviniculturabrasileiraPanorama2009JornalDiadeCampo.pdf), [3](https://www.reuters.com/article/markets/brazil-trade-surplus-falls-sharply-in-2013-idUSL2N0KC0PD/), [4](https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/992336/1/ComunicadoTecnico157.pdf), [5](https://www.decanter.com/wine-news/fifa-world-cup-drives-brazil-wine-export-boom-2309/), [6](https://agrixchange.apeda.in/MarketReport/Exporter%20Guide_Sao%20Paulo%20ATO_Brazil_1-7-2016.pdf), [7](https://en.wikipedia.org/wiki/2014_Brazilian_economic_crisis), [8](https://www.oiv.int/sites/default/files/documents/eng-state-of-the-world-vine-and-wine-sector-april-2022-v6_0.pdf), [9](https://apexbrasil.com.br/content/apexbrasil/br/pt/solucoes/inteligencia/estudos-e-publicacoes/perfil-de-comercio-e-investimentos/perfil-de-comercio-e-investimentos-paraguai-2024.html), [10](https://revistaadega.uol.com.br/artigo/exportacao-de-vinhos-finos-brasileiros-cresce-23-em-2012_5524.html)
    """)

    

    
elif selected == "Importações":
    st.subheader("**Importações**")
    st.dataframe(imp_15anos, use_container_width=True)

elif selected == "Exportações x Importações":
    st.subheader("**Exportações x Importações**")
    st.line_chart(saldo, x='ano', y='saldo_dolar')

elif selected == "Mercados futuros":
    st.subheader("**Mercados futuros**")
    st.info("Seção em construção. Adicione aqui suas análises de projeções/forecast.")
