import streamlit as st
import json
import random
import base64
import html
import urllib.request
import urllib.error
from datetime import datetime
from zoneinfo import ZoneInfo


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
# GitHub 设置
# ============================================================

GITHUB_USERNAME = "ojoj0307"

GITHUB_REPOSITORY = "english-vocabulary"

GITHUB_VOCABULARY_PATH = "vocabulary.json"

GITHUB_DAILY_STATS_PATH = "daily_stats.json"

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

GITHUB_API_BASE = (
    f"https://api.github.com/repos/"
    f"{GITHUB_USERNAME}/"
    f"{GITHUB_REPOSITORY}/contents/"
)


# ============================================================
# 马来西亚时区
# ============================================================

MALAYSIA_TZ = ZoneInfo("Asia/Kuala_Lumpur")


# ============================================================
# 词性
# ============================================================

CATEGORIES = [
    "noun",
    "verb",
    "adjective",
    "adverb"
]


# ============================================================
# GitHub API
# ============================================================

def github_request(
    url,
    method="GET",
    data=None
):

    try:

        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "English-Vocabulary-App"
        }

        if data is not None:

            body = json.dumps(
                data
            ).encode("utf-8")

            headers["Content-Type"] = (
                "application/json"
            )

        else:

            body = None


        request = urllib.request.Request(
            url,
            data=body,
            headers=headers,
            method=method
        )


        with urllib.request.urlopen(
            request,
            timeout=20
        ) as response:

            response_data = response.read()

            if not response_data:
                return {}

            return json.loads(
                response_data.decode("utf-8")
            )


    except urllib.error.HTTPError as e:

        try:

            error_body = e.read().decode(
                "utf-8"
            )

            error_data = json.loads(
                error_body
            )

            error_message = error_data.get(
                "message",
                str(e)
            )

        except Exception:

            error_message = str(e)


        st.error(
            f"GitHub API 错误：{error_message}"
        )

        return None


    except Exception as e:

        st.error(
            f"连接 GitHub 失败：{e}"
        )

        return None


# ============================================================
# 从 GitHub 读取 JSON
# ============================================================

def load_json_from_github(
    file_path,
    default_data
):

    url = (
        GITHUB_API_BASE
        + file_path
    )


    result = github_request(
        url,
        method="GET"
    )


    if result is None:

        return default_data


    if "content" not in result:

        return default_data


    try:

        content = result["content"]

        content = content.replace(
            "\n",
            ""
        )

        decoded = base64.b64decode(
            content
        ).decode(
            "utf-8"
        )

        return json.loads(
            decoded
        )


    except Exception as e:

        st.error(
            f"读取 {file_path} 失败：{e}"
        )

        return default_data


# ============================================================
# 写入 GitHub JSON
# ============================================================

def save_json_to_github(
    file_path,
    data,
    commit_message
):

    url = (
        GITHUB_API_BASE
        + file_path
    )


    # ========================================================
    # 先取得 GitHub 当前文件的 SHA
    # ========================================================

    existing = github_request(
        url,
        method="GET"
    )


    if existing is None:

        return False


    sha = existing.get(
        "sha"
    )


    # ========================================================
    # JSON → UTF-8 → Base64
    # ========================================================

    json_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=4
    )


    encoded_content = base64.b64encode(
        json_text.encode("utf-8")
    ).decode("utf-8")


    payload = {
        "message": commit_message,
        "content": encoded_content
    }


    # 修改已有文件需要 SHA
    if sha:

        payload["sha"] = sha


    # ========================================================
    # 写回 GitHub
    # ========================================================

    result = github_request(
        url,
        method="PUT",
        data=payload
    )


    if result is None:

        return False


    if "content" not in result:

        st.error(
            "GitHub 没有成功保存文件。"
        )

        return False


    return True


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.block-container {
    padding-top: 2.5rem;
    padding-bottom: 0.5rem;
    max-width: 1150px;
}


/* ==========================================================
   标题
   ========================================================== */

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


/* ==========================================================
   Sidebar
   ========================================================== */

section[data-testid="stSidebar"]
div[role="radiogroup"]
label {

    font-size: 19px !important;
    font-weight: 600 !important;

    padding-top: 8px !important;
    padding-bottom: 8px !important;
}


section[data-testid="stSidebar"] p {

    font-size: 18px !important;
    font-weight: 600 !important;
}


/* ==========================================================
   问题
   ========================================================== */

.question {

    font-size: 30px;

    font-weight: 600;

    text-align: center;

    margin: 8px 0 6px 0;

    word-break: break-word;
}


