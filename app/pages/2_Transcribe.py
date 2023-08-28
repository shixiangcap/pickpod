# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import os
import time

import my_task
import streamlit as st
from dotenv import find_dotenv, load_dotenv
from Home import LIBRARY_PATH
from pydub import AudioSegment

from pickpod.config import YDL_OPTIONS, TaskConfig
from pickpod.doc import AudioDocument
from pickpod.utils import PickpodUtils


os.chdir(os.path.split(os.path.realpath(__file__))[0])

# load from env
load_dotenv(find_dotenv(), override=True)
HUGGING_FACE_KEY = os.getenv("HUGGING_FACE_KEY")
CLAUDE_KEY = os.getenv("CLAUDE_KEY")


st.set_page_config(
    page_title="Pickpod Transcribe",
    page_icon="../library/logo.png",
    menu_items={
        "Get Help": "https://github.com/shixiangcap/pickpod",
        "Report a bug": "https://github.com/shixiangcap/pickpod",
        "About": "### Pickpod 是一个基于 `Streamlit` 框架构建的网络服务：\n\n### 它根据您自己的`非共识观点`为您推荐播客。"
    }
)

if "flag_start" not in st.session_state:
    st.session_state.flag_start = False
    st.session_state.pp_url_list = list()
    st.session_state.pp_upload_list = list()

