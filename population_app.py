import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sgis_helper import get_population_data, get_regional_population, get_population_change_rate

# 페이지 설정
st.set_page_config(
    page_title="지역 인구 변화 통계",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 스타일
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');

    * {
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
        background-attachment: fixed;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3436 0%, #636e72 100%);
        color: #e8e8e8;
    }

    [data-testid="stSidebar"] label {
        color: #e8e8e8 !important;
        font-size: 1.1em !important;
        font-weight: 500 !important;
    }

    .main-title {
        text-align: center;
        font-size: 3.5em;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 20px;
    }

    .section-title {
        font-size: 2.2em;
        font-weight: 700;
        margin-top: 30px;
        margin-bottom: 20px;
        border-bottom: 3px solid #667eea;
        padding-bottom: 15px;
        color: #2d3436;
    }

    .metric-box {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 지역 인구 변화 통계</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2em; color: #636e72;">SGIS 통계지리정보 서비스 기반 인구 통계</p>', unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    st.markdown("---")

    view_type = st.radio(
        "조회 유형",
        ["전국 인구 추이", "지역별 인구", "인구 변화율"]
    )

    # 연도 선택
    start_year = st.slider(
        "시작 연도",
        min_value=2015,
        max_value=2026,
        value=2015,
        step=1
    )

    end_year = st.slider(
        "종료 연도",
        min_value=start_year,
        max_value=2026,
        value=2026,
        step=1
    )

    st.markdown("---")
    st.info("💡 SGIS API 키를 .env에 설정해야 실시간 데이터를 조회할 수 있습니다.")

# 데모 데이터 생성 함수
def generate_demo_data():
    """데모용 인구 통계 데이터를 생성한다."""
    import numpy as np

    # 전국 인구 추이 데이터 (2015~2026)
    years = list(range(2015, 2027))
    population = [51780, 51874, 51969, 52051, 52078, 51284, 51062, 51329, 51780, 51344, 51200, 51100]

    demo_national = pd.DataFrame({
        "연도": years,
        "인구(만명)": [p / 10000 for p in population]
    })

    # 지역별 인구 데이터
    regions = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "경기", "강원", "충북",
               "충남", "전북", "전남", "경북", "경남", "제주"]
    demo_regional = pd.DataFrame({
        "지역": regions,
        "인구(만명)": [999, 343, 240, 300, 149, 148, 117, 1352, 152, 160,
                     206, 179, 185, 260, 335, 68],
        "2020년": [974, 330, 235, 295, 145, 142, 112, 1290, 155, 158,
                   200, 180, 190, 270, 340, 65],
        "인구변화율(%)": [2.5, 3.9, 2.1, 1.7, 2.8, 4.2, 4.5, 4.8, -1.9, 1.3,
                     3.0, -0.6, -2.6, -3.7, -1.5, 4.6]
    })

    return demo_national, demo_regional

# 데모 데이터 로드
demo_national, demo_regional = generate_demo_data()

# 1. 전국 인구 추이 탭
if view_type == "전국 인구 추이":
    st.markdown('<div class="section-title">📈 전국 인구 추이</div>', unsafe_allow_html=True)

    # 실제 데이터 조회 시도
    try:
        actual_data = get_population_data(start_year, end_year)
        if "error" not in actual_data:
            data = actual_data
        else:
            st.warning("⚠️ 실시간 데이터 조회 실패. 데모 데이터를 표시합니다.")
            data = None
    except:
        data = None

    if data is None:
        # 데모 데이터 필터링
        filtered_data = demo_national[
            (demo_national["연도"] >= start_year) &
            (demo_national["연도"] <= end_year)
        ].reset_index(drop=True)

        # 세션 상태에 데이터 초기화
        if "population_data" not in st.session_state:
            st.session_state.population_data = filtered_data.copy()

        # 사용자가 편집 가능한 데이터 테이블
        st.markdown("### 📝 데이터 편집")
        st.info("💡 아래 표에서 인구 값을 수정하면 그래프가 자동으로 업데이트됩니다.")

        edited_data = st.data_editor(
            st.session_state.population_data,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed"
        )

        # 편집된 데이터 저장
        st.session_state.population_data = edited_data

        # 라인 차트 (편집된 데이터 사용)
        fig = px.line(
            edited_data,
            x="연도",
            y="인구(만명)",
            markers=True,
            title="",
            labels={"연도": "연도", "인구(만명)": "인구(만 명)"}
        )
        fig.update_layout(
            hovermode="x unified",
            height=500,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

        # 통계 정보
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "최대 인구",
                f"{edited_data['인구(만명)'].max():.2f}만명",
                f"({edited_data['연도'].iloc[edited_data['인구(만명)'].argmax()]}년)"
            )
        with col2:
            st.metric(
                "최소 인구",
                f"{edited_data['인구(만명)'].min():.2f}만명",
                f"({edited_data['연도'].iloc[edited_data['인구(만명)'].argmin()]}년)"
            )
        with col3:
            change = edited_data["인구(만명)"].iloc[-1] - edited_data["인구(만명)"].iloc[0]
            st.metric(
                "기간 변화",
                f"{change:+.2f}만명",
                f"{change/edited_data['인구(만명)'].iloc[0]*100:+.2f}%"
            )

# 2. 지역별 인구 탭
elif view_type == "지역별 인구":
    st.markdown('<div class="section-title">🗺️ 지역별 인구</div>', unsafe_allow_html=True)

    # 실제 데이터 조회 시도
    try:
        actual_data = get_regional_population(year=end_year)
        if "error" not in actual_data:
            data = actual_data
        else:
            st.warning("⚠️ 실시간 데이터 조회 실패. 데모 데이터를 표시합니다.")
            data = None
    except:
        data = None

    if data is None:
        # 데모 데이터 사용
        sorted_data = demo_regional.sort_values("인구(만명)", ascending=False)

        # 막대 차트
        fig = px.bar(
            sorted_data,
            x="지역",
            y="인구(만명)",
            title="",
            labels={"지역": "지역", "인구(만명)": "인구(만 명)"}
        )
        fig.update_layout(
            hovermode="x unified",
            height=500,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

        # 지역 랭킹
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🥇 인구 많은 지역 Top 5")
            top_5 = sorted_data.head(5).reset_index(drop=True)
            for idx, row in top_5.iterrows():
                st.write(f"{idx+1}. **{row['지역']}** - {row['인구(만명)']:.0f}만명")

        with col2:
            st.markdown("### 📉 인구 적은 지역 Top 5")
            bottom_5 = sorted_data.tail(5).reset_index(drop=True)
            for rank, (idx, row) in enumerate(bottom_5.iloc[::-1].iterrows(), 1):
                st.write(f"{rank}. **{row['지역']}** - {row['인구(만명)']:.0f}만명")

        # 데이터 테이블
        st.markdown("### 📋 전체 지역 인구")
        st.dataframe(
            demo_regional.sort_values("인구(만명)", ascending=False),
            use_container_width=True,
            hide_index=True
        )

# 3. 인구 변화율 탭
elif view_type == "인구 변화율":
    st.markdown('<div class="section-title">📊 인구 변화율</div>', unsafe_allow_html=True)

    # 데모 데이터 사용
    sorted_data = demo_regional.sort_values("인구변화율(%)", ascending=True)

    # 변화율 차트 (양수/음수 색상 구분)
    fig = px.bar(
        sorted_data,
        x="인구변화율(%)",
        y="지역",
        orientation="h",
        title="",
        labels={"인구변화율(%)": "인구 변화율(%)", "지역": "지역"}
    )
    fig.update_traces(marker_color=["red" if x < 0 else "green" for x in sorted_data["인구변화율(%)"]])
    fig.update_layout(
        height=600,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    # 증감 통계
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 인구 증가 지역")
        increase = demo_regional[demo_regional["인구변화율(%)"] > 0].sort_values("인구변화율(%)", ascending=False)
        for _, row in increase.iterrows():
            st.write(f"**{row['지역']}** - {row['인구변화율(%)']:+.2f}%")

    with col2:
        st.markdown("### 📉 인구 감소 지역")
        decrease = demo_regional[demo_regional["인구변화율(%)"] < 0].sort_values("인구변화율(%)")
        for _, row in decrease.iterrows():
            st.write(f"**{row['지역']}** - {row['인구변화율(%)']:.2f}%")

    # 데이터 테이블
    st.markdown("### 📋 상세 변화율")
    st.dataframe(
        demo_regional.sort_values("인구변화율(%)", ascending=False),
        use_container_width=True,
        hide_index=True
    )

# 하단 안내 메시지
st.markdown("---")
st.markdown("""
### 📌 사용 방법
1. 사이드바에서 **조회 유형**을 선택하세요
2. **시작/종료 연도**를 설정하여 원하는 기간의 데이터를 조회하세요
3. **SGIS API 키**를 .env에 설정하면 실시간 데이터를 조회할 수 있습니다

### 🔗 참고
- [SGIS 개발자 센터](https://sgis.mods.go.kr/developer/html/main.html)
- [공공데이터 포털](https://www.data.go.kr)

---
*본 앱은 SGIS(통계지리정보 서비스) 데이터를 기반으로 합니다*
""")
