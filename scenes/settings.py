import pygame
from scenes.scene import Escena
from ui.button import Boton
from ui.slider import Slider
from ui.toggle import Toggle
from ui.selector import SelectorHorizontal
from ajustes import ANCHO, ALTO


class EscenaAjustes(Escena):
    NOMBRE_UI = "ajustes"

    def __init__(self, juego):
        super().__init__(juego)
        self._crear_widgets()

    def _crear_widgets(self):
        # --- Layout Global ---
        self.panel_w = 700
        self.x_panel = (ANCHO - self.panel_w) // 2   # Centrado horizontal
        self.label_w = 250                           # Espacio para textos
        self.widget_x = self.x_panel + self.label_w  # Donde empiezan los controles
        self.widget_w = self.panel_w - self.label_w
        
        self.y0 = 140     # Y inicial
        self.fila_h = 65  # Altura de cada fila

        # --- Botones Superiores ---
        self.botones = [
            Boton((20, 20, 130, 42), "< Volver",
                  lambda: self.juego.cambiar_escena("lobby")),
        ]
        
        y = self.y0
        # Volumen Música
        self.slider_musica = Slider((self.widget_x, y+14, self.widget_w - 70, 14),
            self.juego.progreso.vol_musica, 0.0, 1.0,
            lambda v: pygame.mixer.music.set_volume(v),
            lambda: setattr(self.juego.progreso, 'vol_musica', self.slider_musica.valor))
        y += self.fila_h

        # Volumen Efectos
        self.slider_sfx = Slider((self.widget_x, y+14, self.widget_w - 70, 14),
            self.juego.progreso.vol_sfx, 0.0, 1.0,
            lambda v: self.juego.sonidos.set_volumen(v),
            lambda: setattr(self.juego.progreso, 'vol_sfx', self.slider_sfx.valor))
        y += self.fila_h

        # --- FPS ---
        self.sel_fps = SelectorHorizontal(
            (self.widget_x, y, self.widget_w, 42),
            [(30, "30"), (60, "60"), (120, "120")],
            self.juego.progreso.fps,
            self._al_cambiar_fps,
        )
        y += self.fila_h

        # --- Calidad ---
        self.sel_calidad = SelectorHorizontal(
            (self.widget_x, y, self.widget_w, 42),
            [("baja", "Baja"), ("media", "Media"), ("alta", "Alta")],
            self.juego.progreso.calidad,
            self._al_cambiar_calidad,
        )
        y += self.fila_h

        # --- Pantalla Completa ---
        self.toggle_fullscreen = Toggle(
            (self.widget_x, y + 2, 74, 38),
            self.juego.progreso.pantalla_completa,
            self._al_cambiar_fullscreen,
        )
        y += self.fila_h + 20

        # --- Reiniciar Progreso ---
        self.botones.append(Boton(
            (self.x_panel + 100, y, self.panel_w - 200, 46),
            "Reiniciar progreso",
            self._reiniciar_progreso,
        ))
        
        self._filas_y = [
            self.y0,
            self.y0 + self.fila_h,
            self.y0 + self.fila_h * 2,
            self.y0 + self.fila_h * 3,
            self.y0+self.fila_h*4,
        ]

    # ---------- Callbacks ----------
    def _al_cambiar_volumen(self, v):
        self.juego.ajustes["volumen"] = v
        self.juego.sonidos.set_volumen(v)
        try:
            pygame.mixer.music.set_volume(v)
        except Exception:
            pass

    def _al_soltar_volumen(self):
        # Guarda en JSON solo al soltar el mouse para evitar lag
        self.juego.progreso.volumen = self.juego.ajustes["volumen"]

    def _al_cambiar_fps(self, v):
        self.juego.ajustes["fps"] = v
        self.juego.progreso.fps = v

    def _al_cambiar_calidad(self, v):
        self.juego.progreso.calidad = v

    def _al_cambiar_fullscreen(self, v):
        self.juego.progreso.pantalla_completa = v
        try:
            flags = pygame.SCALED
            if v:
                flags |= pygame.FULLSCREEN
            self.juego.pantalla = pygame.display.set_mode(
                (self.juego.ajustes["ancho"], self.juego.ajustes["alto"]),
                flags
            )
        except pygame.error:
            pass

    def _reiniciar_progreso(self):
        self.juego.progreso.resetear()
        self.entrar()   # recarga valores en los widgets

    # ---------- Ciclo ----------
    def entrar(self):
        p = self.juego.progreso
        self.slider_musica.valor = p.vol_musica
        self.slider_musica._actualizar_knob()
        self.slider_sfx.valor = p.vol_sfx
        self.slider_sfx._actualizar_knob()
        self.sel_fps.valor_actual = p.fps
        self.sel_calidad.valor_actual = p.calidad
        self.toggle_fullscreen.valor = p.pantalla_completa
        self.toggle_fullscreen._anim = 1.0 if p.pantalla_completa else 0.0

    def manejar_eventos(self, eventos):
        for e in eventos:
            for b in self.botones:
                if b.manejar_evento(e):
                    self.juego.sonidos.reproducir("click")
                    break
            else:
                if self.slider_musica.manejar_evento(e):
                    continue
                if self.slider_sfx.manejar_evento(e):
                    continue
                if self.sel_fps.manejar_evento(e):
                    self.juego.sonidos.reproducir("click"); continue
                if self.sel_calidad.manejar_evento(e):
                    self.juego.sonidos.reproducir("click"); continue
                if self.toggle_fullscreen.manejar_evento(e):
                    self.juego.sonidos.reproducir("click"); continue

    def actualizar(self, dt):
        super().actualizar(dt)
        self.toggle_fullscreen.actualizar(dt)

    def dibujar(self, pantalla):
        super().dibujar(pantalla)
        
        # Título
        titulo = self.recursos.texto("Ajustes", 44)
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 90)))

        # Etiquetas (Textos) alineados verticalmente con sus controles
        labels = [
            ("Musica",            self._filas_y[0]),
            ("Efectos",           self._filas_y[1]),
            ("FPS",               self._filas_y[2]),
            ("Graficos",   self._filas_y[3]),
            ("Fullscreen", self._filas_y[4]),
        ]
        for txt, y in labels:
            lbl = self.recursos.texto(txt, 20)
            pantalla.blit(lbl, lbl.get_rect(midleft=(self.x_panel, y + 21)))

        # Controles
        self.slider_musica.dibujar(pantalla)
        pct = self.recursos.texto(f"{int(self.slider_musica.valor * 100)}%", 20)
        pantalla.blit(pct, pct.get_rect(midleft=(self.slider_musica.rect.right + 12, self.slider_musica.rect.centery)))

        self.slider_sfx.dibujar(pantalla)
        pct = self.recursos.texto(f"{int(self.slider_sfx.valor * 100)}%", 20)
        pantalla.blit(pct, pct.get_rect(midleft=(self.slider_sfx.rect.right + 12, self.slider_sfx.rect.centery)))

        self.sel_fps.dibujar(pantalla, self.recursos)
        self.sel_calidad.dibujar(pantalla, self.recursos)
        self.toggle_fullscreen.dibujar(pantalla)
        for b in self.botones:
            b.dibujar(pantalla, self.recursos)