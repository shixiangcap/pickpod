# !/usr/bin/env python3.11
# -- coding:utf-8 --**

import datetime
import json
import os
import re
import threading
from typing import List

import requests
import streamlit as st
from dotenv import find_dotenv, load_dotenv
from Home import DATA_PATH

from pickpod.config import YDL_OPTION, TaskConfig
from pickpod.draft import AudioDraft
from pickpod.task import PickpodTask
from pickpod.utils import PickpodUtils


os.chdir(os.path.split(os.path.realpath(__file__))[0])

# load from env
load_dotenv(find_dotenv(), override=True)
HUGGING_FACE_KEY = os.getenv("HUGGING_FACE_KEY")
CLAUDE_KEY = os.getenv("CLAUDE_KEY")
LISTEN_NOTE_KEY = os.getenv("LISTEN_NOTE_KEY")
HTTP_PROXY = os.getenv("HTTP_PROXY")


def my_pickpod_task(pickpod_list: List[PickpodTask]) -> None:
    for pickpod_task in pickpod_list:
        try:
            pickpod_task.pickpod_all_task()
            pickpod_task.save_to_db()
        except Exception as e:
            print("Pickpod task failed, CODE: {}, INFO: {}.".format(e.args[0], e.args[-1]))

def task_set(ln_q, ln_sort_by_date=None, ln_num=None, ln_len_min=None, ln_len_max=None, ln_published_before=None, ln_published_after=None, ln_only_in=None, ln_language=None, ln_region=None, ln_safe_mode=None, ln_unique_podcasts=None, pp_start=None, pp_period=None, pp_language=None, pp_prompt=None, pp_pipeline=None, pp_keyword=None, pp_summary=None, pp_view=None) -> None:
    task_dict = {
        "pp_start": int(datetime.datetime.combine(pp_start, datetime.time()).timestamp()) if pp_start else None,
        "pp_period": pp_period,
        "pp_language": pp_language,
        "pp_prompt": pp_prompt,
        "pp_pipeline": pp_pipeline,
        "pp_keyword": pp_keyword,
        "pp_summary": pp_summary,
        "pp_view": pp_view,
        "ll_list": list()
        }
    if ln_q:
        for num in ln_num:
            task_dict["ll_list"].append({
                "q": ln_q,
                "sort_by_date": ln_sort_by_date,
                "type": "episode",
                "offset": num,
                "len_min": ln_len_min,
                "len_max": ln_len_max,
                "published_before": int(datetime.datetime.combine(ln_published_before, datetime.time()).timestamp() * 1000),
                "published_after": int(datetime.datetime.combine(ln_published_after, datetime.time()).timestamp() * 1000),
                "only_in": ",".join([x[1] for x in ln_only_in]) if len(ln_only_in) > 0 else "title,description,author,audio",
                "language": ln_language,
                "region": ln_region,
                "safe_mode": ln_safe_mode,
                "unique_podcasts": ln_unique_podcasts,
                "page_size": 10,
            })
    st.session_state.task_do = task_dict


st.experimental_set_query_params()
st.set_page_config(
    page_title="Pickpod Assignment",
    page_icon="../data/logo.png",
    menu_items={
        "Get Help": "https://github.com/shixiangcap/pickpod",
        "Report a bug": "https://github.com/shixiangcap/pickpod",
        "About": "### Pickpod 是一个基于 `Streamlit` 框架构建的网络服务：\n\n### 它根据您自己的`非共识观点`为您推荐播客。"
    }
)

