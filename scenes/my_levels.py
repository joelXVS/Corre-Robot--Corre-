import os
import json
import pygame
from scenes.scene import Escena
from ui.button import Boton
from ajustes import ANCHO, ALTO

class EscenaMisNiveles(Escena):
    NOMBRE_UI = "niveles"

    def __init__(self, juego):
        super().__init__(juego)
        self.ruta_usuario = "levels/usuario"
        self.scroll_y = 0
        self.botones = []
        self.card_rects = []
        
        # Variables para renombrar
        self.renombrando = None
        self.texto_nombre = ""

    def entrar(self):
        os.makedirs(self.ruta_usuario, exist_ok=True)
        self.juego.musica("assets/sonidos/lobby.mp3", loop=True)
        self._cargar_niveles()

    def _cargar_niveles(self):
        self.niveles = [f for f in os.listdir(self.ruta_usuario) if f.endswith(".txt")]
        self.niveles.sort()
        
        self.botones = [
            Boton((20, 20, 150, 45), "< Volver", lambda: self.juego.cambiar_escena("lobby"), color=(200, 80, 80)),
            Boton((ANCHO - 220, 20, 200, 45), "+ CREAR NIVEL", self._crear_nuevo, color=(100, 200, 80))
        ]
        
        self.card_rects = []
        y = 100 - self.scroll_y
        for i, archivo in enumerate(self.niveles):
            if -200 < y < ALTO:
                card_rect = pygame.Rect(ANCHO//2 - 300, y, 600, 100)
                self.card_rects.append(card_rect)
                
                self.botones.append(Boton((card_rect.x + 20, card_rect.y + 25, 80, 50), "Jugar", (lambda a=archivo: self._jugar(a)), color=(100, 200, 80)))
                self.botones.append(Boton((card_rect.right - 260, card_rect.y + 25, 100, 50), "Renombrar", (lambda a=archivo: self._iniciar_renombrar(a)), color=(150, 150, 200)))
                self.botones.append(Boton((card_rect.right - 150, card_rect.y + 25, 60, 50), "Editar", (lambda a=archivo: self._editar(a)), color=(100, 150, 200)))
                self.botones.append(Boton((card_rect.right - 80, card_rect.y + 25, 60, 50), "X", (lambda a=archivo: self._borrar(a)), color=(200, 80, 80)))
            y += 120

    def _iniciar_renombrar(self, archivo):
        self.renombrando = archivo
        self.texto_nombre = archivo.replace(".txt", "")

    def _guardar_renombre(self):
        if self.renombrando:
            nuevo_nombre = self.texto_nombre.strip()
            if nuevo_nombre and nuevo_nombre != self.renombrando.replace(".txt", ""):
                ruta_vieja = os.path.join(self.ruta_usuario, self.renombrando)
                ruta_nueva = os.path.join(self.ruta_usuario, nuevo_nombre + ".txt")
                
                # Renombrar txt
                os.rename(ruta_vieja, ruta_nueva)
                
                # Renombrar JSON
                json_viejo = ruta_vieja.replace(".txt", ".json")
                json_nuevo = ruta_nueva.replace(".txt", ".json")
                if os.path.exists(json_viejo):
                    os.rename(json_viejo, json_nuevo)
                    
            self.renombrando = None
            self._cargar_niveles()

    def _crear_nuevo(self):
        self.juego.escenas["editor"].cargar_nivel(None)
        self.juego.cambiar_escena("editor")

    def _editar(self, archivo):
        self.juego.escenas["editor"].cargar_nivel(os.path.join(self.ruta_usuario, archivo))
        self.juego.cambiar_escena("editor")

    def _jugar(self, archivo):
        ruta = os.path.abspath(os.path.join(self.ruta_usuario, archivo))
        cfg = {"archivo": ruta, "nombre": "Mi Nivel", "musica": "Sector_Alpha.mp3", "fondo": "fondos/bg_001.png", "suelo": "suelos/ground001.png"}
        ruta_json = ruta.replace(".txt", ".json")
        if os.path.exists(ruta_json):
            try:
                with open(ruta_json, 'r') as f:
                    datos = json.load(f)
                    cfg.update(datos)
            except: pass
            
        self.juego.nivel_prueba = cfg
        self.juego.return_scene = "mis_niveles"
        self.juego.cambiar_escena("cargando")

    def _borrar(self, archivo):
        try:
            os.remove(os.path.join(self.ruta_usuario, archivo))
            ruta_json = os.path.join(self.ruta_usuario, archivo.replace(".txt", ".json"))
            if os.path.exists(ruta_json):
                os.remove(ruta_json)
            self._cargar_niveles()
        except OSError:
            pass

    def manejar_eventos(self, eventos):
        if self.renombrando:
            for e in eventos:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN:
                        self._guardar_renombre()
                    elif e.key == pygame.K_ESCAPE:
                        self.renombrando = None
                    elif e.key == pygame.K_BACKSPACE:
                        self.texto_nombre = self.texto_nombre[:-1]
                    else:
                        if len(self.texto_nombre) < 16 and e.unicode.isprintable():
                            self.texto_nombre += e.unicode
            return

        for e in eventos:
            if e.type == pygame.MOUSEWHEEL:
                self.scroll_y -= e.y * 30
                max_scroll = max(0, len(self.niveles) * 120 - 300)
                self.scroll_y = max(0, min(self.scroll_y, max_scroll))
                self._cargar_niveles()
            for b in self.botones:
                if b.manejar_evento(e):
                    self.juego.sonidos.reproducir("click")
                    break

    def dibujar(self, pantalla):
        pantalla.fill((30, 40, 60))
        
        for x in range(0, ANCHO, 40):
            pygame.draw.line(pantalla, (40, 50, 70), (x, 0), (x, ALTO))
        for y in range(0, ALTO, 40):
            pygame.draw.line(pantalla, (40, 50, 70), (0, y), (ANCHO, y))

        for i, rect in enumerate(self.card_rects):
            pygame.draw.rect(pantalla, (20, 25, 40), (rect.x, rect.y + 5, rect.width, rect.height), border_radius=10)
            pygame.draw.rect(pantalla, (60, 70, 100), rect, border_radius=10)
            pygame.draw.rect(pantalla, (100, 150, 200), rect, 3, border_radius=10)
            
            # Centrar el nombre vertical y horizontalmente (ajustado para no chocar con botones)
            nombre = self.niveles[i].replace(".txt", "")
            if self.renombrando == self.niveles[i]:
                box_rect = pygame.Rect(rect.x + 100, rect.y + 25, 240, 50)
                pygame.draw.rect(pantalla, (20, 20, 20), box_rect, border_radius=5)
                
                txt = self.recursos.texto(self.texto_nombre + "|", 24, (255, 255, 0))
                pantalla.blit(txt, txt.get_rect(center=box_rect.center))
            else:
                tamano = 28
                max_ancho = 230
                
                txt = self.recursos.texto(nombre, tamano, (255, 255, 255))
                
                while txt.get_width() > max_ancho and tamano > 12:
                    tamano -= 1
                    txt = self.recursos.texto(nombre, tamano, (255, 255, 255))
                    
                pantalla.blit(txt, txt.get_rect(center=(rect.x + 220, rect.centery)))

        titulo = self.recursos.texto("MIS NIVELES", 50)
        sombra = self.recursos.texto("MIS NIVELES", 50, (0, 0, 0))
        pantalla.blit(sombra, sombra.get_rect(center=(ANCHO // 2 + 3, 53)))
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 50)))
        
        if not self.niveles:
            txt = self.recursos.texto("No tienes niveles. ¡Crea uno!", 30, (200, 200, 200))
            pantalla.blit(txt, txt.get_rect(center=(ANCHO // 2, ALTO // 2)))
            
        for b in self.botones:
            b.dibujar(pantalla, self.recursos)
            
        if self.renombrando:
            txt = self.recursos.texto("Presiona ENTER para guardar o ESC para cancelar", 20, (200, 200, 200))
            pantalla.blit(txt, txt.get_rect(center=(ANCHO // 2, ALTO - 30)))