/* ==========================================================
   问题词性
   ========================================================== */

.question-category {

    font-size: 17px;

    font-weight: 500;

    text-align: center;

    margin-bottom: 12px;

    opacity: 0.75;
}


/* ==========================================================
   上一题
   ========================================================== */

.previous-question {

    font-size: 24px;

    font-weight: 600;

    text-align: center;

    margin: 8px 0 6px 0;

    word-break: break-word;
}


.previous-category {

    font-size: 16px;

    font-weight: 500;

    text-align: center;

    margin-bottom: 12px;

    opacity: 0.75;
}


/* ==========================================================
   答案
   ========================================================== */

.answer-text {

    font-size: 16px;

    margin: 5px 0;

    word-break: break-word;
}


/* ==========================================================
   输入框
   ========================================================== */

div[data-testid="stTextInput"] input {

    font-size: 18px;

    height: 42px;
}


/* ==========================================================
   按钮
   ========================================================== */

div.stButton > button {

    min-height: 38px;

    font-size: 15px;
}


/* ==========================================================
   手机
   ========================================================== */

@media (max-width: 700px) {

    .block-container {

        padding-top: 2.5rem;
    }


    .question {

        font-size: 25px;
    }


    .question-category {

        font-size: 16px;
    }


    .previous-question {

        font-size: 21px;
    }


    .previous-category {

        font-size: 15px;
    }


    section[data-testid="stSidebar"]
    div[role="radiogroup"]
    label {

        font-size: 18px !important;
    }

}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 读取词库
# ============================================================

def load_words():

    data = load_json_from_github(
        GITHUB_VOCABULARY_PATH,
        []
    )


    if not isinstance(data, list):

        return []


    changed = False


    # ========================================================
    # 修复旧数据
    # ========================================================

    for word in data:

        if "english" not in word:

            word["english"] = ""

            changed = True


        if "chinese" not in word:

            word["chinese"] = ""

            changed = True


        if "category" not in word:

            word["category"] = "noun"

            changed = True


        if word.get("category") not in CATEGORIES:

            word["category"] = "noun"

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


    # ========================================================
    # 如果旧 JSON 没有 category 等资料
    # 自动同步回 GitHub
    # ========================================================

    if changed:

        save_json_to_github(
            GITHUB_VOCABULARY_PATH,
            data,
            "Update vocabulary data"
        )


    return data


# ============================================================
# 当前词库
# ============================================================

words = load_words()


# ============================================================
# 保存词库
# ============================================================

def save_words():

    return save_json_to_github(
        GITHUB_VOCABULARY_PATH,
        words,
        "Update vocabulary"
    )


# ============================================================
# 当前日期
# ============================================================

def get_today():

    return datetime.now(
        MALAYSIA_TZ
    ).strftime(
        "%Y-%m-%d"
    )


# ============================================================
# 每日统计默认值
# ============================================================

def get_default_daily_stats():

    return {
        "date": get_today(),
        "answered": 0,
        "correct": 0
    }


# ============================================================
# 读取每日统计
# ============================================================

def load_daily_stats():

    data = load_json_from_github(
        GITHUB_DAILY_STATS_PATH,
        get_default_daily_stats()
    )


    if not isinstance(
        data,
        dict
    ):

        data = get_default_daily_stats()


    today = get_today()


    # ========================================================
    # 日期改变 → 清零
    # ========================================================

    if data.get("date") != today:

        data = get_default_daily_stats()

        save_daily_stats(
            data
        )


    return data


# ============================================================
# 保存每日统计
# ============================================================

def save_daily_stats(data):

    return save_json_to_github(
        GITHUB_DAILY_STATS_PATH,
        data,
        "Update daily statistics"
    )


# ============================================================
# 每日统计
# ============================================================

daily_stats = load_daily_stats()


# ============================================================
# 计算概率
# ============================================================

def calculate_probability(word):

    if not words:

        return 0


    total_weight = sum(

        max(
            1,
            int(
                item.get(
                    "weight",
                    3
                )
            )
        )

        for item in words
    )


    if total_weight == 0:

        return 0


    current_weight = max(
        1,
        int(
            word.get(
                "weight",
                3
            )
        )
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
            int(
                word.get(
                    "weight",
                    3
                )
            )
        )

        for word in words
    ]


    return random.choices(
        words,
        weights=weights,
        k=1
    )[0]


# ============================================================
# 浏览器发音
# ============================================================

