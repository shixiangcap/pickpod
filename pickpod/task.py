# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import os
import time
from queue import Queue

from pydub import AudioSegment

from pickpod.api import ClaudeClient
from pickpod.config import TaskConfig
from pickpod.doc import AudioDocument
from pickpod.utils import PickpodUtils


class PickpodTask(object):

    def __init__(self, audio_doc: AudioDocument, task_config: TaskConfig):
        self.audio_doc = audio_doc
        self.task_config = task_config
        self.task_queue = Queue()
        self.claude_client = ClaudeClient(key_claude=self.task_config.claude)

    def pickpod_with_url(self) -> None:
        try:
            start_time = time.time()
            if not self.task_config.ydl_options.get("outtmpl"):
                self.task_config.ydl_options["outtmpl"] = f"{self.task_config.ydl_path}/{self.audio_doc.uuid}.%(ext)s"
            PickpodUtils.pickpod_ytdlp(self.audio_doc, self.task_config.ydl_options)
            print(f"The downloading is done, using time: {time.time() - start_time} s")

            self.pickpod_all_task()
        except Exception as e:
            print("Pickpod task failed, CODE: {}, INFO: {}.".format(e.args[0], e.args[-1]))
        finally:
            print("Pickpod task completed.")

    def pickpod_with_local(self) -> None:
        try:
            self.audio_doc.path = os.path.abspath(self.audio_doc.path)
            audio_title, audio_ext = os.path.splitext(os.path.basename(self.audio_doc.path))
            self.audio_doc.title = audio_title
            self.audio_doc.ext = audio_ext[1:]
            self.audio_doc.length = len(AudioSegment.from_file(self.audio_doc.path)) / 1000

            self.pickpod_all_task()
        except Exception as e:
            print("Pickpod task failed, CODE: {}, INFO: {}.".format(e.args[0], e.args[-1]))
        finally:
            print("Pickpod task completed.")

    def pickpod_all_task(self) -> None:
        start_time = time.time()
        if self.task_config.queue:
            self.task_config.language, _ = PickpodUtils.pickpod_whisper(self.audio_doc, self.task_config.language, self.task_config.prompt, self.task_queue)
            self.task_queue.put(None)
        else:
            self.task_config.language, _ = PickpodUtils.pickpod_whisper(self.audio_doc, self.task_config.language, self.task_config.prompt, None)
        print(f"The transcription is done, using time: {time.time() - start_time} s")

        if self.task_config.pipeline:
            start_time = time.time()
            PickpodUtils.pickpod_pyannote(self.audio_doc, self.task_config.hugging_face, self.task_config.ydl_path)
            print(f"The speaker diarization is done, using time: {time.time() - start_time} s")
        else:
            print("The speaker diarization has skipped.")

        if self.task_config.keywords:
            print("Getting audio keywords.")
            if self.task_config.language == "zh":
                self.audio_doc.keywords = self.claude_client.get_keywords_zh(" ".join([x.content for x in self.audio_doc.sentence]))
            else:
                self.audio_doc.keywords = self.claude_client.get_keywords_en(" ".join([x.content for x in self.audio_doc.sentence]))
        else:
            print("The claude keywords have skipped.")

        if self.task_config.summary:
            print("Getting audio summary.")
            if self.task_config.language == "zh":
                self.audio_doc.summary = self.claude_client.get_summary_zh(" ".join([x.content for x in self.audio_doc.sentence]))
            else:
                self.audio_doc.summary = self.claude_client.get_summary_en(" ".join([x.content for x in self.audio_doc.sentence]))
        else:
            print("The claude summary has skipped.")

        if self.task_config.views:
            print("Getting audio views.")
            if self.task_config.language == "zh":
                self.audio_doc.views = self.claude_client.get_views_zh(" ".join([x.content for x in self.audio_doc.sentence]))
            else:
                self.audio_doc.views = self.claude_client.get_views_en(" ".join([x.content for x in self.audio_doc.sentence]))
        else:
            print("The claude views have skipped.")
