# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import time
import uuid


class SentenceDraft(object):

    def __init__(
            self,
            sentence_uuid: str = "", # Sentence UUID
            sentence_aid: str = "", # Sentence audio UUID
            sentence_content: str = "", # Sentence content
            sentence_start: float = 0.0, # Sentence start timestamp
            sentence_end: float = 0.0, # Sentence end timestamp
            sentence_speaker: int = 0, # Sentence speaker identifier
            sentence_status: int = 1, # Sentence using status
            sentence_ctime: int = 0, # Sentence create time
            sentence_utime: int = 0 # Sentence update time
            ) -> None:
        self.uuid = sentence_uuid if sentence_uuid else str(uuid.uuid4())
        self.aid = sentence_aid
        self.content = sentence_content
        self.start = sentence_start
        self.end = sentence_end
        self.speaker = sentence_speaker
        self.status = sentence_status
        self.ctime = sentence_ctime if sentence_ctime else int(time.time())
        self.utime = sentence_utime if sentence_utime else int(time.time())

    def insert(self) -> (str, tuple):
        return "INSERT INTO sentence (uuid, audioId, content, start, end, speaker, status, createTime, updateTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (self.uuid, self.aid, self.content, self.start, self.end, self.speaker, self.status, self.ctime, int(time.time()))

    def update(self) -> (str, tuple):
        return "UPDATE sentence SET content=?, start=?, end=?, speaker=?, updateTime=? WHERE uuid=?", (self.content, self.start, self.end, self.speaker, int(time.time()), self.uuid)

    @staticmethod
    def select_by_aid(sentence_aid: str) -> (str, tuple):
        return "SELECT uuid, audioId, content, start, end, speaker, status, createTime, updateTime FROM sentence WHERE audioId=? AND status=? ORDER BY start ASC", (sentence_aid, 1)

    @staticmethod
    def select_by_content(sentence_content: str) -> (str, tuple):
        return "SELECT DISTINCT audioId FROM sentence WHERE content LIKE ? AND status=?", (f"%{sentence_content}%", 1)

    @staticmethod
    def delete_status(sentence_uuid: str) -> (str, tuple):
        return "UPDATE sentence SET status=?, updateTime=? WHERE uuid=?", (0, int(time.time()), sentence_uuid)

    @staticmethod
    def db_init(sentence_draft: tuple) -> object:
        return SentenceDraft(sentence_draft[0], sentence_draft[1], sentence_draft[2], sentence_draft[3], sentence_draft[4], sentence_draft[5], sentence_draft[6], sentence_draft[7], sentence_draft[8])


class SummaryDraft(object):

    def __init__(
            self,
            summary_uuid: str = "", # Summary UUID
            summary_aid: str = "", # Summary audio UUID
            summary_content: str = "", # Summary content
            summary_start: float = 0.0, # Summary start timestamp
            summary_status: int = 1, # Summary using status
            summary_ctime: int = 0, # Summary create time
            summary_utime: int = 0 # Summary update time
            ) -> None:
        self.uuid = summary_uuid if summary_uuid else str(uuid.uuid4())
        self.aid = summary_aid
        self.content = summary_content
        self.start = summary_start
        self.target = 0
        self.status = summary_status
        self.ctime = summary_ctime if summary_ctime else int(time.time())
        self.utime = summary_utime if summary_utime else int(time.time())

    def insert(self) -> (str, tuple):
        return "INSERT INTO formation (uuid, audioId, content, mark, target, status, createTime, updateTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (self.uuid, self.aid, self.content, self.start, self.target, self.status, self.ctime, int(time.time()))

    def update(self) -> (str, tuple):
        return "UPDATE formation SET content=?, mark=?, updateTime=? WHERE uuid=?", (self.content, self.start, int(time.time()), self.uuid)

    @staticmethod
    def select_by_aid(summary_aid: str) -> (str, tuple):
        return "SELECT uuid, audioId, content, mark, status, createTime, updateTime FROM formation WHERE audioId=? AND target=? AND status=? ORDER BY mark ASC", (summary_aid, 0, 1)

    @staticmethod
    def delete_status(summary_uuid: str) -> (str, tuple):
        return "UPDATE formation SET status=?, updateTime=? WHERE uuid=?", (0, int(time.time()), summary_uuid)

    @staticmethod
    def db_init(summary_draft: tuple) -> object:
        return SummaryDraft(summary_draft[0], summary_draft[1], summary_draft[2], summary_draft[3], summary_draft[4], summary_draft[5], summary_draft[6])


