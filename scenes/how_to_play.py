"""Cómo jugar: muestra controles y permite reasignarlos."""
import pygame
from scenes.scene import Escena
from ui.button import Boton
from ajustes import ANCHO, ALTO


class EscenaComoJugar(Escena):
    NOMBRE_UI = "como_jugar"

    ACCIONES = [
        ("izquierda", "Mover Izquierda"),
        ("derecha",   "Mover Derecha"),
        ("salto",     "Saltar"),
        ("pausa",     "Pausa"),
        ("reiniciar", "Reiniciar"),
    ]

    def __init__(self, juego):
        super().__init__(juego)
        self.botones = [
            Boton((20, 20, 130, 42), "< Volver",
                  lambda: self.juego.cambiar_escena("lobby")),
        ]
        self.escuchando = None  # acción esperando nueva tecla

    def _rect_fila(self, i):
        # Los botones van a la derecha del centro (ANCHO // 2 + 30)
        return pygame.Rect(ANCHO // 2 + 30, 190 + i * 65, 220, 45)

    def manejar_eventos(self, eventos):
        if self.escuchando is not None:
            for e in eventos:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        self.escuchando = None
                    else:
                        self.juego.progreso.set_tecla(self.escuchando, e.key)
                        self.escuchando = None
            return

        for e in eventos:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for i, (accion, _) in enumerate(self.ACCIONES):
                    if self._rect_fila(i).collidepoint(e.pos):
                        self.escuchando = accion
                        return
            for b in self.botones:
                if b.manejar_evento(e):
                    self.juego.sonidos.reproducir("click")

    def dibujar(self, pantalla):
        super().dibujar(pantalla)
        
        # Separamos más el título y el subtítulo
        titulo = self.recursos.texto("Cómo Jugar", 44)
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 80)))

        sub = self.recursos.texto("Haz clic sobre una acción para reasignar la tecla", 20, (200, 200, 220))
        pantalla.blit(sub, sub.get_rect(center=(ANCHO // 2, 135)))

        for i, (accion, label) in enumerate(self.ACCIONES):
            rect = self._rect_fila(i)
            escuchando = (self.escuchando == accion)

            # 1. Etiqueta de texto (alineada a la derecha del centro, dejando un margen)
            lbl = self.recursos.texto(label, 24)
            # midright significa que el lado derecho del texto termina exactamente 20px antes del botón
            pantalla.blit(lbl, lbl.get_rect(midright=(rect.x - 30, rect.centery)))

            # 2. Botón de la tecla
            color = (200, 120, 60) if escuchando else (60, 80, 120)
            pygame.draw.rect(pantalla, color, rect, border_radius=8)
            pygame.draw.rect(pantalla, (240, 240, 240), rect, 2, border_radius=8)

            # 3. Texto de la tecla dentro del botón
            nombre = "..." if escuchando else pygame.key.name(self.juego.progreso.tecla(accion)).upper()
            txt = self.recursos.texto(nombre, 22, (255, 255, 255))
            pantalla.blit(txt, txt.get_rect(center=rect.center))

        for b in self.botones:
            b.dibujar(pantalla, self.recursos)