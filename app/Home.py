# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime
from typing import List

import streamlit as st
from dotenv import find_dotenv, load_dotenv
from streamlit.logger import get_logger

from pickpod.api import ClaudeClient
from pickpod.config import DBClient
from pickpod.draft import *


os.chdir(os.path.split(os.path.realpath(__file__))[0])

# load from env
load_dotenv(find_dotenv("./pages/.env"), override=True)
CLAUDE_KEY = os.getenv("CLAUDE_KEY")
HTTP_PROXY = os.getenv("HTTP_PROXY")

LOGGER = get_logger(__name__)

PPDB = DBClient("./data")
PPTB = ["audio", "formation", "sentence"]

tb = [PPDB.fetchone(x, y)[0] for x, y in [DBClient.find_tb(z) for z in PPTB]]
if not (tb[0] and tb[1] and tb[2]):
    PPDB.create_tb()

if not os.path.exists("./data/audio"):
    os.mkdir("./data/audio")
if not os.path.exists("./data/wav"):
    os.mkdir("./data/wav")

# 默认文件下载位置
DATA_PATH = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir, "data"))


def index(df_recommend: List[str], pp_db: DBClient = PPDB) -> None:

    for df_uuid in df_recommend:

        audio_draft: AudioDraft = AudioDraft.db_init([pp_db.fetchone(x, y) for x, y in [AudioDraft.select_by_uuid(df_uuid)]][0])

        with st.expander(f"**标题**：{audio_draft.title}（{audio_draft.origin}任务）\n\n**描述**：{audio_draft.description}"):

            st.caption("基本信息")

            col_tag, col_keyword = st.columns([1, 9])
            with col_tag:
                st.markdown("**标签**：")
            with col_keyword:
                st.markdown("; ".join(audio_draft.keyword.split("\n")))

            st.markdown(f"**原始链接**：[{audio_draft.web}]({audio_draft.web})")

            col_length, col_ctime = st.columns([1, 1])
            with col_length:
                st.markdown(f"**音频时长**：{audio_draft.duration} 秒【{audio_draft.language}】【[查看详情](/Gallery?uuid={audio_draft.uuid})】")
            with col_ctime:
                st.markdown(f'''**创建时间**：{datetime.fromtimestamp(audio_draft.ctime).strftime("%Y-%m-%d %H:%M:%S")}''')

            st.divider()

            st.caption("观点交互", help="请评价由音频中提取出的若干条观点对您的价值")

            view_draft: List[ViewDraft] = [ViewDraft.db_init(vd) for vd in [pp_db.fetchall(x, y) for x, y in [ViewDraft.select_by_aid(audio_draft.uuid)]][0]]

            wiki_add = [True for _ in view_draft]

            for i, vd in enumerate(view_draft):
                col_views_content, col_views_mark = st.columns([6, 1])
                with col_views_content:
                    wiki_add[i] = st.checkbox(vd.content, wiki_add[i], f"checkbox_{vd.uuid}")
                with col_views_mark:
                    vd.value = st.toggle("是否有效", wiki_add[i] and vd.value, f"toggle_{vd.uuid}")

            wiki_save = st.button("保存到知识库", f"button_{audio_draft.uuid}", "已勾选的指定观点表述将被保存到您的知识库集合", use_container_width=True)
            if wiki_save:
                for x, y in [
                    WikiDraft(
                        wiki_aid=vd.aid, wiki_content=vd.content, wiki_value=vd.value
                        ).insert() for i, vd in enumerate(view_draft) if wiki_add[i]
                    ]:
                    pp_db.execute(x, y)
                st.success("您勾选的观点已被保存到知识库集合。", icon="✅")

        for x, y in [z.update() for z in view_draft]:
            pp_db.execute(x, y)


def wiki_gallery(pp_db: DBClient = PPDB) -> None:

    with st.expander("查看我的知识库"):

        wiki_draft: List[WikiDraft] = [WikiDraft.db_init(x) for x in pp_db.fetchall(WikiDraft.select_all())]

        with st.form("编辑我的知识库", True):
            wiki_content = st.text_input("编辑我的知识库", "", help="您可以直接在此处向您的知识库新增观点", placeholder="请在此处输入新增观点的内容，并在下方评价其对您的价值")
            wiki_mark = st.toggle("是否有效", True)
            wiki_submit = st.form_submit_button("添加到我的知识库", help="您的知识库将新增一条观点表述", use_container_width=True)
            if wiki_submit:
                x, y = WikiDraft(wiki_content=wiki_content, wiki_value=wiki_mark).insert()
                pp_db.execute(x, y)

        wiki_remove = [False for _ in wiki_draft]

        for i, wd in enumerate(wiki_draft):
            col_views_content, col_views_mark = st.columns([6, 1])
            with col_views_content:
                wiki_remove[i] = st.checkbox(wd.content, wiki_remove[i], key=f"checkbox_{wd.uuid}")
            with col_views_mark:
                wd.value = st.toggle("是否有效", wd.value, f"toggle_{wd.uuid}")

        wiki_delete = st.button("从我的知识库中删除", help="已勾选的指定观点表述将从您的知识库集合中删除", use_container_width=True)
        if wiki_delete:
            for i, wd in enumerate(wiki_draft):
                if wiki_remove[i]:
                    x, y = WikiDraft.delete_status(wd.uuid)
                else:
                    x, y = wd.update()
                pp_db.execute(x, y)
            st.success("您勾选的观点已从知识库集合中删除。", icon="✅")
        else:
            for x, y in [z.update() for z in wiki_draft]:
                pp_db.execute(x, y)