class ViewDraft(object):

    def __init__(
            self,
            view_uuid: str = "", # View UUID
            view_aid: str = "", # View audio UUID
            view_content: str = "", # View content
            view_value: int = 1, # View evaluation
            view_status: int = 1, # View using status
            view_ctime: int = 0, # View create time
            view_utime: int = 0 # View update time
            ) -> None:
        self.uuid = view_uuid if view_uuid else str(uuid.uuid4())
        self.aid = view_aid
        self.content = view_content
        self.value = view_value
        self.target = 1
        self.status = view_status
        self.ctime = view_ctime if view_ctime else int(time.time())
        self.utime = view_utime if view_utime else int(time.time())

    def insert(self) -> (str, tuple):
        return "INSERT INTO formation (uuid, audioId, content, mark, target, status, createTime, updateTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (self.uuid, self.aid, self.content, self.value, self.target, self.status, self.ctime, int(time.time()))

    def update(self) -> (str, tuple):
        return "UPDATE formation SET content=?, mark=?, updateTime=? WHERE uuid=?", (self.content, self.value, int(time.time()), self.uuid)

    @staticmethod
    def select_by_aid(view_aid: str) -> (str, tuple):
        return "SELECT uuid, audioId, content, mark, status, createTime, updateTime FROM formation WHERE audioId=? AND target=? AND status=? ORDER BY createTime ASC", (view_aid, 1, 1)

    @staticmethod
    def delete_status(view_uuid: str) -> (str, tuple):
        return "UPDATE formation SET status=?, updateTime=? WHERE uuid=?", (0, int(time.time()), view_uuid)

    @staticmethod
    def db_init(view_draft: tuple) -> object:
        return ViewDraft(view_draft[0], view_draft[1], view_draft[2], view_draft[3], view_draft[4], view_draft[5], view_draft[6])


class WikiDraft(object):

    def __init__(
            self,
            wiki_uuid: str = "", # Wiki UUID
            wiki_aid: str = "", # Wiki audio UUID
            wiki_content: str = "", # Wiki content
            wiki_value: int = 1, # Wiki evaluation
            wiki_status: int = 1, # Wiki using status
            wiki_ctime: int = 0, # Wiki create time
            wiki_utime: int = 0 # Wiki update time
            ) -> None:
        self.uuid = wiki_uuid if wiki_uuid else str(uuid.uuid4())
        self.aid = wiki_aid
        self.content = wiki_content
        self.value = wiki_value
        self.target = 2
        self.status = wiki_status
        self.ctime = wiki_ctime if wiki_ctime else int(time.time())
        self.utime = wiki_utime if wiki_utime else int(time.time())

    def insert(self) -> (str, tuple):
        return "INSERT INTO formation (uuid, audioId, content, mark, target, status, createTime, updateTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (self.uuid, self.aid, self.content, self.value, self.target, self.status, self.ctime, int(time.time()))

    def update(self) -> (str, tuple):
        return "UPDATE formation SET content=?, mark=?, updateTime=? WHERE uuid=?", (self.content, self.value, int(time.time()), self.uuid)

    @staticmethod
    def select_by_aid(wiki_aid: str) -> (str, tuple):
        return "SELECT uuid, audioId, content, mark, status, createTime, updateTime FROM formation WHERE audioId=? AND target=? AND status=? ORDER BY createTime ASC", (wiki_aid, 2, 1)

    @staticmethod
    def delete_status(wiki_uuid: str) -> (str, tuple):
        return "UPDATE formation SET status=?, updateTime=? WHERE uuid=?", (0, int(time.time()), wiki_uuid)

    @staticmethod
    def select_by_value(wiki_value: int) -> (str, tuple):
        return "SELECT uuid, audioId, content, mark, status, createTime, updateTime FROM formation WHERE mark=? AND target=? AND status=? ORDER BY createTime ASC", (wiki_value, 2, 1)

    @staticmethod
    def select_all() -> str:
        return "SELECT uuid, audioId, content, mark, status, createTime, updateTime FROM formation WHERE target=2 AND status=1 ORDER BY createTime ASC"

    @staticmethod
    def db_init(wiki_draft: tuple) -> object:
        return WikiDraft(wiki_draft[0], wiki_draft[1], wiki_draft[2], wiki_draft[3], wiki_draft[4], wiki_draft[5], wiki_draft[6])


