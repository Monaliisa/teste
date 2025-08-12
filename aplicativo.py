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

df_ano = imp_15anos.groupby('ano', as_index=False).agg({
    'quantidade_kg': 'sum',
    'quantidade_dolar': 'sum'
})



# Agrupa por ano e país e soma o valor monetário
imp_paises_valor = (
    imp_15anos.groupby(['ano', 'pais'])['quantidade_dolar']
    .sum()
    .reset_index()
)

# Seleciona os top 5 países pelo valor total no período
top_paises_valor = (
    imp_paises_valor.groupby('pais')['quantidade_dolar']
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

# Filtra apenas os top 5
df_top_imp_valor = imp_paises_valor[
    imp_paises_valor['pais'].isin(top_paises_valor)
]


top_paises = imp_15anos.groupby('pais')['quantidade_kg'].sum().sort_values(ascending=False).head(5).reset_index()
evolucao = imp_15anos.groupby(['ano', 'pais'])['quantidade_kg'].sum().reset_index()
imp_15anos = imp_15anos.copy()
imp_15anos['preco_kg'] = imp_15anos['quantidade_dolar'] / imp_15anos['quantidade_kg']



# Aplica o mapeamento manual direto dos continentes
pais_para_continente = {
    "Afeganistão": "Asia",
    "Alemanha, República Democrática": "Europe",
    "Antilhas Holandesas": "North America",
    "Antígua e Barbuda": "North America",
    "Arábia Saudita": "Asia",
    "Austrália": "Oceania",
    "Barein": "Asia",
    "Belice": "North America",
    "Bolívia": "South America",
    "Brasil": "South America",
    "Bulgária": "Europe",
    "Bélgica": "Europe",
    "Camarões": "Africa",
    "Canadá": "North America",
    "Catar": "Asia",
    "Chipre": "Asia",
    "Cingapura": "Asia",
    "Colômbia": "South America",
    "Comores": "Africa",
    "Coreia, Republica Sul": "Asia",
    "Costa do Marfim": "Africa",
    "Croácia": "Europe",
    "Dinamarca": "Europe",
    "Emirados Arabes Unidos": "Asia",
    "Equador": "South America",
    "Eslovaca, Republica": "Europe",
    "Espanha": "Europe",
    "Estados Unidos": "North America",
    "Estônia": "Europe",
    "Filipinas": "Asia",
    "Finlândia": "Europe",
    "França": "Europe",
    "Gana": "Africa",
    "Granada": "North America",
    "Grécia": "Europe",
    "Guiana Francesa": "South America",
    "Guine Bissau": "Africa",
    "Hungria": "Europe",
    "Ilha de Man": "Europe",
    "Ilhas Virgens": "North America",
    "Indonésia": "Asia",
    "Irlanda": "Europe",
    "Irã": "Asia",
    "Itália": "Europe",
    "Japão": "Asia",
    "Jordânia": "Asia",
    "Letônia": "Europe",
    "Libéria": "Africa",
    "Líbano": "Asia",
    "Malavi": "Africa",
    "Malásia": "Asia",
    "Martinica": "North America",
    "Mauritânia": "Africa",
    "Moçambique": "Africa",
    "México": "North America",
    "Namíbia": "Africa",
    "Nicarágua": "North America",
    "Nigéria": "Africa",
    "Noruega": "Europe",
    "Nova Caledônia": "Oceania",
    "Nova Zelândia": "Oceania",
    "Omã": "Asia",
    "Panamá": "North America",
    "Paraguai": "South America",
    "Países Baixos": "Europe",
    "Polônia": "Europe",
    "Porto Rico": "North America",
    "Quênia": "Africa",
    "Reino Unido": "Europe",
    "Rússia": "Europe",
    "Serra Leoa": "Africa",
    "Singapura": "Asia",
    "Suazilândia": "Africa",
    "Suécia": "Europe",
    "Suíça": "Europe",    "São Cristóvão e Névis": "North America",
    "São Vicente e Granadinas": "North America",
    "Tailândia": "Asia",
    "Tanzânia": "Africa",
    "Tcheca, República": "Europe",
    "Toquelau": "Oceania",
    "Tunísia": "Africa",
    "Turquia": "Asia",
    "Uruguai": "South America",
    "Vietnã": "Asia",
    "África do Sul": "Africa",
    "Áustria": "Europe",
    "Angola": "Africa",
    "Anguilla": "North America",
    "Argentina": "South America",
    "Aruba": "North America",
    "Bahamas": "North America",
    "Bangladesh": "Asia",
    "Barbados": "North America",
    "Benin": "Africa",
    "Bermudas": "North America",
    "Bósnia-Herzegovina": "Europe",
    "Cabo Verde": "Africa",
    "Cayman, Ilhas": "North America",
    "Chile": "South America",
    "China": "Asia",
    "Cocos (Keeling), Ilhas": "Asia",
    "Congo": "Africa",
    "Costa Rica": "North America",
    "Cuba": "North America",
    "Curaçao": "North America",
    "Dominica": "North America",
    "El Salvador": "North America",
    "Gibraltar": "Europe",
    "Guatemala": "North America",
    "Guiana": "South America",
    "Guine Equatorial": "Africa",
    "Haiti": "North America",
    "Honduras": "North America",
    "Hong Kong": "Asia",
    "India": "Asia",
    "Iraque": "Asia",
    "Jamaica": "North America",
    "Luxemburgo": "Europe",
    "Macau": "Asia",
    "Malta": "Europe",
    "Marshall, Ilhas": "Oceania",
    "Montenegro": "Europe",
    "Palau": "Oceania",
    "Peru": "South America",
    "Pitcairn": "Oceania",
    "Portugal": "Europe",
    "República Dominicana": "North America",
    "Senegal": "Africa",
    "Suriname": "South America",
    "São Tomé e Príncipe": "Africa",
    "Taiwan (Formosa)": "Asia",
    "Togo": "Africa",
    "Trinidade Tobago": "North America",
    "Tuvalu": "Oceania",
    "Vanuatu": "Oceania",
    "Venezuela": "South America"
}

# Mapeia cada país para seu respectivo continente com base no dicionário 'pais_para_continente'.Caso o país não esteja no dicionário, atribui 'Desconhecido' como valor padrão.
export_15anos = export_15anos.copy()
export_15anos["continente"] = export_15anos["pais"].map(pais_para_continente).fillna("Desconhecido")

# Agrupar os dados por continente
df_agg_cont_15years = export_15anos.groupby("continente")[["quantidade_dolar", "quantidade_kg"]].sum().reset_index()

#Ordenar por valor monetário

df_agg_cont_15years = df_agg_cont_15years.sort_values(by="quantidade_dolar", ascending=False)




# 1. Agrupar e somar os valores monetários anuais para exportação
df_export_anual = export_15anos.groupby('ano')['quantidade_dolar'].sum().reset_index()
df_export_anual = df_export_anual.rename(columns={'quantidade_dolar': 'Total_Exportacao'})

# 2. Agrupar e somar os valores monetários anuais para importação
df_import_anual = imp_15anos.groupby('ano')['quantidade_dolar'].sum().reset_index()
df_import_anual = df_import_anual.rename(columns={'quantidade_dolar': 'Total_Importacao'})

# 3. Unir os dois dataframes em um único, baseado no campo 'Ano'
df_consolidado = pd.merge(df_export_anual, df_import_anual, on='ano')







# -----------------------
# Sidebar / Navegação
# -----------------------
with st.sidebar:
    selected = option_menu(
        menu_title="Menu",
        options=["Geral", "Exportações", "Importações",
                 "Mercados futuros", "Sobre"],
        icons=["house", "arrow-bar-up", "arrow-bar-down",
               "arrows-angle-expand", "graph-up"],
        menu_icon="menu-up",
        default_index=0,
    )





# -----------------------
# Páginas
# -----------------------



# Página Geral


if selected == "Geral":
    st.title(" 🍇 Panorama da Vitivinicultura Brasileira")
    
    st.markdown("""
    A vitivinicultura brasileira teve início em **1970**, no estado do **Rio Grande do Sul**, e desde então vem se consolidando como uma tradição cultural na produção de vinhos, sucos, espumantes e outros derivados. Atualmente, cerca de **90%** das uvas utilizadas na produção nacional provêm do próprio estado gaúcho, que é o principal polo do setor no país.  
    
    O mercado internacional de vinhos representa uma das maiores oportunidades de crescimento para a vitivinicultura brasileira. Nos últimos anos, o Brasil tem buscado fortalecer sua presença no comércio exterior, tanto por meio da exportação de rótulos nacionais quanto da importação estratégica de vinhos estrangeiros.  
    
    Este relatório apresenta uma análise das importações e exportações de vinhos com origem no Rio Grande do Sul, buscando identificar padrões, tendências e oportunidades. O estudo considera tanto o volume quanto o valor movimentado ao longo dos anos, oferecendo um panorama do desempenho do setor no comércio internacional.
    """)

    st.header(' 📋 Visão geral dos dados')    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Exportações (amostra)**")
        st.dataframe(export_15anos.head(50), use_container_width=True)
    with c2:
        st.markdown("**Importações (amostra)**")
        st.dataframe(imp_15anos.head(50), use_container_width=True)

    


# Página Exportações
elif selected == "Exportações":
    st.subheader(" 📤 Exportações")  

    st.markdown("""
    As exportações representam um componente estratégico para o fortalecimento do setor vitivinícola brasileiro.  
    A análise histórica dos últimos anos permite identificar tendências, picos de crescimento e mercados prioritários.  

    Com base nos dados apresentados em gráficos da evolução da quantidade e crescimento percentual, observa-se uma evolução significativa das exportações brasileiras de vinhos entre **2009** e **2023**.
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
    Essa tendência de crescimento contínuo tem sido impulsionada por **estratégias de marketing**, **melhoria na qualidade dos produtos**, **diversificação de mercados** e **aumento da competitividade** frente a outros produtores internacionais.  

    Para entender melhor os acontecimentos relevantes neste período, podemos relacionar a exportação por **quantidade** e por **valor**.
    """)


    # --- Barras agrupadas: Valor x Quantidade ---
    fig_export_most_amount = go.Figure(data=[
        go.Bar(name='Valor (US$)',     x=df_agg['ano'], y=df_agg['quantidade_dolar']),
        go.Bar(name='Quantidade (kg)', x=df_agg['ano'], y=df_agg['quantidade_kg'])
    ])
    fig_export_most_amount.update_layout(
        barmode='group', xaxis_title='Ano', yaxis_title='Valores',
        title='Exportações por Ano: Valor x Quantidade',
        legend_title='Indicador',
        xaxis=dict(type='category'),
        template='plotly_white', height=500
    )
    st.plotly_chart(fig_export_most_amount, use_container_width=True)

    
    st.markdown("""
    Ao analisar esse histórico, dois picos chamam a atenção: o expressivo aumento de **quantidade** em **2009** e o salto no **valor exportado** em **2013**.  

    O crescimento de **2009** está diretamente relacionado à adoção do *Prêmio de Escoamento de Produção (PEP)* pelo Governo Federal, o que elevou o volume exportado, mas sem proporcionar aumento em valor, agravado pela **crise econômica global**.  

    Já o pico de **2013** também foi influenciado pelo *PEP*, mas contou ainda com o impacto positivo do programa de promoção internacional **Wine of Brazil**.  

    Na tabela abaixo, há possíveis acontecimentos que podem estar relacionados aos períodos.
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

    st.markdown("""
Os principais destinos do **vinho brasileiro** no mercado internacional revelam uma forte concentração nas exportações para o **Paraguai**, seguido por **Rússia**, **Estados Unidos**, **China** e **Reino Unido**.
""")
    
    # Top 5 países por VALOR acumulado (usando seu export_paises e top_paises já criados)
    export = pd.read_csv('dados/exportacao_vinho_ready.csv', sep=',')
    export_15anos = export[export['ano'].isin(anos_validos)].copy()

    export_paises = (
    export_15anos.groupby(['ano', 'pais'])['quantidade_dolar']
    .sum().reset_index()
    )
    top_paises = (
        export_paises.groupby('pais')['quantidade_dolar']
        .sum().sort_values(ascending=False).head(5).index
    )
    df_top_export = export_paises[export_paises['pais'].isin(top_paises)]

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
Ao analisar a evolução desses países ao longo do tempo, nota-se que o **Paraguai** se consolidou como o principal destino dos vinhos nacionais em relação a **valor monetário** e **quantidade**, especialmente a partir de **2016**, com um crescimento consistente e expressivo até **2022**.  

Esse avanço pode ser atribuído a fatores como a **proximidade geográfica**, **acordos comerciais regionais** no âmbito do **Mercosul** e **menor barreira de entrada no mercado**. Trata-se de um exemplo claro de como o fortalecimento de parcerias regionais pode alavancar o setor vitivinícola nacional.
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
Por outro lado, mercados estratégicos como **Estados Unidos**, **Reino Unido** e **China** mantêm-se com valores mais discretos, mas estáveis, sugerindo que há espaço para expansão, desde que estratégias adequadas sejam adotadas.  
Esses países, reconhecidos por seu **alto consumo per capita** e **exigência de qualidade**, representam uma oportunidade para o reposicionamento do vinho brasileiro como um produto de **valor agregado**, voltado ao público premium.  
Para isso, será essencial investir em **diferenciação** por meio de **certificações de qualidade**, **presença em feiras internacionais**, **parcerias comerciais sólidas** e ações de marketing voltadas à **valorização da identidade e da origem** do vinho nacional.

A **Rússia**, embora tenha apresentado um pico atípico de importações em **2013**, possivelmente em razão do **Prêmio de Escoamento de Produção (PEP)**, não manteve a consistência nos anos seguintes. Isso indica **volatilidade** e **dependência de fatores externos**, como questões **geopolíticas** e **econômicas**, reforçando a importância de uma estratégia de **diversificação de mercados**, priorizando aqueles com maior **estabilidade** e **previsibilidade comercial**.

De forma geral, os dados apontam que, embora o Brasil ainda não seja protagonista no cenário global de exportação de vinhos, há **avanços concretos** e **oportunidades evidentes**.  
A expansão passa pela **segmentação de produtos** para diferentes perfis de mercado, **valorização do território brasileiro** e **maior articulação entre produtores, governo e entidades de promoção comercial**.  
Com **planejamento**, **investimentos** e **posicionamento estratégico**, é possível ampliar a **presença internacional** dos vinhos brasileiros e consolidar sua **reputação** como produto **competitivo, autêntico e de qualidade**.
""")



    st.markdown("""
    **Referências:** [1](https://revistacultivar.com/artigos/atuacao-do-brasil-no-mercado-vitivinicola-mundial-n-panorama-2009), [2](https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/661539/1/VitiviniculturabrasileiraPanorama2009JornalDiadeCampo.pdf), [3](https://www.reuters.com/article/markets/brazil-trade-surplus-falls-sharply-in-2013-idUSL2N0KC0PD/), [4](https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/992336/1/ComunicadoTecnico157.pdf), [5](https://www.decanter.com/wine-news/fifa-world-cup-drives-brazil-wine-export-boom-2309/), [6](https://agrixchange.apeda.in/MarketReport/Exporter%20Guide_Sao%20Paulo%20ATO_Brazil_1-7-2016.pdf), [7](https://en.wikipedia.org/wiki/2014_Brazilian_economic_crisis), [8](https://www.oiv.int/sites/default/files/documents/eng-state-of-the-world-vine-and-wine-sector-april-2022-v6_0.pdf), [9](https://apexbrasil.com.br/content/apexbrasil/br/pt/solucoes/inteligencia/estudos-e-publicacoes/perfil-de-comercio-e-investimentos/perfil-de-comercio-e-investimentos-paraguai-2024.html), [10](https://revistaadega.uol.com.br/artigo/exportacao-de-vinhos-finos-brasileiros-cresce-23-em-2012_5524.html)
    """)

    st.dataframe(export_15anos, use_container_width=True)





#Página Importações
    
elif selected == "Importações":
    st.subheader(" 📥 Importações")


    st.markdown("""Ao observar a evolução da quantidade de vinho importado pelo Brasil nos últimos 15 anos, nota-se uma trajetória de crescimento consistente, com variações pontuais. O gráfico evidencia dois períodos de destaque: o salto significativo entre 2016 e 2017 e o novo avanço expressivo entre 2019 e 2020.
    """)

        # ---- Escolha da métrica
    metrica = st.radio(
        "Métrica do gráfico:",
        options=["Quantidade (kg)", "Valor (US$)"],
        horizontal=True,
    )
    y_col = "quantidade_kg" if metrica == "Quantidade (kg)" else "quantidade_dolar"
    y_label = "Quantidade Total (kg)" if y_col == "quantidade_kg" else "Valor Total (US$)"

    # ---- Dataframe para plot
    df_plot = imp_grouped[['ano', y_col]].copy()
    df_plot = df_plot[(df_plot[y_col].notna()) & (df_plot[y_col] > 0)]
    df_plot = df_plot.sort_values('ano')

    # ---- Slider de anos
    min_ano, max_ano = int(df_plot['ano'].min()), int(df_plot['ano'].max())
    anos = st.slider("Intervalo de anos", min_ano, max_ano, (min_ano, max_ano))
    df_plot = df_plot.query('@anos[0] <= ano <= @anos[1]')

    # ---- Gráfico
    fig = px.line(
        df_plot,
        x='ano',
        y=y_col,
        markers=True,
        title=f"Evolução da {metrica} de Vinho Importado no Brasil",
        color_discrete_sequence=['royalblue']
    )

    fig.update_traces(
        line=dict(width=3),
        hovertemplate=(
            "Ano: %{x}<br>" +
            (f"{y_label.split(' (')[0]}: " + ("%{y:,.0f} kg" if y_col == "quantidade_kg" else "US$ %{y:,.0f}")) +
            "<extra></extra>"
        )
    )

    fig.update_layout(
        title_font=dict(size=20, family='Arial', color='black'),
        xaxis_title='Ano',
        yaxis_title=y_label,
        xaxis=dict(showgrid=True, gridcolor='lightgray', griddash='dot', tickmode='linear'),
        yaxis=dict(showgrid=True, gridcolor='lightgray', griddash='dot',
                tickformat=',.0f' if y_col == 'quantidade_kg' else '$,.0f'),
        plot_bgcolor='white',
        hovermode='x unified',
        height=520,
        margin=dict(l=40, r=20, t=60, b=40)
    )

    # Range slider/botões no próprio gráfico (além do slider Streamlit)
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=list([
                    dict(count=5, label='5a', step='year', stepmode='backward'),
                    dict(count=10, label='10a', step='year', stepmode='backward'),
                    dict(step='all', label='Tudo')
                ])
            )
        )
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
            O crescimento registrado entre 2016 e 2017 esteve associado a fatores como a redução da comercialização de vinhos finos nacionais e a queda acentuada na produção de uvas em 2016, que elevou os preços dos produtos nacionais. Essa conjuntura favoreceu os importados, especialmente aqueles que ofereciam preços competitivos e qualidade equivalente ou superior[11]. Soma-se a isso o aumento no número de consumidores de vinho no país [11]
                
            Já em 2020, o aumento das importações esteve fortemente ligado ao contexto da pandemia de COVID-19, que impulsionou o consumo doméstico e acelerou a expansão dos canais de venda online, como e-commerces e clubes de assinatura. A impossibilidade de frequentar bares e restaurantes fez com que o vinho se consolidasse como uma opção de consumo em casa, ampliando a demanda.[12]. Vale destacar que os de importados tiveram um acréscimo de 22% nas vendas[13].

            Ao restringir a análise aos cinco principais países fornecedores, nota-se uma trajetória estável, sem grandes oscilações, o que indica relações comerciais consistentes ao longo do período.
            
    """)



    # (Opcional) Filtro de anos no Streamlit
    min_ano, max_ano = int(df_top_imp_valor['ano'].min()), int(df_top_imp_valor['ano'].max())
    anos = st.slider("Selecione o intervalo de anos", min_ano, max_ano, (min_ano, max_ano))
    df_top_imp_valor = df_top_imp_valor.query('@anos[0] <= ano <= @anos[1]')

    # --- Gráfico (Plotly)
    fig = px.line(
        df_top_imp_valor,
        x='ano', y='quantidade_dolar', color='pais',
        markers=True,
        title='Importação de vinho: evolução por país (Top 5)',
        labels={'quantidade_dolar': 'Valor Monetário', 'ano': 'Ano'}
    )

    # Personalizações (sem grid e fundo branco)
    fig.update_traces(hovertemplate='ano: %{x}<br>quantidade_dolar: %{y:,.0f} kg<extra></extra>')
    fig.update_xaxes(showgrid=False, dtick=1)
    fig.update_yaxes(showgrid=False, tickformat=',.0f')
    fig.update_layout(
        legend_title_text='País',
        plot_bgcolor='white',   # fundo do gráfico
        paper_bgcolor='white',  # fundo externo
        title_font=dict(size=20, family='Arial', color='black'),
        hovermode='x unified',
        height=520,
        margin=dict(l=40, r=20, t=60, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""Nesse recorte, o Chile apresenta predominância absoluta, seguido por Argentina, Portugal, Itália e Espanha. Essa configuração reflete, sobretudo, a competitividade de preços, a proximidade geográfica e os acordos comerciais que facilitam a entrada de vinhos desses países no Brasil.
    """)
    
        # --- Gráfico de barras
    fig_bar = px.bar(
        top_paises,
        x='pais',
        y='quantidade_kg',
        title='Top 5 Países Exportadores de Vinho para o Brasil (em Quantidade)',
        text='quantidade_kg',
        color='pais'
    )

    fig_bar.update_traces(
        texttemplate='%{text:,.0f}',  # formata com separador de milhar
        textposition='outside'
    )

    fig_bar.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        yaxis_title="Quantidade (kg)",
        xaxis_title="País",
        template="plotly_white",
        height=500
    )

    # --- Exibir no Streamlit
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("""No Chile é atualmente o quarto maior exportador mundial de vinho, posição que evidencia sua relevância no mercado global [14]. No contexto brasileiro, mantém há anos a liderança no abastecimento, sustentada por uma relação comercial estável e de longa data. Um marco nesse vínculo foi o ACE-35 (Acordo de Complementação Econômica nº 35) [15], que aboliu todas as tarifas de importação entre Brasil e Chile a partir de 2014, tendo o vinho como um dos protagonistas desse cenário [16].                
    O abastecimento do mercado interno permanece dependente de países como Chile e Argentina, beneficiados por acordos comerciais e competitividade de preços. Esse quadro reforça o desafio de aumentar a participação dos vinhos nacionais por meio de estratégias de qualidade e valorização da produção local.
    """)

    st.markdown("""
    **Referências:**

    [11](https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1100897/1/ComunicadoTecnico207.pdf)
    [12](https://veja.abril.com.br/gastronomia/como-brasil-se-tornou-um-dos-poucos-mercados-prosperos-para-vinho-em-2020/)
    [13](https://www.winesa.com.br/setor-comemora-recorde-no-consumo-de-vinho-no-brasil-em-2020/)
    [14](https://www.ilo.org/sites/default/files/2024-11/Research%20Brief%20Wine%20Reinecke%20Torres%20October%202024.pdf)
    [15](https://www.gov.br/mdic/pt-br/assuntos/noticias/mdic/brasil-e-chile-assinam-acordo-de-livre-comercio)
    [16](https://www.folhadelondrina.com.br/economia/importacoes-do-chile-tem-salto-no-brasil-no-ultimo-ano-3065494e.html?d=1)
    """)
    st.dataframe(imp_15anos)


