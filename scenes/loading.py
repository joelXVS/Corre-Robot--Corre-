import math
import random
import pygame
from scenes.scene import Escena
from ajustes import ANCHO, ALTO


class EscenaCargando(Escena):
    NOMBRE_UI = None

    def __init__(self, juego):
        super().__init__(juego)
        self.tiempo_restante = 0.0
        self.destino = "juego"
        self._angulo = 0.0

    def entrar(self):
        self.juego.detener_musica()
        self.juego.sonidos.reproducir("start")
        self.tiempo_restante = random.uniform(2.0, 4.0)
        self._angulo = 0.0

    def actualizar(self, dt):
        self._angulo = (self._angulo + dt * 300) % 360
        self.tiempo_restante -= dt
        if self.tiempo_restante <= 0:
            self.juego.cambiar_escena(self.destino)

    def dibujar(self, pantalla):
        pantalla.fill((0, 0, 0))
        cx, cy = ANCHO // 2, ALTO // 2
        for i in range(12):
            ang = math.radians(self._angulo + i * 30)
            x = cx + math.cos(ang) * 30
            y = cy + math.sin(ang) * 30
            alpha = int(255 * (i / 12))
            pygame.draw.circle(pantalla, (alpha, alpha, alpha),
                               (int(x), int(y)), 4)