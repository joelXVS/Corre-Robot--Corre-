import pygame


class Slider:
    def __init__(self, rect, valor, minimo, maximo, al_cambiar=None, al_soltar=None):
        self.rect = pygame.Rect(rect)
        self.valor = valor
        self.minimo = minimo
        self.maximo = maximo
        self.al_cambiar = al_cambiar
        self.al_soltar = al_soltar
        self.arrastrando = False
        self.knob = pygame.Rect(0, 0, 18, self.rect.height + 14)
        self._actualizar_knob()

    def _actualizar_knob(self):
        rango = self.maximo - self.minimo
        t = 0.0 if rango == 0 else (self.valor - self.minimo) / rango
        t = max(0.0, min(1.0, t))
        cx = self.rect.x + int(t * self.rect.width)
        self.knob.center = (cx, self.rect.centery)

    def _set_desde_x(self, x):
        t = (x - self.rect.x) / self.rect.width
        t = max(0.0, min(1.0, t))
        nuevo = self.minimo + t * (self.maximo - self.minimo)
        if nuevo != self.valor:
            self.valor = nuevo
            self._actualizar_knob()
            if self.al_cambiar:
                self.al_cambiar(self.valor)

    def manejar_evento(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.knob.collidepoint(e.pos) or self.rect.collidepoint(e.pos):
                self.arrastrando = True
                self._set_desde_x(e.pos[0])
                return True
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if self.arrastrando:
                self.arrastrando = False
                if self.al_soltar:
                    self.al_soltar()
                return True
        elif e.type == pygame.MOUSEMOTION and self.arrastrando:
            self._set_desde_x(e.pos[0])
            return True
        return False

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, (50, 50, 70), self.rect, border_radius=6)
        rango = max(0.0001, self.maximo - self.minimo)
        t = (self.valor - self.minimo) / rango
        ancho_fill = int(max(0.0, min(1.0, t)) * self.rect.width)
        if ancho_fill > 0:
            pygame.draw.rect(
                pantalla, (100, 180, 240),
                (self.rect.x, self.rect.y, ancho_fill, self.rect.height),
                border_radius=6,
            )
        pygame.draw.circle(pantalla, (240, 240, 250),
                           self.knob.center, self.knob.width // 2)
        pygame.draw.circle(pantalla, (30, 30, 40),
                           self.knob.center, self.knob.width // 2, 2)