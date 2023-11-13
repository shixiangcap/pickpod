# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import re
from typing import Dict, List

import requests


PROMPT_KEYWORD_ZH = "Human:你的任务是对下面的文本提取不超过10个关键词，每个关键词都应简明扼要，不能重复，且必须用中文输出，文本如下：\"{}\"\n\nAssistant:"
PROMPT_KEYWORD_EN = "Human:Your task is to extract no more than 10 keywords from the received text. Each keyword should be concise and non-repetitive. The text is as follows: \"{}\"\n\nAssistant:"
PROMPT_SUMMARY_ZH = "Human:从音频文本中创建不超过30个关键时刻，包括时间，您的答案应简明，并以00:00:00开头，以{}结尾。你的回答必须翻译成简体中文。\n\nAssistant:好的，我已经清楚规则了，我会用简体中文根据我所接收到的文本创建包括时间的关键时刻。\n\nHuman:文本：\"大家好,这里是阶梯计划第五期，我们做阶梯计划这个平台主要是希望针对加密生态的关键问题进行真诚的讨论与深入的分析。介绍一下，我是Frank Lee，DeFi和智能合约安全从业者。\"\n\nAssistant:00:00:00 - 介绍节目\n\nHuman:文本:\"{}\"\n\nAssistant:"
PROMPT_SUMMARY_EN = "Human:Create no more than 30 key moments from the audio text, including the time. Your answer should be concise and start with 00:00:00, end with {}. Your answer must be translated into English.\n\nAssistant:Sure, I konw the rule. I'll create key moments from the recived text including the time in English.\n\nHuman:TEXT: \"Hello everyone, this is phase 5 of the Ladder Project. We created the Ladder Project as a platform for sincere discussion and in-depth analysis of key issues in the crypto ecosystem. By the way, I'm Frank Lee, a DeFi and smart contract security practitioner.\"\n\nAssistant:00:00:00 - Introducing the Program\n\nHuman:TEXT: \"{}\"\n\nAssistant:"
PROMPT_VIEW_ZH = "Human:用中文回答文中有哪些反常识或者有尖锐态度的新观点？请输出7到8个，并说明和常识不一致的具体原因。\n\nAssistant:好的，我明白要求和输出的格式了，请给我具体的文字。\n\nHuman:文本：\"{}\"\n\nAssistant:"
PROMPT_VIEW_EN = "Human:What unconventional or sharp attitudes are there in the following transcript? List the five most important ones and explain why they contradict the consensus. The language you respond in must be consistent with the language of the transcript. The text is as follows: \"{}\"\n\nAssistant:"
PROMPT_RECOMMEND_NONE = "Human:请对以下{}段不同的音频文本进行排序。对于表达的观点越新颖、尖锐、反常识的音频文本，它的排序结果应当越靠前，我越有可能收听。你可以直接输出一串代表推荐顺序的阿拉伯数字，不用附加额外说明。\n\nAssistant:好的，我明白要求和输出的格式了，请给我具体的文字。\n\nHuman:音频文本：\"{}\"\n\nAssistant:"
PROMPT_RECOMMEND_WIKI = "Human:请对以下{}段不同的音频文本进行排序，我将分别提供一系列我感兴趣和不感兴趣的观点由于参考。对于表达的观点符合我的情趣，且越新颖、尖锐、反常识的音频文本，它的排序结果应当越靠前，我越有可能收听；反之对于表达的观点令我不感兴趣，或平庸并已经成为常识的音频文本，它的排序应当靠后，我不会收听。你可以直接输出一串代表推荐顺序的阿拉伯数字，不用附加额外说明。\n\nAssistant:好的，我明白要求和输出的格式了，请给我具体的文字。\n\nHuman:我感兴趣的观点：\"{}\"\n\n我不感兴趣的观点：\"{}\"\n\n音频文本：\"{}\"\n\nAssistant:"


def t2s(t: str = "") -> int:
    h, m, s = t.strip().split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)

def s2t(t: float = 0.0) -> str:
    m, s = divmod(int(t), 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)


