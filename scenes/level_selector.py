import pygame
from scenes.scene import Escena
from ui.button import Boton
from ajustes import ANCHO, ALTO


class EscenaNiveles(Escena):
    NOMBRE_UI = "niveles"

    def __init__(self, juego):
        super().__init__(juego)
        self.mostrar_info = False
        self._crear_botones()
        
    def entrar(self):
        self.juego.musica("assets/sonidos/lobby.mp3", loop=True)

    def _crear_botones(self):
        self.botones = [
            Boton((20, 20, 130, 42), "< Volver",
                  lambda: self.juego.cambiar_escena("lobby")),
        ]
        total = len(self.juego.niveles)
        ancho_btn, alto_btn, sep, cols = 110, 110, 20, 5
        x0 = (ANCHO - (cols * (ancho_btn + sep) - sep)) // 2
        y0 = 160
        
        for i in range(total):
            fila, col = i // cols, i % cols
            x = x0 + col * (ancho_btn + sep)
            y = y0 + fila * (alto_btn + sep)
            desbloqueado = i <= self.juego.nivel_max_desbloqueado
            
            # La función debe estar DENTRO del bucle para capturar el valor de 'i'
            def jugar(idx=i):
                self.juego.indice_nivel = idx
                self.juego.return_scene = "niveles" # <--- Soluciona el bug de retorno
                self.juego.cambiar_escena("cargando")
                
            self.botones.append(
                Boton((x, y, ancho_btn, alto_btn), f"{i+1}", jugar, desbloqueado)
            )

        self.botones.append(Boton((ANCHO - 170, 20, 150, 42), "Info",
                                  self._toggle_info, color=(70, 130, 200)))

    def _toggle_info(self):
        self.mostrar_info = not self.mostrar_info

    def manejar_eventos(self, eventos):
        if self.mostrar_info:
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if pygame.Rect(ANCHO // 2 - 100, ALTO - 80, 200, 50).collidepoint(e.pos):
                        self.mostrar_info = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    self.mostrar_info = False
            return
        super().manejar_eventos(eventos)

    def dibujar(self, pantalla):
        super().dibujar(pantalla)
        titulo = self.recursos.texto("Selecciona un nivel", 40)
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 90)))

        if self.mostrar_info:
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 210))
            pantalla.blit(overlay, (0, 0))

            panel = pygame.Rect(ANCHO // 2 - 320, 100, 640, ALTO - 200)
            pygame.draw.rect(pantalla, (40, 50, 75), panel, border_radius=12)
            pygame.draw.rect(pantalla, (100, 150, 220), panel, 3, border_radius=12)

            titulo2 = self.recursos.texto("Información de niveles", 28)
            pantalla.blit(titulo2, titulo2.get_rect(center=(panel.centerx, panel.y + 35)))

            y = panel.y + 80
            for i, cfg in enumerate(self.juego.niveles_cfg[:10]):
                nombre = cfg.get("nombre", f"Nivel {i+1}")
                musica = cfg.get("musica", "Sin música")
                linea = f"{i+1}. {nombre}  —  {musica}"
                txt = self.recursos.texto(linea, 20, (220, 220, 240))
                pantalla.blit(txt, (panel.x + 25, y))
                y += 32
                if y > panel.bottom - 80: break

            btn = Boton((ANCHO // 2 - 100, ALTO - 80, 200, 50), "Cerrar", self._toggle_info)
            btn.dibujar(pantalla, self.recursos)