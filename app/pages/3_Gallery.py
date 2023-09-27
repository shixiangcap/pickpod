# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

import streamlit as st
from Home import LIBRARY_PATH, index, load_from_json, wiki_gallery


os.chdir(os.path.split(os.path.realpath(__file__))[0])


st.set_page_config(
    page_title="Pickpod Gallery",
    page_icon="../library/logo.png",
    menu_items={
        "Get Help": "https://github.com/shixiangcap/pickpod",
        "Report a bug": "https://github.com/shixiangcap/pickpod",
        "About": "### Pickpod 是一个基于 `Streamlit` 框架构建的网络服务：\n\n### 它根据您自己的`非共识观点`为您推荐播客。"
    }
)

if "pp_search" not in st.session_state:
    st.session_state.pp_search = False
    st.session_state.audio_gallery = {
        x.uuid: x for x in sorted([
            load_from_json(os.path.splitext(y)[0]) for y in os.listdir(f"{LIBRARY_PATH}/doc")
            if os.path.splitext(y)[-1] == ".json"
            ], key=lambda z: z.ctime)
        }

with st.sidebar:

    st.header("搜索 Pickpod")

    pp_q = st.text_input("关键词", help="您输入的关键词将被逐字匹配")
    pp_range = st.multiselect("匹配的字段范围", [["标题", "title"], ["描述", "description"], ["关键词", "keywords"], ["正文", "sentence"]], [["标题", "title"], ["描述", "description"], ["关键词", "keywords"], ["正文", "sentence"]], format_func=lambda x: x[0], help="若选择的内容为空，则意味着在所有字段中搜索")
    pp_search = st.button("开始搜索", help="Pickpod 将按照您的要求在库中搜索，这将花费一定时间", use_container_width=True)
    if pp_search:
        st.session_state.pp_search = True

    gallery_list = dict()

    if st.session_state.pp_search:

        st.header("结果 Pickpod")

        pp_range = [x[1] for x in pp_range]

        for audio_uuid, audio_doc in st.session_state.audio_gallery.items():

            if "title" in pp_range and pp_q in audio_doc.title:
                pass
            elif "description" in pp_range and pp_q in audio_doc.description:
                pass
            elif "keywords" in pp_range and pp_q in " ".join(audio_doc.keywords):
                pass
            elif "sentence" in pp_range and pp_q in " ".join([x.content for x in audio_doc.sentence]):
                pass
            else:
                continue

            audio_stamp = datetime.fromtimestamp(audio_doc.ctime)
            audio_time = f"{audio_stamp.year}年{audio_stamp.month}月"

            if gallery_list.get(audio_time) is None:
                gallery_list[audio_time] = dict(定时=list(), 网络=list(), 本地=list())

            gallery_list[audio_time][audio_doc.origin].append(audio_uuid)

    else:

        st.header("库 Pickpod")

        for audio_uuid, audio_doc in st.session_state.audio_gallery.items():

            audio_stamp = datetime.fromtimestamp(audio_doc.ctime)
            audio_time = f"{audio_stamp.year}年{audio_stamp.month}月"

            if gallery_list.get(audio_time) is None:
                gallery_list[audio_time] = dict(定时=list(), 网络=list(), 本地=list())

            gallery_list[audio_time][audio_doc.origin].append(audio_uuid)

    for audio_time, audio_dict in gallery_list.items():

        with st.expander(audio_time):
            audio_origin = st.selectbox("Pickpod 任务的来源", ["定时", "网络", "本地"], key=f"{audio_time}_select", help="请选择指定的 Pickpod 文稿来源")
            audio_params = st.radio("Pickpod 文稿", audio_dict[audio_origin], format_func=lambda x: st.session_state.audio_gallery[x].title, key=f"{audio_time}_radio", captions=["; ".join(st.session_state.audio_gallery[x].keywords) for x in audio_dict[audio_origin]], label_visibility="collapsed")
            st.button("前往", key=f"{audio_time}_button", on_click=st.experimental_set_query_params, kwargs=dict(uuid=audio_params), use_container_width=True)

    pp_return = st.button("返回", help="返回首页", use_container_width=True)
    if pp_return:
        st.session_state.pp_search = False


st.write("# 查看 Pickpod 文稿详情 🔎")

df_name = st.experimental_get_query_params().get("uuid")

if df_name:

    with open(f"{LIBRARY_PATH}/doc/{df_name[0]}.json", "r", encoding="utf-8") as fr:
        df_json = json.load(fr)
        st.json(df_json)

else:

    with open(f"{LIBRARY_PATH}/wiki.json", "r", encoding="utf-8") as f:
        df_wiki = json.load(f)

    if len(df_wiki.get("recommend", list())):
        st.markdown("以下是 **Pickpod** 为您最新精选的播客：")
        index(df_wiki)
    else:
        st.info("ℹ️ **Pickpod** 暂未发现播客，您可以在简单[配置](/Configuration)后开始您的第一次[转录](/Transcribe)")

st.divider()

wiki_gallery(df_wiki)

with open("./library/wiki.json", "w") as f:
    f.write(json.dumps(df_wiki, indent=4, separators=(",", ": "), ensure_ascii=False))
