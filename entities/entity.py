"""Clase base de todo elemento con hitbox."""
import pygame


class Entidad(pygame.sprite.Sprite):
    def __init__(self, x, y, ancho, alto):
        super().__init__()
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.vel_x = 0
        self.vel_y = 0
        self.animacion = None

    @property
    def hitbox(self):
        return self.rect

    def colisiona_con(self, otra):
        return self.rect.colliderect(otra.rect)

    def actualizar(self, dt):
        if self.animacion:
            self.animacion.actualizar(dt)

    def dibujar(self, pantalla, offset=(0, 0)):
        if not self.animacion:
            return
        img = self.animacion.frame_actual()
        pantalla.blit(img, (self.rect.x - offset[0], self.rect.y - offset[1]))