def pronunciation_button(
    text,
    key
):

    encoded = base64.b64encode(
        str(text).encode(
            "utf-8"
        )
    ).decode(
        "ascii"
    )


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
                new SpeechSynthesisUtterance(
                    text
                );


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

st.title(
    "📚 English Vocabulary"
)


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

    st.header(
        "📚 词库管理"
    )


    # ========================================================
    # 添加
    # ========================================================

    st.subheader(
        "➕ 添加单词"
    )


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


    category = st.selectbox(
        "词性",
        CATEGORIES,
        index=0
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


        elif len(english_list) != len(
            chinese_list
        ):

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

                # ==================================================
                # 英文 + 中文 + 词性
                # 三项全部相同才算重复
                # ==================================================

                exists = any(

                    item["english"].strip().lower()
                    == english.strip().lower()

                    and

                    item["chinese"].strip()
                    == chinese.strip()

                    and

                    item.get(
                        "category",
                        "noun"
                    )
                    == category

                    for item in words
                )


                if exists:

                    duplicate += 1


                else:

                    words.append(
                        {
                            "english": english,
                            "chinese": chinese,
                            "category": category,
                            "weight": 3,
                            "correct": 0,
                            "wrong": 0
                        }
                    )

                    added += 1


            # ====================================================
            # 写入 GitHub
            # ====================================================

            if save_words():

                st.success(
                    f"成功添加 {added} 个单词，并已保存到 GitHub。"
                )


                if duplicate:

                    st.info(
                        f"{duplicate} 个完全相同的单词没有添加。"
                    )


    st.divider()


    # ========================================================
    # 编辑
    # ========================================================

    st.subheader(
        "✏️ 编辑词库"
    )


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

            f"{word['english']} → "
            f"{word['chinese']} "
            f"({word.get('category', 'noun')})"

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


            new_category = st.selectbox(
                "词性",
                CATEGORIES,

                index=CATEGORIES.index(
                    word.get(
                        "category",
                        "noun"
                    )
                )

                if word.get(
                    "category",
                    "noun"
                ) in CATEGORIES

                else 0,

                key=f"edit_category_{index}"
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

                    new_english = (
                        new_english.strip()
                    )

                    new_chinese = (
                        new_chinese.strip()
                    )


                    if not new_english:

                        st.warning(
                            "英文不能为空。"
                        )

                        st.stop()


                    if not new_chinese:

                        st.warning(
                            "中文不能为空。"
                        )

                        st.stop()


                    # ==================================================
                    # 检查修改后是否与其他词条重复
                    # ==================================================

                    duplicate = False


                    for other_index, other_word in enumerate(
                        words
                    ):

                        if other_index == index:

                            continue


                        if (

                            other_word["english"]
                            .strip()
                            .lower()

                            ==

                            new_english
                            .lower()

                            and

                            other_word["chinese"]
                            .strip()

                            ==

                            new_chinese

                            and

                            other_word.get(
                                "category",
                                "noun"
                            )

                            ==

                            new_category

                        ):

                            duplicate = True

                            break


                    if duplicate:

                        st.error(
                            "修改后的单词与现有词条重复。"
                        )

                        st.stop()


                    word["english"] = (
                        new_english
                    )

                    word["chinese"] = (
                        new_chinese
                    )

                    word["category"] = (
                        new_category
                    )


                    if save_words():

                        st.success(
                            "修改成功，已同步到 GitHub。"
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

                        st.success(
                            "删除成功，已同步到 GitHub。"
                        )

                        st.rerun()


# ============================================================
#
# 查看词库
#
# ============================================================

elif page == "📖 查看词库":

    st.header(
        "📖 我的词库"
    )


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

                filtered_words.append(
                    word
                )

            elif (

                search.lower()
                in word["english"].lower()

                or

                search
                in word["chinese"]

            ):

                filtered_words.append(
                    word
                )


        st.caption(
            f"找到 {len(filtered_words)} 个单词"
        )


        col1, col2, col3, col4, col5, col6, col7 = st.columns(
            [2, 2, 1.2, 1, 1.3, 0.7, 0.7]
        )


        col1.write("**英文**")

        col2.write("**中文**")

        col3.write("**词性**")

        col4.write("**权重**")

        col5.write("**概率**")

        col6.write("**✓**")

        col7.write("**✗**")


        st.divider()


        for word in filtered_words:

            col1, col2, col3, col4, col5, col6, col7 = st.columns(
                [2, 2, 1.2, 1, 1.3, 0.7, 0.7]
            )


            col1.write(
                word["english"]
            )


            col2.write(
                word["chinese"]
            )


            col3.write(
                word.get(
                    "category",
                    "noun"
                )
            )


            col4.write(
                word["weight"]
            )


            col5.write(
                f"{calculate_probability(word):.2f}%"
            )


            col6.write(
                word["correct"]
            )


            col7.write(
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
        # 题型改变
        # ====================================================

        if (

            question_type
            != st.session_state.question_type

        ):

            st.session_state.question_type = (
                question_type
            )

            st.session_state.current_word_index = (
                None
            )

            st.session_state.last_word_index = (
                None
            )

            st.session_state.last_answer = (
                ""
            )

            st.session_state.last_correct = (
                None
            )


        # ====================================================
        # 防止 index 超出
        # ====================================================

        if (

            st.session_state.current_word_index
            is None

            or

            st.session_state.current_word_index
            >= len(words)

        ):

            selected_word = get_random_word()


            if selected_word is not None:

                st.session_state.current_word_index = (
                    words.index(
                        selected_word
                    )
                )


        current_index = (
            st.session_state.current_word_index
        )


        word = words[
            current_index
        ]


        current_category = word.get(
            "category",
            "noun"
        )


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

                last_word = words[
                    last_index
                ]


                last_category = (
                    last_word.get(
                        "category",
                        "noun"
                    )
                )


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

                        <div class="previous-category">
                            {html.escape(
                                last_category
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

                        <div class="previous-category">
                            {html.escape(
                                last_category
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

                        last_word["wrong"] = max(
                            0,
                            int(
                                last_word["wrong"]
                            ) - 1
                        )


                        last_word["correct"] = (
                            int(
                                last_word["correct"]
                            ) + 1
                        )


                        last_word["weight"] = max(
                            1,
                            int(
                                last_word["weight"]
                            ) - 2
                        )


                        # 保存到 GitHub
                        save_words()


                        # 今日正确数 +1
                        daily_stats["correct"] = (
                            int(
                                daily_stats.get(
                                    "correct",
                                    0
                                )
                            ) + 1
                        )


                        save_daily_stats(
                            daily_stats
                        )


                        st.session_state.last_correct = (
                            True
                        )


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

                    <div class="question-category">
                        {html.escape(
                            current_category
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

                    <div class="question-category">
                        {html.escape(
                            current_category
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
                # 答案不能为空
                # ==========================================

                if not answer:

                    st.warning(
                        "请输入答案后再提交。"
                    )

                    st.stop()


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
                        int(
                            word["correct"]
                        ) + 1
                    )


                    word["weight"] = max(
                        1,
                        int(
                            word["weight"]
                        ) - 1
                    )


                    is_correct = True


                # ==========================================
                # 错误
                # ==========================================

                else:

                    word["wrong"] = (
                        int(
                            word["wrong"]
                        ) + 1
                    )


                    word["weight"] = min(
                        20,
                        int(
                            word["weight"]
                        ) + 2
                    )


                    is_correct = False


                # ==========================================
                # 保存到 GitHub
                # ==========================================

                save_success = save_words()


                # ==========================================
                # 每日统计
                # ==========================================

                today = get_today()


                if daily_stats.get(
                    "date"
                ) != today:

                    daily_stats = {
                        "date": today,
                        "answered": 0,
                        "correct": 0
                    }


                daily_stats["answered"] = (

                    int(
                        daily_stats.get(
                            "answered",
                            0
                        )
                    )

                    + 1

                )


                if is_correct:

                    daily_stats["correct"] = (

                        int(
                            daily_stats.get(
                                "correct",
                                0
                            )
                        )

                        + 1

                    )


                save_daily_stats(
                    daily_stats
                )


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
                        words.index(
                            next_word
                        )
                    )


                # ==========================================
                # 保存失败
                # ==========================================

                if not save_success:

                    st.error(
                        "⚠️ GitHub 数据保存失败。"
                    )


                # ==========================================
                # 刷新
                # ==========================================

                st.rerun()


        # ====================================================
        # 底部每日统计
        # ====================================================

        st.divider()


        daily_stats = load_daily_stats()


        today_answered = int(
            daily_stats.get(
                "answered",
                0
            )
        )


        today_correct = int(
            daily_stats.get(
                "correct",
                0
            )
        )


        col1, col2 = st.columns(2)


        col1.metric(
            "今日答数",
            today_answered
        )


        col2.metric(
            "今日正确",
            today_correct
        )
