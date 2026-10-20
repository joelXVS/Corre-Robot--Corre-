"""Gestor de sonidos. Si falta un archivo, ese sonido queda en silencio."""
import os
import pygame


class Sonidos:
    RUTA = "assets/sonidos"
    EXTENSIONES = (".wav", ".ogg")

    NOMBRES = [
        "salto", "danio001", "danio002", "danio003", "danio004", "danio005", "bateria_baja", "bateria_recargada", "engranaje", "codigo",
        "codigo_secreto", "door_open", "door_close", "victoria", "derrota", "click", "start",
    ]

    def __init__(self, volumen=0.5):
        self.sonidos = {}
        self.volumen = volumen
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            return

        for nombre in self.NOMBRES:
            self.sonidos[nombre] = self._cargar(nombre)
        self.set_volumen(volumen)

    def _cargar(self, nombre):
        for ext in self.EXTENSIONES:
            ruta = os.path.join(self.RUTA, nombre + ext)
            if os.path.exists(ruta):
                try:
                    return pygame.mixer.Sound(ruta)
                except pygame.error:
                    return None
        return None

    def reproducir(self, nombre):
        s = self.sonidos.get(nombre)
        if s is not None:
            s.play()

    def set_volumen(self, v):
        self.volumen = max(0.0, min(1.0, v))
        for s in self.sonidos.values():
            if s is not None:
                s.set_volume(self.volumen)