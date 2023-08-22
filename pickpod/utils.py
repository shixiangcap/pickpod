# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import gc
import os
from queue import Queue
from typing import Any, Dict, List

import opencc
import torch
import yt_dlp
from faster_whisper import WhisperModel
from pyannote.audio import Pipeline
from pydub import AudioSegment

from pickpod.doc import AudioDocument, SentenceDocument


class PickpodUtils(object):

    @staticmethod
    def get_overlap(interval_1: SentenceDocument, interval_2: Any):
        """
        Calculation the interval overlap
        """
        start_1, end_1 = interval_1.start, interval_1.end
        start_2, end_2 = interval_2.start, interval_2.end
        intersection = max(0, min(end_1, end_2) - max(start_1, start_2))
        union = end_1 - start_1
        if union == 0:
            return 0.0
        return intersection / union

    @staticmethod
    def get_speaker_by_time(sentence_stamp: List[SentenceDocument], pyannote_stamp: List[Any]):
        """
        Align the timestamps
        """
        for sentence in sentence_stamp:
            max_overlap = -1
            for pyannote in pyannote_stamp:
                overlap = PickpodUtils.get_overlap(sentence, pyannote[0])
                if overlap > max_overlap:
                    max_overlap = overlap
                    sentence.speaker = int(pyannote[2][8:])
        return sentence_stamp

    @staticmethod
    def pickpod_ytdlp(audio_doc: AudioDocument, ydl_options: Dict[str, Any]) -> None:
        """
        Download audio with yt_dlp
        """
        with yt_dlp.YoutubeDL(ydl_options) as ydl:
            ydl_info = ydl.extract_info(audio_doc.url, download=True)
            # print(ydl_info)
        if not audio_doc.title:
            audio_doc.title = ydl_info.get("title", "")
        if not audio_doc.description:
            audio_doc.description = ydl_info.get("description", "")
        ydl_json = ydl.sanitize_info(ydl_info).get("requested_downloads", [[]])[0]
        if ydl_json.get("ext", ""):
            audio_doc.ext = ydl_json.get("ext", "")
        else:
            audio_doc.ext = os.path.splitext(ydl_json.get("filepath", ""))[1][1:]
        audio_doc.path = ydl_json.get("filepath", "")
        if not audio_doc.length:
            audio_doc.length = len(AudioSegment.from_file(audio_doc.path)) / 1000

    @staticmethod
    def pickpod_whisper(audio_doc: AudioDocument, task_language: str = None, task_prompt: str = None, task_queue: Queue = None, model_file: str = "large-v2") -> (str, float):
        """
        Get audio document with faster_whisper
        """
        whisper_model = WhisperModel(model_file, device="cuda", compute_type="float16")
        whisper_segments, whisper_info = whisper_model.transcribe(
            audio_doc.path,
            language=task_language,
            initial_prompt=task_prompt,
            word_timestamps=False
        )
        print(f"Detected language \"{whisper_info.language}\" with probability {whisper_info.language_probability * 100.0}%")
        for seg in whisper_segments:
            sentence_document = SentenceDocument(
                sentence_content=opencc.OpenCC("t2s").convert(seg.text.strip()),
                sentence_start=seg.start,
                sentence_end=seg.end
                )
            audio_doc.sentence.append(sentence_document)
            if task_queue:
                task_queue.put(sentence_document)
        return task_language if task_language else whisper_info.language, whisper_info.language_probability * 100.0

    @staticmethod
    def pickpod_pyannote(audio_doc: AudioDocument, key_hugging_face: str, ydl_path: str) -> None:
        """
        Execute speaker diarization with pyannote.audio
        """
        pyannote_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1", use_auth_token=key_hugging_face)
        if audio_doc.ext.lower() != "wav":
            wav_path = f"{ydl_path}/{audio_doc.uuid}.wav"
            pyannote_wav = AudioSegment.from_file(audio_doc.path)
            pyannote_wav.export(wav_path, format="wav")
            pyannote_stamp = pyannote_pipeline({"uri": "blabal", "audio": wav_path})
        else:
            pyannote_stamp = pyannote_pipeline({"uri": "blabal", "audio": audio_doc.path})
        audio_doc.sentence = PickpodUtils.get_speaker_by_time(audio_doc.sentence, list(pyannote_stamp.itertracks(yield_label=True)))

    @staticmethod
    def static_clean() -> None:
        """
        Clean all cache
        """
        gc.collect()
        torch.cuda.empty_cache()
