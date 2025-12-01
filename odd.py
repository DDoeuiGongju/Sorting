import streamlit as st
import random
import time
import matplotlib.pyplot as plt
import platform
import koreanize_matplotlib

# ------------------- 한글 폰트 설정 -------------------
system_name = platform.system()
if system_name == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif system_name == 'Darwin':
    plt.rc('font', family='AppleGothic')
else:
    plt.rc('font', family='NanumGothic')
plt.rc('axes', unicode_minus=False)
# -----------------------------------------------------

# 페이지 설정
st.set_page_config(page_title="정렬 알고리즘 시각화 (수업용)", layout="wide")

st.markdown("""
<style>
    .stButton>button { width: 100%; }
    .metric-card { background-color: #f0f2f6; padding: 10px; border-radius: 5px; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("🎓 정렬 알고리즘 비교 학습 도구")
st.markdown("교과서 예제 값을 직접 입력하거나 랜덤 데이터로 실습해보세요.")

# ------------------- 사이드바 설정 -------------------
st.sidebar.header("설정")
algo_option = st.sidebar.selectbox(
    "알고리즘 선택",
    ("버블 정렬 (Bubble Sort)", "선택 정렬 (Selection Sort)", "삽입 정렬: 일반 (뒤에서 비교&이동)", "삽입 정렬: 교과서 (앞에서 탐색 후 밀기)")
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

def plot_bar(arr, highlight_indices=[], color='skyblue', title=""):
    fig, ax = plt.subplots(figsize=(10, 4))
    colors = [color] * len(arr)

    for idx in highlight_indices:
        if idx < len(colors):
            colors[idx] = 'red'

    ax.bar(range(len(arr)), arr, color=colors)

    max_val = max(arr) if arr else 100
    ax.set_ylim(0, max_val * 1.2)

    for i, v in enumerate(arr):
        ax.text(i, v + (max_val * 0.02), str(v), ha='center', fontsize=9)
    ax.set_title(title)
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
            <p><strong>비교 횟수:</strong> {comparisons}회</p>
            <p><strong>교환(이동) 횟수:</strong> {swaps}회</p>
            <hr>
            <p>{current_action}</p>
        </div>
        """, unsafe_allow_html=True)


# ------------------- 정렬 알고리즘 -------------------

def bubble_sort(arr):
    n = len(arr)
    comparisons = 0
    swaps = 0
    for i in range(n):
        for j in range(0, n - i - 1):
            comparisons += 1
            plot_placeholder.pyplot(plot_bar(arr, [j, j + 1], title=f"버블 정렬: {arr[j]} vs {arr[j + 1]} 비교"))
            update_status(comparisons, swaps, f"{arr[j]}와 {arr[j + 1]} 비교 중")
            time.sleep(speed)
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                plot_placeholder.pyplot(plot_bar(arr, [j, j + 1], 'orange', title="교환 발생!"))
                update_status(comparisons, swaps, f"{arr[j + 1]} ↔ {arr[j]} 교환")
                time.sleep(speed)
    return comparisons, swaps


def selection_sort(arr):
    n = len(arr)
    comparisons = 0
    swaps = 0
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            plot_placeholder.pyplot(plot_bar(arr, [min_idx, j], title=f"최솟값 찾기: 현재 최소 {arr[min_idx]} vs {arr[j]}"))
            update_status(comparisons, swaps, "최솟값 탐색 중")
            time.sleep(speed)
            if arr[j] < arr[min_idx]:
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            swaps += 1
            plot_placeholder.pyplot(plot_bar(arr, [i, min_idx], 'orange', title="최솟값 배치"))
            update_status(comparisons, swaps, f"{arr[i]} 위치로 최솟값 이동")
            time.sleep(speed)
    return comparisons, swaps


def insertion_sort_standard(arr):
    comparisons = 0
    swaps = 0
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            plot_placeholder.pyplot(plot_bar(arr, [j, j + 1], title=f"일반 삽입: {arr[j]} vs {key} 비교"))
            update_status(comparisons, swaps, f"뒤({j})에서부터 비교 중")
            time.sleep(speed)
            if arr[j] > key:
                arr[j + 1] = arr[j]
                swaps += 1
                arr[j] = key
                plot_placeholder.pyplot(plot_bar(arr, [j, j + 1], 'orange', title="밀어내기 (Shift)"))
                j -= 1
            else:
                break
        arr[j + 1] = key
        plot_placeholder.pyplot(plot_bar(arr, [j + 1], 'green', title=f"{key} 삽입 완료"))
    return comparisons, swaps


def insertion_sort_textbook(arr):
    comparisons = 0
    swaps = 0

    for i in range(1, len(arr)):
        key = arr[i]  # 삽입할 값 기억해두기
        insert_pos = i

        # 1. 탐색 단계 (비교만 수행, 이동 없음)
        for j in range(i):
            comparisons += 1
            plot_placeholder.pyplot(plot_bar(arr, [j, i], title=f"위치 탐색: {arr[j]} vs {key}(타겟)"))
            update_status(comparisons, swaps, f"앞({j})에서부터 들어갈 자리 찾는 중")
            time.sleep(speed)

            if arr[j] > key:
                insert_pos = j
                break

                # 2. 이동 단계 (Shift: 한 칸씩 밀어내기)
        if insert_pos != i:
            # i-1부터 insert_pos까지 역순으로 내려오며 덮어쓰기
            for k in range(i - 1, insert_pos - 1, -1):
                arr[k + 1] = arr[k]  # 오른쪽으로 복사
                swaps += 1

                # 시각화: 현재 밀려나는 막대와, 비어질 공간 표현
                plot_placeholder.pyplot(plot_bar(arr, [k, k + 1], 'orange', title=f"공간 만들기: {arr[k]} → 오른쪽 밀기"))
                update_status(comparisons, swaps, "빈 공간을 만들기 위해 밀어내는 중 (Shift)")
                time.sleep(speed)

            # 3. 삽입 단계
            arr[insert_pos] = key
            plot_placeholder.pyplot(plot_bar(arr, [insert_pos], 'green', title=f"{key} 삽입 완료"))
            update_status(comparisons, swaps, f"{insert_pos}번 위치에 {key} 삽입")
            time.sleep(speed)

    return comparisons, swaps


# 실행 버튼
if st.button("정렬 시작 ▶️"):
    data_copy = st.session_state.data.copy()

    if algo_option == "버블 정렬 (Bubble Sort)":
        c, s = bubble_sort(data_copy)
    elif algo_option == "선택 정렬 (Selection Sort)":
        c, s = selection_sort(data_copy)
    elif algo_option == "삽입 정렬: 일반 (뒤에서 비교&이동)":
        c, s = insertion_sort_standard(data_copy)
    elif algo_option == "삽입 정렬: 교과서 (앞에서 탐색 후 밀기)":
        c, s = insertion_sort_textbook(data_copy)

    st.success(f"정렬 완료! 총 비교: {c}회, 교환/이동: {s}회")
    plot_placeholder.pyplot(plot_bar(data_copy, [], 'green', title="정렬 완료"))

# 초기 데이터 표시
# plot_placeholder.pyplot(plot_bar(st.session_state.data, title="현재 데이터"))
