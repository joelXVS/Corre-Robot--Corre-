import pygame
from entities.entity import Entidad
from ajustes import COLOR_PUERTA, TAM_TILE


class Puerta(Entidad):
    def __init__(self, x, y, ancho, alto, animacion=None):
        super().__init__(x, y, ancho, alto)
        self.animacion = animacion
        self.animando = False

    def animar(self):
        if not self.animando and self.animacion:
            self.animando = True
            self.animacion.reiniciar()

    def actualizar(self, dt):
        if self.animando and self.animacion:
            self.animacion.actualizar(dt)

    def dibujar(self, pantalla, offset=(0, 0)):
        if self.animacion:
            img = self.animacion.frame_actual()
            pantalla.blit(img, (self.rect.x - offset[0], self.rect.y - offset[1]))
        else:
            pygame.draw.rect(
                pantalla, COLOR_PUERTA,
                (self.rect.x - offset[0], self.rect.y - offset[1],
                 self.rect.width, self.rect.height)
            )