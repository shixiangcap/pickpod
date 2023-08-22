# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import json
import time
import uuid
from typing import Any, Dict, List


class SentenceDocument(object):

    def __init__(
            self,
            sentence_start: float = 0.0, # Sentence start timestamp
            sentence_end: float = 0.0, # Sentence end timestamp
            sentence_content: str = "", # Sentence content
            sentence_speaker: int = 0 # Sentence speaker identifier
            ) -> None:
        self.start = sentence_start
        self.end = sentence_end
        self.content = sentence_content
        self.speaker = sentence_speaker


class SummaryDocument(object):

    def __init__(
            self,
            summary_start: int = 0, # Summary start timestamp
            summary_content: str = "" # Summary content
            ) -> None:
        self.start = summary_start
        self.content = summary_content


class ViewDocument(object):

    def __init__(
            self,
            view_content: str = "", # View content
            view_mark: bool = False # View evaluation
            ) -> None:
        self.content = view_content
        self.mark = view_mark


class AudioDocument(object):

    def __init__(
            self,
            audio_uuid: str = "", # Audio UUID
            audio_title: str = "", # Audio title
            audio_ext: str = "", # Audio extension
            audio_web: str = "", # Audio website
            audio_url: str = "", # Audio download
            audio_length: float = 0.0, # Audio duration
            audio_description: str = "", # Audio description
            audio_keywords: List[str] = list(), # Audio keywords
            audio_path: str = "", # Audio file path
            audio_sentence: List[SentenceDocument] = list(), # Audio sentence list
            audio_summary: List[SummaryDocument] = list(), # Audio summary list
            audio_view: List[ViewDocument] = list(), # Audio viewpoint list
            audio_origin: str = "", # Audio origin
            audio_ctime: int = 0, # Audio create time
            audio_utime: int = 0 # Audio update time
            ) -> None:
        self.uuid = audio_uuid if audio_uuid != "" else str(uuid.uuid4())
        self.title = audio_title
        self.ext = audio_ext
        self.web = audio_web
        self.url = audio_url
        self.length = audio_length
        self.description = audio_description
        self.keywords = audio_keywords
        self.path = audio_path
        self.sentence = audio_sentence
        self.summary = audio_summary
        self.views = audio_view
        self.origin = audio_origin
        self.ctime = audio_ctime if audio_ctime != 0 else int(time.time())
        self.utime = audio_utime if audio_utime != 0 else int(time.time())

    @property
    def __dict__(self) -> Dict[str, Any]:
        return {
            "uuid": self.uuid,
            "title": self.title,
            "ext": self.ext,
            "web": self.web,
            "url": self.url,
            "length": self.length,
            "description": self.description,
            "keywords": self.keywords,
            "path": self.path,
            "sentence": [x.__dict__ for x in self.sentence],
            "summary": [x.__dict__ for x in self.summary],
            "views": [x.__dict__ for x in self.views],
            "origin": self.origin,
            "ctime": self.ctime,
            "utime": self.utime
        }

    def doc_update_time(self) -> None:
        self.utime = int(time.time())

    def doc_safe_name(self) -> str:
        return self.title \
            .replace("\\", "") \
            .replace("\"", "") \
            .replace("/", "") \
            .replace(":", "") \
            .replace("*", "") \
            .replace("?", "") \
            .replace("<", "") \
            .replace(">", "") \
            .replace("|", "")

    def save_as_json(self, json_path: str = "", use_title: bool = False) -> None:
        if not json_path:
            if use_title:
                json_path = f"{self.doc_safe_name()}.json"
            else:
                json_path = f"{self.uuid}.json"
        self.doc_update_time()
        with open(json_path, "w") as f:
            f.write(json.dumps(self.__dict__, indent=4, separators=(",", ": "), ensure_ascii=False))
