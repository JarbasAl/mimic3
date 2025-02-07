#!/usr/bin/env python3
"""Base classes for Open Text to Speech systems"""
import io
import typing
import wave
from abc import ABCMeta, abstractmethod
from contextlib import AbstractContextManager
from dataclasses import dataclass


@dataclass
class Settings:
    """Current settings for TTS system"""

    voice: typing.Optional[str] = None
    """Current voice key"""

    language: typing.Optional[str] = None
    """Current language (e.g., en_US)"""

    volume: typing.Optional[float] = None
    """Current speaking volume"""

    rate: typing.Optional[float] = None
    """Current speaking rate"""

    pitch: typing.Optional[float] = None
    """Current speaking pitch"""

    other_settings: typing.Optional[typing.Mapping[str, typing.Any]] = None
    """Custom settings"""


@dataclass
class BaseToken(metaclass=ABCMeta):
    """Base class for spoken tokens"""

    text: str
    """Text of the token"""


@dataclass
class Word(BaseToken):
    """Token representing a single word"""

    role: typing.Optional[str] = None
    """Role of the word (typically part of speech)"""


@dataclass
class Phonemes(BaseToken):
    """Token representing a phonemized word"""

    alphabet: typing.Optional[str] = None
    """Phoneme alphabet (e.g., ipa)"""


@dataclass
class SayAs(BaseToken):
    """Token representing a word or phrase that must be spoken a particular way"""

    interpret_as: str
    """Implementation-dependent token interpretation (e.g., characters or digits)"""

    format: typing.Optional[str] = None
    """Implementation-dependent token format (depends on interpret_as)"""


@dataclass
class _BaseResultDefaults:
    """Base class of results from TTS end_utterance"""

    tag: typing.Optional[typing.Any] = None
    """Optional tag to associate with results"""


@dataclass
class BaseResult(metaclass=ABCMeta):
    """Base class of results from TTS end_utterance"""


@dataclass
class _AudioResultBase:
    """Synthesized audio result"""

    sample_rate_hz: int
    """Sample rate in Hertz (e.g., 22050)"""

    sample_width_bytes: int
    """Sample width in bytes (e.g., 2)"""

    num_channels: int
    """Number of audio channels (e.g., 1)"""

    audio_bytes: bytes
    """Raw audio bytes (no header)"""


@dataclass
class AudioResult(BaseResult, _BaseResultDefaults, _AudioResultBase):
    """Synthesized audio result"""

    def to_wav_bytes(self) -> bytes:
        """Convert audio bytes to WAV"""
        with io.BytesIO() as wav_io:
            wav_file: wave.Wave_write = wave.open(wav_io, "wb")
            with wav_file:
                wav_file.setframerate(self.sample_rate_hz)
                wav_file.setsampwidth(self.sample_width_bytes)
                wav_file.setnchannels(self.num_channels)
                wav_file.writeframes(self.audio_bytes)

            return wav_io.getvalue()


@dataclass
class _MarkResultBase:
    """Result indicating a <mark> has been reached in SSML"""

    name: str
    """Name of the <mark>"""


@dataclass
class MarkResult(BaseResult, _BaseResultDefaults, _MarkResultBase):
    """Result indicating a <mark> has been reached in SSML"""


@dataclass
class Voice:
    """Details of a voice in a text to speech system"""

    key: str
    """Unique key that can be used to reference the voice"""

    name: str
    """Human-readable name of the voice"""

    language: str
    """Language of the voice (e.g., en_US)"""

    description: str
    """Human-readable description of the voice"""

    speakers: typing.Optional[typing.Sequence[str]] = None
    """List of speakers within the voice model if multi-speaker"""

    properties: typing.Optional[typing.Mapping[str, typing.Any]] = None
    """Additional properties associated with the voice"""

    @property
    def is_multispeaker(self) -> bool:
        """True if voice has multiple speakers"""
        return (self.speakers is not None) and (len(self.speakers) > 1)


class TextToSpeechSystem(AbstractContextManager, metaclass=ABCMeta):
    """Abstract base class for open text to speech systems.

    Expected usage:

    begin_utterance()
    speak_text(...)
    add_break(...)
    set_mark(...)
    speak_tokens(...)
    speak_text(...)
    results = end_utterance()

    In between begin_utterance() and end_utterance(), the voice/language may
    also be changed.
    """

    @property
    @abstractmethod
    def voice(self) -> str:
        """Get the current voice key"""

    @voice.setter
    def voice(self, new_voice: str):
        """Set the current voice key"""

    @property
    @abstractmethod
    def language(self) -> str:
        """Get the current voice language"""

    @language.setter
    def language(self, new_language: str):
        """Set the current voice language"""

    def shutdown(self):
        """Called by the host program when the text to speech system should be stopped"""

    def __exit__(self, exc_type, exc_value, traceback):
        """Automatically call shutdown when context manager has exited"""
        self.shutdown()

    @abstractmethod
    def get_voices(self) -> typing.Iterable[Voice]:
        """Returns an iterable of available voices"""

    @abstractmethod
    def begin_utterance(self):
        """Begins a new utterance"""

    @abstractmethod
    def speak_text(self, text: str):
        """Speaks text using the underlying system's tokenization mechanism.

        Becomes an AudioResult in end_utterance()
        """

    @abstractmethod
    def speak_tokens(self, tokens: typing.Iterable[BaseToken]):
        """Speak user-defined tokens.

        Becomes an AudioResult in end_utterance()
        """

    @abstractmethod
    def add_break(self, time_ms: int):
        """Add milliseconds of silence to the current utterance.

        Becomes an AudioResult in end_utterance()
        """

    @abstractmethod
    def set_mark(self, name: str):
        """Set a named mark at this point in the utterance.

        Becomes a MarkResult in end_utterance()
        """

    @abstractmethod
    def end_utterance(self) -> typing.Iterable[BaseResult]:
        """Complete an utterance after begin_utterance().

        Returns an iterable of results (audio, marks, etc.)
        """
