# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import json
import os
import time
from datetime import datetime
from typing import List

import streamlit as st
from streamlit.logger import get_logger

from pickpod.doc import ViewDocument


os.chdir(os.path.split(os.path.realpath(__file__))[0])

LOGGER = get_logger(__name__)

if not os.path.exists("./library/audio"):
    os.mkdir("./library/audio")

if not os.path.exists("./library/doc"):
    os.mkdir("./library/doc")

if not os.path.exists("./library/wav"):
    os.mkdir("./library/wav")

# 默认文件下载位置
LIBRARY_PATH = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir, "library"))


# TODO: Pickpod 为您最新精选的播客将依据其阐述观点对您个人的价值来排序
def index(df_index: List[str] = list()) -> None:

    for df_name in df_index:
        with open(f"{LIBRARY_PATH}/doc/{df_name}.json", "r", encoding="utf-8") as fr:
            df_json = json.load(fr)

            with st.expander(f"""**标题**：{df_json.get("title")}（{df_json.get("origin")}任务）\n\n**描述**：{df_json.get("description")}"""):

                st.caption(f"""基本信息""")

                col_tag, col_keywords = st.columns([1, 9])
                with col_tag:
                    st.markdown("**标签**：")
                with col_keywords:
                    st.markdown("; ".join(df_json.get("keywords")))

                st.markdown(f"""**原始链接**：[{df_json.get("web")}]({df_json.get("web")})""")

                col_length, col_ctime = st.columns([1, 1])
                with col_length:
                    st.markdown(f"""**音频时长**：{df_json.get("length")} 秒【[查看详情](/Gallery?uuid={df_json.get("uuid")})】""")
                with col_ctime:
                    st.markdown(f"""**创建时间**：{datetime.utcfromtimestamp(df_json.get("ctime")).strftime("%Y-%m-%d %H:%M:%S")}""")

                st.divider()

                st.caption("观点交互")

                pp_views_list = [ViewDocument(x.get("content"), x.get("mark")) for x in df_json.get("views")]

                for i, view_doc in enumerate(pp_views_list):
                    col_views_content, col_views_mark = st.columns([4, 1])
                    with col_views_content:
                        st.markdown(view_doc.content)
                    with col_views_mark:
                        view_doc.mark = st.toggle("是否有效", view_doc.mark, f"""{df_json.get("uuid")}_{i}""", "请评价音频中该条观点对您的价值")

            df_json["utime"] = int(time.time())
            df_json["views"] = [x.__dict__ for x in pp_views_list]
            with open(f"{LIBRARY_PATH}/doc/{df_name}.json", "w", encoding="utf-8") as fw:
                fw.write(json.dumps(df_json, indent=4, separators=(",", ": "), ensure_ascii=False))


def run() -> None:

    st.set_page_config(
        page_title="Pickpod Home",
        page_icon="./library/logo.png",
        menu_items={
            "Get Help": "https://github.com/shixiangcap/pickpod",
            "Report a bug": "https://github.com/shixiangcap/pickpod",
            "About": "### Pickpod 是一个基于 `Streamlit` 框架构建的网络服务：\n\n### 它根据您自己的`非共识观点`为您推荐播客。"
        }
    )

    st.write("# 欢迎使用 Pickpod 🏠")

    with open("./library/index.txt", "r") as f:
        df_index = [y.strip() for x, y in enumerate(f.readlines()) if x < 10 and y]

    if len(df_index):
        st.markdown("以下是 **Pickpod** 为您最新精选的播客：")
        index(df_index)
    else:
        st.info("ℹ️ **Pickpod** 暂未发现播客，您可以在简单[配置](/Configuration)后开始您的第一次[转录](/Transcribe)")


if __name__ == "__main__":
    run()
