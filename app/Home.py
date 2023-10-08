# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime
from typing import Dict, List

import streamlit as st
from dotenv import find_dotenv, load_dotenv
from streamlit.logger import get_logger

from pickpod.api import ClaudeClient
from pickpod.doc import *


os.chdir(os.path.split(os.path.realpath(__file__))[0])

# load from env
load_dotenv(find_dotenv("./pages/.env"), override=True)
CLAUDE_KEY = os.getenv("CLAUDE_KEY")

LOGGER = get_logger(__name__)

if not os.path.exists("./library/audio"):
    os.mkdir("./library/audio")

if not os.path.exists("./library/doc"):
    os.mkdir("./library/doc")

if not os.path.exists("./library/wav"):
    os.mkdir("./library/wav")

# 默认文件下载位置
LIBRARY_PATH = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir, "library"))


def load_from_json(uuid: str = "") -> AudioDocument:
    audio_doc = AudioDocument(audio_uuid=uuid)
    with open(f"{LIBRARY_PATH}/doc/{uuid}.json", "r", encoding="utf-8") as fr:
        df_json = json.load(fr)
        audio_doc.title = df_json.get("title")
        audio_doc.ext = df_json.get("ext")
        audio_doc.web = df_json.get("web")
        audio_doc.url = df_json.get("url")
        audio_doc.length = df_json.get("length")
        audio_doc.description = df_json.get("description")
        audio_doc.keywords = df_json.get("keywords")
        audio_doc.path = df_json.get("path")
        audio_doc.sentence = [SentenceDocument(x.get("start"), x.get("end"), x.get("content"), x.get("speaker")) for x in df_json.get("sentence", list())]
        audio_doc.summary = [SummaryDocument(x.get("start"), x.get("content")) for x in df_json.get("summary", list())]
        audio_doc.views = [ViewDocument(x.get("content"), x.get("mark")) for x in df_json.get("views", list())]
        audio_doc.origin = df_json.get("origin")
        audio_doc.ctime = df_json.get("ctime")
        audio_doc.utime = df_json.get("utime")
    return audio_doc


if "audio_gallery" not in st.session_state:
    st.session_state.audio_gallery = {
        x.uuid: x for x in sorted([
            load_from_json(os.path.splitext(y)[0]) for y in os.listdir(f"{LIBRARY_PATH}/doc")
            if os.path.splitext(y)[-1] == ".json"
            ], key=lambda z: z.ctime)
        }


def index(df_wiki: Dict[str, List[str or Dict]]) -> None:

    for df_name in df_wiki["recommend"]:

        audio_doc = load_from_json(df_name)

        with st.expander(f"""**标题**：{audio_doc.title}（{audio_doc.origin}任务）\n\n**描述**：{audio_doc.description}"""):

            st.caption(f"""基本信息""")

            col_tag, col_keywords = st.columns([1, 9])
            with col_tag:
                st.markdown("**标签**：")
            with col_keywords:
                st.markdown("; ".join(audio_doc.keywords))

            st.markdown(f"""**原始链接**：[{audio_doc.web}]({audio_doc.web})""")

            col_length, col_ctime = st.columns([1, 1])
            with col_length:
                st.markdown(f"""**音频时长**：{audio_doc.length} 秒【[查看详情](/Gallery?uuid={audio_doc.uuid})】""")
            with col_ctime:
                st.markdown(f"""**创建时间**：{datetime.fromtimestamp(audio_doc.ctime).strftime("%Y-%m-%d %H:%M:%S")}""")

            st.divider()

            st.caption("观点交互", help="请评价由音频中提取出的若干条观点对您的价值")

            wiki_add = [True for _ in audio_doc.views]

            for i, view_doc in enumerate(audio_doc.views):
                col_views_content, col_views_mark = st.columns([6, 1])
                with col_views_content:
                    wiki_add[i] = st.checkbox(view_doc.content, wiki_add[i], f"checkbox_{audio_doc.uuid}_{i}")
                with col_views_mark:
                    view_doc.mark = st.toggle("是否有效", wiki_add[i] and view_doc.mark, f"toggle_{audio_doc.uuid}_{i}")

            wiki_save = st.button("保存到知识库", f"""button_{audio_doc.uuid}""", "已勾选的指定观点表述将被保存到您的知识库集合", use_container_width=True)
            if wiki_save:
                df_wiki["view_set"] = df_wiki.get("view_set", list())
                df_wiki["view_set"].extend([y.__dict__ for x, y in enumerate(audio_doc.views) if wiki_add[x]])
                st.success("您勾选的观点已被保存到知识库集合。", icon="✅")

        audio_doc.save_as_json(f"{LIBRARY_PATH}/doc/{df_name}.json")