class AudioDraft(object):

    def __init__(
            self,
            audio_uuid: str = "", # Audio UUID
            audio_title: str = "", # Audio title
            audio_ext: str = "", # Audio extension
            audio_web: str = "", # Audio website
            audio_url: str = "", # Audio download
            audio_duration: float = 0.0, # Audio duration
            audio_language: str = "", # Audio language
            audio_description: str = "", # Audio description
            audio_keyword: str = "", # Audio keyword
            audio_path: str = "", # Audio file path
            audio_origin: str = "", # Audio origin
            audio_status: int = 1, # Audio using status
            audio_ctime: int = 0, # Audio create time
            audio_utime: int = 0 # Audio update time
            ) -> None:
        self.uuid = audio_uuid if audio_uuid else str(uuid.uuid4())
        self.title = audio_title
        self.ext = audio_ext
        self.web = audio_web
        self.url = audio_url
        self.duration = audio_duration
        self.language = audio_language
        self.description = audio_description
        self.keyword = audio_keyword
        self.path = audio_path
        self.origin = audio_origin
        self.status = audio_status
        self.ctime = audio_ctime if audio_ctime else int(time.time())
        self.utime = audio_utime if audio_utime else int(time.time())

    def insert(self) -> (str, tuple):
        return "INSERT INTO audio (uuid, title, ext, web, url, duration, language, description, keyword, path, origin, status, createTime, updateTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (self.uuid, self.title, self.ext, self.web, self.url, self.duration, self.language, self.description, self.keyword, self.path, self.origin, self.status, self.ctime, int(time.time()))

    def update(self) -> (str, tuple):
        return "UPDATE audio SET title=?, web=?, url=?, language=?, description=?, keyword=?, origin=?, updateTime=? WHERE uuid=?", (self.title, self.web, self.url, self.language, self.description, self.keyword, self.origin, int(time.time()), self.uuid)

    @staticmethod
    def select_by_uuid(audio_uuid: str) -> (str, tuple):
        return "SELECT uuid, title, ext, web, url, duration, language, description, keyword, path, origin, status, createTime, updateTime FROM audio WHERE uuid=? AND status=? LIMIT 1", (audio_uuid, 1)

    @staticmethod
    def delete_status(audio_uuid: str) -> (str, tuple):
        return "UPDATE audio SET status=?, updateTime=? WHERE uuid=?", (0, int(time.time()), audio_uuid)

    @staticmethod
    def count_num() -> str:
        return "SELECT count(1) FROM audio WHERE status=1"

    @staticmethod
    def sort_by_ctime(reverse: int = 0) -> str:
        return f'''SELECT createTime FROM audio WHERE status=1 ORDER BY createTime {"DESC" if reverse else "ASC"}'''

    @staticmethod
    def select_by_ctime(time_min: int, time_max: int) -> (str, tuple):
        return "SELECT uuid FROM audio WHERE createTime>=? AND createTime<? AND status=1 ORDER BY createTime DESC", (time_min, time_max)

    @staticmethod
    def select_all_uuid() -> str:
        return "SELECT uuid, origin, createTime FROM audio WHERE status=1 ORDER BY createTime DESC"

    @staticmethod
    def select_title_uuid(audio_title: str, time_min: int, time_max: int) -> (str, tuple):
        return "SELECT uuid, origin, createTime FROM audio WHERE title LIKE ? AND createTime>=? AND createTime<? AND status=1", (f"%{audio_title}%", time_min, time_max)

    @staticmethod
    def select_description_uuid(audio_description: str, time_min: int, time_max: int) -> (str, tuple):
        return "SELECT uuid, origin, createTime FROM audio WHERE description LIKE ? AND createTime>=? AND createTime<? AND status=1", (f"%{audio_description}%", time_min, time_max)

    @staticmethod
    def select_keyword_uuid(audio_keyword: str, time_min: int, time_max: int) -> (str, tuple):
        return "SELECT uuid, origin, createTime FROM audio WHERE keyword LIKE ? AND createTime>=? AND createTime<? AND status=1", (f"%{audio_keyword}%", time_min, time_max)

    @staticmethod
    def select_sentence_uuid(audio_uuid: str, time_min: int, time_max: int) -> (str, tuple):
        return "SELECT uuid, origin, createTime FROM audio WHERE uuid=? AND createTime>=? AND createTime<? AND status=1 LIMIT 1", (audio_uuid, time_min, time_max)

    @staticmethod
    def db_init(audio_draft: tuple) -> object:
        return AudioDraft(audio_draft[0], audio_draft[1], audio_draft[2], audio_draft[3], audio_draft[4], audio_draft[5], audio_draft[6], audio_draft[7], audio_draft[8], audio_draft[9], audio_draft[10], audio_draft[11], audio_draft[12], audio_draft[13])
