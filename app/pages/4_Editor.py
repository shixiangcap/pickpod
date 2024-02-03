# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import os

import streamlit as st
from Home import DATA_PATH

from pickpod.api import s2t
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

df_name = st.query_params.to_dict().get("uuid")

if df_name:

    audio_draft: AudioDraft = AudioDraft.db_init([PPDB.fetchone(x, y) for x, y in [
        AudioDraft.select_by_uuid(df_name)
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
            st.success(f"Pickpod 任务：{audio_draft.uuid}已从数据库中删除，请关闭此页面。", icon="✅")
        else:
            db_sql.append(audio_draft.update())

    elif pp_audio == 1:

        with open(audio_draft.path, "rb") as f:
            audio_bytes = f.read()

        st.audio(audio_bytes, format=f"audio/mp4", start_time=0)

        sentence_draft = [SentenceDraft.db_init(sd) for sd in [
            PPDB.fetchall(x, y) for x, y in [SentenceDraft.select_by_aid(audio_draft.uuid)]
            ][0]]

        for sd in sentence_draft:

            sd.content = st.text_input("文稿内容", sd.content, key=f"text_{sd.uuid}", placeholder="请编辑该时间范围内音频的文稿内容")

            col_speaker, col_start, col_end = st.columns([1, 1, 1])
            with col_speaker:
                sd.speaker = st.number_input(f"说话人", 0, value=sd.speaker, step=1, key=f"speaker_{sd.uuid}", help="请编辑该时间范围内音频的说话人编号", placeholder=f"初始：{sd.speaker}")
            with col_start:
                sd.start = st.number_input(f"起始时间：{s2t(sd.start)}", 0.0, max(audio_draft.duration, sd.end), sd.start, 0.01, key=f"start_{sd.uuid}", help="请编辑该段音频文稿内容的起始时间，此处涉及一定换算", placeholder=f"初始：{sd.start}秒")
            with col_end:
                sd.end = st.number_input(f"中止时间：{s2t(sd.end)}", sd.start, max(audio_draft.duration, sd.end), sd.end, 0.01, key=f"end_{sd.uuid}", help="请编辑该段音频文稿内容的中止时间，此处涉及一定换算", placeholder=f"初始：{sd.end}秒")

            if st.button("删除该段文稿", f"button_{sd.uuid}", "将该段文稿从 Pickpod 库中删除，若出现页面错误，请前往“Home”页以重新开始", use_container_width=True):
                x, y = SentenceDraft.delete_status(sd.uuid)
                PPDB.execute(x, y)
                st.success(f"Pickpod 文稿：{sd.uuid}已从数据库中删除。", icon="✅")
            else:
                db_sql.append(sd.update())

    elif pp_audio == 2:

        summary_draft = [SummaryDraft.db_init(sd) for sd in [
            PPDB.fetchall(x, y) for x, y in [SummaryDraft.select_by_aid(audio_draft.uuid)]
            ][0]]

        with st.form("添加摘要", True):
            summary_content = st.text_input("添加摘要", help="您可以直接在此处为该 Pickpod 任务新增一条摘要", placeholder="请在此处输入新增摘要的内容")
            summary_start = st.number_input("时间节点", 0.0, audio_draft.duration, 0.0, 0.01, help="请标记与该条摘要相关的音频时间节点，此处涉及一定换算", placeholder="请在此处输入新增摘要在对应音频中的位置")
            summary_submit = st.form_submit_button("添加到 Pickpod 库", "该 Pickpod 任务下将新增一条音频文稿摘要", use_container_width=True)
            if summary_submit:
                x, y = SummaryDraft(summary_aid=audio_draft.uuid, summary_content=summary_content, summary_start=summary_start).insert()
                PPDB.execute(x, y)
                st.rerun()

        for sd in summary_draft:

            sd.content = st.text_area("摘要内容", sd.content, key=f"text_{sd.uuid}", placeholder="请编辑该条摘要的内容")

            sd.start = st.number_input(f"起始时间：{s2t(sd.start)}", 0.0, audio_draft.duration, sd.start, 0.01, key=f"start_{sd.uuid}", help="请标记与该条摘要相关的音频时间节点，此处涉及一定换算", placeholder=f"初始：{sd.start}秒")

            if st.button("删除该条摘要", f"button_{sd.uuid}", "将该条摘要从 Pickpod 库中删除，若出现页面错误，请前往“Home”页以重新开始", use_container_width=True):
                x, y = SummaryDraft.delete_status(sd.uuid)
                PPDB.execute(x, y)
                st.success(f"Pickpod 摘要：{sd.uuid}已从数据库中删除。", icon="✅")
            else:
                db_sql.append(sd.update())

    elif pp_audio == 3:

        view_draft = [ViewDraft.db_init(sd) for sd in [
            PPDB.fetchall(x, y) for x, y in [ViewDraft.select_by_aid(audio_draft.uuid)]
            ][0]]

        with st.form("添加观点表述", True):
            view_content = st.text_input("添加观点表述", help="您可以直接在此处为该 Pickpod 任务新增一条观点表述", placeholder="请在此处输入新增观点的内容，并在下方评价其对您的价值")
            view_value = st.toggle("是否有效", True)
            view_submit = st.form_submit_button("添加到 Pickpod 库", "该 Pickpod 任务下将新增一条观点表述", use_container_width=True)
            if view_submit:
                x, y = ViewDraft(view_aid=audio_draft.uuid, view_content=view_content, view_value=view_value).insert()
                PPDB.execute(x, y)
                st.rerun()

        for vd in view_draft:

            vd.content = st.text_area("观点表述内容", vd.content, key=f"text_{vd.uuid}", placeholder="请在此处编辑该条观点的内容，并在下方评价其对您的价值")

            vd.value = st.toggle("是否有效", vd.value, f"toggle_{vd.uuid}")

            if st.button("删除该条观点表述", f"button_{vd.uuid}", "将该条观点表述从 Pickpod 库中删除，若出现页面错误，请前往“Home”页以重新开始", use_container_width=True):
                x, y = ViewDraft.delete_status(vd.uuid)
                PPDB.execute(x, y)
                st.success(f"Pickpod 观点表述：{vd.uuid}已从数据库中删除。", icon="✅")
            else:
                db_sql.append(vd.update())

    if st.button("保存更新", help="您修改的内容将在 Pickpod 库中生效", use_container_width=True):
        for x, y in db_sql:
            PPDB.execute(x, y)
        st.success(f"Pickpod 任务：{audio_draft.uuid}已在数据库中更新", icon="✅")

else:

    st.info("ℹ️ **Pickpod** 暂未选择任务，您可以在“Gallery”页中选择指定播客点击“前往编辑”以开始")
