"""
Módulo de audio procedural y efectos sonoros utilizando Pygame Mixer y NumPy.
Permite disfrutar de efectos sonoros inmersivos sin requerir archivos de audio externos.
"""
from __future__ import annotations
import math
import numpy as np
import pygame
from typing import Optional, Dict


class SoundManager:
    _instance: Optional[SoundManager] = None
    _initialized: bool = False

    def __init__(self):
        self.enabled: bool = True
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self._init_mixer()

    @classmethod
    def get_instance(cls) -> SoundManager:
        if cls._instance is None:
            cls._instance = SoundManager()
        return cls._instance

    def _init_mixer(self):
        if SoundManager._initialized:
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            SoundManager._initialized = True
            self._generate_procedural_sounds()
        except Exception as e:
            print(f"Aviso: No se pudo inicializar pygame.mixer ({e}). El juego correrá sin audio.")
            self.enabled = False

    def _generate_procedural_sounds(self):
        sample_rate = 44100

        def make_sound(samples: np.ndarray) -> pygame.mixer.Sound:
            # Ensure 16-bit stereo
            scaled = np.int16(samples * 32767)
            stereo = np.column_stack((scaled, scaled))
            return pygame.sndarray.make_sound(stereo)

        try:
            # 1. Click
            dur = 0.05
            t = np.linspace(0, dur, int(sample_rate * dur), False)
            wave = np.sin(2 * np.pi * 800 * t) * np.exp(-t * 80)
            self.sounds["click"] = make_sound(wave * 0.4)

            # 2. Dados
            dur = 0.25
            t = np.linspace(0, dur, int(sample_rate * dur), False)
            noise = (np.random.rand(len(t)) * 2 - 1) * np.exp(-t * 12)
            filter_wave = np.sin(2 * np.pi * 350 * t) * 0.5 + noise * 0.5
            self.sounds["dice"] = make_sound(filter_wave * 0.5)

            # 3. Carta
            dur = 0.15
            t = np.linspace(0, dur, int(sample_rate * dur), False)
            freq = np.linspace(400, 1200, len(t))
            wave = np.sin(2 * np.pi * freq * t) * np.exp(-t * 20)
            self.sounds["card"] = make_sound(wave * 0.3)

            # 4. Gong / Plaga (campana grave)
            dur = 1.0
            t = np.linspace(0, dur, int(sample_rate * dur), False)
            wave = (
                np.sin(2 * np.pi * 110 * t) * 0.6 +
                np.sin(2 * np.pi * 220 * t) * 0.3 +
                np.sin(2 * np.pi * 330 * t) * 0.1
            ) * np.exp(-t * 3.5)
            self.sounds["gong"] = make_sound(wave * 0.6)

            # 5. Fanfarria de Victoria
            dur = 0.8
            t = np.linspace(0, dur, int(sample_rate * dur), False)
            # Arpegio Do - Mi - Sol - Do agudo
            step = len(t) // 4
            wave = np.zeros_like(t)
            freqs = [261.63, 329.63, 392.00, 523.25]
            for i, f in enumerate(freqs):
                sub_t = t[i * step:(i + 1) * step] - (i * dur / 4)
                wave[i * step:(i + 1) * step] = np.sin(2 * np.pi * f * sub_t) * np.exp(-sub_t * 5)
            self.sounds["fanfare"] = make_sound(wave * 0.5)

            # 6. Alerta
            dur = 0.3
            t = np.linspace(0, dur, int(sample_rate * dur), False)
            freq = 600 + np.sin(2 * np.pi * 15 * t) * 200
            wave = np.sin(2 * np.pi * freq * t) * np.exp(-t * 5)
            self.sounds["alert"] = make_sound(wave * 0.4)

        except Exception as e:
            print(f"Error generando sonidos procedurales: {e}")

    def play(self, sound_name: str):
        if not self.enabled:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def toggle_mute(self) -> bool:
        self.enabled = not self.enabled
        return self.enabled
