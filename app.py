import streamlit as st
import json
import random
import os
import base64
import html


# ============================================================
# 页面设置
# ============================================================

st.set_page_config(
    page_title="English Vocabulary",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 数据文件
#
# 永远放在 app.py 所在的文件夹
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "vocabulary.json"
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.block-container {
    padding-top: 0.6rem;
    padding-bottom: 0.5rem;
    max-width: 1150px;
}

h1 {
    font-size: 26px !important;
    margin-bottom: 5px !important;
}

h2 {
    font-size: 21px !important;
}

h3 {
    font-size: 18px !important;
}

.question {
    font-size: 30px;
    font-weight: 600;
    text-align: center;
    margin: 8px 0 12px 0;
    word-break: break-word;
}

.previous-question {
    font-size: 24px;
    font-weight: 600;
    text-align: center;
    margin: 8px 0 12px 0;
    word-break: break-word;
}

.answer-text {
    font-size: 16px;
    margin: 5px 0;
    word-break: break-word;
}

div[data-testid="stTextInput"] input {
    font-size: 18px;
    height: 42px;
}

div.stButton > button {
    min-height: 38px;
    font-size: 15px;
}

@media (max-width: 700px) {

    .question {
        font-size: 25px;
    }

    .previous-question {
        font-size: 21px;
    }

}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 创建默认词库
# ============================================================

def create_empty_file():

    if not os.path.exists(DATA_FILE):

        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                [],
                f,
                ensure_ascii=False,
                indent=4
            )


# ============================================================
# 读取词库
# ============================================================

def load_words():

    create_empty_file()

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

            if not isinstance(data, list):
                return []

            # 修复旧数据
            changed = False

            for word in data:

                if "english" not in word:
                    word["english"] = ""

                    changed = True

                if "chinese" not in word:
                    word["chinese"] = ""

                    changed = True

                if "weight" not in word:
                    word["weight"] = 3

                    changed = True

                if "correct" not in word:
                    word["correct"] = 0

                    changed = True

                if "wrong" not in word:
                    word["wrong"] = 0

                    changed = True

            if changed:

                save_words_to_file(data)

            return data

    except Exception as e:

        st.error(
            f"读取词库失败：{e}"
        )

        return []


# ============================================================
# 保存词库
# ============================================================

def save_words_to_file(data):

    temp_file = DATA_FILE + ".tmp"

    try:

        # 先写临时文件
        with open(
            temp_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4
            )

            # 确保写入磁盘
            f.flush()
            os.fsync(f.fileno())

        # 再替换正式文件
        os.replace(
            temp_file,
            DATA_FILE
        )

        return True

    except Exception as e:

        st.error(
            f"保存词库失败：{e}"
        )

        return False


# ============================================================
# 每次启动读取
# ============================================================

words = load_words()


# ============================================================
# 保存当前词库
# ============================================================

def save_words():

    return save_words_to_file(words)


# ============================================================
# 计算概率
# ============================================================

def calculate_probability(word):

    if not words:
        return 0

    total_weight = sum(
        max(
            1,
            int(item.get("weight", 3))
        )
        for item in words
    )

    if total_weight == 0:
        return 0

    current_weight = max(
        1,
        int(word.get("weight", 3))
    )

    return (
        current_weight
        / total_weight
        * 100
    )


# ============================================================
# 随机抽题
# ============================================================

def get_random_word():

    if not words:
        return None

    weights = [
        max(
            1,
            int(word.get("weight", 3))
        )
        for word in words
    ]

    return random.choices(
        words,
        weights=weights,
        k=1
    )[0]


# ============================================================
# 永久统计
# ============================================================

def get_total_correct():

    return sum(
        int(word.get("correct", 0))
        for word in words
    )


def get_total_wrong():

    return sum(
        int(word.get("wrong", 0))
        for word in words
    )


# ============================================================
# 浏览器发音
# ============================================================

