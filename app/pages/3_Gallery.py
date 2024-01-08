# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

import streamlit as st
from Home import DATA_PATH, index, wiki_gallery

from pickpod.api import s2t
from pickpod.config import DBClient, TaskConfig
from pickpod.draft import AudioDraft, SentenceDraft, SummaryDraft, ViewDraft, WikiDraft
from pickpod.task import PickpodTask


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
    st.session_state.pp_start = 0
    st.session_state.pp_set = False

df_name = st.experimental_get_query_params().get("uuid")

if df_name:

    audio_draft: AudioDraft = AudioDraft.db_init([PPDB.fetchone(x, y) for x, y in [
        AudioDraft.select_by_uuid(df_name[0])
        ]][0])

    pickpod_task = PickpodTask(audio_draft, TaskConfig())
    pickpod_task.sentence_draft = [SentenceDraft.db_init(sd) for sd in [
        PPDB.fetchall(x, y) for x, y in [SentenceDraft.select_by_aid(audio_draft.uuid)]
        ][0]]
    pickpod_task.summary_draft = [SummaryDraft.db_init(sd) for sd in [
        PPDB.fetchall(x, y) for x, y in [SummaryDraft.select_by_aid(audio_draft.uuid)]
        ][0]]
    pickpod_task.view_draft = [ViewDraft.db_init(sd) for sd in [
        PPDB.fetchall(x, y) for x, y in [ViewDraft.select_by_aid(audio_draft.uuid)]
        ][0]]

with st.sidebar:

    st.header("搜索 Pickpod")

    pp_q = st.text_input("关键词", help="您输入的关键词将被逐字匹配")
    pp_uuid_min = PPDB.fetchone(AudioDraft.sort_by_ctime(0))[0] if PPDB.fetchone(AudioDraft.sort_by_ctime(0)) else 0
    pp_uuid_max = PPDB.fetchone(AudioDraft.sort_by_ctime(1))[0] if PPDB.fetchone(AudioDraft.sort_by_ctime(1)) else int(datetime.now().timestamp())
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
        st.experimental_set_query_params()
        st.rerun()

    if df_name:
        st.header(f"{audio_draft.origin}任务摘要", help="从选择的段落开始播放")
        df_start = min(int(st.radio("摘要", pickpod_task.summary_draft, format_func=lambda x: x.content, captions=[s2t(sd.start) for sd in pickpod_task.summary_draft], label_visibility="collapsed").start), int(audio_draft.duration))
        st.session_state.pp_start = st.session_state.pp_start if st.session_state.pp_set else df_start


st.write("# 查看 Pickpod 文稿详情 🔎")

with open(f"{DATA_PATH}/task.json", "r", encoding="utf-8") as f:
    df_wiki = json.load(f)

if df_name:

    st.caption("标题")

    st.markdown(f"##### {audio_draft.title}")

    with open(audio_draft.path, "rb") as f:
        audio_bytes = f.read()

    st.audio(audio_bytes, format=f"audio/mp4", start_time=st.session_state.pp_start)
    st.session_state.pp_start = 0
    st.session_state.pp_set = False

    col_download, col_web = st.columns([1, 1])

    with col_download:
        st.download_button("导出音频", audio_bytes, f"{pickpod_task.audio_safe_name()}.{audio_draft.ext}", help="下载以标题命名的音频文件", use_container_width=True)

    with col_web:
        st.link_button("前往原始链接", audio_draft.web, help="查看原始网页", disabled=False if audio_draft.web else True, use_container_width=True)

    st.caption("关键词")

    st.markdown("; ".join(audio_draft.keyword.split("\n")))

    st.caption("描述")

    st.markdown(audio_draft.description)

    with st.expander(f"**语言代码**：{audio_draft.language}（[{audio_draft.url}]({audio_draft.url})）"):

        st.caption("观点交互", help="请评价由音频中提取出的若干条观点对您的价值")

        wiki_add = [True for _ in pickpod_task.view_draft]

        for i, vd in enumerate(pickpod_task.view_draft):
            col_views_content, col_views_mark = st.columns([6, 1])
            with col_views_content:
                wiki_add[i] = st.checkbox(vd.content, wiki_add[i], f"checkbox_{vd.uuid}")
            with col_views_mark:
                vd.value = st.toggle("是否有效", wiki_add[i] and vd.value, f"toggle_{vd.uuid}")

        wiki_save = st.button("保存到知识库", "已勾选的指定观点表述将被保存到您的知识库集合", use_container_width=True)
        if wiki_save:
            for x, y in [
                WikiDraft(
                    wiki_aid=vd.aid, wiki_content=vd.content, wiki_value=vd.value
                    ).insert() for i, vd in enumerate(pickpod_task.view_draft) if wiki_add[i]
                ]:
                PPDB.execute(x, y)
            st.success("您勾选的观点已被保存到知识库集合。", icon="✅")

        for x, y in [z.update() for z in pickpod_task.view_draft]:
            PPDB.execute(x, y)

        col_duration, col_ext = st.columns([1, 1])
        with col_duration:
            st.markdown(f"**音频时长**：{audio_draft.duration} 秒")
        with col_ext:
            st.markdown(f"**音频格式**：{audio_draft.ext.upper()}")

        col_ctime, col_utime = st.columns([1, 1])
        with col_ctime:
            st.markdown(f'''**任务创建时间**：{datetime.fromtimestamp(audio_draft.ctime).strftime("%Y-%m-%d %H:%M:%S")}''')
        with col_utime:
            st.markdown(f'''**任务更新时间**：{datetime.fromtimestamp(audio_draft.utime).strftime("%Y-%m-%d %H:%M:%S")}''')

    st.caption("文稿")

    for sd in pickpod_task.sentence_merge():

        st.markdown(f"**说话人**：{sd.speaker}（{s2t(sd.start)} -> {s2t(sd.end)}）")

        col_content, col_set = st.columns([9, 1])
        with col_content:
            st.markdown(sd.content)
        with col_set:
            if st.button("定位", key=sd.uuid, help="从此段落开始播放", use_container_width=True):
                st.session_state.pp_start = min(int(sd.start), int(audio_draft.duration))
                st.session_state.pp_set = True
                st.rerun()

    col_json, col_txt, col_edit = st.columns([1, 1, 1])

    with col_json:
        st.download_button("导出JSON", json.dumps(pickpod_task.__dict__, indent=4, separators=(",", ": "), ensure_ascii=False), f"{pickpod_task.audio_safe_name()}.json", use_container_width=True)

    with col_txt:
        st.download_button("导出文稿", pickpod_task.__str__, f"{pickpod_task.audio_safe_name()}.txt", use_container_width=True)

    with col_edit:
        st.link_button("前往编辑", f"/Editor?uuid={audio_draft.uuid}", help="编辑任务内容", use_container_width=True)

else:

    df_wiki["pp_recommend"] = df_wiki.get("pp_recommend", list())

    if len(df_wiki["pp_recommend"]):
        st.markdown("以下是 **Pickpod** 为您最新精选的播客：")
        index(df_wiki["pp_recommend"], PPDB)
    else:
        st.info("ℹ️ **Pickpod** 暂未发现播客，您可以在简单[配置](/Configuration)后开始您的第一次[转录](/Transcribe)")

st.divider()

wiki_gallery(PPDB)
