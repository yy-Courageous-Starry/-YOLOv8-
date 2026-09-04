import os
import time

import pymysql
import streamlit as st

from ultralytics import YOLO

# ========== 页面配置 ==========
st.set_page_config(page_title="道路坑洞智能检测系统", page_icon="🛣️", layout="wide", initial_sidebar_state="expanded")


# ========== 灰蓝配色像素风 CSS（含白色高亮） ==========
def inject_pixel_css():
    st.markdown(
        """
    <style>
    /* 全局灰蓝像素风 */
    @import url('https://fonts.googleapis.com/css2?family=Press+Start-2P&family=VT323&display=swap');

    html, body, .stApp {
        background-color: #1e2a36;
        background-image: 
            linear-gradient(rgba(100, 150, 200, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(100, 150, 200, 0.05) 1px, transparent 1px);
        background-size: 20px 20px;
        font-family: 'VT323', monospace;
    }

    /* 灰蓝色标题 */
    h1, h2, h3, .stTitle, .stSubheader {
        font-family: 'Press Start 2P', monospace !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 2px 2px 0px #2c4c6c, -1px -1px 0px #8aacc8;
        color: #c0d9f0 !important;
    }

    /* 灰蓝边框和按钮 */
    .stButton > button, .stFormSubmitButton > button, button[kind="primary"] {
        font-family: 'Press Start 2P', monospace !important;
        background: #1e2a36 !important;
        color: #a0c0e0 !important;
        border: 2px solid #4a6f8f !important;
        border-radius: 0px !important;
        box-shadow: 3px 3px 0px #2c4c6c !important;
        transition: 0.05s linear !important;
        font-size: 12px !important;
        padding: 8px 16px !important;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        background: #4a6f8f !important;
        color: #ffffff !important;
        box-shadow: 1px 1px 0px #2c4c6c !important;
        transform: translate(2px, 2px);
    }

    /* 输入框灰蓝风格 */
    .stTextInput > div > div > input, .stTextInput > div > div > input:focus {
        background-color: #1a2530 !important;
        border: 2px solid #6c8eb0 !important;
        border-radius: 0px !important;
        font-family: 'VT323', monospace !important;
        font-size: 18px !important;
        color: #b8d4f0 !important;
        box-shadow: none !important;
    }

    /* 文件上传器灰蓝风 */
    .stFileUploader > div > div > button {
        background: #1e2a36 !important;
        border: 2px solid #6c8eb0 !important;
        border-radius: 0px !important;
        font-family: 'Press Start 2P', monospace !important;
        color: #a0c0e0 !important;
    }
    .stFileUploader > div > div > button:hover {
        background: #4a6f8f !important;
        color: #ffffff !important;
    }

    /* 侧边栏灰蓝半透明 */
    .css-1d391kg, .stSidebar {
        background-color: rgba(30, 42, 54, 0.95) !important;
        border-right: 3px solid #4a6f8f !important;
        backdrop-filter: blur(4px);
    }

    /* Expander 灰蓝风格 */
    .streamlit-expanderHeader {
        font-family: 'Press Start 2P', monospace !important;
        background-color: #1e2a36 !important;
        border: 2px solid #4a6f8f !important;
        border-radius: 0px !important;
        color: #a0c0e0 !important;
    }
    .streamlit-expanderContent {
        border-left: 2px solid #4a6f8f !important;
        border-right: 2px solid #4a6f8f !important;
        border-bottom: 2px solid #4a6f8f !important;
        background-color: #1a2530 !important;
    }

    /* 像素方框容器 (灰蓝边框) */
    .pixel-frame {
        border: 4px solid #6c8eb0;
        padding: 10px;
        background: #1a2530aa;
        box-shadow: 6px 6px 0px 0px #2c4c6c;
        margin: 10px 0px;
        transition: 0.1s linear;
        image-rendering: pixelated;
        image-rendering: crisp-edges;
    }
    .pixel-frame img {
        display: block;
        margin: 0 auto;
        border: none;
        image-rendering: pixelated;
    }

    /* 状态栏灰蓝风格 */
    .stAlert, .stSuccess, .stError, .stInfo {
        border-radius: 0px !important;
        font-family: 'VT323', monospace !important;
        font-size: 18px !important;
        border-left: 8px solid #6c8eb0 !important;
        background-color: #1a2530 !important;
        color: #c0d9f0 !important;
    }

    /* 进度状态灰蓝 */
    .stStatus {
        background-color: #1e2a36 !important;
        border: 2px solid #4a6f8f !important;
        color: #a0c0e0 !important;
    }

    hr {
        border-top: 2px dashed #4a6f8f;
    }

    /* ===== 白色高亮突出显示 ===== */
    .stTextInput label,
    .stFileUploader label,
    .custom-white {
        color: #ffffff !important;
        font-weight: bold !important;
    }
    .highlight-text {
        color: #ffffff !important;
        font-weight: bold;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


# 注入css
inject_pixel_css()


# ========== 数据库连接（第一段代码） ==========
def get_db_connection():
    return pymysql.connect(
        host="localhost", user="root", password="Yuan13888057275", database="yolo26", charset="utf8mb4"
    )


def verify_user(username, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM user WHERE username = %s AND password = %s"
        cursor.execute(sql, (username, password))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except Exception as e:
        st.error(f"数据库连接错误：{e!s}")
        return False


# ========== 初始化 session_state ==========
if "is_login" not in st.session_state:
    st.session_state.is_login = False
if "login_username" not in st.session_state:
    st.session_state.login_username = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "home_page"

# ========== 路径 100% 使用第一段代码 ==========
UPLOAD_PATH = r"images/upload"
RESULT_PATH = r"images/result"
MODEL_PATH = r"runs/detect/train4/weights/best.pt"

os.makedirs(UPLOAD_PATH, exist_ok=True)
os.makedirs(RESULT_PATH, exist_ok=True)


# ========== 辅助函数: 带像素边框的图片显示 ==========
def display_with_pixel_frame(image, caption="", key=None):
    col_frame = st.container()
    with col_frame:
        st.markdown('<div class="pixel-frame">', unsafe_allow_html=True)
        st.image(image, caption=caption, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)


# ========== 登录页面（数据库验证） ==========
def login_page():
    _col1, col2, _col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 登录终端")
        st.markdown("---")
        with st.form("login_form"):
            username = st.text_input("账号", key="login_user", placeholder="请输入管理员账号")
            password = st.text_input("密码", type="password", key="login_pass", placeholder="请输入登录密码")
            submit = st.form_submit_button("登录系统", use_container_width=True)

            if submit:
                if verify_user(username, password):
                    st.session_state.is_login = True
                    st.session_state.login_username = username
                    succ = st.success("登录成功，跳转中...")
                    time.sleep(1)
                    succ.empty()
                    st.rerun()
                else:
                    err = st.error("账号或密码错误")
                    time.sleep(1.5)
                    err.empty()

        st.markdown(
            """
        <div style='text-align:center; margin-top:30px; padding-top:10px; border-top:1px dashed #4a6f8f;'>
            <span style='color:#8aacc8; font-family:VT323; font-size:16px;'>小组成员： 袁源 | 王梓越 | 高睿  </span><br>
            <span style='color:#8aacc8; font-family:VT323; font-size:16px;'> 杨欣子 | 贺紫妍 | 铁盛达 </span><br>
        </div>
        """,
            unsafe_allow_html=True,
        )


# ========== 系统首页 ==========
def home_page():
    st.markdown("## 坑洞检测系统")
    st.markdown("---")
    st.markdown(f"### 欢迎回来，用户  {st.session_state.login_username}")
    st.markdown(
        """
    <div style="background:#1a2530; border:2px solid #4a6f8f; padding:12px; font-family:VT323; color:#ffffff; font-weight:bold;">
    系统已就绪，请前往左侧菜单进行图片检测
    </div>
    """,
        unsafe_allow_html=True,
    )


# ========== 图片检测页面（路径完全使用第一段） ==========
def img_detect_page():
    st.markdown("## 图片检测")
    st.markdown('<span class="custom-white"> 上传图片，启动检测</span>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("选择图片文件", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

    if uploaded_file is not None:
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown('<h3 class="custom-white">待检测图片</h3>', unsafe_allow_html=True)
            display_with_pixel_frame(uploaded_file, caption="待检测源影像")

        detect_btn = st.button("开始检测", type="primary", use_container_width=True)

        if detect_btn:
            with st.status("启动检测...", expanded=True) as status:
                try:
                    # ======================
                    # 路径 100% 第一段
                    # ======================
                    status.info("💾 图像保存中...")
                    filename = str(int(time.time())) + ".jpg"
                    save_path = os.path.join(UPLOAD_PATH, filename)

                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getvalue())

                    status.success("✅ 图像已保存")
                    status.info("🤖 加载YOLO检测模型...")

                    # 模型路径也用第一段
                    model = YOLO(MODEL_PATH)

                    status.info("🔍 正在进行坑洞检测...")
                    results = model.predict(source=save_path)

                    status.success("✅ 检测完成，生成结果中...")
                    detect_result_path = results[0].save(filename=os.path.join(RESULT_PATH, filename))

                    with col_right:
                        st.markdown('<h3 class="custom-white">检测结果</h3>', unsafe_allow_html=True)
                        display_with_pixel_frame(detect_result_path, caption="检测区域")

                    status.update(label="🎉 检测任务已完成！", state="complete", expanded=False)

                except Exception as e:
                    status.update(label=f"检测失败: {e!s}", state="error")
                    st.error("检测失败，请检查图像或模型配置")
    else:
        st.info("等待上传图像...")


# ========== 后台主页面 ==========
def index_page():
    with st.sidebar:
        st.markdown("## 导览栏")
        st.markdown("---")
        with st.expander("系统管理", expanded=True):
            if st.button("系统首页", key="nav_home", use_container_width=True):
                st.session_state.current_page = "home_page"
                st.rerun()
        with st.expander("检测功能", expanded=True):
            if st.button("图片检测", key="nav_img", use_container_width=True):
                st.session_state.current_page = "img_detect_page"
                st.rerun()
        st.markdown("---")
        if st.button("退出账号", use_container_width=True):
            st.session_state.is_login = False
            st.session_state.login_username = None
            st.rerun()

    page_map = {
        "home_page": home_page,
        "img_detect_page": img_detect_page,
    }
    page_map[st.session_state.current_page]()


# ========== 主入口 ==========
if st.session_state.is_login:
    index_page()
else:
    login_page()
