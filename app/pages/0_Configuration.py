# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import os
import subprocess

import requests
import streamlit as st
import torch
from dotenv import find_dotenv, load_dotenv
from pyannote.audio import Pipeline


os.chdir(os.path.split(os.path.realpath(__file__))[0])

# load from env
load_dotenv(find_dotenv(), override=True)
HUGGING_FACE_KEY = os.getenv("HUGGING_FACE_KEY")
CLAUDE_KEY = os.getenv("CLAUDE_KEY")
LISTEN_NOTE_KEY = os.getenv("LISTEN_NOTE_KEY")


def env_set(input_hugging_face: str, input_claude: str, input_listen_note: str) -> None:
    with open("./.env", "w") as f:
        f.write(f"HUGGING_FACE_KEY={input_hugging_face}\n")
        f.write(f"CLAUDE_KEY={input_claude}\n")
        f.write(f"LISTEN_NOTE_KEY={input_listen_note}\n")


st.experimental_set_query_params()
st.set_page_config(
    page_title="Pickpod Configuration",
    page_icon="../library/logo.png",
    menu_items={
        "Get Help": "https://github.com/shixiangcap/pickpod",
        "Report a bug": "https://github.com/shixiangcap/pickpod",
        "About": "### Pickpod 是一个基于 `Streamlit` 框架构建的网络服务：\n\n### 它根据您自己的`非共识观点`为您推荐播客。"
    }
)

with st.sidebar:

    st.header("配置第三方工具")

    input_hugging_face = st.text_input("Hugging Face Key", value=HUGGING_FACE_KEY, help="请输入您的 Hugging Face 开发者密钥")

    input_claude = st.text_input("Claude Key", value=CLAUDE_KEY, help="请输入您的 Claude 开发者密钥")

    input_listen_note = st.text_input("Listen Notes Key", value=LISTEN_NOTE_KEY, help="请输入您的 Listen Notes 开发者密钥")

    button_save, button_reset = st.columns([1, 1])

    with button_save:
        click_save=st.button("保存并测试", help="您输入的密钥将覆盖原有配置", on_click=env_set, kwargs=dict(input_hugging_face=input_hugging_face, input_claude=input_claude, input_listen_note=input_listen_note), use_container_width=True)

    with button_reset:
        click_reset = st.button("重置", help="您的配置信息将被清空", on_click=env_set, kwargs=dict(input_hugging_face="YOUR_HUGGING_FACE_KEY", input_claude="YOUR_CLAUDE_KEY", input_listen_note="YOUR_LISTEN_NOTE_KEY"), use_container_width=True)

st.write("# 测试 Pickpod 配置信息 🔧")

if not click_save:

    st.write("#### CUDA 可用性")
    st.code(">>> import torch\n>>> torch.cuda.is_available()", language="python")

    st.write("#### FFMPEG 可用性")
    st.code(">>> ffmpeg -version", language="bash")

    st.write("#### Hugging Face 可用性")
    st.code(">>> from pyannote.audio import Pipeline\n>>> Pipeline.from_pretrained(\"pyannote/speaker-diarization@2.1\", use_auth_token=HUGGING_FACE_KEY)", language="python")

    st.write("#### Claude 可用性")
    st.code("curl --request POST --url https://api.anthropic.com/v1/complete \\\n     --header \"accept: application/json\" \\\n     --header \"anthropic-version: 2023-06-01\" \\\n     --header \"content-type: application/json\" \\\n     --header \"x-api-key: $ANTHROPIC_API_KEY\" \\\n     --data '{\"model\": \"claude-2\", \"max_tokens_to_sample\": 256, \"prompt\": \"Human: Hello, world!\\n\\nAssistant:\"}'", language="bash")

    test_region, test_language = st.columns([1, 1])

    with test_region:
        st.write("#### Listen Notes 支持的国家和地区")
        st.code("curl -X GET -s \"https://listen-api.listennotes.com/api/v2/regions\" \\\n     -H \"X-ListenAPI-Key: <SIGN UP FOR API KEY>\"", language="bash")

    with test_language:
        st.write("#### Listen Notes 支持的语言")
        st.code("curl -X GET -s \"https://listen-api.listennotes.com/api/v2/languages\" \\\n     -H \"X-ListenAPI-Key: <SIGN UP FOR API KEY>\"", language="bash")

