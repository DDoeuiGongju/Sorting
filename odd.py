import streamlit as st
import random
import time
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os


# ------------------- [필수] 만능 한글 폰트 설정 -------------------
def setup_custom_font():
    font_file = 'NanumGothic.ttf'
    url = 'https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf'

    if not os.path.exists(font_file):
        import urllib.request
        urllib.request.urlretrieve(url, font_file)

    fm.fontManager.addfont(font_file)
    plt.rc('font', family='NanumGothic')
    plt.rc('axes', unicode_minus=False)


setup_custom_font()
# -------------------------------------------------------------

# 페이지 설정
st.set_page_config(page_title="정렬 알고리즘 시각화 (수업용)", layout="wide")

st.markdown("""
<style>
    .stButton>button { width: 100%; }
    .metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #ddd; }
    h3 { margin-bottom: 0px; }
</style>
""", unsafe_allow_html=True)

st.title("🎓 정렬 알고리즘 비교 학습 도구")
st.markdown("교과서 예제 값을 직접 입력하거나 랜덤 데이터로 실습해보세요.")

# ------------------- 사이드바 설정 -------------------
st.sidebar.header("설정")
algo_option = st.sidebar.selectbox(
    "알고리즘 선택",
    ("버블 정렬 (Bubble Sort)", "선택 정렬 (Selection Sort)", "삽입 정렬: 일반 (뒤에서 비교&이동)", "삽입 정렬: 교과서 (앞에서 탐색 후 이동)")
)

speed = st.sidebar.slider("애니메이션 속도 (초)", 0.01, 1.0, 0.3)

st.sidebar.markdown("---")
st.sidebar.subheader("데이터 입력 방식")
input_method = st.sidebar.radio("방식 선택", ("랜덤 생성", "직접 입력"))


# 데이터 초기화
def generate_random_data(n):
    return random.sample(range(1, 101), n)


if 'data' not in st.session_state:
    st.session_state.data = generate_random_data(10)

# 입력 UI 처리
if input_method == "랜덤 생성":
    data_size = st.sidebar.slider("데이터 개수", 5, 20, 10)
    if st.sidebar.button("🎲 데이터 무작위 섞기"):
        st.session_state.data = generate_random_data(data_size)

else:  # 직접 입력 모드
    default_text = "19, 80, 77, 11, 54"
    user_input = st.sidebar.text_input("숫자를 쉼표(,)로 구분해 입력", value=default_text)

    if st.sidebar.button("✅ 입력한 데이터 적용"):
        try:
            new_data = [int(x.strip()) for x in user_input.split(',') if x.strip()]
            if len(new_data) < 2:
                st.error("데이터는 최소 2개 이상 입력해주세요.")
            else:
                st.session_state.data = new_data
                st.success("데이터가 적용되었습니다!")
        except ValueError:
            st.error("숫자와 쉼표(,)만 입력할 수 있습니다.")


# ------------------- 그래프 및 시각화 로직 -------------------

def plot_bar(arr, highlight_indices=[], highlight_color='#ff5252', title="", sorted_indices=[]):
    fig, ax = plt.subplots(figsize=(10, 4))

    # 1. 기본 색상 (하늘색)
    colors = ['#b3e5fc'] * len(arr)

    # 2. 정렬 완료된 구역 색상 (노란색)
    for idx in sorted_indices:
        if idx < len(arr):
            colors[idx] = '#fff9c4'  # 연한 노란색

    # 3. 강조(비교/이동) 색상 (빨강/주황) - 가장 최우선
    for idx in highlight_indices:
        if idx < len(arr):
            colors[idx] = highlight_color

    ax.bar(range(len(arr)), arr, color=colors, edgecolor='black', linewidth=0.5)

    max_val = max(arr) if arr else 100
    ax.set_ylim(0, max_val * 1.25)

    for i, v in enumerate(arr):
        # 글자 좀 더 진하게
        font_weight = 'bold' if i in highlight_indices else 'normal'
        ax.text(i, v + (max_val * 0.02), str(v), ha='center', fontsize=10, fontweight=font_weight)

    ax.set_title(title, fontsize=14, pad=10)
    ax.axis('off')
    return fig


