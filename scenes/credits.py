from scenes.scene import Escena
from ui.button import Boton
from ajustes import ANCHO, ALTO


class EscenaCreditos(Escena):
    NOMBRE_UI = "creditos"

    CREDITOS = [
        "Corre Robot, Corre!",
        "version 1.0",
        "",
        "Paradigmas de Programación",
        "Fundación de Educación Superior Nueva América",
        "Tutor: Julián García Solorzano",
        "",
        "",
        "Jose Angel Perea Valencia",
        "",
        "Apoyo moral: Jean Pierre Vallecilla Perlaza",
        "",
        "",
        "Enfoque: Programación Orientada a Objetos",
        "Motor: pygame",
        "Fuente: Minecraft Standart",
        "",
        "Gracias por jugar",
        "_ _ _ _ _ _ _ A _"
    ]

    def __init__(self, juego):
        super().__init__(juego)
        self.botones.append(Boton((20, 20, 130, 42), "< Volver",
                                  lambda: self.juego.cambiar_escena("lobby")))
        self.scroll_y = ALTO
        self.velocidad = 45

    def actualizar(self, dt):
        super().actualizar(dt)
        self.scroll_y -= self.velocidad * dt
        alto_total = len(self.CREDITOS) * 40
        if self.scroll_y < -alto_total:
            self.scroll_y = ALTO

    def dibujar(self, pantalla):
        super().dibujar(pantalla)
        for i, linea in enumerate(self.CREDITOS):
            if not linea:
                continue
            y = self.scroll_y + i * 40
            if -40 < y < ALTO:
                txt = self.recursos.texto(linea, 26)
                pantalla.blit(txt, txt.get_rect(center=(ANCHO // 2, y)))