#Página Mercados Futuros

elif selected == "Mercados futuros":
    st.subheader(" 📈 Mercados futuros")
    

    st.markdown("""A análise do fluxo comercial de vinhos revela uma balança deficitária para o Brasil. Enquanto as importações apresentam trajetória ascendente e consistente, as exportações permanecem em patamares significativamente inferiores, com oscilações discretas e crescimento modesto.""")

    fig = go.Figure()

    # Exportação
    fig.add_trace(go.Scatter(
        x=df_consolidado['ano'],
        y=df_consolidado['Total_Exportacao'],
        mode='lines+markers',
        name='Total Exportação (US$)',
        line=dict(color='green', width=3),
        marker=dict(size=7),
        hovertemplate='Ano: %{x}<br>Exportação: US$ %{y:,.0f}<extra></extra>'
    ))

    # Importação
    fig.add_trace(go.Scatter(
        x=df_consolidado['ano'],
        y=df_consolidado['Total_Importacao'],
        mode='lines+markers',
        name='Total Importação (US$)',
        line=dict(color='red', width=3),
        marker=dict(size=7),
        hovertemplate='Ano: %{x}<br>Importação: US$ %{y:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title='Comparação Anual de Exportação e Importação de Vinho (Últimos 15 anos)',
        xaxis_title='Ano',
        yaxis_title='Valor Monetário (em Milhões de US$)',
        template='plotly_white',
        hovermode='x unified',
        xaxis=dict(tickmode='linear'),
        yaxis=dict(tickformat='$,.2s'),  # mostra em K/M/B
        legend_title_text='Fluxo Comercial',
        height=520,
        margin=dict(l=40, r=20, t=60, b=40)
    )

# Exibir no Streamlit
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(""" Esse descompasso reforça a necessidade de estratégias voltadas à valorização e ampliação da presença dos rótulos nacionais no exterior.
    O recente tarifaço imposto pelos Estados Unidos — terceiro maior importador de vinhos brasileiros — tende a agravar esse cenário. Na mais recente rodada de aumento de tarifas sobre produtos brasileiros, o vinho não foi incluído entre os itens isentos, o que reduz sua competitividade no mercado norte-americano e reforça a urgência em diversificar destinos de exportação para mitigar riscos comerciais.
    Diante desse contexto, é essencial compreender para onde os vinhos brasileiros estão sendo enviados atualmente. A distribuição das exportações por continente revela que a América do Sul concentra a maior fatia em valor monetário.
    """)

    pais_para_continente_lower = {
        "afeganistao": "Asia",
    "alemanha_republica_democratica": "Europe",
    "antilhas_holandesas": "North America",
    "antigua_e_barbuda": "North America",
    "arabia_saudita": "Asia",
    "australia": "Oceania",
    "barein": "Asia",
    "belice": "North America",
    "bolivia": "South America",
    "brasil": "South America",
    "bulgaria": "Europe",
    "belgica": "Europe",
    "camaroes": "Africa",
    "canada": "North America",
    "catar": "Asia",
    "chipre": "Asia",
    "cingapura": "Asia",
    "colombia": "South America",
    "comores": "Africa",
    "coreia_republica_sul": "Asia",
    "costa_do_marfim": "Africa",
    "croacia": "Europe",
    "dinamarca": "Europe",
    "emirados_arabes_unidos": "Asia",
    "equador": "South America",
    "eslovaca_republica": "Europe",
    "espanha": "Europe",
    "estados_unidos": "North America",
    "estonia": "Europe",
    "filipinas": "Asia",
    "finlandia": "Europe",
    "franca": "Europe",
    "gana": "Africa",
    "granada": "North America",
    "grecia": "Europe",
    "guiana_francesa": "South America",
    "guine_bissau": "Africa",
    "hungria": "Europe",
    "ilha_de_man": "Europe",
    "ilhas_virgens": "North America",
    "indonesia": "Asia",
    "irlanda": "Europe",
    "ira": "Asia",
    "italia": "Europe",
    "japao": "Asia",
    "jordania": "Asia",
    "letonia": "Europe",
    "liberia": "Africa",
    "libano": "Asia",
    "malavi": "Africa",
    "malasia": "Asia",
    "martinica": "North America",
    "mauritania": "Africa",
    "mocambique": "Africa",
    "mexico": "North America",
    "namibia": "Africa",
    "nicaragua": "North America",
    "nigeria": "Africa",
    "noruega": "Europe",
    "nova_caledonia": "Oceania",
    "nova_zelandia": "Oceania",
    "oma": "Asia",
    "panama": "North America",
    "paraguai": "South America",
    "paises_baixos": "Europe",
    "polonia": "Europe",
    "porto_rico": "North America",
    "quenia": "Africa",
    "reino_unido": "Europe",
    "russia": "Europe",
    "serra_leoa": "Africa",
    "singapura": "Asia",
    "suazilandia": "Africa",
    "suecia": "Europe",
    "suica": "Europe",
    "sao_cristovao_e_nevis": "North America",
    "sao_vicente_e_granadinas": "North America",
    "tailandia": "Asia",
    "tanzania": "Africa",
    "tcheca_republica": "Europe",
    "toquelau": "Oceania",
    "tunisia": "Africa",
    "turquia": "Asia",
    "uruguai": "South America",
    "vietna": "Asia",
    "africa_do_sul": "Africa",
    "austria": "Europe",
    "angola": "Africa",
    "anguilla": "North America",
    "argentina": "South America",
    "aruba": "North America",
    "bahamas": "North America",
    "bangladesh": "Asia",
    "barbados": "North America",
    "benin": "Africa",
    "bermudas": "North America",
    "bosnia_herzegovina": "Europe",
    "cabo_verde": "Africa",
    "cayman_ilhas": "North America",
    "chile": "South America",
    "china": "Asia",
    "cocos_keeling_ilhas": "Asia",
    "congo": "Africa",
    "costa_rica": "North America",
    "cuba": "North America",
    "curacao": "North America",
    "dominica": "North America",
    "el_salvador": "North America",
    "gibraltar": "Europe",
    "guatemala": "North America",
    "guiana": "South America",
    "guine_equatorial": "Africa",
    "haiti": "North America",
    "honduras": "North America",
    "hong_kong": "Asia",
    "india": "Asia",
    "iraque": "Asia",
    "jamaica": "North America",
    "luxemburgo": "Europe",
    "macau": "Asia",
    "malta": "Europe",
    "marshall_ilhas": "Oceania",
    "montenegro": "Europe",
    "palau": "Oceania",
    "peru": "South America",
    "pitcairn": "Oceania",
    "portugal": "Europe",
    "republica_dominicana": "North America",
    "senegal": "Africa",
    "suriname": "South America",
    "sao_tome_e_principe": "Africa",
    "taiwan_formosa": "Asia",
    "togo": "Africa",
    "trinidade_tobago": "North America",
    "tuvalu": "Oceania",
    "vanuatu": "Oceania",
    "venezuela": "South America",
    }
    
    df_exportacao = pd.read_csv('dados/exportacao_vinho_ready.csv', sep=',')

    export_15anos = df_exportacao[df_exportacao['ano'].isin(anos_validos)]

    export_15anos["continente"] = export_15anos["pais"].map(pais_para_continente_lower).fillna("Desconhecido")

    df_agg_cont_15years = export_15anos.groupby("continente")[["quantidade_dolar", "quantidade_kg"]].sum().reset_index()

    df_agg_cont_15years = df_agg_cont_15years.sort_values(by="quantidade_dolar", ascending=False)

    fig = px.bar(
        df_agg_cont_15years,
        x="continente",
        y="quantidade_dolar",
        title="Exportações por Continente (15 anos)",
        labels={"continente": "Continente", "quantidade_dolar": "Valor Monetário Exportado"},
        color="continente",  
        text="quantidade_dolar"  
    )

    # Personalização extra
    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')  # formata números sem casas decimais
    fig.update_layout(
        xaxis_tickangle=-45,
        template='plotly_white',
        showlegend=False
    )

    # figZ = px.bar(
    #     df_agg_cont_15years,
    #     x="continente",
    #     y="quantidade_dolar",
    #     title="Exportações por Continente (15 anos)",
    #     labels={"continente": "Continente", "quantidade_dolar": "Valor Monetário Exportado"},
    #     color="continente",
    #     text="quantidade_dolar"
    # )

    # # Personalização extra
    # figZ.update_traces(
    #     texttemplate='%{text:,.0f}',  # formata números sem casas decimais
    #     textposition='outside'
    # )
    # figZ.update_layout(
    #     xaxis_tickangle=-45,
    #     template='plotly_white',
    #     showlegend=False
    # )

    # Exibir no Streamlit
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    Dentro dessa região, a Colômbia surge como um mercado promissor a ser explorado. O consumo per capita entre os colombianos é de 1,2 litro por ano, mas a expectativa é que dobre ou triplique nos próximos anos. Tornando-se um mercado atraente para o negócio do vinho[17].

    Vale destacar ainda que, diferentemente de países vizinhos como Chile e Argentina, grandes produtores e fortes concorrentes no mercado internacional, a Colômbia não possui tradição significativa na produção de vinhos, o que a torna fortemente dependente de importações.

    Embora a Europa seja tradicionalmente vista como um mercado de prestígio, não se apresenta como prioridade estratégica no curto prazo. Isso porque, o aumento das tarifas norte-americanas sobre vinhos europeus pode levar produtores da União Europeia a redirecionar rótulos para o Brasil, intensificando a concorrência com o produto nacional[18].

    Já no continente asiático, apesar de a China (7º maior importador em valor monetário) e o Japão (5º) registraram queda no consumo de vinho, acompanhando a retração global, eles seguiram entre os maiores importadores mundiais. O Japão se destaca pelo segundo maior preço médio pago por litro entre os principais importadores (€6,35), enquanto a China mantém um valor expressivo (€5,21)[19], o que indica potencial para exportações de vinhos brasileiros, especialmente aqueles de maior valor agregado.
    """)


    st.markdown("""
    **Referências:**

    [17](https://cambiocolombia.com/gastronomia/vinos-mercado-cultura-crecimiento-colombia)
    [18](https://www.correiobraziliense.com.br/economia/2025/05/7160612-o-problema-do-mercado-de-vinhos-brasileiros-comeca-com-a-tributacao-diz-empresario.html)
    [19](https://vino-joy.com/2025/04/17/oiv-global-wine-consumption-hits-historic-low-how-is-asia-faring/)
    """)

elif selected == "Sobre":
    st.subheader(" 📊 Sobre")
    st.markdown("""
    Este projeto foi desenvolvido por estudantes da **Turma 10 DTAT** da **FIAP – Pós Tech em Data Analytics** como trabalho de conclusão da **Fase 1 – Data Analysis and Exploration**.  

    O estudo teve como objetivo explorar, tratar e analisar bases públicas do setor vitivinícola do Estado do Rio Grande do Sul, gerando visualizações e insights estratégicos para compreender o comércio de vinhos no cenário nacional e internacional.  

    **Equipe:**  
    - Daniele Oliveira
    - Hélio Ricardo
    - Marcelo Cruz
    - Monalisa Meyrelle     
    
    Links úteis:
                
    * [Notebook do projeto](https://colab.research.google.com/drive/1LH_YP_es4C5SK1nv1l2sPcLCG01ImHsg?usp=sharing)
    * [Vitivinicultura](http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_01)
    
    **Agosto de 2025**
    """)
  