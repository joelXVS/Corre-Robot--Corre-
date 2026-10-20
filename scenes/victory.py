import pygame
from scenes.scene import Escena
from ui.button import Boton
from ajustes import ANCHO


class EscenaVictoria(Escena):
    NOMBRE_UI = None
    es_victoria_total = False

    def __init__(self, juego):
        super().__init__(juego)

    def entrar(self):
        self.juego.detener_musica()
        self.botones = []
        y = 330
        if not self.es_victoria_total:
            self.botones.append(Boton(
                (ANCHO // 2 - 220, y, 200, 54), "Siguiente",
                lambda: self.juego.cambiar_escena("cargando"),
            ))
        self.botones.append(Boton(
            (ANCHO // 2 + 20 if not self.es_victoria_total else ANCHO // 2 - 100,
             y, 200, 54), "Salir",
            lambda: self.juego.cambiar_escena(self.juego.return_scene),
        ))

    def dibujar(self, pantalla):
        pantalla.fill((10, 30, 20))
        if self.es_victoria_total:
            titulo = self.recursos.texto("¡JUEGO COMPLETADO!", 60)
            sub = self.recursos.texto("Has llevado al robot hasta el final", 26)
        else:
            titulo = self.recursos.texto("¡Nivel superado!", 56)
            sub = self.recursos.texto(
                f"Nivel {self.juego.indice_nivel + 1} completado", 26
            )

        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 130)))
        pantalla.blit(sub, sub.get_rect(center=(ANCHO // 2, 210)))

        pts = self.recursos.texto(
            f"Puntaje total: {self.juego.puntaje_actual}", 30
        )
        pantalla.blit(pts, pts.get_rect(center=(ANCHO // 2, 270)))

        for b in self.botones:
            b.dibujar(pantalla, self.recursos)