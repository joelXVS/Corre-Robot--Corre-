from scenes.scene import Escena
from ui.button import Boton
from ajustes import ANCHO


class EscenaDerrota(Escena):
    NOMBRE_UI = None

    def __init__(self, juego):
        super().__init__(juego)

    def entrar(self):
        self.juego.detener_musica()
        self.botones = [
            Boton((ANCHO // 2 - 220, 340, 200, 54), "Reintentar",
                  lambda: self.juego.cambiar_escena("cargando")),
            Boton((ANCHO // 2 + 20, 340, 200, 54), "Salir",
                  lambda: self.juego.cambiar_escena(self.juego.return_scene)),
        ]

    def dibujar(self, pantalla):
        pantalla.fill((35, 10, 10))
        titulo = self.recursos.texto("Sistema apagado", 56, (255, 120, 120))
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 160)))

        sub = self.recursos.texto(
            "El robot no pudo continuar", 26, (255, 200, 200)
        )
        pantalla.blit(sub, sub.get_rect(center=(ANCHO // 2, 230)))

        niv = self.recursos.texto(
            f"Nivel {self.juego.indice_nivel + 1}", 24
        )
        pantalla.blit(niv, niv.get_rect(center=(ANCHO // 2, 280)))

        for b in self.botones:
            b.dibujar(pantalla, self.recursos)