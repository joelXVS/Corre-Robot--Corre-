import pygame
from scenes.scene import Escena
from ui.button import Boton
from ajustes import ANCHO, ALTO


class EscenaPersonajes(Escena):
    NOMBRE_UI = "personajes"

    def __init__(self, juego):
        super().__init__(juego)
        self.personajes = self.recursos.personajes()    # [(meta, anims), ...]
        self.indice = self.juego.personaje_seleccionado
        self.mostrar_stats = False
        self._crear_botones()

    def _crear_botones(self):
        self.botones.append(Boton((20, 20, 130, 42), "< Volver",
                                  lambda: self.juego.cambiar_escena("lobby")))
        self.botones.append(Boton((ANCHO // 2 - 220, 430, 100, 50), "<", self._prev))
        self.botones.append(Boton((ANCHO // 2 + 120, 430, 100, 50), ">", self._next))
        self.botones.append(Boton((ANCHO // 2 - 100, 430, 200, 50), "Elegir", self._elegir))
        self.botones.append(Boton((ANCHO - 180, 20, 160, 42), "Estadísticas", self._toggle_stats))

    def _toggle_stats(self):
        self.mostrar_stats = not self.mostrar_stats
        
    def _prev(self):
        self.indice = (self.indice - 1) % len(self.personajes)

    def _next(self):
        self.indice = (self.indice + 1) % len(self.personajes)

    def _elegir(self):
        meta, _ = self.personajes[self.indice]
        if not self.juego.progreso.esta_desbloqueado(meta):
            return
        self.juego.personaje_seleccionado = self.indice

    def actualizar(self, dt):
        super().actualizar(dt)
        for _, anims in self.personajes:
            anims["idle"].actualizar(dt)
            
    def manejar_eventos(self, eventos):
        if self.mostrar_stats:
            # Solo permitir cerrar el panel
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    # Botón de cerrar
                    rect_cerrar = pygame.Rect(ANCHO//2 - 100, ALTO - 100, 200, 50)
                    if rect_cerrar.collidepoint(e.pos):
                        self.mostrar_stats = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    self.mostrar_stats = False
            return
        super().manejar_eventos(eventos)

    def dibujar(self, pantalla):
        super().dibujar(pantalla)
        meta, anims = self.personajes[self.indice]
        frame = anims["idle"].frame_actual()
        img = pygame.transform.scale(frame, (frame.get_width() * 4,
                                             frame.get_height() * 4))
        pantalla.blit(img, img.get_rect(center=(ANCHO // 2, 250)))

        titulo = self.recursos.texto("Mi personaje", 38)
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 80)))

        txt = self.recursos.texto(meta["nombre"], 34)
        pantalla.blit(txt, txt.get_rect(center=(ANCHO // 2, 140)))

        stats = self.recursos.texto(
            f"Vida {meta['vida_maxima']}   Energía {meta['energia_maxima']}", 22
        )
        pantalla.blit(stats, stats.get_rect(center=(ANCHO // 2, 340)))

        desbloqueado = self.juego.progreso.esta_desbloqueado(meta)
        if not desbloqueado:
            lock = self.recursos.texto(
                f"BLOQUEADO — {meta['requisito']}", 22, (255, 100, 100)
            )
            pantalla.blit(lock, lock.get_rect(center=(ANCHO // 2, 380)))
        elif self.indice == self.juego.personaje_seleccionado:
            sel = self.recursos.texto("(Seleccionado)", 22, (120, 255, 120))
            pantalla.blit(sel, sel.get_rect(center=(ANCHO // 2, 380)))
            
        if self.mostrar_stats:
            # Overlay semi-transparente
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            pantalla.blit(overlay, (0, 0))

            s = self.juego.progreso.stats
            titulo = self.recursos.texto("Estadísticas de Progreso", 40)
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO//2, 100)))

            lines = [
                f"Niveles Completados: {s['total_completados']}",
                f"Baterías Recogidas: {s['baterias_recogidas']}",
                f"Engranajes Recogidos: {s['engranajes_recogidos']}",
                f"Códigos Encontrados: {s['codigos_recogidos']}",
                f"Código Secreto: {'SÍ' if s['codigo_secreto_encontrado'] else 'NO'}",
                f"Puntuación Máxima: {s['puntuacion_maxima']}",
            ]
            y = 180
            for line in lines:
                txt = self.recursos.texto(line, 24)
                pantalla.blit(txt, txt.get_rect(center=(ANCHO//2, y)))
                y += 40

            # Botón cerrar
            btn_cerrar = Boton((ANCHO//2 - 100, y + 20, 200, 50), "Cerrar", self._toggle_stats)
            btn_cerrar.dibujar(pantalla, self.recursos)