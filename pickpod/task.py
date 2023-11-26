# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import json
import os
import time
from copy import deepcopy
from typing import Any, Dict, List

from pydub import AudioSegment

from pickpod.api import ClaudeClient, s2t
from pickpod.config import DBClient, TaskConfig
from pickpod.draft import AudioDraft, SentenceDraft, SummaryDraft, ViewDraft
from pickpod.utils import PickpodUtils


class PickpodTask(object):

    def __init__(self, audio_draft: AudioDraft, task_config: TaskConfig) -> None:
        self.audio_draft = audio_draft
        self.task_config = task_config
        self.sentence_draft = list()
        self.sentence_pipeline = list()
        self.sentence_text = ""
        self.summary_draft = list()
        self.view_draft = list()
        self.claude_client = ClaudeClient(key_claude=self.task_config.claude, http_proxy=self.task_config.proxy)

    def pickpod_with_url(self) -> None:
        try:
            start_time = time.time()
            if not self.task_config.ydl_option.get("outtmpl"):
                self.task_config.ydl_option["outtmpl"] = f"{self.task_config.path_wav}/{self.audio_draft.uuid}.%(ext)s"
            if not self.task_config.ydl_option.get("proxy") and self.task_config.proxy:
                self.task_config.ydl_option["proxy"] = self.task_config.proxy
            PickpodUtils.pickpod_ytdlp(self.audio_draft, self.task_config.ydl_option)
            print(f"The downloading is done, using time: {time.time() - start_time} s")

            self.pickpod_all_task()
        except Exception as e:
            print("Pickpod task failed, CODE: {}, INFO: {}.".format(e.args[0], e.args[-1]))
        finally:
            print("Pickpod task completed.")

    def pickpod_with_local(self) -> None:
        try:
            self.audio_draft.path = os.path.abspath(self.audio_draft.path)
            audio_title, audio_ext = os.path.splitext(os.path.basename(self.audio_draft.path))
            self.audio_draft.title = audio_title
            self.audio_draft.ext = audio_ext[1:]
            self.audio_draft.duration = len(AudioSegment.from_file(self.audio_draft.path)) / 1000

            self.pickpod_all_task()
        except Exception as e:
            print("Pickpod task failed, CODE: {}, INFO: {}.".format(e.args[0], e.args[-1]))
        finally:
            print("Pickpod task completed.")

    def pickpod_all_task(self) -> None:
        start_time = time.time()
        _ = PickpodUtils.pickpod_whisper(self.audio_draft, self.task_config.language, self.task_config.prompt, self.sentence_draft)
        self.task_config.language = self.task_config.language if self.task_config.language else self.audio_draft.language
        self.sentence_text = " ".join([x.content for x in self.sentence_draft])
        print(f"The transcription is done, using time: {time.time() - start_time} s")

        if self.task_config.pipeline:
            start_time = time.time()
            self.sentence_pipeline = PickpodUtils.pickpod_pyannote(self.audio_draft, self.task_config.hugging_face, self.task_config.path_wav)
            print(f"The speaker diarization is done, using time: {time.time() - start_time} s")
            PickpodUtils.get_speaker_by_time(self.sentence_draft, self.sentence_pipeline)
        else:
            print("The speaker diarization has skipped.")

        if self.task_config.keyword:
            print("Getting audio keywords.")
            if self.task_config.language == "zh":
                self.audio_draft.keyword = "\n".join(self.claude_client.get_keyword_zh(self.sentence_text))
            else:
                self.audio_draft.keyword = "\n".join(self.claude_client.get_keyword_en(self.sentence_text))
        else:
            print("The claude keywords have skipped.")

        if self.task_config.summary:
            print("Getting audio summary.")
            if self.task_config.language == "zh":
                self.summary_draft = [
                    SummaryDraft(
                        summary_aid=self.audio_draft.uuid,
                        summary_content=x[1],
                        summary_start=x[0]
                        )
                    for x in self.claude_client.get_summary_zh(self.audio_draft.duration, self.sentence_text)
                    ]
            else:
                self.summary_draft = [
                    SummaryDraft(
                        summary_aid=self.audio_draft.uuid,
                        summary_content=x[1],
                        summary_start=x[0]
                        )
                    for x in self.claude_client.get_summary_en(self.audio_draft.duration, self.sentence_text)
                    ]
        else:
            print("The claude summary has skipped.")

        if self.task_config.view:
            print("Getting audio views.")
            if self.task_config.language == "zh":
                self.view_draft = [
                    ViewDraft(
                        view_aid=self.audio_draft.uuid,
                        view_content=x
                        )
                    for x in self.claude_client.get_view_zh(self.sentence_text)
                    ]
            else:
                self.view_draft = [
                    ViewDraft(
                        view_aid=self.audio_draft.uuid,
                        view_content=x
                        )
                    for x in self.claude_client.get_view_en(self.sentence_text)
                    ]
        else:
            print("The claude views have skipped.")

    def audio_safe_name(self) -> str:
        return self.audio_draft.title \
            .replace("\\", "") \
            .replace("\"", "") \
            .replace("/", "") \
            .replace(":", "") \
            .replace("*", "") \
            .replace("?", "") \
            .replace("<", "") \
            .replace(">", "") \
            .replace("|", "")

    def sentence_merge(self, current_sd: SentenceDraft = None) -> List[SentenceDraft]:
        merge_result = list()
        for sentence in self.sentence_draft:
            if current_sd is None:
                current_sd = deepcopy(sentence)
            elif current_sd.speaker == sentence.speaker:
                current_sd.content = f"{current_sd.content} {sentence.content}"
                current_sd.end = sentence.end
            else:
                merge_result.append(current_sd)
                current_sd = deepcopy(sentence)
        merge_result.append(current_sd)
        return merge_result

    @property
    def __dict__(self) -> Dict[str, Any]:
        return {
            "audio": self.audio_draft.__dict__,
            "sentence": [x.__dict__ for x in self.sentence_draft],
            "summary": [x.__dict__ for x in self.summary_draft],
            "view": [x.__dict__ for x in self.view_draft]
        }

    @property
    def __str__(self) -> str:
        return "\n".join([f"Speaker {x.speaker} (from {s2t(x.start)} to {s2t(x.end)}): {x.content}" for x in self.sentence_merge()])

    def save_to_json(self, json_path: str = "", use_title: bool = False) -> None:
        if not json_path:
            json_path = f"{self.audio_safe_name()}.json" if use_title else f"{self.audio_draft.uuid}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.__dict__, indent=4, separators=(",", ": "), ensure_ascii=False))

    def save_to_txt(self, txt_path: str = "", use_title: bool = True) -> None:
        if not txt_path:
            txt_path = f"{self.audio_safe_name()}.txt" if use_title else f"{self.audio_draft.uuid}.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(self.__str__)

    def save_to_db(self) -> None:
        db_client = DBClient(self.task_config.path_db)
        db_sql = [self.audio_draft.insert()]
        for sd in self.sentence_draft:
            db_sql.append(sd.insert())
        for sd in self.summary_draft:
            db_sql.append(sd.insert())
        for vd in self.view_draft:
            db_sql.append(vd.insert())
        for x, y in db_sql:
            db_client.execute(x, y)
        db_client.close()