col1, col2 = st.columns([3, 1])
plot_placeholder = col1.empty()
info_placeholder = col2.empty()


def update_status(comparisons, swaps, current_action):
    with info_placeholder.container():
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 현재 상태</h3>
            <p style='margin: 5px 0;'><strong>비교 횟수:</strong> {comparisons}회</p>
            <p style='margin: 5px 0;'><strong>교환 및 이동 횟수:</strong> {swaps}회</p>
            <hr style='margin: 10px 0;'>
            <p style='color: #333; font-weight: bold;'>{current_action}</p>
        </div>
        """, unsafe_allow_html=True)

        # 색상 범례 표시
        st.markdown("""
        <div style="margin-top: 10px; font-size: 12px; color: gray;">
            <span style="color: #b3e5fc;">■</span> 미정렬 
            <span style="color: #fff9c4;">■</span> 정렬완료 
            <span style="color: #ff5252;">■</span> 비교 
            <span style="color: #ffb74d;">■</span> 교환/이동
        </div>
        """, unsafe_allow_html=True)


# ------------------- 정렬 알고리즘 -------------------

def bubble_sort(arr):
    n = len(arr)
    comparisons = 0
    swaps = 0
    sorted_idxs = []

    for i in range(n):
        for j in range(0, n - i - 1):
            comparisons += 1
            sorted_idxs = list(range(n - i, n))

            plot_placeholder.pyplot(
                plot_bar(arr, [j, j + 1], highlight_color='#ff5252', title=f"버블 정렬: {arr[j]} vs {arr[j + 1]} 비교",
                         sorted_indices=sorted_idxs))
            update_status(comparisons, swaps, f"현재 {arr[j]}와 {arr[j + 1]} 비교 중")
            time.sleep(speed)

            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                plot_placeholder.pyplot(plot_bar(arr, [j, j + 1], highlight_color='#ffb74d', title="위치 교환",
                                                 sorted_indices=sorted_idxs))
                update_status(comparisons, swaps, f"{arr[j + 1]} ↔ {arr[j]} 자리 교환")
                time.sleep(speed)

        sorted_idxs = list(range(n - i - 1, n))

    return comparisons, swaps


def selection_sort(arr):
    n = len(arr)
    comparisons = 0
    swaps = 0
    sorted_idxs = []

    for i in range(n):
        min_idx = i
        sorted_idxs = list(range(0, i))

        for j in range(i + 1, n):
            comparisons += 1
            plot_placeholder.pyplot(plot_bar(arr, [min_idx, j], highlight_color='#ff5252',
                                             title=f"최솟값 탐색: 현재 최소 {arr[min_idx]} vs {arr[j]}",
                                             sorted_indices=sorted_idxs))
            update_status(comparisons, swaps, f"나머지 중 최솟값 찾는 중 ({arr[j]} 확인)")
            time.sleep(speed)

            if arr[j] < arr[min_idx]:
                min_idx = j

        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            swaps += 1
            plot_placeholder.pyplot(plot_bar(arr, [i, min_idx], highlight_color='#ffb74d', title="최솟값 배치 (교환)",
                                             sorted_indices=sorted_idxs))
            update_status(comparisons, swaps, f"찾은 최솟값 {arr[i]}을(를) {i}번 인덱스로 교환(이동)")
            time.sleep(speed)

    return comparisons, swaps


def insertion_sort_standard(arr):
    # 일반적인 삽입 정렬 (뒤에서부터 비교하며 교환)
    comparisons = 0
    swaps = 0

    for i in range(1, len(arr)):
        j = i
        sorted_idxs = list(range(0, i))

        while j > 0:
            comparisons += 1
            plot_placeholder.pyplot(
                plot_bar(arr, [j-1, j], highlight_color='#ff5252', title=f"일반 삽입: {arr[j-1]} vs {arr[j]} 비교",
                         sorted_indices=sorted_idxs))
            update_status(comparisons, swaps, f"앞의 값({arr[j-1]})과 비교 중")
            time.sleep(speed)

            if arr[j-1] > arr[j]:
                # [수정] Shift 대신 Swap(교환) 사용
                arr[j-1], arr[j] = arr[j], arr[j-1]
                swaps += 1

                plot_placeholder.pyplot(plot_bar(arr, [j-1, j], highlight_color='#ffb74d', title="위치 교환",
                                                 sorted_indices=sorted_idxs))
                update_status(comparisons, swaps, f"{arr[j]}가 더 작으므로 앞으로 교환")
                j -= 1
                time.sleep(speed)
            else:
                break

        sorted_idxs = list(range(0, i + 1))
        plot_placeholder.pyplot(
            plot_bar(arr, [j], highlight_color='#4caf50', title=f"{arr[j]} 정렬 위치 확정", sorted_indices=sorted_idxs))
        update_status(comparisons, swaps, "자리 찾기 완료")
        time.sleep(speed)

    return comparisons, swaps


def insertion_sort_textbook(arr):
    # 교과서 방식 (앞에서 탐색 후 -> 교환하며 이동)
    comparisons = 0
    swaps = 0

    for i in range(1, len(arr)):
        key = arr[i]
        insert_pos = i
        sorted_idxs = list(range(0, i)) 

        # 1. 탐색
        for j in range(i):
            comparisons += 1
            plot_placeholder.pyplot(plot_bar(arr, [j, i], highlight_color='#ff5252', title=f"위치 탐색: {arr[j]} vs {key}",
                                             sorted_indices=sorted_idxs))
            update_status(comparisons, swaps, f"{arr[j]}와(과) {key} 비교 중")
            time.sleep(speed)

            if arr[j] > key:
                insert_pos = j
                break

        # 2. 이동 (Swap으로 처리)
        if insert_pos != i:
            # i번째부터 목표지점(insert_pos)까지 역순으로 교환하며 내려감
            for k in range(i, insert_pos, -1):
                arr[k], arr[k-1] = arr[k-1], arr[k]
                swaps += 1
                
                plot_placeholder.pyplot(
                    plot_bar(arr, [k-1, k], highlight_color='#ffb74d', title=f"위치 교환",
                             sorted_indices=sorted_idxs))
                update_status(comparisons, swaps, f"{arr[k-1]}을(를) 앞으로 보내기 위해 교환")
                time.sleep(speed)

            sorted_idxs = list(range(0, i + 1))
            plot_placeholder.pyplot(plot_bar(arr, [insert_pos], highlight_color='#4caf50', title=f"{key} 삽입 완료",
                                             sorted_indices=sorted_idxs))
            update_status(comparisons, swaps, f"{insert_pos}번 위치에 {key} 정렬 완료")
            time.sleep(speed)
        else:
            sorted_idxs = list(range(0, i + 1))
            plot_placeholder.pyplot(
                plot_bar(arr, [i], highlight_color='#4caf50', title=f"{key} 제자리 유지", sorted_indices=sorted_idxs))
            update_status(comparisons, swaps, "이동 없음")
            time.sleep(speed)

    return comparisons, swaps

# 실행 버튼
if st.button("정렬 시작 ▶️"):
    data_copy = st.session_state.data.copy()
    c, s = 0, 0

    if algo_option == "버블 정렬 (Bubble Sort)":
        c, s = bubble_sort(data_copy)
    elif algo_option == "선택 정렬 (Selection Sort)":
        c, s = selection_sort(data_copy)
    elif algo_option == "삽입 정렬: 일반 (뒤에서 비교&이동)":
        c, s = insertion_sort_standard(data_copy)
    elif algo_option == "삽입 정렬: 교과서 (앞에서 탐색 후 이동)":
        c, s = insertion_sort_textbook(data_copy)

    st.success(f"정렬 완료! 총 비교: {c}회, 교환/이동: {s}회")
    plot_placeholder.pyplot(plot_bar(data_copy, [], title="최종 정렬 완료", sorted_indices=range(len(data_copy))))

# 초기 데이터 표시
# plot_placeholder.pyplot(plot_bar(st.session_state.data, title="초기 데이터"))
