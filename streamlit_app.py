import json
import requests  # pip install requests
import streamlit as st  # pip install streamlit
from streamlit_lottie import st_lottie  # pip install streamlit-lottie
import pandas as pd
import time
import os
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import pearsonr


# GitHub: https://github.com/andfanilo/streamlit-lottie
# Lottie Files: https://lottiefiles.com/

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

#st.title(':bar_chart: 2024년 미추홀구 예산')
#st.markdown('<style>div.block-containner{padding-top:1rem;}</style>', unsafe_allow_html=True)

# 화면 중앙에 위치하도록 스타일 설정
st.markdown(
    """
    <style>
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 0.5vh;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 제목을 div 태그로 감싸서 스타일 적용
st.markdown('<div class="centered"><h1 style="text-align:center;">📊 2024년 인천광역시 예산</h1></div>', unsafe_allow_html=True)
st.title("   ")

lottie_loading = load_lottiefile("lottiefiles/loading.json")  # replace link to local lottie file
loading_state = st.empty()
#lottie_hello = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_M9p23l.json")
#lottie_loading = load_lottieurl("https://lottie.host/efece630-073b-49e3-8240-1a8a9c118346/KbRGnvFFOG.json")
# st_lottie(
#     lottie_loading,
#     speed=1,
#     reverse=False,
#     loop=True,
#     quality="low", # medium ; high
#     renderer="canvas", # svg, canvas
#     height=None,
#     width=None,
#     key=None,
# )
@st.cache
def load_data():
    data =pd.read_excel('budget/budget_incheon_2024.xlsx')
    return data

with loading_state.container():
    with st.spinner('데이터 읽어오는 중...'):
        st_lottie(lottie_loading, width=300)
        data = load_data()
    st.success('로딩 완료!')
    
loading_state.empty()

df = data.copy()
df = df.drop(0)
df.reset_index(inplace=True, drop=True)

selected_columns = ['회계연도', '부서명', '세부사업명', '예산액', '산출근거명','산출근거식','단위사업명', '편성목명']
df = df[selected_columns]
budget = df.copy()

budget['예산액'] = (budget['예산액']  / 100000).apply(np.floor)
budget = budget.sort_values(by='예산액',ascending=False)

department = df['부서명'].unique()
#st.sidebar.subheader('부서명 선택')
selected_department = st.sidebar.selectbox('부서명',department) 

with st.expander("인천광역시 예산", expanded=False):
    st.dataframe(df,use_container_width=True)

col1, col2 = st.columns(2)
with col1:  
    fig = px.pie(budget, values='예산액', names='부서명',
                title='<b>인천광역시 예산 현황</b><br><sub>2024년</sub>',
                template='simple_white',color_discrete_sequence = px.colors.qualitative.Set2)
    fig.update_traces(textposition='inside', textinfo = 'percent+label', 
            textfont_color='white')
    fig.update_layout(title = {
        'text': '<b>인천광역시 2024년 예산 현황</b>',
        'y': 0.95,
        'x': 0.4,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    fig.update_traces(hoverinfo='label+percent+value', 
                    hovertemplate='%{label}: %{value:,.0f}억원')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df_group = budget.groupby('부서명').sum()
    df_group.reset_index(inplace=True)
    df_top = df_group.nlargest(10,'예산액')
    fig = px.bar(df_top,x='부서명', y='예산액',
                template= 'simple_white',text = df_top['예산액'].apply(lambda x: f'{x:,.0f}'))
    fig.update_layout(title = {
        'text':  f'<b>인천광역시 예산 현황</b><br><sub>2024년 상위10개 부서</sub>',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    #fig.update_layout(yaxis_tickformat=',.0s')
    fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='억원')
    #fig.update_layout(title_x=0.5)
    fig.update_xaxes(tickangle=45)
    fig.update_traces(hovertemplate='%{label}: %{value:,.0f}억원')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
df_businss = df.copy()
df_businss['예산액'] = (df_businss['예산액']  / 1000).apply(np.floor)
df_businss = df_businss.sort_values(by='예산액',ascending=False)

fig = px.treemap(df_businss, path=['부서명','세부사업명'], values='예산액',
    height=800, width= 800, color_discrete_sequence=px.colors.qualitative.Light24) #px.colors.qualitative.Pastel2)
fig.update_layout(title = {
    'text': '2024년 인천광역시 예산 현황',
    'y': 0.95,
    'x': 0.5,
    'xanchor': 'center',
    'yanchor': 'top',
    'font': {'color': 'white',
            'size' : 25}}, margin = dict(t=100, l=25, r=25, b=25))
fig.update_traces(marker = dict(line=dict(width = 1, color = 'black')))
fig.update_traces(texttemplate='%{label}: %{value:,.0f}백만원' , textposition='middle center', 
                textfont_color='black') 
fig.update_traces(#hoverinfo='label+percent+value', 
                hovertemplate='%{label}: %{value:,.0f}백만원')
fig.update_traces(hoverlabel=dict(font_size=16, font_family="Arial", font_color="white"))
fig.update_layout(font=dict(size=20))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2) 
with col1:
    budget_of_department = df[df['부서명']== selected_department]
    budget_of_department['예산액'] = (budget_of_department['예산액'] / 1000).apply(np.floor)

    fig = px.pie(budget_of_department, values='예산액', names='세부사업명',
            template='simple_white',color_discrete_sequence = px.colors.qualitative.Pastel)
    fig.update_traces(textposition='inside', textinfo = 'percent+label', 
            textfont_color='white')
    fig.update_layout(title = {
    'text': f'<b>{selected_department} 예산 현황</b><br><sub>2024년 세부사업</sub>',
    'y': 0.95,
    'x': 0.4,
    'xanchor': 'center',
    'yanchor': 'top',
    'font': {'color': 'white',
            'size' : 20}}, margin = {'t': 80} )
    fig.update_traces(hoverinfo='label+percent+value', 
                    hovertemplate='%{label}: %{value:,.0f}백만원')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.treemap(budget_of_department, path=['단위사업명','세부사업명','편성목명'], values='예산액',
    height=800, width= 800, color_discrete_sequence=px.colors.qualitative.Pastel2) #px.colors.qualitative.Pastel2)
    fig.update_layout(title = {
        'text': f'2024년 {selected_department} 예산 현황',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = dict(t=100, l=25, r=25, b=25))
    fig.update_traces(marker = dict(line=dict(width = 1, color = 'black')))
    fig.update_traces(texttemplate='%{label}: %{value:,.0f}백만원' , textposition='middle center', 
                    textfont_color='black') 
    fig.update_traces(#hoverinfo='label+percent+value', 
                    hovertemplate='%{label}: %{value:,.0f}백만원')
    fig.update_traces(hoverlabel=dict(font_size=16, font_family="Arial", font_color="white"))
    fig.update_layout(font=dict(size=20))
    st.plotly_chart(fig, use_container_width=True)

