# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit.logger import get_logger


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


def index() -> [pd.DataFrame, dict]:

    with open("./library/index.txt", "r") as f:
        df_index = [y.replace("\n", "") for x, y in enumerate(f.readlines()) if x < 10 and y != ""]

    df_config = {
        "title": st.column_config.TextColumn("音频标题", width="large"),
        "url": st.column_config.LinkColumn("原始链接", width="medium"),
        "length": st.column_config.NumberColumn("音频时长", width="small", format="%.3f 秒",),
        "path": st.column_config.LinkColumn("在本地浏览器中打开", width="medium"),
        "ctime": st.column_config.DatetimeColumn("创建时间", width="medium"),
    }

    df_dict = {x: list() for x in df_config.keys()}

    for df_name in df_index:
        with open(f"./library/doc/{df_name}.json", "r", encoding="utf-8") as f:
            df_json = json.load(f)
            df_dict["title"].append(df_json.get("title"))
            df_dict["url"].append(df_json.get("url"))
            df_dict["length"].append(df_json.get("length"))
            df_dict["path"].append(f'''file://{df_json.get("path")}''')
            df_dict["ctime"].append(datetime.utcfromtimestamp(df_json.get("ctime")).strftime("%Y-%m-%d %H:%M:%S"))

    df = pd.DataFrame(df_dict)

    return df, df_config


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

    st.markdown("以下是 **Pickpod** 为您最新精选的播客：")

    df_data, df_config = index()

    st.dataframe(df_data, use_container_width=True, hide_index=True, column_config=df_config)

    # TODO: Pickpod 为您最新精选的播客将依据其阐述观点对您个人的价值来排序
    # TODO: 您也可以通过交互来重新评估观点的价值


if __name__ == "__main__":
    run()
