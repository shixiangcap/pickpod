# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import gc
import os
from queue import Queue
from typing import Any, Dict, List

import opencc
import torch
import torchaudio
import yt_dlp
from faster_whisper import WhisperModel
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
from pydub import AudioSegment

from pickpod.draft import AudioDraft, SentenceDraft


class PickpodUtils(object):

    @staticmethod
    def get_overlap(interval_1: SentenceDraft, interval_2: Any) -> float:
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
    def get_speaker_by_time(sentence_stamp: List[SentenceDraft], pyannote_stamp: List[Any]) -> None:
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

    @staticmethod
    def pickpod_ytdlp(audio_draft: AudioDraft, ydl_option: Dict[str, Any]) -> None:
        """
        Download audio with yt_dlp
        """
        with yt_dlp.YoutubeDL(ydl_option) as ydl:
            ydl_info = ydl.extract_info(audio_draft.url, download=True)
            # print(ydl_info)
        if not audio_draft.title:
            audio_draft.title = ydl_info.get("title", "")
        if not audio_draft.description:
            audio_draft.description = ydl_info.get("description", "")
        ydl_json = ydl.sanitize_info(ydl_info).get("requested_downloads", [[]])[0]
        if ydl_json.get("ext", ""):
            audio_draft.ext = ydl_json.get("ext", "")
        else:
            audio_draft.ext = os.path.splitext(ydl_json.get("filepath", ""))[1][1:]
        audio_draft.path = ydl_json.get("filepath", "")
        if not audio_draft.duration:
            audio_draft.duration = len(AudioSegment.from_file(audio_draft.path)) / 1000

    @staticmethod
    def pickpod_whisper(audio_draft: AudioDraft, task_language: str = None, task_prompt: str = None, sentence_draft: Queue or List = None, model_file: str = "large-v3") -> float:
        """
        Get audio document with faster_whisper
        """
        if torch.cuda.is_available():
            whisper_model = WhisperModel(model_file, device="cuda", compute_type="float16")
        else:
            whisper_model = WhisperModel(model_file, device="cpu", compute_type="int8")
        whisper_segments, whisper_info = whisper_model.transcribe(
            audio_draft.path,
            language=task_language,
            initial_prompt=task_prompt
        )
        audio_draft.language = whisper_info.language
        print(f"Detected language \"{whisper_info.language}\" with probability {whisper_info.language_probability * 100.0}%")
        for seg in whisper_segments:
            sd = SentenceDraft(
                sentence_aid=audio_draft.uuid,
                sentence_content=opencc.OpenCC("t2s").convert(seg.text.strip()),
                sentence_start=round(seg.start, 3),
                sentence_end=round(seg.end, 3)
                )
            if isinstance(sentence_draft, List):
                sentence_draft.append(sd)
            elif isinstance(sentence_draft, Queue):
                sentence_draft.put(sd)
        return whisper_info.language_probability * 100.0

    @staticmethod
    def pickpod_pyannote(audio_draft: AudioDraft, key_hugging_face: str, path_wav: str) -> List[Any]:
        """
        Execute speaker diarization with pyannote.audio
        """
        pyannote_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.0", use_auth_token=key_hugging_face)
        if torch.cuda.is_available():
            try:
                pyannote_pipeline.to(torch.device("cuda"))
            except Exception as e:
                pyannote_pipeline.to(torch.device("cpu"))
                print("CUDA pyannote failed, CODE: {}, INFO: {}.".format(e.args[0], e.args[-1]))
        with ProgressHook() as hook:
            if audio_draft.ext.lower() != "wav":
                path_wav = f"{path_wav}/{audio_draft.uuid}.wav"
                pyannote_wav = AudioSegment.from_file(audio_draft.path)
                pyannote_wav.export(path_wav, format="wav")
                waveform, sample_rate = torchaudio.load(path_wav)
            else:
                waveform, sample_rate = torchaudio.load(audio_draft.path)
            pyannote_stamp = pyannote_pipeline({"waveform": waveform, "sample_rate": sample_rate}, hook=hook)
        return list(pyannote_stamp.itertracks(yield_label=True))

    @staticmethod
    def static_clean() -> None:
        """
        Clean all cache
        """
        gc.collect()
        torch.cuda.empty_cache()