elif click_save and not click_reset:

    st.write("#### CUDA 可用性")
    test_cuda = torch.cuda.is_available()
    code_cuda = f">>> import torch\n>>> torch.cuda.is_available()\n    {test_cuda}"
    st.code(code_cuda, language="python")

    st.write("#### FFMPEG 可用性")
    try:
        test_ffmpeg = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        info_ffmpeg = test_ffmpeg.stdout.decode("utf-8").replace("\n", "\n    ")
        error_ffmpeg = f'''错误代码：{test_ffmpeg.returncode}\n错误信息：{test_ffmpeg.stderr.decode("utf-8")}'''
    except FileNotFoundError as e:
        info_ffmpeg = ""
        error_ffmpeg = f"错误代码：{e.errno}\n错误信息：{e.strerror}"
    code_ffmpeg = f">>> ffmpeg -version\n    {info_ffmpeg}\n{error_ffmpeg}"
    st.code(code_ffmpeg, language="bash")

    st.write("#### Hugging Face 可用性")
    pyannote_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1", use_auth_token=HUGGING_FACE_KEY)
    if pyannote_pipeline is None:
        test_hugging_face = f"Could not download \"pyannote/speaker-diarization\" pipeline.\n    It might be because the pipeline is private or gated so make\n    sure to authenticate. Visit https://hf.co/settings/tokens to\n    create your access token and retry with:\n\n    >>> Pipeline.from_pretrained(\"pyannote/speaker-diarization\", use_auth_token=YOUR_AUTH_TOKEN)\n\n    If this still does not work, it might be because the pipeline is gated:\n    visit https://hf.co/pyannote/speaker-diarization to accept the user conditions."
    else:
        test_hugging_face = type(pyannote_pipeline)
    code_hugging_face = f">>> from pyannote.audio import Pipeline\n>>> Pipeline.from_pretrained(\"pyannote/speaker-diarization@2.1\", use_auth_token=HUGGING_FACE_KEY)\n    {test_hugging_face}"
    st.code(code_hugging_face, language="python")

    st.write("#### Claude 可用性")
    url_claude = "https://api.anthropic.com/v1/complete"
    header_claude = {"accept": "application/json", "anthropic-version": "2023-06-01", "content-type": "application/json", "x-api-key": CLAUDE_KEY}
    body_claude = {"model": "claude-2", "max_tokens_to_sample": 256, "prompt": "Human: Hello, world!\n\nAssistant:"}
    resp_claude = requests.request("POST", url=url_claude, headers=header_claude, json=body_claude)
    st.code("curl --request POST --url https://api.anthropic.com/v1/complete \\\n     --header \"accept: application/json\" \\\n     --header \"anthropic-version: 2023-06-01\" \\\n     --header \"content-type: application/json\" \\\n     --header \"x-api-key: $ANTHROPIC_API_KEY\" \\\n     --data '{\"model\": \"claude-2\", \"max_tokens_to_sample\": 256, \"prompt\": \"Human: Hello, world!\\n\\nAssistant:\"}'", language="bash")
    st.json(resp_claude.json(), expanded=True)

    test_region, test_language = st.columns([1, 1])

    with test_region:
        st.write("#### Listen Notes 支持的国家和地区")
        url_region = "https://listen-api.listennotes.com/api/v2/regions"
        header_region = {"X-ListenAPI-Key": LISTEN_NOTE_KEY}
        resp_region= requests.request("GET", url_region, headers=header_region)
        st.code("curl -X GET -s \"https://listen-api.listennotes.com/api/v2/regions\" \\\n     -H \"X-ListenAPI-Key: <SIGN UP FOR API KEY>\"", language="bash")
        st.json(resp_region.json(), expanded=True)

    with test_language:
        st.write("#### Listen Notes 支持的语言")
        url_language = "https://listen-api.listennotes.com/api/v2/languages"
        header_language = {"X-ListenAPI-Key": LISTEN_NOTE_KEY}
        resp_language= requests.request("GET", url_language, headers=header_language)
        st.code("curl -X GET -s \"https://listen-api.listennotes.com/api/v2/languages\" \\\n     -H \"X-ListenAPI-Key: <SIGN UP FOR API KEY>\"", language="bash")
        st.json(resp_language.json(), expanded=True)
