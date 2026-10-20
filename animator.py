"""Sistema de animación por secuencia + divisor propio de spritesheets."""
import pygame

class Animacion:
    """Reproduce una secuencia de frames a cierta velocidad."""

    def __init__(self, frames, fps=8, loop=True):
        assert frames, "Animacion necesita al menos un frame"
        self.frames = frames
        self.fps = fps
        self.loop = loop
        self.indice = 0
        self.tiempo = 0.0
        self.terminada = False

    def actualizar(self, dt):
        if self.terminada and not self.loop:
            return
        self.tiempo += dt
        if self.tiempo >= 1.0 / self.fps:
            self.tiempo = 0.0
            self.indice += 1
            if self.indice >= len(self.frames):
                if self.loop:
                    self.indice = 0
                else:
                    self.indice = len(self.frames) - 1
                    self.terminada = True

    def frame_actual(self):
        return self.frames[self.indice]

    def reiniciar(self):
        self.indice = 0
        self.tiempo = 0.0
        self.terminada = False

    def clonar(self):
        return Animacion(self.frames, self.fps, self.loop)