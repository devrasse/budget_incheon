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
st.markdown('<div class="centered"><h1 style="text-align:center;">📊 2024년 미추홀구 예산(부서별) </h1></div>', unsafe_allow_html=True)
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
    data =pd.read_excel('budget_2024.xlsx')
    return data

with loading_state.container():
    with st.spinner('데이터 읽어오는 중...'):
        st_lottie(lottie_loading, width=300)
        df = load_data()
    st.success('로딩 완료!')
    
loading_state.empty()

budget = df.copy()
budget = budget.dropna(subset=['산출근거식'])
# #budget.drop(0, inplace=True)
selected_columns = ['회계연도', '예산구분', '세부사업명', '부서명', '예산액', '자체재원','단위사업명','편성목명']
budget = budget[selected_columns]

budget['자체재원'] = budget['자체재원'].fillna(0).apply(lambda x: int(x) if str(x).isdigit() and x != '' else 0)


budget_group = budget.groupby(['회계연도','부서명']).sum()
budget_group.reset_index(inplace=True)


# 주어진 문자열을 쉼표로 분리하여 부서명 리스트를 생성
department_order = [
    "기획예산실", "스마트정책실", "미디어홍보실", "감사실", "총무과", "안전총괄과",
    "시민공동체과", "평생학습과", "민원여권과", "재무과", "세무1과", "세무2과", "문화예술과",
    "체육진흥과", "일자리정책과", "경제지원과", "복지정책과", "기초생활보장과", "노인장애인복지과",
    "여성가족과", "보육정책과", "환경보전과", "자원순환과", "건설과", "도시계획과", "공원녹지과", "교통행정과",
    "자동차관리과", "토지정보과", "도시재생과", "건축과", "공공시설과", "주택관리과", "도시정비과", "도시경관과",
    "보건행정과", "건강증진과", "치매정신건강과", "위생과", "숭의보건지소", "숭의1·3동", "숭의2동", "숭의4동",
    "용현1·4동", "용현2동", "용현3동", "용현5동", "학익1동", "학익2동", "도화1동", "도화2·3동", "주안1동", "주안2동",
    "주안3동", "주안4동", "주안5동", "주안6동", "주안7동", "주안8동", "관교동", "문학동","의회사무국"
]

# 주어진 순서대로 부서명을 정렬
sorted_department = budget_group['부서명'].astype('category').cat.set_categories(department_order).sort_values()
st.sidebar.header('미추홀구 예산 부서별')

#st.sidebar.subheader('부서명 선택')
selected_department = st.sidebar.selectbox('부서명',sorted_department) 


with st.expander("미추홀구 예산", expanded=False):
    st.dataframe(budget,use_container_width=True)

highlight_department = selected_department

col1, col2 = st.columns(2)
budget_group['자체재원'] = (budget_group['자체재원']  / 1000).apply(np.floor)
budget_group['예산액'] = (budget_group['예산액']  / 1000).apply(np.floor)
budget_group = budget_group.sort_values(by='예산액',ascending=False)

