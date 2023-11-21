# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

import streamlit as st
from Home import DATA_PATH, index, wiki_gallery

from pickpod.config import DBClient
from pickpod.draft import AudioDraft, SentenceDraft, SummaryDraft, ViewDraft


os.chdir(os.path.split(os.path.realpath(__file__))[0])

PPDB = DBClient(DATA_PATH)


st.set_page_config(
    page_title="Pickpod Gallery",
    page_icon="../data/logo.png",
    menu_items={
        "Get Help": "https://github.com/shixiangcap/pickpod",
        "Report a bug": "https://github.com/shixiangcap/pickpod",
        "About": "### Pickpod 是一个基于 `Streamlit` 框架构建的网络服务：\n\n### 它根据您自己的`非共识观点`为您推荐播客。"
    }
)

if "pp_search" not in st.session_state:
    st.session_state.pp_search = False

with st.sidebar:

    st.header("搜索 Pickpod")

    pp_q = st.text_input("关键词", help="您输入的关键词将被逐字匹配")
    pp_uuid_min = PPDB.fetchone(AudioDraft.sort_by_ctime(0))[0]
    pp_uuid_max = PPDB.fetchone(AudioDraft.sort_by_ctime(1))[0]
    pp_date = st.date_input("时间段", [datetime.fromtimestamp(pp_uuid_min), datetime.fromtimestamp(pp_uuid_max)], datetime.fromtimestamp(pp_uuid_min), datetime.fromtimestamp(pp_uuid_max), help="请选择 Pickpod 任务的创建时间范围", format="YYYY.MM.DD")
    pp_range = st.multiselect("匹配的字段范围", [["标题", "title"], ["描述", "description"], ["关键词", "keyword"], ["正文", "sentence"]], [["标题", "title"], ["描述", "description"], ["关键词", "keyword"], ["正文", "sentence"]], format_func=lambda x: x[0], help="若选择的内容为空，则意味着在所有字段中搜索")
    pp_search = st.button("开始搜索", help="Pickpod 将按照您的要求在库中搜索，这将花费一定时间", use_container_width=True)
    if pp_search:
        st.session_state.pp_search = True

    gallery_list = dict()

    if st.session_state.pp_search:

        st.header("结果 Pickpod")

        pp_range = [x[1] for x in pp_range] if len(pp_range) > 0 else ["title", "description", "keyword", "sentence"]

        if pp_q:

            pp_audio = list()

            if "title" in pp_range:
                pp_audio.extend([PPDB.fetchall(x, y) for x, y in [AudioDraft.select_title_uuid(
                    pp_q,
                    datetime(pp_date[0].year, pp_date[0].month, pp_date[0].day).timestamp(),
                    datetime(pp_date[1].year, pp_date[1].month, pp_date[1].day).timestamp() + 24 * 3600
                )]][0])

            if "description" in pp_range:
                pp_audio.extend([PPDB.fetchall(x, y) for x, y in [AudioDraft.select_description_uuid(
                    pp_q,
                    datetime(pp_date[0].year, pp_date[0].month, pp_date[0].day).timestamp(),
                    datetime(pp_date[1].year, pp_date[1].month, pp_date[1].day).timestamp() + 24 * 3600
                )]][0])

            if "keyword" in pp_range:
                pp_audio.extend([PPDB.fetchall(x, y) for x, y in [AudioDraft.select_keyword_uuid(
                    pp_q,
                    datetime(pp_date[0].year, pp_date[0].month, pp_date[0].day).timestamp(),
                    datetime(pp_date[1].year, pp_date[1].month, pp_date[1].day).timestamp() + 24 * 3600
                )]][0])

            if "sentence" in pp_range:
                pp_audio.extend([[
                    PPDB.fetchone(u, v) for u, v in [AudioDraft.select_sentence_uuid(
                        z[0],
                        datetime(pp_date[0].year, pp_date[0].month, pp_date[0].day).timestamp(),
                        datetime(pp_date[1].year, pp_date[1].month, pp_date[1].day).timestamp() + 24 * 3600
                        )]
                    ][0] for z in [PPDB.fetchall(x, y) for x, y in [SentenceDraft.select_by_content(pp_q)]][0]
                    ])

            pp_audio = sorted(set(pp_audio), key=lambda x: x[2], reverse=True)

        else:

            pp_audio = PPDB.fetchall(AudioDraft.select_all_uuid())

    else:

        st.header("库 Pickpod")

        pp_audio = PPDB.fetchall(AudioDraft.select_all_uuid())

    for audio_uuid, audio_origin, audio_ctime in pp_audio:

        audio_stamp = datetime.fromtimestamp(audio_ctime)
        audio_time = f"{audio_stamp.year}年{audio_stamp.month}月"

        if gallery_list.get(audio_time) is None:
            gallery_list[audio_time] = dict(定时=list(), 网络=list(), 本地=list())

        gallery_list[audio_time][audio_origin].append(audio_uuid)

    for audio_time, audio_dict in gallery_list.items():

        with st.expander(audio_time):
            audio_origin = st.selectbox("Pickpod 任务的来源", ["定时", "网络", "本地"], key=f"{audio_time}_select", help="请选择指定的 Pickpod 文稿来源")
            audio_params = st.radio(
                "Pickpod 文稿",
                audio_dict[audio_origin],
                format_func=lambda z: [AudioDraft.db_init(PPDB.fetchone(x, y)) for x, y in [AudioDraft.select_by_uuid(z)]][0].title,
                key=f"{audio_time}_radio",
                captions=["; ".join(ad.keyword.split("\n")) for ad in [
                    AudioDraft.db_init(PPDB.fetchone(x, y)) for x, y in [
                        AudioDraft.select_by_uuid(z) for z in audio_dict[audio_origin]
                        ]
                    ]],
                label_visibility="collapsed"
                )
            st.button("前往", key=f"{audio_time}_button", on_click=st.experimental_set_query_params, kwargs=dict(uuid=audio_params), use_container_width=True)

    pp_return = st.button("返回", help="返回首页", use_container_width=True)
    if pp_return:
        st.session_state.pp_search = False
        st.rerun()


