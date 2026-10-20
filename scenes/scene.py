"""Escena base: fondo animado desde assets/spritesheets/ui_<nombre>.png + botones."""
import os
import pygame
from animator import Animacion
from spritesheet import DivisorSpritesheet
from ajustes import ANCHO, ALTO


class Escena:
    NOMBRE_UI = None
    FRAMES_UI = (ANCHO, ALTO, 1)   # (ancho_frame, alto_frame, nframes)

    def __init__(self, juego):
        self.juego = juego
        self.recursos = juego.recursos
        self.botones = []
        self.fondo_anim = self._cargar_fondo()

    def _cargar_fondo(self):
        if not self.NOMBRE_UI:
            return None
        ruta = f"assets/spritesheets/ui_{self.NOMBRE_UI}.png"
        if not os.path.exists(ruta):
            return None
        aw, ah, n = self.FRAMES_UI
        frames = DivisorSpritesheet.dividir(ruta, aw, ah, n, 1)
        return Animacion(frames, fps=8)

    # ---------- Ciclo de vida ----------
    def entrar(self):
        pass

    def salir(self):
        pass

    def manejar_eventos(self, eventos):
        for e in eventos:
            for b in self.botones:
                if b.manejar_evento(e):
                    self.juego.sonidos.reproducir("click")
                    break

    def actualizar(self, dt):
        if self.fondo_anim:
            self.fondo_anim.actualizar(dt)

    def dibujar(self, pantalla):
        if self.fondo_anim:
            pantalla.blit(self.fondo_anim.frame_actual(), (0, 0))
        else:
            pantalla.fill((20, 20, 30))
        for b in self.botones:
            b.dibujar(pantalla, self.recursos)