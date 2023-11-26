# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import os

import streamlit as st
from Home import DATA_PATH

from pickpod.config import DBClient
from pickpod.draft import AudioDraft, SentenceDraft, SummaryDraft, ViewDraft


os.chdir(os.path.split(os.path.realpath(__file__))[0])

PPDB = DBClient(DATA_PATH)


st.set_page_config(
    page_title="Pickpod Editor",
    page_icon="../data/logo.png",
    menu_items={
        "Get Help": "https://github.com/shixiangcap/pickpod",
        "Report a bug": "https://github.com/shixiangcap/pickpod",
        "About": "### Pickpod 是一个基于 `Streamlit` 框架构建的网络服务：\n\n### 它根据您自己的`非共识观点`为您推荐播客。"
    }
)

with st.sidebar:

    st.header("编辑 Pickpod")

    pp_audio = st.selectbox("Pickpod 任务内容", range(0, 4), format_func=lambda x: ["音频", "文稿", "摘要", "观点"][x], help="请选择需要编辑的 Pickpod 任务内容")

st.write("# 修改 Pickpod 任务结果 📝")

df_name = st.experimental_get_query_params().get("uuid")

if df_name:

    audio_draft: AudioDraft = AudioDraft.db_init([PPDB.fetchone(x, y) for x, y in [
        AudioDraft.select_by_uuid(df_name[0])
        ]][0])

    db_sql = list()

    if pp_audio == 0:

        audio_draft.web = st.text_input("主页", audio_draft.web, placeholder="请编辑该音频的主页链接")

        audio_draft.language = st.text_input("语言", audio_draft.language, placeholder="请编辑该音频使用的语言")

        audio_draft.title = st.text_area("标题", audio_draft.title, placeholder="请编辑该音频的标题")

        audio_draft.description = st.text_area("描述", audio_draft.description, placeholder="请编辑该音频的描述")

        audio_draft.keyword = st.text_area("关键词", audio_draft.keyword, 260, placeholder="请编辑该音频的关键词")

        audio_draft.origin = st.selectbox("来源", ["定时", "网络", "本地"], help="请选择 Pickpod 任务的来源")

        if st.button("删除该任务", help="将该任务从 Pickpod 库中删除，若出现页面错误，请前往“Home”页以重新开始", use_container_width=True):
            x, y = AudioDraft.delete_status(audio_draft.uuid)
            PPDB.execute(x, y)
            st.success(f"Pickpod任务：{audio_draft.uuid}已从数据库中删除，请关闭此页面。", icon="✅")
        else:
            db_sql.append(audio_draft.update())

    elif pp_audio == 1:

        with open(audio_draft.path, "rb") as f:
            audio_bytes = f.read()

        st.audio(audio_bytes, format=f"audio/mp4", start_time=0)

        sentence_draft = [SentenceDraft.db_init(sd) for sd in [
            PPDB.fetchall(x, y) for x, y in [SentenceDraft.select_by_aid(audio_draft.uuid)]
            ][0]]

    elif pp_audio == 2:

        summary_draft = [SummaryDraft.db_init(sd) for sd in [
            PPDB.fetchall(x, y) for x, y in [SummaryDraft.select_by_aid(audio_draft.uuid)]
            ][0]]

    elif pp_audio == 3:

        view_draft = [ViewDraft.db_init(sd) for sd in [
            PPDB.fetchall(x, y) for x, y in [ViewDraft.select_by_aid(audio_draft.uuid)]
            ][0]]

    if st.button("保存更新", help="您修改的内容将在 Pickpod 库中生效", use_container_width=True):
        for x, y in db_sql:
            PPDB.execute(x, y)
        st.info(f"ℹ️Pickpod任务：{audio_draft.uuid}已在数据库中更新")

else:

    st.info("ℹ️ **Pickpod** 暂未选择任务，您可以在“Gallery”页中选择指定播客点击“前往编辑”以开始")
