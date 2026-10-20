import pygame


class SelectorHorizontal:
    def __init__(self, rect, opciones, valor_actual, al_cambiar=None):
        self.rect = pygame.Rect(rect)
        self.opciones = list(opciones)     # [(valor, label), ...]
        self.valor_actual = valor_actual
        self.al_cambiar = al_cambiar
        self._rects = []
        self._recalc()

    def _recalc(self):
        n = max(1, len(self.opciones))
        w = self.rect.width // n
        self._rects = [
            pygame.Rect(self.rect.x + i * w, self.rect.y, w, self.rect.height)
            for i in range(n)
        ]

    def manejar_evento(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i, r in enumerate(self._rects):
                if r.collidepoint(e.pos):
                    self.valor_actual = self.opciones[i][0]
                    if self.al_cambiar:
                        self.al_cambiar(self.valor_actual)
                    return True
        return False

    def dibujar(self, pantalla, recursos):
        for i, (val, label) in enumerate(self.opciones):
            r = self._rects[i]
            activo = (val == self.valor_actual)
            hover = r.collidepoint(pygame.mouse.get_pos())
            if activo:
                color = (100, 180, 240)
            elif hover:
                color = (90, 130, 180)
            else:
                color = (60, 80, 110)
            pygame.draw.rect(pantalla, color, r, border_radius=6)
            pygame.draw.rect(pantalla, (240, 240, 240), r, 2, border_radius=6)
            txt = recursos.texto(label, 20)
            pantalla.blit(txt, txt.get_rect(center=r.center))