def run() -> None:

    st.set_page_config(
        page_title="Pickpod Home",
        page_icon="./data/logo.png",
        menu_items={
            "Get Help": "https://github.com/shixiangcap/pickpod",
            "Report a bug": "https://github.com/shixiangcap/pickpod",
            "About": "### Pickpod 是一个基于 `Streamlit` 框架构建的网络服务：\n\n### 它根据您自己的`非共识观点`为您推荐播客。"
        }
    )

    with open("./data/task.json", "r", encoding="utf-8") as f:
        df_wiki = json.load(f)

    with st.sidebar:

        st.header("我的 Pickpod")

        if PPDB.fetchone(AudioDraft.count_num())[0] > 0:

            pp_mode = st.selectbox("推荐模式", [False, True], format_func=lambda x: "知识库模式" if x else "简单模式", help="请选择 Pickpod 在推荐播客时是否需要参考您的知识库")
            pp_uuid_min = PPDB.fetchone(AudioDraft.sort_by_ctime(0))[0]
            pp_uuid_max = PPDB.fetchone(AudioDraft.sort_by_ctime(1))[0]
            pp_date = st.date_input("推荐范围", [datetime.fromtimestamp(pp_uuid_max), datetime.fromtimestamp(pp_uuid_max)], datetime.fromtimestamp(pp_uuid_min), datetime.fromtimestamp(pp_uuid_max), help="请选择 Pickpod 所推荐播客对应任务的创建时间范围", format="YYYY.MM.DD")

            pp_list =  [
                z[0] for z in [
                    PPDB.fetchall(x, y) for x, y in [
                        AudioDraft.select_by_ctime(
                            datetime(pp_date[0].year, pp_date[0].month, pp_date[0].day).timestamp(),
                            datetime(pp_date[1].year, pp_date[1].month, pp_date[1].day).timestamp() + 24 * 3600
                            )
                        ]
                    ][0]
                ] if len(pp_date) == 2 else list()

            with st.expander(f"本次推荐共涉及{len(pp_list)}篇播客"):
                pp_select = st.selectbox("您可以在以下播客中选择需要推荐的具体范围", [True, False], format_func=lambda x: "全选" if x else "全不选", help="若取消勾选，则对应播客不会出现在排序结果中（建议一次性选择不超过20条）")
                audio_select = [
                    st.checkbox(ad.title, pp_select, f"checkbox_{ad.uuid}", help="; ".join(ad.keyword.split("\n"))) for ad in [
                        AudioDraft.db_init(PPDB.fetchone(x, y)) for x, y in [
                            AudioDraft.select_by_uuid(z) for z in pp_list
                            ]
                        ]
                    ]

            pp_recommend = st.button("更新推荐", help="Pickpod 将按照您的要求在库中搜索，这将花费一定时间", use_container_width=True)

            if pp_recommend:

                claude_client = ClaudeClient(CLAUDE_KEY, HTTP_PROXY)

                pp_list = [pp_list[x] for x, y in enumerate(audio_select) if y]

                if pp_mode:

                    pp_sort = claude_client.get_recommend_wiki(
                        [
                            " ".join([SentenceDraft.db_init(s).content for s in sd]) for sd in [
                                PPDB.fetchall(x, y) for x, y in [SentenceDraft.select_by_aid(z) for z in pp_list]
                                ]
                            ],
                        {
                            True: [
                                WikiDraft.db_init(wd).content for wd in [
                                    PPDB.fetchall(x, y) for x, y in [WikiDraft.select_by_value(1)]
                                    ][0]
                                ],
                            False: [
                                WikiDraft.db_init(wd).content for wd in [
                                    PPDB.fetchall(x, y) for x, y in [WikiDraft.select_by_value(0)]
                                    ][0]
                                ],
                            }
                    )

                else:

                    pp_sort = claude_client.get_recommend_none(
                        [
                            " ".join([SentenceDraft.db_init(s).content for s in sd]) for sd in [
                                PPDB.fetchall(x, y) for x, y in [SentenceDraft.select_by_aid(z) for z in pp_list]
                                ]
                            ]
                        )

                df_wiki["pp_recommend"] = [pp_list[x] for x in pp_sort]

        else:

            st.info("ℹ️ 暂无可以推荐的播客")

    st.write("# 欢迎使用 Pickpod 🏠")

    df_wiki["pp_recommend"] = df_wiki.get("pp_recommend", list())

    if len(df_wiki["pp_recommend"]):

        st.markdown("以下是 **Pickpod** 为您最新精选的播客：")

        index(df_wiki["pp_recommend"])

    else:

        st.info("ℹ️ **Pickpod** 暂未发现播客，您可以在简单[配置](/Configuration)后开始您的第一次[转录](/Transcribe)")

    st.divider()

    wiki_gallery()

    with open("./data/task.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(df_wiki, indent=4, separators=(",", ": "), ensure_ascii=False))

    PPDB.close()


if __name__ == "__main__":
    run()