st.write("# 查看 Pickpod 文稿详情 🔎")

df_name = st.experimental_get_query_params().get("uuid")

with open(f"{DATA_PATH}/task.json", "r", encoding="utf-8") as f:
    df_wiki = json.load(f)

if df_name:

    st.caption("1⃣️ 音频文件信息", unsafe_allow_html=False)
    st.json(AudioDraft.db_init([
        PPDB.fetchone(x, y) for x, y in [
            AudioDraft.select_by_uuid(df_name[0])
            ]
        ][0]).__dict__)

    st.caption("2⃣️ 音频文件文稿", unsafe_allow_html=False)
    st.json([SentenceDraft.db_init(sd).__dict__ for sd in [
        PPDB.fetchall(x, y) for x, y in [
            SentenceDraft.select_by_aid(df_name[0])
            ]
        ][0]], expanded=False)

    st.caption("3⃣️ 音频文件文稿摘要", unsafe_allow_html=False)
    st.json([SummaryDraft.db_init(sd).__dict__ for sd in [
        PPDB.fetchall(x, y) for x, y in [
            SummaryDraft.select_by_aid(df_name[0])
            ]
        ][0]], expanded=False)

    st.caption("4⃣️ 音频文件表述观点", unsafe_allow_html=False)
    st.json([ViewDraft.db_init(sd).__dict__ for sd in [
        PPDB.fetchall(x, y) for x, y in [
            ViewDraft.select_by_aid(df_name[0])
            ]
        ][0]], expanded=False)

else:

    df_wiki["pp_recommend"] = df_wiki.get("pp_recommend", list())

    if len(df_wiki["pp_recommend"]):
        st.markdown("以下是 **Pickpod** 为您最新精选的播客：")
        index(df_wiki["pp_recommend"], PPDB)
    else:
        st.info("ℹ️ **Pickpod** 暂未发现播客，您可以在简单[配置](/Configuration)后开始您的第一次[转录](/Transcribe)")

st.divider()

wiki_gallery(PPDB)