with col1:
    fig = px.pie(budget_group, values='예산액', names='부서명',
                title='<b>미추홀구 예산 현황</b><br><sub>2024년</sub>',
                template='simple_white',color_discrete_sequence = px.colors.qualitative.Set2)
    fig.update_traces(textposition='inside', textinfo = 'percent+label', 
            textfont_color='white')
    fig.update_layout(title = {
        'text': '<b>미추홀구 예산 현황</b><br><sub>2024년 부서별 예산현황</sub>',
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
    color_discrete_map = {highlight_department: 'blue'}
    for department in budget_group['부서명']:
        if department != highlight_department:
            color_discrete_map[department] = 'gray'

    fig = px.pie(budget_group, values='예산액', names='부서명',
                title=f'<b>미추홀구 예산 현황</b><br><sub>2024년 {selected_department}</sub>',
                template='simple_white')
    fig.update_traces(marker=dict(colors=budget_group['부서명'].map(color_discrete_map)),
                    textposition='inside', textinfo = 'percent+label',textfont_color='white')
    fig.update_layout(title = {
        'text': f'<b>미추홀구 예산 현황</b><br><sub>2024년 {selected_department}</sub>',
        'y': 0.95,
        'x': 0.4,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    fig.update_traces(hoverinfo='label+percent+value', 
                    hovertemplate='%{label}: %{value:,.0f}백만원')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2) 
budget_group = budget_group.sort_values(by='자체재원',ascending=False)
with col1:
    fig = px.pie(budget_group, values='자체재원', names='부서명',
                title='<b>미추홀구 예산 현황</b><br><sub>2024년</sub>',
                template='simple_white',color_discrete_sequence = px.colors.qualitative.Set2)
    fig.update_traces(textposition='inside', textinfo = 'percent+label', 
            textfont_color='white')
    fig.update_layout(title = {
        'text': '<b>미추홀구 예산 현황(구비)</b><br><sub>2024년 부서별 예산현황</sub>',
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
    color_discrete_map = {highlight_department: 'blue'}
    for department in budget_group['부서명']:
        if department != highlight_department:
            color_discrete_map[department] = 'gray'

    fig = px.pie(budget_group, values='자체재원', names='부서명',
                title='<b>미추홀구 예산 현황</b><br><sub>2024년</sub>',
                template='simple_white',color_discrete_sequence = px.colors.qualitative.Set2)
    fig.update_traces(marker=dict(colors=budget_group['부서명'].map(color_discrete_map)),
                    textposition='inside', textinfo = 'percent+label', textfont_color='white')
    fig.update_layout(title = {
        'text': f'<b>미추홀구 예산 현황(구비)</b><br><sub>2024년 {selected_department}</sub>',
        'y': 0.95,
        'x': 0.4,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    fig.update_traces(hoverinfo='label+percent+value', 
                    hovertemplate='%{label}: %{value:,.0f}백만원')
    st.plotly_chart(fig, use_container_width=True)
    
st.markdown("---")
col1, col2 = st.columns(2) 
budget_of_department = budget[budget['부서명']== selected_department]
budget_of_department['자체재원'] = (budget_of_department['자체재원']  / 1000).apply(np.floor)
#budget_of_department['자체재원'] = (department_of_recycle['자체재원']  / 1000).apply(np.floor)
#department_of_recycle = budget_2024[budget_2024['부서명'] == '자원순환과']
with col1:
    fig = px.treemap(budget_group, path=['부서명'], values='예산액',
        height=800, width= 800, color_discrete_sequence=px.colors.qualitative.Set1) #px.colors.qualitative.Pastel2)
    fig.update_layout(title = {
        'text': '2024년 미추홀구 예산 현황',
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

st.markdown("---")
col1, col2 = st.columns(2) 

with col1:
    fig = px.treemap(budget_group, path=['부서명'], values='자체재원',
        height=800, width= 800, color_discrete_sequence=px.colors.qualitative.Set1) #px.colors.qualitative.Pastel2)
    fig.update_layout(title = {
        'text': '2024년 미추홀구 예산 현황(구비)',
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


with col2:
    fig = px.treemap(budget_of_department, path=['단위사업명','세부사업명','편성목명'], values='자체재원',
        height=800, width= 800, color_discrete_sequence=px.colors.qualitative.Pastel2) #px.colors.qualitative.Pastel2)
    fig.update_layout(title = {
        'text': f'2024년 {selected_department} 예산 현황(구비)',
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

st.markdown("---")
col1, col2 = st.columns(2)
department_group = budget_of_department.groupby(by='세부사업명').sum()
budget_top10_recycle = department_group.nlargest(10,'예산액')
budget_top10_recycle = budget_top10_recycle.sort_values(by='예산액',ascending=False)
budget_top10_recycle.reset_index(inplace=True)
department_group.reset_index(inplace = True)

with col1:
    fig = px.pie(department_group, values='예산액', names='세부사업명',
            template='simple_white',color_discrete_sequence = px.colors.qualitative.Set2)
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
    fig = px.bar(budget_top10_recycle,x='세부사업명', y='예산액',
                labels={'자체재원': '구비', '세부사업명': '사업명'},
                template= 'simple_white',text = budget_top10_recycle['예산액'].apply(lambda x: f'{x:,.0f}'))
    fig.update_layout(title = {
        'text':  f'<b>{selected_department} 예산 현황</b><br><sub>2024년 세부사업(상위10개 사업)</sub>',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    #fig.update_layout(yaxis_tickformat=',.0s')
    fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
    #fig.update_layout(title_x=0.5)
    fig.update_xaxes(tickangle=45)
    fig.update_traces(hovertemplate='%{label}: %{value:,.0f}백만원')

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2)
budget_top10_recycle = department_group.nlargest(10,'자체재원')
budget_top10_recycle = budget_top10_recycle.sort_values(by='자체재원',ascending=False)
budget_top10_recycle.reset_index(inplace=True)
department_group.reset_index(inplace = True)

with col1:
    fig = px.pie(department_group, values='자체재원', names='세부사업명',
            template='simple_white',color_discrete_sequence = px.colors.qualitative.Set2)
    fig.update_traces(textposition='inside', textinfo = 'percent+label', 
            textfont_color='white')
    fig.update_layout(title = {
        'text': f'<b>{selected_department} 예산 현황(구비)</b><br><sub>2024년 세부사업</sub>',
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
    fig = px.bar(budget_top10_recycle,x='세부사업명', y='자체재원',
                labels={'자체재원': '구비', '세부사업명': '사업명'},
                template= 'simple_white',text = budget_top10_recycle['예산액'].apply(lambda x: f'{x:,.0f}'))
    fig.update_layout(title = {
        'text':  f'<b>{selected_department} 예산 현황(구비)</b><br><sub>2024년 세부사업(상위10개 사업)</sub>',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    #fig.update_layout(yaxis_tickformat=',.0s')
    fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
    #fig.update_layout(title_x=0.5)
    fig.update_xaxes(tickangle=45)
    fig.update_traces(hovertemplate='%{label}: %{value:,.0f}백만원')

    st.plotly_chart(fig, use_container_width=True)