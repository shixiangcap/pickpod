# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import os
from typing import Any, Dict


# yt-dlp basic configuration
YDL_OPTIONS = {
    "format": "m4a/bestaudio/best",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "m4a",
        }]
    }


class TaskConfig(object):
    """
    Configuration class for a pickpod task.
    Every argument is optional.
    If using speaker diarization, a Hugging Face Key is required.
    If using summary, keywords, or views, a Claude Key is needed.
    """

    def __init__(
            self,
            key_hugging_face: str = "", # User key for hugging face
            key_claude: str = "", # User key for claude
            ydl_options: Dict[str, Any] = None, # Configuration of yt_dlp
            ydl_path: str = "", # Audio download path
            task_language: str = "", # Audio language for WhisperModel
            task_prompt: str = "", # Audio prompt for WhisperModel
            queue: bool = False, # Get sentence queue or not
            pipeline: bool = False, # Get speaker diarization or not
            keyword: bool = False, # Get keyword or not
            summary: bool = False, # Get summary or not
            view: bool = False # Get view or not
            ) -> None:
        self.hugging_face = key_hugging_face
        self.claude = key_claude
        self.ydl_options = ydl_options if ydl_options else YDL_OPTIONS
        self.ydl_path = ydl_path if ydl_path else os.getcwd()
        self.language = task_language if task_language else None
        self.prompt = task_prompt if task_prompt else None
        self.queue = queue
        self.pipeline = pipeline
        self.keywords = keyword
        self.summary = summary
        self.views = view