def run():

    with st.sidebar:

        pp_origin = st.selectbox("需要转录的音频来源", (1, 0), index=0, format_func=lambda x: "网络" if x else "本地", help="请选择您需要转录的音频是来自网络还是本地文件。", disabled=st.session_state.flag_start)

        pp_language = st.text_input("转录目标语言", help="若不指定，模型将在播客节目的前30秒内自动检测语言。可选语言代码可参考：https://github.com/openai/whisper/blob/main/whisper/tokenizer.py", disabled=st.session_state.flag_start)

        pp_prompt = st.text_input("模型提示", help="您可以输入一段文字以给予转录模型一定提示。", disabled=st.session_state.flag_start)

        pp_pipeline = st.selectbox("执行声纹分割聚类", (True, False), index=0, format_func=lambda x: "是" if x else "否", help="是否对于音频文件执行声纹分割聚类以识别说话人。", disabled=st.session_state.flag_start)

        pp_keyword = st.selectbox("执行文稿关键词提取", (True, False), index=0, format_func=lambda x: "是" if x else "否", help="是否对于转录的文稿提取关键词。", disabled=st.session_state.flag_start)

        pp_summary = st.selectbox("执行文稿摘要提取", (True, False), index=0, format_func=lambda x: "是" if x else "否", help="是否对于转录的文稿提取带有时间戳的摘要。", disabled=st.session_state.flag_start)

        pp_view = st.selectbox("执行文稿观点提取", (True, False), index=0, format_func=lambda x: "是" if x else "否", help="是否对于转录的文稿提取其所表述的观点。", disabled=st.session_state.flag_start)

        if pp_origin:

            pp_url_list = st.text_area("网络视频链接", help="请在每行输入一个链接用以获取来自网络的音频。", placeholder="例如：\nhttps://www.youtube.com/watch?v=xxxxxxxx\nhttps://www.bilibili.com/video/xxxxxxxx/", disabled=st.session_state.flag_start)
            pp_url_list = [x for x in pp_url_list.split("\n") if x]
            if len(pp_url_list) > len(st.session_state.pp_url_list):
                st.session_state.pp_url_list = pp_url_list

        else:

            pp_upload_list = st.file_uploader("上传本地音频文件", ["m4a", "mp3", "wav", "mp4"], True, help="您可以上传一个或多个符合格式要求的本地音频文件。", disabled=st.session_state.flag_start)
            pp_upload_list = [(x.name, x.getvalue()) for x in pp_upload_list if x]
            if len(pp_upload_list) > len(st.session_state.pp_upload_list):
                st.session_state.pp_upload_list = pp_upload_list

        button_start, button_restart = st.columns([1, 1])

        with button_start:
            click_start=st.button("开始任务", help="Pickpod 将开始为您转录音频文稿，这将花费一定时间。", use_container_width=True, disabled=st.session_state.flag_start)

        with button_restart:
            click_restart= st.button("刷新页面", help="您可以单击右上角“Stop”按钮以立即停止本次任务，也可以通过此按钮停止任务并刷新页面，Pickpod 将仅保存已完成的部分数据", use_container_width=True, disabled=not st.session_state.flag_start)

    st.write("# 执行 Pickpod 音频转录 🎤")

    if click_start and not click_restart:

        st.session_state.flag_start = True

        st.experimental_rerun()

    elif not click_start and click_restart:

        st.session_state.flag_start = False

        st.session_state.pp_url_list = list()

        st.session_state.pp_upload_list = list()

        st.experimental_rerun()

    if st.session_state.flag_start:

        if (pp_origin and len(st.session_state.pp_url_list) == 0) or (not pp_origin and len(st.session_state.pp_upload_list) == 0):

            st.warning("未检测到符合条件的音频来源", icon="⚠️")

        elif pp_origin and len(st.session_state.pp_url_list) > 0:

            for web_url in st.session_state.pp_url_list:
                with st.expander(f"任务链接：{web_url}"):
                    task_config = TaskConfig(
                        key_hugging_face=HUGGING_FACE_KEY,
                        key_claude=CLAUDE_KEY,
                        ydl_path=LIBRARY_PATH,
                        task_language=pp_language,
                        task_prompt=pp_prompt,
                        pipeline=pp_pipeline,
                        keyword=pp_keyword,
                        summary=pp_summary,
                        view=pp_view,
                        )

                    st.caption("1⃣️ 存储音频文件到本地", unsafe_allow_html=False)
                    start_time = time.time()
                    audio_doc = AudioDocument(audio_web=web_url, audio_url=web_url, audio_origin="网络")
                    YDL_OPTIONS["outtmpl"] = f"{LIBRARY_PATH}/audio/{audio_doc.uuid}.%(ext)s"
                    PickpodUtils.pickpod_ytdlp(audio_doc, YDL_OPTIONS)
                    st.info(f"ℹ️ 音频文件下载完成，用时：{time.time() - start_time} 秒")

                    my_task.my_pickpod_task(audio_doc, task_config)

            PickpodUtils.static_clean()
            st.success("所有音频已转录完成，您可以前往“Gallery”页查看", icon="✅")
            st.session_state.pp_url_list = list()

        elif not pp_origin and len(st.session_state.pp_upload_list) > 0:

            for upload_file in st.session_state.pp_upload_list:
                with st.expander(f"文件名：{upload_file[0]}"):
                    task_config = TaskConfig(
                        key_hugging_face=HUGGING_FACE_KEY,
                        key_claude=CLAUDE_KEY,
                        ydl_path=LIBRARY_PATH,
                        task_language=pp_language,
                        task_prompt=pp_prompt,
                        pipeline=pp_pipeline,
                        keyword=pp_keyword,
                        summary=pp_summary,
                        view=pp_view,
                        )

                    st.caption("1⃣️ 存储音频文件到本地", unsafe_allow_html=False)
                    start_time = time.time()
                    audio_title, audio_ext = os.path.splitext(upload_file[0])
                    audio_doc = AudioDocument(audio_title=audio_title, audio_ext=audio_ext[1:], audio_origin="本地")
                    audio_doc.path = f"{LIBRARY_PATH}/audio/{audio_doc.uuid}.{audio_doc.ext}"
                    with open(audio_doc.path, "wb") as f:
                        f.write(upload_file[1])
                    audio_doc.length = len(AudioSegment.from_file(audio_doc.path)) / 1000
                    st.info(f"ℹ️ 音频文件下载完成，用时：{time.time() - start_time} 秒")

                    my_task.my_pickpod_task(audio_doc, task_config)

            PickpodUtils.static_clean()
            st.success("所有音频已转录完成，您可以前往“Gallery”页查看", icon="✅")
            st.session_state.pp_upload_list = list()

        st.session_state.flag_start = False

    elif not st.session_state.flag_start:

        st.info("ℹ️ 请先制定您的任务参数")


if __name__ == "__main__":
    run()
