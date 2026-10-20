import pygame
from scenes.scene import Escena
from ui.icon_button import (
    BotonIcono,
    icono_play, icono_x, icono_niveles,
    icono_personajes, icono_ajustes, icono_creditos,
    icono_mis_niveles, icono_como_jugar,
)
from ajustes import ANCHO, ALTO


class EscenaLobby(Escena):
    NOMBRE_UI = "lobby"

    def __init__(self, juego):
        super().__init__(juego)
        self._crear_botones()

    def entrar(self):
        meta = self.juego.recursos.meta_personaje(self.juego.personaje_seleccionado)
        if not self.juego.progreso.esta_desbloqueado(meta):
            self.juego.personaje_seleccionado = 0
        # No reinicia si ya se está reproduciendo
        self.juego.musica("assets/sonidos/lobby.mp3", loop=True)

    def _crear_botones(self):
        botones = []
        tam_lateral = 120
        tam_play = 180
        sep = 30
        total_ancho = tam_lateral + sep + tam_play + sep + tam_lateral
        x0 = (ANCHO - total_ancho) // 2
        y_central = 170

        botones.append(BotonIcono(
            (x0, y_central + (tam_play - tam_lateral) // 2, tam_lateral, tam_lateral),
            icono_personajes,
            lambda: self.juego.cambiar_escena("personajes"),
            color=(150, 90, 200),
            sprite_nombre="personajes",
        ))

        botones.append(BotonIcono(
            (x0 + tam_lateral + sep, y_central, tam_play, tam_play),
            icono_play,
            lambda: self.juego.cambiar_escena("cargando"),
            color=(80, 200, 90),
            sprite_nombre="play",
        ))

        botones.append(BotonIcono(
            (x0 + tam_lateral + sep + tam_play + sep,
             y_central + (tam_play - tam_lateral) // 2, tam_lateral, tam_lateral),
            icono_mis_niveles,
            lambda: self.juego.cambiar_escena("mis_niveles"),
            color=(200, 150, 60),
            sprite_nombre="mis_niveles",
        ))

        tam = 92
        sep2 = 22
        total = tam * 4 + sep2 * 3
        xb = (ANCHO - total) // 2
        y_inf = 400
        opciones_inf = [
            (icono_niveles,    (70, 130, 200),  "niveles",     "niveles"),
            (icono_como_jugar, (100, 180, 200), "como_jugar",  "como_jugar"),
            (icono_ajustes,    (200, 150, 60),  "ajustes",     "ajustes"),
            (icono_creditos,   (70, 180, 200),  "creditos",    "creditos"),
        ]
        for i, (fn, color, destino, sprite) in enumerate(opciones_inf):
            botones.append(BotonIcono(
                (xb + i * (tam + sep2), y_inf, tam, tam),
                fn,
                (lambda d=destino: self.juego.cambiar_escena(d)),
                color=color,
                sprite_nombre=sprite,
            ))

        botones.append(BotonIcono(
            (ANCHO - 70, 20, 50, 50), icono_x,
            lambda: setattr(self.juego, "corriendo", False),
            es_cerrar=True,
            sprite_nombre="x",
        ))

        self.botones = botones

    def manejar_eventos(self, eventos):
        for e in eventos:
            for b in self.botones:
                if b.manejar_evento(e):
                    self.juego.sonidos.reproducir("click")
                    break

    def actualizar(self, dt):
        super().actualizar(dt)
        for b in self.botones: b.actualizar(dt)

    def dibujar(self, pantalla):
        if self.fondo_anim: pantalla.blit(self.fondo_anim.frame_actual(), (0, 0))
        else: pantalla.fill((20, 20, 30))

        titulo = self.recursos.texto("Corre Robot, Corre!", 52)
        sombra = self.recursos.texto("Corre Robot, Corre!", 52, (0, 0, 0))
        cx = ANCHO // 2
        pantalla.blit(sombra, sombra.get_rect(center=(cx + 3, 103)))
        pantalla.blit(titulo, titulo.get_rect(center=(cx, 100)))

        frags = self.juego.progreso.stats["fragmentos_secretos"]
        if frags:
            total = self.juego.total_secretos
            codigo = "".join(sorted(frags))
            parcial = codigo + "_" * (total - len(codigo))
            txt = self.recursos.texto(f"Código: {parcial}", 20, (200, 200, 255))
            pantalla.blit(txt, txt.get_rect(center=(cx, 160)))

        for b in self.botones:
            b.dibujar(pantalla, self.recursos)