class ClaudeClient(object):

    def __init__(self, key_claude: str = "", http_proxy: str = None) -> None:
        self.url = "https://api.anthropic.com/v1/complete"
        self.header = {
            "accept": "application/json",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "x-api-key": key_claude
        }
        self.body = {"model": "claude-2", "max_tokens_to_sample": 10000}
        self.proxy = {"http": http_proxy, "https": http_proxy} if http_proxy else None

    def get_keyword_zh(self, doc: str = "") -> List[str]:
        self.body["prompt"] = PROMPT_KEYWORD_ZH.format(doc)
        claude_response = requests.request("POST", url=self.url, headers=self.header, json=self.body, proxies=self.proxy)
        claude_keyword = claude_response.json().get("completion", "")
        print(claude_keyword)
        return [y.strip() for x in [
            re.sub("^\d*\.\s|^\d*\.|^-\s|^-|^\s*|\s$", "", x).split(",")
            for x in claude_keyword.split("\n\n")[1].split("\n")
        ] for y in x]

    def get_keyword_en(self, doc: str = "") -> List[str]:
        self.body["prompt"] = PROMPT_KEYWORD_EN.format(doc)
        claude_response = requests.request("POST", url=self.url, headers=self.header, json=self.body, proxies=self.proxy)
        claude_keyword = claude_response.json().get("completion", "")
        print(claude_keyword)
        return [y.strip() for x in [
            re.sub("^\d*\.\s|^\d*\.|^-\s|^-|^\s*|\s$", "", x).split(",")
            for x in claude_keyword.split("\n\n")[1].split("\n")
            ] for y in x]

    def get_summary_zh(self, duration: float = 0.0, doc: str = "") -> List[tuple]:
        self.body["prompt"] = PROMPT_SUMMARY_ZH.format(s2t(duration), doc)
        claude_response = requests.request("POST", url=self.url, headers=self.header, json=self.body, proxies=self.proxy)
        claude_summary = claude_response.json().get("completion", "")
        print(claude_summary)
        return [
            (t2s(re.match("^\s*\d\d:\d\d:\d\d", x).group()), re.sub("^\s*\d\d:\d\d:\d\d\s*-\s*", "", x).strip())
            for x in claude_summary.split("\n")
            if x and re.match("^\s*\d\d:\d\d:\d\d", x)
        ]

    def get_summary_en(self, duration: float = 0.0, doc: str = "") -> List[tuple]:
        self.body["prompt"] = PROMPT_SUMMARY_EN.format(s2t(duration), doc)
        claude_response = requests.request("POST", url=self.url, headers=self.header, json=self.body, proxies=self.proxy)
        claude_summary = claude_response.json().get("completion", "")
        print(claude_summary)
        return [
            (t2s(re.match("^\s*\d\d:\d\d:\d\d", x).group()), re.sub("^\s*\d\d:\d\d:\d\d\s*-\s*", "", x).strip())
            for x in claude_summary.split("\n")
            if x and re.match("^\s*\d\d:\d\d:\d\d", x)
        ]

    def get_view_zh(self, doc: str = "") -> List[str]:
        self.body["prompt"] = PROMPT_VIEW_ZH.format(doc)
        claude_response = requests.request("POST", url=self.url, headers=self.header, json=self.body, proxies=self.proxy)
        claude_view = claude_response.json().get("completion", "")
        print(claude_view)
        return [
            re.sub("^\d*\.\s|^\d*\.|^-\s|^-|^\s*|\s$", "", x).strip()
            for x in claude_view.split("\n")
            if x
        ]

    def get_view_en(self, doc: str = "") -> List[str]:
        self.body["prompt"] = PROMPT_VIEW_EN.format(doc)
        claude_response = requests.request("POST", url=self.url, headers=self.header, json=self.body, proxies=self.proxy)
        claude_view = claude_response.json().get("completion", "")
        print(claude_view)
        return [
            re.sub("^\d*\.\s|^\d*\.|^-\s|^-|^\s*|\s$", "", x).strip()
            for x in claude_view.split("\n")
            if x
        ]

    def get_recommend_none(self, doc_list: List[str] = list()) -> List[int]:
        self.body["prompt"] = PROMPT_RECOMMEND_NONE.format(
            len(doc_list),
            "\n\n".join([f"第{x + 1}篇音频文本: {y}" for x, y in enumerate(doc_list)])
        )
        claude_response = requests.request("POST", url=self.url, headers=self.header, json=self.body, proxies=self.proxy)
        claude_sort = claude_response.json().get("completion", "")
        print(claude_sort)
        claude_sort = [max(int(x.strip()) - 1, 0) for x in re.findall(r"\s\d+|\d+\s", claude_sort) if int(x.strip()) <= len(doc_list)]
        claude_sort = sorted(set(claude_sort), key=claude_sort.index)
        claude_sort.extend(list(set([x for x in range(len(doc_list))]) - set(claude_sort)))
        print(claude_sort)
        return claude_sort

    def get_recommend_wiki(self, doc_list: List[str] = list(), view_dict: Dict[bool, List[str]] = dict()) -> List[int]:
        self.body["prompt"] = PROMPT_RECOMMEND_WIKI.format(
            len(doc_list),
            "\n\n".join([f"观点{x + 1}: {y}" for x, y in enumerate(view_dict[True])]),
            "\n\n".join([f"观点{x + 1}: {y}" for x, y in enumerate(view_dict[False])]),
            "\n\n".join([f"第{x + 1}篇音频文本: {y}" for x, y in enumerate(doc_list)])
        )
        claude_response = requests.request("POST", url=self.url, headers=self.header, json=self.body, proxies=self.proxy)
        claude_sort = claude_response.json().get("completion", "")
        print(claude_sort)
        claude_sort = [max(int(x.strip()) - 1, 0) for x in re.findall(r"\s\d+|\d+\s", claude_sort) if int(x.strip()) <= len(doc_list)]
        claude_sort = sorted(set(claude_sort), key=claude_sort.index)
        claude_sort.extend(list(set([x for x in range(len(doc_list))]) - set(claude_sort)))
        print(claude_sort)
        return claude_sort