def pronunciation_button(text, key):

    encoded = base64.b64encode(
        str(text).encode("utf-8")
    ).decode("ascii")

    html_code = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <style>

        body {{
            margin: 0;
            padding: 0;
            background: transparent;

            display: flex;
            justify-content: center;
            align-items: center;
        }}

        button {{
            border: none;
            background: transparent;

            cursor: pointer;

            font-size: 21px;

            padding: 2px 6px;
        }}

        button:hover {{
            transform: scale(1.15);
        }}

        </style>

    </head>

    <body>

        <button
            onclick="speak()"
            title="British English"
        >
            🔊
        </button>

        <script>

        function speak() {{

            const encoded = "{encoded}";

            const text =
                decodeURIComponent(
                    escape(
                        atob(encoded)
                    )
                );

            window.speechSynthesis.cancel();

            const speech =
                new SpeechSynthesisUtterance(text);

            speech.lang = "en-GB";

            speech.rate = 0.85;

            window.speechSynthesis.speak(
                speech
            );
        }}

        </script>

    </body>

    </html>
    """

    st.components.v1.html(
        html_code,
        height=35,
        width=50,
        scrolling=False
    )


# ============================================================
# Session State
# ============================================================

if "current_word_index" not in st.session_state:

    st.session_state.current_word_index = None


if "question_type" not in st.session_state:

    st.session_state.question_type = "中译英"


if "last_word_index" not in st.session_state:

    st.session_state.last_word_index = None


if "last_answer" not in st.session_state:

    st.session_state.last_answer = ""


if "last_correct" not in st.session_state:

    st.session_state.last_correct = None


# ============================================================
# 标题
# ============================================================

st.title("📚 English Vocabulary")


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    page = st.radio(
        "功能",
        [
            "🎯 开始练习",
            "📚 词库管理",
            "📖 查看词库"
        ]
    )


# ============================================================
#
# 词库管理
#
# ============================================================

if page == "📚 词库管理":

    st.header("📚 词库管理")

    # ========================================================
    # 添加
    # ========================================================

    st.subheader("➕ 添加单词")

    col1, col2 = st.columns(2)

    with col1:

        english_text = st.text_area(
            "英文",
            height=100,
            placeholder="we\ni\nyou"
        )

    with col2:

        chinese_text = st.text_area(
            "中文",
            height=100,
            placeholder="我们\n我\n你"
        )

    if st.button(
        "➕ 添加",
        use_container_width=True
    ):

        english_list = [
            x.strip()
            for x in english_text.splitlines()
            if x.strip()
        ]

        chinese_list = [
            x.strip()
            for x in chinese_text.splitlines()
            if x.strip()
        ]

        if not english_list:

            st.warning(
                "请输入英文单词。"
            )

        elif len(english_list) != len(chinese_list):

            st.error(
                "英文和中文的数量必须相同。"
            )

        else:

            added = 0
            duplicate = 0

            for english, chinese in zip(
                english_list,
                chinese_list
            ):

                exists = any(
                    item["english"].strip().lower()
                    == english.strip().lower()
                    for item in words
                )

                if exists:

                    duplicate += 1

                else:

                    words.append(
                        {
                            "english": english,
                            "chinese": chinese,
                            "weight": 3,
                            "correct": 0,
                            "wrong": 0
                        }
                    )

                    added += 1

            if save_words():

                st.success(
                    f"成功添加 {added} 个单词。"
                )

                if duplicate:

                    st.info(
                        f"{duplicate} 个重复单词没有添加。"
                    )

    st.divider()

    # ========================================================
    # 编辑
    # ========================================================

    st.subheader("✏️ 编辑词库")

    search = st.text_input(
        "🔍 搜索",
        placeholder="输入英文或中文"
    )

    for index, word in enumerate(words):

        if search:

            if (
                search.lower()
                not in word["english"].lower()
                and
                search
                not in word["chinese"]
            ):

                continue

        with st.expander(
            f"{word['english']} → {word['chinese']}"
        ):

            col1, col2 = st.columns(2)

            with col1:

                new_english = st.text_input(
                    "英文",
                    value=word["english"],
                    key=f"edit_en_{index}"
                )

            with col2:

                new_chinese = st.text_input(
                    "中文",
                    value=word["chinese"],
                    key=f"edit_cn_{index}"
                )

            st.caption(
                f"权重：{word['weight']}  | "
                f"概率：{calculate_probability(word):.2f}%  | "
                f"正确：{word['correct']}  | "
                f"错误：{word['wrong']}"
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "💾 保存",
                    key=f"save_{index}",
                    use_container_width=True
                ):

                    word["english"] = (
                        new_english.strip()
                    )

                    word["chinese"] = (
                        new_chinese.strip()
                    )

                    if save_words():

                        st.success(
                            "修改成功"
                        )

                        st.rerun()

            with col2:

                if st.button(
                    "🗑️ 删除",
                    key=f"delete_{index}",
                    use_container_width=True
                ):

                    words.pop(index)

                    if save_words():

                        st.rerun()


# ============================================================
#
# 查看词库
#
# ============================================================

elif page == "📖 查看词库":

    st.header("📖 我的词库")

    if not words:

        st.info(
            "目前没有单词。"
        )

    else:

        search = st.text_input(
            "🔍 搜索词库",
            placeholder="输入英文或中文"
        )

        filtered_words = []

        for word in words:

            if not search:

                filtered_words.append(word)

            elif (
                search.lower()
                in word["english"].lower()
                or
                search
                in word["chinese"]
            ):

                filtered_words.append(word)

        st.caption(
            f"找到 {len(filtered_words)} 个单词"
        )

        col1, col2, col3, col4, col5, col6 = st.columns(
            [2, 2, 1, 1.3, 0.7, 0.7]
        )

        col1.write("**英文**")
        col2.write("**中文**")
        col3.write("**权重**")
        col4.write("**概率**")
        col5.write("**✓**")
        col6.write("**✗**")

        st.divider()

        for word in filtered_words:

            col1, col2, col3, col4, col5, col6 = st.columns(
                [2, 2, 1, 1.3, 0.7, 0.7]
            )

            col1.write(
                word["english"]
            )

            col2.write(
                word["chinese"]
            )

            col3.write(
                word["weight"]
            )

            col4.write(
                f"{calculate_probability(word):.2f}%"
            )

            col5.write(
                word["correct"]
            )

            col6.write(
                word["wrong"]
            )


# ============================================================
#
# 开始练习
#
# ============================================================

elif page == "🎯 开始练习":

    if not words:

        st.warning(
            "词库为空，请先到「词库管理」添加单词。"
        )

    else:

        # ====================================================
        # 题型
        # ====================================================

        question_type = st.radio(
            "题型",
            [
                "中译英",
                "英译中"
            ],
            horizontal=True
        )


        # ====================================================
        # 如果题型改变
        # ====================================================

        if (
            question_type
            != st.session_state.question_type
        ):

            st.session_state.question_type = (
                question_type
            )

            st.session_state.current_word_index = None

            st.session_state.last_word_index = None

            st.session_state.last_answer = ""

            st.session_state.last_correct = None


        # ====================================================
        # 防止 index 超出
        # ====================================================

        if (
            st.session_state.current_word_index is None
            or
            st.session_state.current_word_index
            >= len(words)
        ):

            selected_word = get_random_word()

            if selected_word is not None:

                st.session_state.current_word_index = (
                    words.index(selected_word)
                )


        # ====================================================
        # 当前单词
        # ====================================================

        current_index = (
            st.session_state.current_word_index
        )

        word = words[current_index]


        # ====================================================
        # 左右布局
        # ====================================================

        left, right = st.columns(
            [1, 1],
            gap="large"
        )


        # ====================================================
        # 左边：上一题
        # ====================================================

        with left:

            st.markdown(
                "### 上一题"
            )

            last_index = (
                st.session_state.last_word_index
            )

            if last_index is None:

                st.caption(
                    "开始答题后显示上一题"
                )

            elif last_index >= len(words):

                st.caption(
                    "上一题不存在"
                )

            else:

                last_word = words[last_index]


                # ==========================================
                # 中译英
                # ==========================================

                if question_type == "中译英":

                    st.markdown(
                        f"""
                        <div class="previous-question">
                            {html.escape(
                                last_word["chinese"]
                            )}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    st.markdown(
                        f"""
                        <div class="answer-text">
                            你的答案：
                            <b>
                            {html.escape(
                                st.session_state.last_answer
                            )}
                            </b>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    st.markdown(
                        f"""
                        <div class="answer-text">
                            正确答案：
                            <b>
                            {html.escape(
                                last_word["english"]
                            )}
                            </b>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    pronunciation_button(
                        last_word["english"],
                        "last_cn_en"
                    )


                # ==========================================
                # 英译中
                # ==========================================

                else:

                    st.markdown(
                        f"""
                        <div class="previous-question">
                            {html.escape(
                                last_word["english"]
                            )}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    pronunciation_button(
                        last_word["english"],
                        "last_en_cn"
                    )


                    st.markdown(
                        f"""
                        <div class="answer-text">
                            你的答案：
                            <b>
                            {html.escape(
                                st.session_state.last_answer
                            )}
                            </b>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    st.markdown(
                        f"""
                        <div class="answer-text">
                            正确答案：
                            <b>
                            {html.escape(
                                last_word["chinese"]
                            )}
                            </b>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                # ==========================================
                # 判断
                # ==========================================

                if st.session_state.last_correct:

                    st.success(
                        "正确",
                        icon="✅"
                    )

                else:

                    st.error(
                        "错误",
                        icon="❌"
                    )


                    # ======================================
                    # 近义词
                    # ======================================

                    if st.button(
                        "我的答案也是近义词 ✓",
                        key="similar_answer",
                        use_container_width=True
                    ):

                        # 撤销之前的错误
                        last_word["wrong"] = max(
                            0,
                            int(last_word["wrong"]) - 1
                        )


                        # 增加正确
                        last_word["correct"] = (
                            int(last_word["correct"]) + 1
                        )


                        # 降低权重
                        last_word["weight"] = max(
                            1,
                            int(last_word["weight"]) - 2
                        )


                        # 立即保存
                        save_words()


                        st.session_state.last_correct = True


                        st.rerun()


        # ====================================================
        # 右边：下一题
        # ====================================================

        with right:

            st.markdown(
                "### 下一题"
            )


            # ==============================================
            # 中译英
            # ==============================================

            if question_type == "中译英":

                st.markdown(
                    f"""
                    <div class="question">
                        {html.escape(
                            word["chinese"]
                        )}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # ==============================================
            # 英译中
            # ==============================================

            else:

                st.markdown(
                    f"""
                    <div class="question">
                        {html.escape(
                            word["english"]
                        )}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


                pronunciation_button(
                    word["english"],
                    "current_sound"
                )


            # ==============================================
            # 输入答案
            # ==============================================

            with st.form(
                key="answer_form",
                clear_on_submit=True
            ):

                answer = st.text_input(
                    "答案",
                    label_visibility="collapsed",
                    placeholder="输入答案后按 Enter",
                    autocomplete="off"
                )


                submitted = st.form_submit_button(
                    "提交",
                    use_container_width=True
                )


            # ==============================================
            # 判断
            # ==============================================

            if submitted:

                answer = answer.strip()


                # ==========================================
                # 中译英
                # ==========================================

                if question_type == "中译英":

                    correct_answer = (
                        word["english"]
                        .strip()
                        .lower()
                    )

                    user_answer = (
                        answer
                        .strip()
                        .lower()
                    )


                # ==========================================
                # 英译中
                # ==========================================

                else:

                    correct_answer = (
                        word["chinese"]
                        .strip()
                    )

                    user_answer = (
                        answer
                        .strip()
                    )


                # ==========================================
                # 正确
                # ==========================================

                if user_answer == correct_answer:

                    word["correct"] = (
                        int(word["correct"]) + 1
                    )


                    word["weight"] = max(
                        1,
                        int(word["weight"]) - 1
                    )


                    is_correct = True


                # ==========================================
                # 错误
                # ==========================================

                else:

                    word["wrong"] = (
                        int(word["wrong"]) + 1
                    )


                    word["weight"] = min(
                        20,
                        int(word["weight"]) + 2
                    )


                    is_correct = False


                # ==========================================
                # ★ 立即永久保存
                # ==========================================

                save_success = save_words()


                # ==========================================
                # 保存上一题
                # ==========================================

                st.session_state.last_word_index = (
                    current_index
                )


                st.session_state.last_answer = (
                    answer
                )


                st.session_state.last_correct = (
                    is_correct
                )


                # ==========================================
                # 随机下一题
                # ==========================================

                next_word = get_random_word()


                if next_word is not None:

                    st.session_state.current_word_index = (
                        words.index(next_word)
                    )


                # ==========================================
                # 如果保存失败
                # ==========================================

                if not save_success:

                    st.error(
                        "⚠️ 数据保存失败，请检查 vocabulary.json 权限。"
                    )


                # ==========================================
                # 刷新
                # ==========================================

                st.rerun()


        # ====================================================
        # 底部统计
        # ====================================================

        st.divider()


        # 重新读取文件
        # 确保统计来自永久数据

        saved_words = load_words()


        total_correct = sum(
            int(w.get("correct", 0))
            for w in saved_words
        )


        total_wrong = sum(
            int(w.get("wrong", 0))
            for w in saved_words
        )


        total_answered = (
            total_correct
            + total_wrong
        )


        col1, col2 = st.columns(2)


        col1.metric(
            "答数",
            total_answered
        )


        col2.metric(
            "正确",
            total_correct
        )