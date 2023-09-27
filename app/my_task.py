# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import os
import threading
import time
from queue import Queue

import streamlit as st

from pickpod.api import ClaudeClient
from pickpod.config import TaskConfig
from pickpod.doc import AudioDocument
from pickpod.utils import PickpodUtils


def my_pickpod_whisper(audio_doc: AudioDocument, task_language: str = None, task_prompt: str = None, task_queue: Queue = None) -> None:
    task_language, task_probability = PickpodUtils.pickpod_whisper(audio_doc, task_language, task_prompt, task_queue)
    task_queue.put(None)
    task_queue.put((task_language, task_probability))


def my_pickpod_task(audio_doc: AudioDocument, task_config: TaskConfig):
    try:
        st.caption("2⃣️ 获取音频文件文稿", unsafe_allow_html=False)
        start_time = time.time()
        task_queue = Queue()
        task_thread = threading.Thread(target=my_pickpod_whisper, args=(audio_doc, task_config.language, task_config.prompt, task_queue, ))
        task_thread.start()
        while True:
            sentence_document = task_queue.get()
            if not sentence_document:
                break
            column_start, column_content = st.columns([1, 6])
            with column_start:
                st.text("%.2fs" % (sentence_document.start))
            with column_content:
                st.text(str(sentence_document.content))
        task_thread.join()
        task_config.language, task_probability = task_queue.get()
        st.text(f"已检测到音频文件的语言为：{task_config.language}\n评估检测准确率为：{task_probability}%\n处理中，请稍后......")
        st.info(f"ℹ️ 音频文件文稿已完成，用时：{time.time() - start_time}秒")

        st.caption("3⃣️ 执行音频文件声纹分割聚类", unsafe_allow_html=False)
        if task_config.pipeline:
            start_time = time.time()
            PickpodUtils.pickpod_pyannote(audio_doc, task_config.hugging_face, os.path.join(task_config.ydl_path, "wav"))
            st.info(f"ℹ️ 音频文件声纹分割聚类完成，用时：{time.time() - start_time}秒")
        else:
            st.info(f"ℹ️ 音频文件声纹分割聚类已跳过")

        claude_client = ClaudeClient(key_claude=task_config.claude)

        st.caption("4⃣️ 提取音频文件关键词", unsafe_allow_html=False)
        if task_config.keywords:
            if task_config.language == "zh":
                audio_doc.keywords = claude_client.get_keywords_zh(" ".join([x.content for x in audio_doc.sentence]))
            else:
                audio_doc.keywords = claude_client.get_keywords_en(" ".join([x.content for x in audio_doc.sentence]))
        else:
            st.info(f"ℹ️ 提取音频文件关键词已跳过")

        st.caption("5⃣️ 提取音频文件文稿摘要", unsafe_allow_html=False)
        if task_config.summary:
            if task_config.language == "zh":
                audio_doc.summary = claude_client.get_summary_zh(" ".join([x.content for x in audio_doc.sentence]))
            else:
                audio_doc.summary = claude_client.get_summary_en(" ".join([x.content for x in audio_doc.sentence]))
        else:
            st.info(f"ℹ️ 提取音频文件文稿摘要已跳过")

        st.caption("6⃣️ 提取音频文件表述观点", unsafe_allow_html=False)
        if task_config.views:
            if task_config.language == "zh":
                audio_doc.views = claude_client.get_views_zh(" ".join([x.content for x in audio_doc.sentence]))
            else:
                audio_doc.views = claude_client.get_views_en(" ".join([x.content for x in audio_doc.sentence]))
        else:
            st.info(f"ℹ️ 提取音频文件表述观点已跳过")

    except Exception as e:
        st.error("语音识别处理失败，错误码：{}，错误信息：{}。".format(e.args[0], e.args[-1]))

    finally:
        audio_doc.save_as_json(json_path=f"{task_config.ydl_path}/doc/{audio_doc.uuid}.json")
