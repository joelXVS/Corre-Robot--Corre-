import pygame
from entities.entity import Entidad
from ajustes import DANIO_PINCHO, COLOR_PINCHO


class Obstaculo(Entidad):
    """Pinchos / sierras: dañan al tocar."""

    def __init__(self, x, y, ancho, alto, tipo='^', imagen=None):
        super().__init__(x, y, ancho, alto)
        self.danio = DANIO_PINCHO
        self.tipo = tipo
        self.imagen = imagen # <--- NUEVO: Guardamos la imagen

    def aplicar_efecto(self, robot):
        robot.recibir_danio(self.danio)

    def dibujar(self, pantalla, offset=(0, 0)):
        # Si tenemos la imagen de la spritesheet, la dibujamos
        if self.imagen:
            pantalla.blit(self.imagen, (self.rect.x - offset[0], self.rect.y - offset[1]))
            return