with st.sidebar:

    st.header("任务参数选项")

    tab_get_task, tab_do_task = st.tabs(["播客获取任务", "播客转录任务"])

    with tab_get_task:

        st.header("必填项")
        ln_q = st.text_input("关键词", help="例如人物、地点、主题...您可以使用双引号进行逐字匹配，例如\"game of thrones\"。否则就是模糊搜索。")

        st.header("选填项")
        ln_sort_by_date = st.selectbox("按日期排序", (1, 0), index=1, format_func=lambda x: "是" if x else "否", help="如果选“是”，则按日期排序。否则按相关性排序。")
        ln_num = st.selectbox("获取播客的数量", ([0], [0, 10], [0, 10, 20]), index=0, format_func=lambda x: len(x) * 10, help="如果选“10”，则单次任务将一次性处理10期播客节目，以此类推。")
        ln_len_min = st.number_input("播客节目时长最小值", min_value=0, value=0, step=1, help="单集音频长度：以分钟为单位。")
        ln_len_max = st.number_input("播客节目时长最大值", min_value=0, value=180, step=1, help="单集音频长度：以分钟为单位。")
        ln_published_before = st.date_input("该日期之前发布", datetime.datetime.today(), min_value=datetime.date.fromtimestamp(0), max_value=datetime.datetime.today(), help="仅筛选在此日期之前发布的播客节目。", format="YYYY-MM-DD")
        ln_published_after = st.date_input("该日期之后发布", datetime.date.fromtimestamp(0), min_value=datetime.date.fromtimestamp(0), max_value=ln_published_before, help="仅筛选在此日期之后发布的播客节目。", format="YYYY-MM-DD")
        ln_only_in = st.multiselect("仅在以下字段范围内匹配", [["标题", "title"], ["描述", "description"], ["作者", "author"], ["音频", "audio"]], [["标题", "title"], ["描述", "description"], ["作者", "author"], ["音频", "audio"]], format_func=lambda x: x[0], help="若选择的内容为空，则意味着在所有字段中搜索")
        ln_language = st.text_input("语言", help="限制搜索结果为指定的一种语言。若未指定，则可能是任意语言。", placeholder="可选项见“Configuration”页")
        ln_region = st.text_input("地区", help="限制搜索结果为指定的一个地区（例如：“us”、“gb”、...）。若未指定，则可能是任意区域。", placeholder="可选项见“Configuration”页")
        ln_safe_mode = st.selectbox("安全模式", (1, 0), index=1, format_func=lambda x: "是" if x else "否", help="是否排除带有露骨语言的播客节目。")
        ln_unique_podcasts = st.selectbox("唯一的播客", (1, 0), index=1, format_func=lambda x: "是" if x else "否", help="是否在搜索结果中对于每个博客仅保留一期节目。")

    with tab_do_task:

        st.header("选填项")
        pp_start = st.date_input("开始日期", datetime.datetime.today(), min_value=datetime.datetime.today(), help="请选定一个开始执行任务的日期。", format="YYYY-MM-DD")
        pp_period = st.selectbox("执行周期", (1, 7, 30), index=0, format_func=lambda x: f"{x}天", help="请选定执行任务的间隔周期。")
        pp_language = st.text_input("转录目标语言", help="若不指定，模型将在播客节目的前30秒内自动检测语言。可选语言代码可参考：https://github.com/openai/whisper/blob/main/whisper/tokenizer.py")
        pp_prompt = st.text_input("模型提示", help="您可以输入一段文字以给予转录模型一定提示。")
        pp_pipeline = st.selectbox("执行声纹分割聚类", (True, False), index=0, format_func=lambda x: "是" if x else "否", help="是否对于音频文件执行声纹分割聚类以识别说话人。")
        pp_keyword = st.selectbox("执行文稿关键词提取", (True, False), index=0, format_func=lambda x: "是" if x else "否", help="是否对于转录的文稿提取关键词。")
        pp_summary = st.selectbox("执行文稿摘要提取", (True, False), index=0, format_func=lambda x: "是" if x else "否", help="是否对于转录的文稿提取带有时间戳的摘要。")
        pp_view = st.selectbox("执行文稿观点提取", (True, False), index=0, format_func=lambda x: "是" if x else "否", help="是否对于转录的文稿提取其所表述的观点。")

    button_save, button_do, button_clean = st.columns([1, 1, 1])

    with button_save:
        click_dict = dict(ln_q=ln_q, ln_sort_by_date=ln_sort_by_date, ln_num=ln_num, ln_len_min=ln_len_min, ln_len_max=ln_len_max, ln_published_before=ln_published_before, ln_published_after=ln_published_after, ln_only_in=ln_only_in, ln_language=ln_language, ln_region=ln_region, ln_safe_mode=ln_safe_mode, ln_unique_podcasts=ln_unique_podcasts, pp_start=pp_start, pp_period=pp_period, pp_language=pp_language, pp_prompt=pp_prompt, pp_pipeline=pp_pipeline, pp_keyword=pp_keyword, pp_summary=pp_summary, pp_view=pp_view)
        click_save=st.button("保存并测试", help="您输入的参数将覆盖原有配置，且Listen Notes API将被测试", on_click=task_set, kwargs=click_dict, use_container_width=True)

    with button_do:
        click_dict = dict(ln_q=ln_q, ln_sort_by_date=ln_sort_by_date, ln_num=ln_num, ln_len_min=ln_len_min, ln_len_max=ln_len_max, ln_published_before=ln_published_before, ln_published_after=ln_published_after, ln_only_in=ln_only_in, ln_language=ln_language, ln_region=ln_region, ln_safe_mode=ln_safe_mode, ln_unique_podcasts=ln_unique_podcasts, pp_language=pp_language, pp_prompt=pp_prompt, pp_pipeline=pp_pipeline, pp_keyword=pp_keyword, pp_summary=pp_summary, pp_view=pp_view)
        click_do= st.button("立即执行", help="您可以立即开始执行本次任务", on_click=task_set, kwargs=click_dict, use_container_width=True)

    with button_clean:
        click_dict = dict(ln_q="")
        click_clean = st.button("清除", help="您的配置信息将被清空", on_click=task_set, kwargs=click_dict, use_container_width=True)

    if click_save or click_clean:
        with open(f"{DATA_PATH}/task.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(st.session_state.task_do, indent=4, separators=(",", ": "), ensure_ascii=False))

st.write("# 定制 Pickpod 周期任务 📒")

if not click_save and not click_do:

    with open(f"{DATA_PATH}/task.json", "r", encoding="utf-8") as f:
        task_dict = json.load(f)

    st.write("#### 已保存的参数选项")

    write_clean, metric_clean = st.columns([1, 1])

    with write_clean:
        st.json(task_dict, expanded=True)

    with metric_clean:
        st.metric("预计每月将消耗的 Listen Notes API 额度", str(len(task_dict.get("ll_list", list())) * ((30 // task_dict.get("pp_period")) if task_dict.get("pp_period") else 0)) + "次", help="测试过程同样将消耗一定数量的额度")

elif click_save and not click_do and not click_clean:

    with open(f"{DATA_PATH}/task.json", "r", encoding="utf-8") as f:
        task_dict = json.load(f)

    st.write("#### 已保存的参数选项")

    write_clean, metric_clean = st.columns([1, 1])

    with write_clean:
        st.json(task_dict, expanded=True)

    with metric_clean:
        st.metric("预计每月将消耗的 Listen Notes API 额度", str(len(task_dict.get("ll_list", list())) * ((30 // task_dict.get("pp_period")) if task_dict.get("pp_period") else 0)) + "次", help="测试过程同样将消耗一定数量的额度")

    st.write("#### 测试结果")

    for task_ll in task_dict.get("ll_list", list()):
        task_resp = requests.request("GET", "https://listen-api.listennotes.com/api/v2/search", headers={"X-ListenAPI-Key": LISTEN_NOTE_KEY}, params=task_ll, proxies={"http": HTTP_PROXY, "https": HTTP_PROXY} if HTTP_PROXY else None)
        st.json(task_resp.json(), expanded=False)

elif not click_save and click_do and not click_clean:

    task_pp_list = list()

    for task_ll in st.session_state.task_do.get("ll_list", list()):
        task_resp = requests.request("GET", "https://listen-api.listennotes.com/api/v2/search", headers={"X-ListenAPI-Key": LISTEN_NOTE_KEY}, params=task_ll, proxies={"http": HTTP_PROXY, "https": HTTP_PROXY} if HTTP_PROXY else None)
        if task_resp.json().get("total", 0) > task_ll.get("offset", 0):
            for task_results in task_resp.json().get("results", list()):
                task_pp_list.append(task_results)

    metric_api, metric_task = st.columns([1, 1])

    with metric_api:
        st.metric("本次任务消耗的 Listen Notes API 额度", str(len(st.session_state.task_do.get("ll_list", list()))) + "次")
        st.write("#### 任务参数")
        st.json(st.session_state.task_do, expanded=True)

    with metric_task:
        st.metric("本次任务共将转录的播客节目数量", str(len(task_pp_list)) + "期")
        st.write("#### 播客参数")

        pickpod_list = list()

        task_config = TaskConfig(
            key_hugging_face=HUGGING_FACE_KEY,
            key_claude=CLAUDE_KEY,
            path_wav=os.path.join(DATA_PATH, "wav"),
            path_db=DATA_PATH,
            task_language=pp_language,
            task_prompt=pp_prompt,
            task_proxy=HTTP_PROXY,
            pipeline=pp_pipeline,
            keyword=pp_keyword,
            summary=pp_summary,
            view=pp_view,
            )

        for podcast in task_pp_list:
            st.json(podcast, expanded=False)
            st.caption("请等待将存储音频文件到本地", unsafe_allow_html=False)
            audio_draft = AudioDraft(
                audio_title=podcast.get("title_original", ""),
                audio_web=podcast.get("listennotes_url", ""),
                audio_url=podcast.get("audio", ""),
                audio_duration=podcast.get("audio_length_sec", 0),
                audio_description=re.sub(r"<[^>]*?>", "", podcast.get("description_original", "")),
                audio_origin="定时")
            if task_config.proxy:
                YDL_OPTION["proxy"] = task_config.proxy
            YDL_OPTION["outtmpl"] = f"{DATA_PATH}/audio/{audio_draft.uuid}.%(ext)s"
            try:
                PickpodUtils.pickpod_ytdlp(audio_draft, YDL_OPTION)
                st.info(f"ℹ️ 音频文件下载完成")
                pickpod_list.append(PickpodTask(audio_draft, task_config))
            except Exception as e:
                st.error("音频文件下载失败，已跳过。错误码：{}，错误信息：{}。".format(e.args[0], e.args[-1]))

        pickpod_thread = threading.Thread(target=my_pickpod_task, args=(pickpod_list, ))
        pickpod_thread.start()

    st.info("ℹ️ 定制任务已在后台启动，您可以在晚些时候前往“Gallery”页查看")
