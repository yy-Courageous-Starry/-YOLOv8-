# 使用streamlit构建web应用
# 1、导入streamlit库
import streamlit as st
import time
from ultralytics import YOLO
import pymysql
import os

# -------------------------- 初始化session_state --------------------------
if "is_login" not in st.session_state:
    st.session_state.is_login = False
if "login_username" not in st.session_state:
    st.session_state.login_username = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "home_page"


# -------------------------- 数据库连接 --------------------------
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Yuan13888057275",
        database="yolo26",
        charset="utf8mb4"
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
        st.error(f"数据库连接错误：{str(e)}")
        return False


# -------------------------- 登录页面 --------------------------
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("欢迎登录")
        with st.form("login_form"):
            username = st.text_input(label="账号", key="user_name", placeholder="请输入账号")
            password = st.text_input(label="密码", type="password", key="password", placeholder="请输入密码")
            submit_button = st.form_submit_button(label="登录", use_container_width=True)

            if submit_button:
                if verify_user(username, password):
                    st.session_state.is_login = True
                    st.session_state.login_username = username
                    msg = st.success("登录成功")
                    time.sleep(1)
                    msg.empty()
                    st.rerun()
                else:
                    msg = st.error("账号或密码错误")
                    time.sleep(2)
                    msg.empty()


# -------------------------- 系统首页 --------------------------
def home_page():
    st.title("欢迎使用我的检测系统")
    st.write("欢迎使用车牌/人脸检测系统")


# -------------------------- 图片检测页面 --------------------------
def img_detect_page():
    st.title("车牌检测页面-----图片")
    file_uploader = st.file_uploader(label="请选择图片", type=["jpg", "png", "jpeg"])

    if file_uploader is not None:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("待检测图片")
            st.image(image=file_uploader)

            if st.button(label="开始检测", type="primary"):
                with st.status(label="准备开始处理图片....", expanded=True) as status:
                    upload_path = r"D:\workspace\ynufe_yolo\images\upload"
                    result_path = r"D:\workspace\ynufe_yolo\images\result"
                    os.makedirs(upload_path, exist_ok=True)
                    os.makedirs(result_path, exist_ok=True)

                    status.info("准备开始把图片写入磁盘...")
                    filename = str(int(time.time())) + ".jpg"

                    with open(os.path.join(upload_path, filename), "wb") as f:
                        f.write(file_uploader.getvalue())

                    status.success("文件已经写入磁盘...")
                    status.info("正在加载YOLO车牌检测模型...")

                    model_path = r"D:\workspace\ynufe_yolo\runs\detect\train\weights\best.pt"
                    model = YOLO(model_path)

                    status.info("开始执行检测...")
                    results = model.predict(source=os.path.join(upload_path, filename))

                    status.success("检测完成，开始存储检测结果...")
                    detect_result_path = results[0].save(filename=os.path.join(result_path, filename))

                    status.success("检测结果存储成功...")
                    with col2:
                        st.subheader("检测结果图片...")
                        st.image(image=detect_result_path)
                        status.success("检测任务完成...")


# -------------------------- 页面路由 --------------------------
page_functions = {
    "home_page": home_page,
    "img_detect_page": img_detect_page,
}


def index_page():
    st.title("车牌检查系统")
    with st.sidebar:
        st.title("CC的车牌检查中心")
        username = st.session_state.login_username
        st.write(f"欢迎{username}使用")

        with st.expander("系统管理"):
            if st.button("系统首页", key="home_page", use_container_width=True):
                st.session_state.current_page = "home_page"
                st.rerun()

        with st.expander("车牌检测"):
            if st.button("图片检测", key="img_detect_page", use_container_width=True):
                st.session_state.current_page = "img_detect_page"
                st.rerun()

    # ✅ 这里是修复的关键！
    if "current_page" in st.session_state:
        page_functions[st.session_state.current_page]()


# -------------------------- 主程序 --------------------------
if st.session_state.is_login:
    index_page()
else:
    login_page()