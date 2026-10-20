"""Gestor central de recursos: fuentes, iconos HUD, animaciones y fondos de UI."""
import os
import pygame
from animator import Animacion
from spritesheet import DivisorSpritesheet
from ajustes import ANCHO, ALTO, FUENTE, TAM_TILE


class Recursos:
    RUTA_FUENTE = FUENTE

    # Cada personaje ocupa 3 filas (idle / caminar / salto) en personajes.png
    PERSONAJES = [
        {"nombre": "Atlas",    "fila_idle": (0, 70, 72, 0), "fila_caminar": (1, 70, 72, 0), "fila_salto": (2, 70, 72, 0), "fila_daño": (3, 70, 72, 0), "fila_muerte": (4, 70, 72, 0), "color": (100, 200, 255), "vida_maxima": 43800, "energia_maxima": 80, "requisito": None},
        {"nombre": "MIO",      "fila_idle": (0, 74, 73, 0), "fila_caminar": (1, 74, 73, 0), "fila_salto": (2, 74, 73, 0), "fila_daño": (3, 74, 73, 0), "fila_muerte": (4, 74, 73, 0), "color": (255, 160, 200), "vida_maxima": 54150, "energia_maxima": 80, "requisito": "Completa 5 niveles"},
        {"nombre": "Nyx",      "fila_idle": (0, 88, 77, 0), "fila_caminar": (1, 88, 77, 0), "fila_salto": (2, 88, 77, 0), "fila_daño": (3, 88, 77, 0), "fila_muerte": (4, 88, 77, 0), "color": (160, 255, 180), "vida_maxima": 60000, "energia_maxima": 90, "requisito": "Completa 15 niveles"},
        {"nombre": "Vega",     "fila_idle": (0, 78, 76, 0), "fila_caminar": (1, 78, 76, 0), "fila_salto": (2, 78, 76, 0), "fila_daño": (3, 78, 76, 0), "fila_muerte": (4, 78, 76, 0), "color": (255, 160, 200), "vida_maxima": 46200, "energia_maxima": 100, "requisito": "Recoge 1000 ítems"},
        {"nombre": "Xperia51", "fila_idle": (0, 80, 80, 0), "fila_caminar": (1, 80, 80, 0), "fila_salto": (2, 80, 80, 0), "fila_daño": (3, 80, 80, 0), "fila_muerte": (4, 80, 80, 0), "color": (160, 255, 180), "vida_maxima": 68000, "energia_maxima": 100, "requisito": "Encuentra el código secreto"},
    ]

    def __init__(self):
        self._fuentes = {}
        self._iconos = None
        self._anim_items = {}
        self._anim_robots = {}
        self._personajes_cache = None

    # ---------- Fuentes ----------
    def fuente(self, tamano):
        if tamano not in self._fuentes:
            if os.path.exists(self.RUTA_FUENTE):
                self._fuentes[tamano] = pygame.font.Font(self.RUTA_FUENTE, tamano)
            else:
                self._fuentes[tamano] = pygame.font.SysFont("Arial", tamano)
        return self._fuentes[tamano]

    def texto(self, txt, tamano=20, color=(255, 255, 255)):
        return self.fuente(tamano).render(str(txt), True, color)

    # ---------- Iconos del HUD ----------
    def iconos_hud(self):
        if self._iconos is not None:
            return self._iconos
        ruta = "assets/spritesheets/hud_iconos.png"
        nombres = ["vida", "energia", "puntaje", "nivel"]
        if os.path.exists(ruta):
            frames = DivisorSpritesheet.dividir_fila(ruta, 32, 32, 0, len(nombres))
            self._iconos = dict(zip(nombres, frames))
        else:
            colores = {"vida": (220, 60, 60), "energia": (60, 180, 220),
                       "puntaje": (220, 200, 60), "nivel": (120, 200, 120)}
            self._iconos = {}
            for n, c in colores.items():
                s = pygame.Surface((32, 32), pygame.SRCALPHA)
                pygame.draw.circle(s, c, (16, 16), 13)
                pygame.draw.circle(s, (0, 0, 0), (16, 16), 13, 2)
                self._iconos[n] = s
        return self._iconos
    
    # ---------- Bloques y Enemigos Nuevos ----------
    def _cargar_bloques(self):
        if hasattr(self, "_bloques"): return self._bloques
        ruta = "assets/spritesheets/bloques.png"
        if os.path.exists(ruta):
            # La imagen tiene 8 columnas y 6 filas (8x6)
            self._bloques = DivisorSpritesheet.dividir(ruta, 32, 32, 8, 6)
        else:
            self._bloques = []
        return self._bloques
    
    def obtener_bloque(self, char):
        """Devuelve el Surface del bloque escalado a TAM_TILE."""
        bloques = self._cargar_bloques()
        
        if not bloques:
            return None
            
        # Mapeo exacto de caracteres a (fila, columna) en la spritesheet
        mapeo = {
            # Bloques no rotables
            '#': (0, 0), '$': (0, 1), '%': (0, 2), '&': (0, 3), '/': (0, 4), '=': (0, 5),
            # Flechas rotables
            'L': (0, 6), 'R': (0, 7), 'U': (1, 0), 'D': (1, 1),
            # Bloques especiales rotables
            'q': (1, 2), 'w': (1, 3), 'e': (1, 4), 'r': (1, 5),
            't': (1, 6), 'y': (1, 7), 'u': (2, 0), 'i': (2, 1),
            'o': (2, 2), 'p': (2, 3), 'a': (2, 4), 's': (2, 5),
            'd': (2, 6), 'f': (2, 7),
            # Rejilla rotable
            'g': (3, 0), 'h': (3, 1), 'j': (3, 2), 'k': (3, 3),
            # Losa rotable
            'l': (3, 4), 'ñ': (3, 5), 'z': (3, 6), 'x': (3, 7),
            # Bloque especial rotable
            'c': (4, 0), 'v': (4, 1), 'b': (4, 2), 'n': (4, 3),
            
            # Pinchos
            '{': (4, 4), '}': (4, 5), 'm': (4, 6), ',': (4, 7),
            '[': (5, 0), ']': (5, 1), '.': (5, 2), '-': (5, 3),
            '^': (5, 4), '>': (5, 5), '~': (5, 6), '<': (5, 7),
        }
        
        if char not in mapeo:
            return None
            
        fila, col = mapeo[char]
        idx = fila * 8 + col
        
        if idx >= len(bloques):
            return None
            
        img = bloques[idx]
        return pygame.transform.scale(img, (TAM_TILE, TAM_TILE))
    
    def anim_enemigo(self, nombre="enemigo001"):
        ruta = f"assets/spritesheets/{nombre}.png"
        if not os.path.exists(ruta): return None
                    
        if nombre == "enemigo001":
            frames = DivisorSpritesheet.dividir(ruta, 20, 11, 5, 1)
            frames_scaled = [pygame.transform.scale(f, (TAM_TILE, TAM_TILE)) for f in frames]
            anim = Animacion(frames_scaled, fps=6)
            return {"idle": anim, "walk": anim, "attack": anim} 
            
        elif nombre in ("enemigo002", "enemigo003"):
            # Tamaños exactos por fila (ancho, alto) según tu código
            sizes = [(49, 71, 8, 40), (53, 79, 8, 40), (80, 73, 7, 60)] if nombre == "enemigo002" else [(62, 54, 8, 40), (60, 64, 8, 40), (74, 58, 8, 40)]
            
            hoja = pygame.image.load(ruta).convert_alpha()
            frames = []
            y_offset = 0
            
            # Recorremos las filas sumando la altura anterior para no cortar mal
            for w, h, c, tam in sizes:
                for col in range(c):
                    rect = pygame.Rect(col * w, y_offset, w, h)
                    if rect.right <= hoja.get_width() and rect.bottom <= hoja.get_height():
                        surf = hoja.subsurface(rect).copy()
                        surf = pygame.transform.scale(surf, (tam, TAM_TILE))
                        frames.append(surf)
                y_offset += h # Sumamos la altura de esta fila para la siguiente
                
            idle = Animacion(frames[0:8], fps=6)
            walk = Animacion(frames[8:16], fps=10)
            attack = Animacion(frames[16:24], fps=8, loop=True) 
            
            return {"idle": idle, "walk": walk, "attack": attack}
                
        return None
    
    # ---------- Ítems (clon para no compartir estado) ----------
    def anim_item(self, nombre):
        if nombre not in self._anim_items:
            self._anim_items[nombre] = self._construir_anim_item(nombre)
        return self._anim_items[nombre].clonar()

    def _construir_anim_item(self, nombre):
        ruta = f"assets/spritesheets/{nombre}.png"
        colores = {"bateria": (255, 220, 50),
                   "engranaje": (180, 180, 200),
                   "codigo": (100, 255, 100),
                   "codigo_secreto": (255, 100, 255),}
        
        tamano = {"bateria": (36, 36, 8),
                   "engranaje": (48, 48, 12),
                   "codigo": (48, 48, 8),
                   "codigo_secreto": (48, 48, 8),}
        
        if os.path.exists(ruta):
            frames = DivisorSpritesheet.dividir(ruta, tamano.get(nombre, (24, 24, 4))[0], tamano.get(nombre, (24, 24, 4))[1], tamano.get(nombre, (24, 24, 4))[2], 1)
            return Animacion(frames, fps=8)
        surf = pygame.Surface(tamano.get(nombre, (24, 24, 4)), pygame.SRCALPHA)
        
        pygame.draw.rect(surf, colores.get(nombre, (255, 255, 255)), (0, 0, tamano.get(nombre, (24, 24, 4))[0], tamano.get(nombre, (24, 24, 4))[1]))
        pygame.draw.rect(surf, (0, 0, 0), (0, 0, tamano.get(nombre, (24, 24, 4))[0], tamano.get(nombre, (24, 24, 4))[1]), 1)
        return Animacion([surf], fps=1)

    # ---------- Robot según personaje ----------
    def anim_robot(self, indice_personaje):
        if indice_personaje not in self._anim_robots:
            self._anim_robots[indice_personaje] = self._construir_anim_robot(indice_personaje)
        return {k: v.clonar() for k, v in self._anim_robots[indice_personaje].items()}

    def _construir_anim_robot(self, indice_personaje):
        meta = self.PERSONAJES[indice_personaje % len(self.PERSONAJES)]
        ruta = f"assets/spritesheets/{meta['nombre']}.png"
        
        if os.path.exists(ruta):
            hoja = pygame.image.load(ruta).convert_alpha()
            
            # Lista de filas en orden usando las tuplas (fila, ancho, alto)
            filas = [
                meta["fila_idle"],
                meta["fila_caminar"],
                meta["fila_salto"],
                meta["fila_daño"],
                meta["fila_muerte"]
            ]
            
            # Calculamos los Y offsets sumando las alturas
            y_offsets = []
            y_actual = 0
            for _, w, h, margen in filas:
                y_offsets.append(y_actual)
                y_actual += h + margen
                
            animaciones = {}
            nombres = ["idle", "caminar", "salto", "daño", "muerte"]
            frames_count = [8, 8, 7, 6, 8] # Cantidad de frames por fila
            fps_val = [8, 10, 8, 8, 8]
            
            for i, nombre in enumerate(nombres):
                _, w, h, _ = filas[i]
                y_off = y_offsets[i]
                frames = []
                
                for c in range(frames_count[i]):
                    rect = pygame.Rect(c * w, y_off, w, h)
                    if rect.right <= hoja.get_width() and rect.bottom <= hoja.get_height():
                        surf = hoja.subsurface(rect).copy()
                        
                        # Escalado proporcional para que no se vea aplastado
                        ratio = min(38 / w, 46 / h)
                        nuevo_w = int(w * ratio)
                        nuevo_h = int(h * ratio)
                        surf = pygame.transform.scale(surf, (nuevo_w, nuevo_h))
                        
                        # Lienzo transparente de 32x40 y alineación abajo
                        lienzo = pygame.Surface((32, 40), pygame.SRCALPHA)
                        offset_x = (32 - nuevo_w) // 2
                        offset_y = 40 - nuevo_h
                        lienzo.blit(surf, (offset_x, offset_y))
                        
                        frames.append(lienzo)

                animaciones[nombre] = Animacion(
                    frames, 
                    fps=fps_val[i], 
                    loop=(nombre not in ["salto", "daño", "muerte"])
                )
            return animaciones        
        
    def anim_puerta(self):
        ruta = "assets/spritesheets/door.png"
        if not os.path.exists(ruta):
            return None
            
        hoja = pygame.image.load(ruta).convert_alpha()
        w_total, h_total = hoja.get_size()
        
        # Asumimos 18 frames horizontales
        ancho_f = w_total // 16
        frames = []
        for col in range(16):
            rect = pygame.Rect(col * ancho_f, 0, ancho_f, h_total)
            surf = pygame.transform.scale(hoja.subsurface(rect).copy(), (TAM_TILE, TAM_TILE))
            frames.append(surf)
            
        return Animacion(frames, fps=10, loop=False)
        
    # ---------- Catálogo de personajes (para el selector) ----------
    def meta_personaje(self, indice_personaje):
        return self.PERSONAJES[indice_personaje % len(self.PERSONAJES)]

    def personajes(self):
        """[(meta_dict, anims), ...] — para el selector."""
        if self._personajes_cache is None:
            self._personajes_cache = [
                (meta, self._construir_anim_robot(i))
                for i, meta in enumerate(self.PERSONAJES)
            ]
        return self._personajes_cache

    # ---------- Fondos animados de interfaces ----------
    def fondo_nivel(self, nombre):
        if not nombre:
            return None
        ruta = f"assets/{nombre}"
        if not os.path.exists(ruta):
            return None
        img = pygame.image.load(ruta).convert_alpha()
        img = pygame.transform.scale(img, (ANCHO, ALTO))
        img.set_alpha(int(255 * 0.8))
        return img

    def tile_suelo(self, nombre):
        if not nombre:
            return None
        ruta = f"assets/{nombre}"
        if not os.path.exists(ruta):
            return None
        return pygame.image.load(ruta).convert_alpha()