import pygame

class Boton:
    def __init__(self, rect, texto, al_click=None, habilitado=True, color=(100, 200, 80)):
        self.rect = pygame.Rect(rect)
        self.texto = texto
        self.al_click = al_click
        self.habilitado = habilitado
        self.color_base = color

    def manejar_evento(self, evento):
        if not self.habilitado:
            return False
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                if self.al_click:
                    self.al_click()
                return True
        return False

    def dibujar(self, pantalla, recursos):
        hover = self.habilitado and self.rect.collidepoint(pygame.mouse.get_pos())
        if not self.habilitado:
            color = (80, 80, 80); borde = (50, 50, 50)
        else:
            if hover:
                color = tuple(min(255, c + 30) for c in self.color_base)
            else:
                color = self.color_base
            borde = (40, 40, 40)

        sombra = pygame.Rect(self.rect.x, self.rect.y + 5, self.rect.width, self.rect.height)
        pygame.draw.rect(pantalla, (20, 20, 20), sombra, border_radius=8)
        pygame.draw.rect(pantalla, color, self.rect, border_radius=8)
        pygame.draw.rect(pantalla, borde, self.rect, 3, border_radius=8)
        pygame.draw.rect(pantalla, (255, 255, 255), self.rect.inflate(-6, -6), 2, border_radius=6)

        tamano = max(10, int(self.rect.height * 0.4))
        ancho_max = self.rect.width - 12
        texto = self.texto
        # Ajustar tamaño
        while tamano > 8 and recursos.texto(texto, tamano).get_width() > ancho_max:
            tamano -= 1
        # Recortar si aún no cabe
        if recursos.texto(texto, tamano).get_width() > ancho_max:
            while len(texto) > 1 and recursos.texto(texto + "...", tamano).get_width() > ancho_max:
                texto = texto[:-1]
            texto = texto + "..."

        txt = recursos.texto(texto, tamano, (255, 255, 255))
        pantalla.blit(txt, txt.get_rect(center=self.rect.center))