def wiki_gallery(df_wiki: Dict[str, List[str or Dict]]) -> None:

    with st.expander("查看我的知识库"):

        wiki_views = [ViewDocument(x.get("content"), x.get("mark")) for x in df_wiki.get("view_set", list())]

        with st.form("编辑我的知识库", True):
            view_content = st.text_input("编辑我的知识库", "", help="您可以直接在此处向您的知识库新增观点", placeholder="请在此处输入新增观点的内容，并在下方评价其对您的价值")
            view_mark = st.toggle("是否有效", True)
            view_submit = st.form_submit_button("添加到我的知识库", help="您的知识库将新增一条观点表述", use_container_width=True)
            if view_submit:
                wiki_views.insert(0, ViewDocument(view_content, view_mark))

        wiki_remove= [False for _ in wiki_views]

        for i, view_doc in enumerate(wiki_views):
            col_views_content, col_views_mark = st.columns([6, 1])
            with col_views_content:
                wiki_remove[i] = st.checkbox(view_doc.content, key=f"checkbox_wiki_{i}")
            with col_views_mark:
                view_doc.mark = st.toggle("是否有效", view_doc.mark, f"toggle_wiki_{i}")

        wiki_delete = st.button("从我的知识库中删除", help="已勾选的指定观点表述将从您的知识库集合中删除", use_container_width=True)
        if wiki_delete:
            df_wiki["view_set"] = [y.__dict__ for x, y in enumerate(wiki_views) if not wiki_remove[x]]
            st.success("您勾选的观点已被保存到知识库集合。", icon="✅")
        else:
            df_wiki["view_set"] = [x.__dict__ for x in wiki_views]


def run() -> None:

    st.experimental_set_query_params()
    st.set_page_config(
        page_title="Pickpod Home",
        page_icon="./library/logo.png",
        menu_items={
            "Get Help": "https://github.com/shixiangcap/pickpod",
            "Report a bug": "https://github.com/shixiangcap/pickpod",
            "About": "### Pickpod 是一个基于 `Streamlit` 框架构建的网络服务：\n\n### 它根据您自己的`非共识观点`为您推荐播客。"
        }
    )

    with open("./library/wiki.json", "r", encoding="utf-8") as f:
        df_wiki = json.load(f)

    with st.sidebar:

        st.header("我的 Pickpod")

        if len(st.session_state.audio_gallery.keys()) > 0:

            pp_mode = st.selectbox("推荐模式", [False, True], format_func=lambda x: "知识库模式" if x else "简单模式", help="请选择 Pickpod 在推荐播客时是否需要参考您的知识库")
            pp_uuid_min = st.session_state.audio_gallery[list(st.session_state.audio_gallery.keys())[0]].ctime
            pp_uuid_max = st.session_state.audio_gallery[list(st.session_state.audio_gallery.keys())[-1]].ctime
            pp_date = st.date_input("推荐范围", [datetime.fromtimestamp(pp_uuid_min), datetime.fromtimestamp(pp_uuid_max)], datetime.fromtimestamp(pp_uuid_min), datetime.fromtimestamp(pp_uuid_max), help="请选择 Pickpod 所推荐播客对应任务的创建时间范围", format="YYYY.MM.DD")

            pp_list = [x for x, y in st.session_state.audio_gallery.items() if datetime(pp_date[0].year, pp_date[0].month, pp_date[0].day).timestamp() <= y.ctime and datetime(pp_date[1].year, pp_date[1].month, pp_date[1].day + 1).timestamp() > y.ctime]

            with st.expander(f"本次推荐共涉及{len(pp_list)}篇播客"):
                pp_select = st.selectbox("您可以在以下播客中选择需要推荐的具体范围", [True, False], format_func=lambda x: "全选" if x else "全不选", help="若取消勾选，则对应播客不会出现在排序结果中（建议一次性选择不超过20条）")
                audio_select = [st.checkbox(st.session_state.audio_gallery[x].title, pp_select, f"checkbox_{x}", help="; ".join(st.session_state.audio_gallery[x].keywords)) for x in pp_list]

            pp_recommend = st.button("更新推荐", help="Pickpod 将按照您的要求在库中搜索，这将花费一定时间", use_container_width=True)

            if pp_recommend:

                claude_client = ClaudeClient(CLAUDE_KEY)

                pp_list = [pp_list[x] for x, y in enumerate(audio_select) if y]

                if pp_mode:

                    pp_sort = claude_client.get_recommend_wiki(
                        [" ".join([x.content for x in st.session_state.audio_gallery[y].sentence]) for y in pp_list], 
                        {
                            True: [x.get("content") for x in df_wiki.get("view_set", list()) if x.get("mark")],
                            False: [x.get("content") for x in df_wiki.get("view_set", list()) if not x.get("mark")]
                        }
                    )

                else:

                    pp_sort = claude_client.get_recommend_none([" ".join([x.content for x in st.session_state.audio_gallery[y].sentence]) for y in pp_list])

                df_wiki["recommend"] = [pp_list[x] for x in pp_sort]

        else:

            st.info("ℹ️ 暂无可以推荐的播客")

    st.write("# 欢迎使用 Pickpod 🏠")

    df_wiki["recommend"] = df_wiki.get("recommend", list())

    if len(df_wiki["recommend"]):

        st.markdown("以下是 **Pickpod** 为您最新精选的播客：")

        index(df_wiki)

    else:

        st.info("ℹ️ **Pickpod** 暂未发现播客，您可以在简单[配置](/Configuration)后开始您的第一次[转录](/Transcribe)")

    st.divider()

    wiki_gallery(df_wiki)

    with open("./library/wiki.json", "w") as f:
        f.write(json.dumps(df_wiki, indent=4, separators=(",", ": "), ensure_ascii=False))


if __name__ == "__main__":
    run()
