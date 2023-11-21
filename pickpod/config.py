# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import os
import sqlite3
from typing import Any, Dict


# yt-dlp basic configuration
YDL_OPTION = {
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
            ydl_option: Dict[str, Any] = None, # Configuration of yt_dlp
            path_wav: str = "", # WAV output path
            path_db: str = "", # Database save path
            task_language: str = "", # Audio language for WhisperModel
            task_prompt: str = "", # Audio prompt for WhisperModel
            task_proxy: str = "",
            pipeline: bool = False, # Get speaker diarization or not
            keyword: bool = False, # Get keyword or not
            summary: bool = False, # Get summary or not
            view: bool = False # Get view or not
            ) -> None:
        self.hugging_face = key_hugging_face
        self.claude = key_claude
        self.ydl_option = ydl_option if ydl_option else YDL_OPTION
        self.path_wav = path_wav if path_wav else os.getcwd()
        self.path_db = path_db if path_db else os.getcwd()
        self.language = task_language if task_language else None
        self.prompt = task_prompt if task_prompt else None
        self.proxy = task_proxy if task_proxy else None
        self.pipeline = pipeline
        self.keyword = keyword
        self.summary = summary
        self.view = view

class DBClient(object):

    def __init__(self, path_db: str = "", name_db: str = "pickpod.db") -> None:
        self.conn = sqlite3.connect(os.path.join(path_db, name_db))

    def create_tb(self) -> None:
        cur = self.conn.cursor()
        cur.executescript("""
            PRAGMA foreign_keys = false;

            -- ----------------------------
            -- Table structure for audio
            -- ----------------------------
            DROP TABLE IF EXISTS "audio";
            CREATE TABLE "audio" (
            "id" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM PRIMARY KEY AUTOINCREMENT,
            "uuid" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
            "title" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
            "ext" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
            "web" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
            "url" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
            "duration" real NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
            "language" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
            "description" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
            "keyword" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
            "path" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
            "origin" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
            "status" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 1 COLLATE RTRIM,
            "createTime" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
            "updateTime" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM
            );

            -- ----------------------------
            -- Table structure for formation
            -- ----------------------------
            DROP TABLE IF EXISTS "formation";
            CREATE TABLE "formation" (
            "id" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM PRIMARY KEY AUTOINCREMENT,
            "uuid" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
            "audioId" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
            "content" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
            "mark" real NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
            "target" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
            "status" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 1 COLLATE RTRIM,
            "createTime" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
            "updateTime" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM
            );

            -- ----------------------------
            -- Table structure for sentence
            -- ----------------------------
            DROP TABLE IF EXISTS "sentence";
            CREATE TABLE "sentence" (
            "id" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM PRIMARY KEY AUTOINCREMENT,
            "uuid" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
            "audioId" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
            "content" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
            "start" real NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
            "end" real NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
            "speaker" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
            "status" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 1 COLLATE RTRIM,
            "createTime" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
            "updateTime" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM
            );

            -- ----------------------------
            -- Auto increment value for audio
            -- ----------------------------
            UPDATE "main"."sqlite_sequence" SET seq = 0 WHERE name = 'audio';

            -- ----------------------------
            -- Auto increment value for formation
            -- ----------------------------
            UPDATE "main"."sqlite_sequence" SET seq = 0 WHERE name = 'formation';

            -- ----------------------------
            -- Auto increment value for sentence
            -- ----------------------------
            UPDATE "main"."sqlite_sequence" SET seq = 0 WHERE name = 'sentence';

            PRAGMA foreign_keys = true;
        """)
        cur.close()
        self.conn.commit()

    @staticmethod
    def find_tb(name_tb: str) -> (str, tuple):
        return "SELECT count(1) FROM sqlite_master WHERE type=? AND name=?", ("table", name_tb)

    def execute(self, sql: str = "", arg: tuple = tuple()) -> None:
        cur = self.conn.cursor()
        cur.execute(sql, arg)
        print(f"Affected rows: {cur.rowcount}")
        cur.close()
        self.conn.commit()

    def fetchone(self, sql: str = "", arg: tuple = tuple()) -> tuple:
        cur = self.conn.cursor()
        cur.execute(sql, arg)
        obj = cur.fetchone()
        cur.close()
        self.conn.commit()
        return obj

    def fetchall(self, sql: str = "", arg: tuple = tuple()) -> tuple:
        cur = self.conn.cursor()
        cur.execute(sql, arg)
        obj = cur.fetchall()
        cur.close()
        self.conn.commit()
        return obj

    def close(self) -> None:
        self.conn.close()
