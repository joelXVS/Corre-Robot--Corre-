import pygame


class Toggle:
    def __init__(self, rect, valor, al_cambiar=None):
        self.rect = pygame.Rect(rect)
        self.valor = valor
        self.al_cambiar = al_cambiar
        self._anim = 1.0 if valor else 0.0

    def manejar_evento(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.rect.collidepoint(e.pos):
                self.valor = not self.valor
                if self.al_cambiar:
                    self.al_cambiar(self.valor)
                return True
        return False

    def actualizar(self, dt):
        obj = 1.0 if self.valor else 0.0
        self._anim += (obj - self._anim) * min(1.0, dt * 14)

    def dibujar(self, pantalla):
        base = (60 + int(80 * self._anim), 90 + int(90 * self._anim),
                110 + int(130 * self._anim))
        pygame.draw.rect(pantalla, base, self.rect,
                         border_radius=self.rect.height // 2)
        kn = self.rect.height - 8
        x = self.rect.x + 4 + self._anim * (self.rect.width - kn - 8)
        pygame.draw.circle(pantalla, (240, 240, 250),
                           (int(x + kn // 2), self.rect.centery), kn // 2)
        pygame.draw.circle(pantalla, (30, 30, 40),
                           (int(x + kn // 2), self.rect.centery), kn // 2, 2)