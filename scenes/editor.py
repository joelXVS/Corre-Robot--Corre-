import os
import json
import pygame
import math
from scenes.scene import Escena
from ui.button import Boton
from ajustes import ANCHO, ALTO, TAM_TILE


class EscenaEditor(Escena):
    NOMBRE_UI = None
    FILAS_EDITABLES = 12

    def __init__(self, juego):
        super().__init__(juego)
        self.offset_y = 50
        self.palette_y = ALTO - 160 

        self.filas = self.FILAS_EDITABLES
        self._cache_sprites = {}
        self.columnas = 2000
        self.grid = [[' ' for _ in range(self.columnas)] for _ in range(self.filas)]
        self.habilidades_codigo = {}
        
        # Zoom
        self.zoom = 1.0
        
        self.cam_x = 0
        self.cam_y = 0
        self.archivo_actual = None

        # Estados de UI
        self.tab_actual = "BUILD"
        self.pagina_build = 0
        self.herramienta = "pincel"
        self.char_actual = '#'
        self.swipe_activo = False
        self.borrador_activo = False
        self.arrastrando_borrador = False
        self.dist_mov = 1
        
        # Selección y arrastre
        self.seleccion = [] 
        self.drag_seleccion_start = None
        self.arrastrando_cam = False
        self.drag_start = (0, 0)
        
        # Modales
        self.pausado = False
        self.mostrar_config = False
        self.configurando_habilidad = None 
        self.char_previo = None 

        # Configuración del nivel
        self.cfg_fondo = "fondos/bg_001.png"
        self.cfg_suelo = "None"
        self.cfg_musica = "Sector_Alpha.mp3"
        self.listas_assets = self._escanear_assets()
        self.idx_fondo = 0
        self.idx_suelo = 0
        self.idx_musica = 0
        
        self._actualizar_tamano_grilla()
        self._crear_botones()
        self._inicializar_grid()

    def _escanear_assets(self):
        fondos = sorted(os.listdir("assets/fondos")) if os.path.exists("assets/fondos") else ["None"]
        suelos = sorted(os.listdir("assets/suelos")) if os.path.exists("assets/suelos") else ["None"]
        musicas = sorted(m for m in os.listdir("assets/sonidos") if m.endswith(".mp3") or m.endswith(".ogg"))
        musicas = [m for m in musicas if "lobby" not in m]
        return {"fondos": fondos, "suelos": ["None"], "musicas": musicas}

    def _inicializar_grid(self):
        self.grid = [[' ' for _ in range(self.columnas)] for _ in range(self.filas)]
        self.habilidades_codigo.clear()

    def entrar(self):
        self.juego.detener_musica()
        self.pausado = False
        self.mostrar_config = False
        self.seleccion.clear()
        self.borrador_activo = False

    def cargar_nivel(self, ruta):
        self.archivo_actual = ruta
        self._inicializar_grid()
        self.cam_x = 0
        self.cam_y = 0
        self.pausado = False
        self.mostrar_config = False

        if ruta and os.path.exists(ruta):
            with open(ruta, 'r', encoding='utf-8') as f:
                lineas = f.read().splitlines()
            
            if len(lineas) >= 2:
                interior = lineas[1:-1]
            else:
                interior = lineas
                
            interior.reverse()
            for r, linea in enumerate(interior):
                if r >= self.filas: break
                linea = linea.ljust(self.columnas)
                for c, char in enumerate(linea):
                    if 0 <= r < self.columnas:
                        self.grid[r][c] = char
                        
            ruta_json = ruta.replace(".txt", ".json")
            if os.path.exists(ruta_json):
                try:
                    with open(ruta_json, 'r') as f:
                        datos = json.load(f)
                        self.cfg_musica = datos.get("musica", self.cfg_musica)
                        self.cfg_fondo = datos.get("fondo", self.cfg_fondo)
                        self.cfg_suelo = datos.get("suelo", self.cfg_suelo)
                        for k, v in datos.get("codigos", {}).items():
                            r, c = map(int, k.split(','))
                            self.habilidades_codigo[(r, c)] = v
                except: pass

    # ---------- BOTONES Y UI ----------
    def _crear_botones(self):
        self.botones_top = [
            Boton((10, 10, 100, 40), "Config", self._toggle_config, color=(100, 150, 200)),
            Boton((ANCHO - 115, 10, 100, 40), "Menú", self._pausar, color=(200, 80, 80)),
        ]

        self.tabs = [
            ("BUILD", 10, (80, 200, 100)),
            ("EDIT", 50, (60, 180, 220)),
            ("DELETE", 90, (220, 80, 80)),
        ]

        # Herramientas Generales
        self.btn_pincel = Boton((ANCHO - 120, self.palette_y + 10, 110, 30), "Pincel", lambda: self._set_herr("pincel"), color=(80, 160, 220))
        self.btn_swipe = Boton((ANCHO - 120, self.palette_y + 45, 110, 30), "SWIPE", self._toggle_swipe, color=(180, 150, 60))
        
        # Zoom
        self.btn_zoom_in = Boton((ANCHO - 120, self.palette_y + 80, 50, 30), "Zoom +", self._zoom_in, color=(150, 150, 150))
        self.btn_zoom_out = Boton((ANCHO - 60, self.palette_y + 80, 50, 30), "Zoom -", self._zoom_out, color=(150, 150, 150))

        # Botones de Edición
        self.btn_move_up  = Boton((240, self.palette_y + 10, 40, 30), "^", lambda: self._mover_seleccion(0, -1), color=(100, 100, 100))
        self.btn_move_izq = Boton((195, self.palette_y + 50, 40, 30), "<-", lambda: self._mover_seleccion(-1, 0), color=(100, 100, 100))
        self.btn_move_der = Boton((285, self.palette_y + 50, 40, 30), "->", lambda: self._mover_seleccion(1, 0), color=(100, 100, 100))
        self.btn_move_dn  = Boton((240, self.palette_y + 90, 40, 30), "v", lambda: self._mover_seleccion(0, 1), color=(100, 100, 100))
        
        self.btn_dist_1 = Boton((360, self.palette_y + 20, 35, 30), "1", lambda: self._set_dist(1), color=(100, 100, 100))
        self.btn_dist_3 = Boton((400, self.palette_y + 20, 35, 30), "3", lambda: self._set_dist(3), color=(100, 100, 100))
        self.btn_dist_5 = Boton((440, self.palette_y + 20, 35, 30), "5", lambda: self._set_dist(5), color=(100, 100, 100))
                
        # Botones DELETE
        self.btn_delete_sel = Boton((160, self.palette_y + 20, 150, 40), "Borrar Selección", self._borrar_seleccion, color=(220, 80, 80))
        self.btn_borrador = Boton((320, self.palette_y + 20, 150, 40), "Borrador", self._toggle_borrador, color=(200, 100, 50))

        # Grid de BUILD (Paginado) - Añadidos todos los nuevos elementos
        self.lista_build = [
            # Página 1
            ('#', 'Bloque'), ('$', 'Bloque plano'), ('%', 'Bloque de vidrio roto'), ('&', 'Bloque cincelado'), 
            ('/', 'Bloque enrrejado'), ('=', 'Bloque azul'), ('L', 'Flecha izquierda'), ('R', 'Flecha derecha'), 
            ('U', 'Flecha arriba'), ('D', 'Flecha abajo'),
            # Página 2
            ('q', 'Especial 1.1'), ('w', 'Especial 1.2'), ('e', 'Especial 1.3'), ('r', 'Especial 1.4'), 
            ('t', 'Especial 2.1'), ('y', 'Especial 2.2'), ('u', 'Especial 2.3'), ('i', 'Especial 2.4'),
            ('o', 'Especial 3.1'), ('p', 'Especial 3.2'), 
            # Página 3
            ('a', 'Especial 3.3'), ('s', 'Especial 3.4'), ('d', 'Especial 4.1'), ('f', 'Especial 4.2'),
            ('g', 'Bloque de Rejilla 1.1'), ('h', 'Bloque de Rejilla 1.2'), ('j', 'Bloque de Rejilla 1.3'), ('k', 'Bloque de Rejilla 1.4'), 
            ('l', 'Losa 1.1'), ('ñ', 'Losa 1.2'),
            # Página 4
            ('z', 'Losa 1.3'), ('x', 'Losa 1.4'), ('c', 'Bloque Especial 5.1'), ('v', 'Bloque Especial 5.2'), 
            ('b', 'Bloque Especial 5.3'), ('n', 'Bloque Especial 5.4'), ('{', 'Pincho triple 1'), ('}', 'Pincho triple 2'), 
            ('m', 'Pincho triple 3'), (',', 'Pincho triple 4'), 
            # Página 5
            ('[', 'Pincho cuadruple 1'), (']', 'Pincho cuadruple 2'), ('.', 'Pincho cuadruple 3'), ('-', 'Pincho cuadruple 4'),
            ('^', 'Pincho doble 1'), ('>', 'Pincho doble 2'), ('~', 'Pincho doble 3'), ('<', 'Pincho doble 4'),
            ('P', 'Robot'), ('*', 'Puerta'), 
            # Página 6
            ('B', 'Bat'), ('E', 'Engr'), ('C', 'Código'), ('N', 'Coche'), 
            ('K', 'Caminante'), ('H', 'Garbage'), ('?', 'Secreto')
        ]
        
        self.btn_build_items = []
        self.btn_build_prev = Boton((0, 0, 40, 30), "<", self._prev_pagina, color=(150, 150, 150))
        self.btn_build_next = Boton((0, 0, 40, 30), ">", self._next_pagina, color=(150, 150, 150))

        # Menú Pausa
        self.botones_pausa = [
            Boton((ANCHO // 2 - 150, 220, 300, 50), "Reanudar", self._pausar),
            Boton((ANCHO // 2 - 150, 290, 300, 50), "Guardar", self._guardar),
            Boton((ANCHO // 2 - 150, 360, 300, 50), "Probar Nivel", self._probar),
            Boton((ANCHO // 2 - 150, 430, 300, 50), "Salir al Menú", self._intentar_cerrar, color=(200, 80, 80)),
        ]

        # Modal Config
        self.btn_prev_fondo = Boton((0, 0, 40, 40), "<", self._prev_fondo, color=(100, 150, 200))
        self.btn_next_fondo = Boton((0, 0, 40, 40), ">", self._next_fondo, color=(100, 150, 200))
        self.btn_prev_suelo = Boton((0, 0, 40, 40), "<", self._prev_suelo, color=(100, 150, 200))
        self.btn_next_suelo = Boton((0, 0, 40, 40), ">", self._next_suelo, color=(100, 150, 200))
        self.btn_prev_musica = Boton((0, 0, 40, 40), "<", self._prev_musica, color=(100, 150, 200))
        self.btn_next_musica = Boton((0, 0, 40, 40), ">", self._next_musica, color=(100, 150, 200))
        self.btn_ok_config = Boton((0, 0, 200, 50), "OK", self._toggle_config)
        
        # Modal Habilidad
        self.btn_hab_doble = Boton((ANCHO//2 - 100, 200, 200, 40), "Doble Salto", lambda: self._set_hab("doble_salto"))
        self.btn_hab_super = Boton((ANCHO//2 - 100, 250, 200, 40), "Súper Salto", lambda: self._set_hab("super_salto"))
        self.btn_hab_volar = Boton((ANCHO//2 - 100, 300, 200, 40), "Volar", lambda: self._set_hab("volar"))
        self.btn_hab_vel   = Boton((ANCHO//2 - 100, 350, 200, 40), "Súper Velocidad", lambda: self._set_hab("super_velocidad"))
        self.btn_hab_res   = Boton((ANCHO//2 - 100, 400, 200, 40), "Resistencia", lambda: self._set_hab("resistencia"))

    # ---------- FUNCIONES DE APOYO ----------
    def _set_char(self, c): 
        self.char_actual = c
        self.herramienta = "pincel"
        self.tab_actual = "BUILD"
        self.borrador_activo = False

    def _toggle_swipe(self):
        self.swipe_activo = not self.swipe_activo
        self.seleccion.clear()
        if self.swipe_activo:
            self.borrador_activo = False # Desactivar borrador si se activa swipe

    def _toggle_borrador(self):
        self.borrador_activo = not self.borrador_activo
        if self.borrador_activo:
            self.swipe_activo = False # Desactivar swipe si se activa borrador

    def _set_dist(self, d):
        self.dist_mov = d
        
    def _set_herr(self, h):
        self.herramienta = h
        self.tab_actual = "BUILD"

    def _toggle_config(self): self.mostrar_config = not self.mostrar_config
    def _pausar(self): self.pausado = not self.pausado

    def _actualizar_tamano_grilla(self):
        alto_disponible = self.palette_y - self.offset_y
        base_tile = alto_disponible / self.filas
        self.TILE_DISP = max(10, int(base_tile * self.zoom))
        
        if hasattr(self, '_cache_sprites'):
            self._cache_sprites.clear()
            
        max_y = max(0, self.filas * self.TILE_DISP - alto_disponible)
        self.cam_y = max(0, min(self.cam_y, max_y))

    def _zoom_in(self):
        self.zoom = min(2.0, self.zoom + 0.25)
        self._actualizar_tamano_grilla()

    def _zoom_out(self):
        self.zoom = max(0.75, self.zoom - 0.25)
        self._actualizar_tamano_grilla()

    def _prev_fondo(self): self.idx_fondo = (self.idx_fondo - 1) % len(self.listas_assets["fondos"]); self.cfg_fondo = "fondos/" + self.listas_assets["fondos"][self.idx_fondo]
    def _next_fondo(self): self.idx_fondo = (self.idx_fondo + 1) % len(self.listas_assets["fondos"]); self.cfg_fondo = "fondos/" + self.listas_assets["fondos"][self.idx_fondo]
    def _prev_suelo(self): self.idx_suelo = (self.idx_suelo - 1) % len(self.listas_assets["suelos"]); self.cfg_suelo = "suelos/" + self.listas_assets["suelos"][self.idx_suelo]
    def _next_suelo(self): self.idx_suelo = (self.idx_suelo + 1) % len(self.listas_assets["suelos"]); self.cfg_suelo = "suelos/" + self.listas_assets["suelos"][self.idx_suelo]
    def _prev_musica(self): self.idx_musica = (self.idx_musica - 1) % len(self.listas_assets["musicas"]); self.cfg_musica = self.listas_assets["musicas"][self.idx_musica]
    def _next_musica(self): self.idx_musica = (self.idx_musica + 1) % len(self.listas_assets["musicas"]); self.cfg_musica = self.listas_assets["musicas"][self.idx_musica]

    # ---------- Lógica BUILD ----------
    def _prev_pagina(self):
        if self.pagina_build > 0:
            self.pagina_build -= 1
            
    def _next_pagina(self):
        if (self.pagina_build + 1) * 10 < len(self.lista_build):
            self.pagina_build += 1

    # ---------- Lógica EDIT ----------
    def _mover_seleccion(self, dx, dy):
        if not self.seleccion: return
        dx *= self.dist_mov
        dy *= self.dist_mov
        
        datos = []
        for (r, c) in self.seleccion:
            if self.grid[r][c] != ' ':
                char = self.grid[r][c]
                hab = self.habilidades_codigo.pop((r, c), None)
                datos.append((char, hab))
                self.grid[r][c] = ' '
            
        nuevos = []
        for i, (r, c) in enumerate(self.seleccion):
            nr, nc = r + dy, c + dx
            if 0 <= nr < self.filas and 0 <= nc < self.columnas:
                char, hab = datos[i]
                self.grid[nr][nc] = char
                if hab:
                    self.habilidades_codigo[(nr, nc)] = hab
                nuevos.append((nr, nc))
                
        self.seleccion = nuevos

    def _borrar_seleccion(self):
        for (r, c) in self.seleccion:
            if self.grid[r][c] != ' ':
                self.grid[r][c] = ' '
                if (r, c) in self.habilidades_codigo:
                    del self.habilidades_codigo[(r, c)]
        self.seleccion.clear()

    # ---------- Lógica Configuración Código ----------
    def _set_hab(self, hab):
        if self.configurando_habilidad:
            self.habilidades_codigo[self.configurando_habilidad] = hab
        self.configurando_habilidad = None
        self.char_previo = None

    # ---------- Guardar / Cargar ----------
    def _probar(self):
        self._guardar()
        if self.archivo_actual:
            self.juego.nivel_prueba = {
                "archivo": os.path.abspath(self.archivo_actual),
                "nombre": "Test",
                "musica": self.cfg_musica,
                "fondo": self.cfg_fondo,
                "suelo": self.cfg_suelo,
            }
            self.juego.return_scene = "editor"
            self.juego.cambiar_escena("cargando")

    def _guardar(self):
        if not self.archivo_actual:
            os.makedirs("levels/usuario", exist_ok=True)
            num = 1
            while os.path.exists(f"levels/usuario/mi_nivel_{num}.txt"):
                num += 1
            self.archivo_actual = f"levels/usuario/mi_nivel_{num}.txt"

        with open(self.archivo_actual, 'w', encoding='utf-8') as f:
            f.write('#' * self.columnas + '\n')
            for r in range(self.filas - 1, -1, -1):
                linea = ''.join(self.grid[r]).ljust(self.columnas)
                f.write(linea + '\n')
            f.write('#' * self.columnas + '\n')

        ruta_json = self.archivo_actual.replace(".txt", ".json")
        codigos_guardados = {f"{r},{c}": hab for (r, c), hab in self.habilidades_codigo.items()}
        
        with open(ruta_json, 'w') as f:
            json.dump({
                "musica": self.cfg_musica, 
                "fondo": self.cfg_fondo, 
                "suelo": self.cfg_suelo,
                "codigos": codigos_guardados
            }, f)

    def _intentar_cerrar(self):
        self.juego.cambiar_escena("mis_niveles")

    def _get_grid_pos(self, pos):
        mx, my = pos
        if my < self.offset_y or my > self.palette_y: return None
        margen_y = max(0, (self.palette_y - self.offset_y - (self.filas * self.TILE_DISP)) // 2)
        
        col = (mx + self.cam_x) // self.TILE_DISP
        row = (my + self.cam_y - self.offset_y - margen_y) // self.TILE_DISP
        if 0 <= row < self.filas and 0 <= col < self.columnas:
            return row, col
        return None

    # ---------- Eventos ----------
    def manejar_eventos(self, eventos):
        if self.mostrar_config:
            for e in eventos:
                for b in (self.btn_prev_fondo, self.btn_next_fondo, self.btn_prev_suelo, self.btn_next_suelo, self.btn_prev_musica, self.btn_next_musica, self.btn_ok_config):
                    b.manejar_evento(e)
            return
            
        if self.configurando_habilidad:
            for e in eventos:
                for b in (self.btn_hab_doble, self.btn_hab_super, self.btn_hab_volar, self.btn_hab_vel, self.btn_hab_res):
                    b.manejar_evento(e)
            return

        if self.pausado:
            for e in eventos:
                for b in self.botones_pausa:
                    if b.manejar_evento(e):
                        self.juego.sonidos.reproducir("click")
                        return
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    self.pausado = False
            return

        for e in eventos:
            # 1. Clics en UI
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for name, y_off, _ in self.tabs:
                    if pygame.Rect(10, self.palette_y + y_off, 110, 35).collidepoint(e.pos):
                        self.tab_actual = name
                        self.seleccion.clear()
                        return
                
                if self.tab_actual == "BUILD":  
                    if self.btn_pincel.manejar_evento(e): return
                    if self.btn_build_prev.manejar_evento(e): return
                    if self.btn_build_next.manejar_evento(e): return
                    for b in self.btn_build_items:
                        if b.manejar_evento(e): return
                        
                    if self.configurando_habilidad:
                        for e in eventos:
                            for b in (self.btn_hab_doble, self.btn_hab_super, self.btn_hab_volar, self.btn_hab_vel, self.btn_hab_res):
                                b.manejar_evento(e)
                        return
                        
                elif self.tab_actual == "EDIT":
                    if self.btn_swipe.manejar_evento(e): return
                    if self.btn_zoom_in.manejar_evento(e): return
                    if self.btn_zoom_out.manejar_evento(e): return
                    if self.btn_move_izq.manejar_evento(e): return
                    if self.btn_move_der.manejar_evento(e): return
                    if self.btn_move_up.manejar_evento(e): return
                    if self.btn_move_dn.manejar_evento(e): return
                    if self.btn_dist_1.manejar_evento(e): return
                    if self.btn_dist_3.manejar_evento(e): return
                    if self.btn_dist_5.manejar_evento(e): return
                    
                elif self.tab_actual == "DELETE":
                    if self.btn_swipe.manejar_evento(e): return
                    if self.btn_zoom_in.manejar_evento(e): return
                    if self.btn_zoom_out.manejar_evento(e): return
                    if self.btn_delete_sel.manejar_evento(e): return
                    if self.btn_borrador.manejar_evento(e): return

                for b in self.botones_top:
                    if b.manejar_evento(e): return

            # 2. Interacción con la Grilla
            gpos = self._get_grid_pos(pygame.mouse.get_pos())
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 2: 
                    self.arrastrando_cam = True
                    self.drag_start = e.pos
                elif e.button == 1 and gpos:
                    r, c = gpos
                    
                    # --- DETECCIÓN DE DOBLE CLIC INFALIBLE ---
                    tiempo_actual = pygame.time.get_ticks()
                    es_doble = (gpos == getattr(self, 'ultimo_click_pos', (0,0)) and 
                                tiempo_actual - getattr(self, 'ultimo_click_tiempo', 0) < 300)
                    
                    self.ultimo_click_pos = gpos
                    self.ultimo_click_tiempo = tiempo_actual
                    
                    # --- LÓGICA DE DOBLE CLIC EN 'C' (Funciona en BUILD y EDIT) ---
                    if es_doble and self.grid[r][c] == 'C':
                        self.configurando_habilidad = gpos
                        self.char_previo = None
                        return # Abre el panel y detiene el evento aquí
                        
                    # --- LÓGICA SEGÚN LA PESTAÑA ---
                    if self.tab_actual == "BUILD":
                        if self.char_actual == 'C':
                            if self.grid[r][c] != 'C':
                                # Si la celda no tiene C, la ponemos y abrimos el panel
                                self.char_previo = self.grid[r][c]
                                self.grid[r][c] = 'C'
                                self.configurando_habilidad = gpos
                        else:
                            # Cualquier otro bloque se pinta normal
                            self.grid[r][c] = self.char_actual
                            
                    elif self.tab_actual == "DELETE" and self.borrador_activo:
                        # Borrado instantáneo
                        self.grid[r][c] = ' '
                        if (r, c) in self.habilidades_codigo:
                            del self.habilidades_codigo[(r, c)]
                        self.arrastrando_borrador = True
                        
                    elif self.tab_actual in ("EDIT", "DELETE"):
                        if self.swipe_activo:
                            self.drag_seleccion_start = gpos
                        else:
                            if gpos not in self.seleccion:
                                if self.grid[gpos[0]][gpos[1]] != ' ':
                                    self.seleccion = [gpos]
                            else:
                                self.seleccion.remove(gpos)

            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 2: self.arrastrando_cam = False
                elif e.button == 1:
                    self.arrastrando_borrador = False
                    if self.drag_seleccion_start:
                        if gpos:
                            r1, c1 = self.drag_seleccion_start
                            r2, c2 = gpos
                            r_min, r_max = min(r1, r2), max(r1, r2)
                            c_min, c_max = min(c1, c2), max(c1, c2)
                            for r in range(r_min, r_max + 1):
                                for c in range(c_min, c_max + 1):
                                    if self.grid[r][c] != ' ' and (r, c) not in self.seleccion:
                                        self.seleccion.append((r, c))
                        self.drag_seleccion_start = None

            elif e.type == pygame.MOUSEMOTION:
                if self.arrastrando_cam:
                    self.cam_x -= e.pos[0] - self.drag_start[0]
                    self.cam_y -= e.pos[1] - self.drag_start[1]
                    self.drag_start = e.pos
                    
                    self.cam_x = max(0, min(self.cam_x, self.columnas * self.TILE_DISP - ANCHO))
                    max_y = max(0, self.filas * self.TILE_DISP - (self.palette_y - self.offset_y))
                    self.cam_y = max(0, min(self.cam_y, max_y))

                elif self.arrastrando_borrador and pygame.mouse.get_pressed()[0] and gpos:
                    r, c = gpos
                    self.grid[r][c] = ' '
                    if (r, c) in self.habilidades_codigo:
                        del self.habilidades_codigo[(r, c)]

                elif pygame.mouse.get_pressed()[0] and self.tab_actual == "BUILD" and gpos:
                    r, c = gpos
                    self.grid[r][c] = self.char_actual
                    
            elif e.type == pygame.MOUSEWHEEL:
                if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    self.cam_y -= e.y * self.TILE_DISP
                    max_y = max(0, self.filas * self.TILE_DISP - (self.palette_y - self.offset_y))
                    self.cam_y = max(0, min(self.cam_y, max_y))
                else:
                    self.cam_x -= e.y * self.TILE_DISP
                    self.cam_x = max(0, min(self.cam_x, self.columnas * self.TILE_DISP - ANCHO))

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: self._pausar()

    # ---------- Renderizado ----------
    def _sprite_celda(self, ch):
        if ch in self._cache_sprites: return self._cache_sprites[ch]
        surf = None
        try:
            if ch == 'P': surf = self.recursos.anim_robot(0)["idle"].frame_actual()
            elif ch == 'B': surf = self.recursos.anim_item("bateria").frame_actual()
            elif ch == 'E': surf = self.recursos.anim_item("engranaje").frame_actual()
            elif ch == 'C': surf = self.recursos.anim_item("codigo").frame_actual()
            elif ch == '?': surf = self.recursos.anim_item("codigo_secreto").frame_actual()
            elif ch == 'N': surf = self.recursos.anim_enemigo("enemigo001")["idle"].frame_actual()
            elif ch == 'K': surf = self.recursos.anim_enemigo("enemigo002")["idle"].frame_actual()
            elif ch == 'H': surf = self.recursos.anim_enemigo("enemigo003")["idle"].frame_actual()
            elif ch == '*': surf = self.recursos.anim_puerta().frame_actual()
            else:
                # Todo lo demás (bloques, rampas y pinchos) usa la imagen
                surf = self.recursos.obtener_bloque(ch)
                if not surf:
                    # Fallback por si no hay imagen
                    surf = pygame.Surface((36, 36), pygame.SRCALPHA)
                    pygame.draw.rect(surf, (80, 80, 100), (0, 0, 36, 36))
        except Exception: 
            pass
        
        if surf is not None:
            surf = pygame.transform.scale(surf, (self.TILE_DISP, self.TILE_DISP))
        self._cache_sprites[ch] = surf
        return surf
    
    def dibujar(self, pantalla):
        pantalla.fill((30, 40, 60))
        
        margen_y = max(0, (self.palette_y - self.offset_y - (self.filas * self.TILE_DISP)) // 2)

        for r in range(self.filas):
            for c in range(self.columnas):
                x = c * self.TILE_DISP - self.cam_x
                y = r * self.TILE_DISP + self.offset_y + margen_y - self.cam_y
                
                if -self.TILE_DISP < x < ANCHO and self.offset_y < y < self.palette_y:
                    rect = pygame.Rect(x, y, self.TILE_DISP, self.TILE_DISP)
                    pygame.draw.rect(pantalla, (25, 30, 50) if (r + c) % 2 == 0 else (30, 35, 55), rect)
                    pygame.draw.rect(pantalla, (50, 60, 90), rect, 1)
                    
                    ch = self.grid[r][c]
                    if ch != ' ':
                        surf = self._sprite_celda(ch)
                        if surf: pantalla.blit(surf, rect.topleft)

                    if (r, c) in self.seleccion:
                        pygame.draw.rect(pantalla, (255, 200, 0), rect, 2)

        mx, my = pygame.mouse.get_pos()
        gpos = self._get_grid_pos((mx, my))
        if gpos and not self.pausado and not self.mostrar_config:
            r, c = gpos
            x = c * self.TILE_DISP - self.cam_x
            y = r * self.TILE_DISP + self.offset_y + margen_y - self.cam_y
            s = pygame.Surface((self.TILE_DISP, self.TILE_DISP), pygame.SRCALPHA)
            s.fill((255, 255, 255, 80))
            pantalla.blit(s, (x, y))

        if self.drag_seleccion_start and gpos:
            r1, c1 = self.drag_seleccion_start
            r2, c2 = gpos
            x1 = c1 * self.TILE_DISP - self.cam_x
            y1 = r1 * self.TILE_DISP + self.offset_y + margen_y - self.cam_y
            x2 = c2 * self.TILE_DISP - self.cam_x
            y2 = r2 * self.TILE_DISP + self.offset_y + margen_y - self.cam_y
            rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2-x1)+self.TILE_DISP, abs(y2-y1)+self.TILE_DISP)
            pygame.draw.rect(pantalla, (255, 255, 0), rect, 2)

        pygame.draw.rect(pantalla, (20, 25, 40), (0, 0, ANCHO, self.offset_y))
        pygame.draw.rect(pantalla, (20, 25, 40), (0, self.palette_y, ANCHO, 160))
        pygame.draw.line(pantalla, (0, 255, 255), (0, self.offset_y), (ANCHO, self.offset_y), 2)
        pygame.draw.line(pantalla, (0, 255, 255), (0, self.palette_y), (ANCHO, self.palette_y), 2)

        for name, y_off, col in self.tabs:
            activo = (self.tab_actual == name)
            rect = pygame.Rect(10, self.palette_y + y_off, 110, 35)
            pygame.draw.rect(pantalla, col if activo else (50, 50, 50), rect, border_radius=8)
            pygame.draw.rect(pantalla, (255, 255, 255), rect, 2, border_radius=8)
            txt = self.recursos.texto(name, 18)
            pantalla.blit(txt, txt.get_rect(center=rect.center))

        if self.tab_actual == "BUILD":
            self.btn_build_items = []
            start_idx = self.pagina_build * 10
            items_pag = self.lista_build[start_idx:start_idx+10]
            
            grid_w = 5 * 70 - 10
            start_x = (ANCHO - grid_w) // 2
            
            for i, (char, name) in enumerate(items_pag):
                col = i % 5
                row = i // 5
                x = start_x + col * 70
                y = self.palette_y + 10 + row * 70
                
                rect = pygame.Rect(x, y, 60, 60)
                activo = (self.char_actual == char)
                col_bg = (80, 200, 100) if activo else (80, 100, 150)
                
                pygame.draw.rect(pantalla, col_bg, rect, border_radius=5)
                pygame.draw.rect(pantalla, (255,255,255), rect, 2, border_radius=5)
                
                surf = self._sprite_celda(char)
                if surf:
                    scaled = pygame.transform.scale(surf, (40, 40))
                    pantalla.blit(scaled, scaled.get_rect(center=rect.center))
                
                b = Boton(rect, name, (lambda c=char: self._set_char(c)))
                self.btn_build_items.append(b)
                
            self.btn_build_prev.rect.topleft = (start_x - 50, self.palette_y + 50)
            self.btn_build_next.rect.topleft = (start_x + grid_w + 10, self.palette_y + 50)
            self.btn_build_prev.dibujar(pantalla, self.recursos)
            self.btn_build_next.dibujar(pantalla, self.recursos)

        elif self.tab_actual == "EDIT":
            self.btn_swipe.color_base = (80, 200, 100) if self.swipe_activo else (180, 150, 60)
            self.btn_swipe.texto = "SWIPE ON" if self.swipe_activo else "SWIPE"
            self.btn_swipe.dibujar(pantalla, self.recursos)
            
            self.btn_zoom_in.dibujar(pantalla, self.recursos)
            self.btn_zoom_out.dibujar(pantalla, self.recursos)
            
            self.btn_move_izq.dibujar(pantalla, self.recursos)
            self.btn_move_der.dibujar(pantalla, self.recursos)
            self.btn_move_up.dibujar(pantalla, self.recursos)
            self.btn_move_dn.dibujar(pantalla, self.recursos)
            
            for b, d in [(self.btn_dist_1, 1), (self.btn_dist_3, 3), (self.btn_dist_5, 5)]:
                activo = (self.dist_mov == d)
                pygame.draw.rect(pantalla, (80, 200, 100) if activo else (50, 50, 50), b.rect, border_radius=5)
                pygame.draw.rect(pantalla, (255,255,255), b.rect, 2, border_radius=5)
                txt = self.recursos.texto(str(d), 16)
                pantalla.blit(txt, txt.get_rect(center=b.rect.center))

        elif self.tab_actual == "DELETE":
            self.btn_swipe.color_base = (80, 200, 100) if self.swipe_activo else (180, 150, 60)
            self.btn_swipe.texto = "SWIPE ON" if self.swipe_activo else "SWIPE"
            self.btn_swipe.dibujar(pantalla, self.recursos)
            
            self.btn_borrador.color_base = (80, 200, 100) if self.borrador_activo else (200, 100, 50)
            self.btn_borrador.texto = "BORRADOR ON" if self.borrador_activo else "Borrador"
            self.btn_borrador.dibujar(pantalla, self.recursos)
            
            self.btn_zoom_in.dibujar(pantalla, self.recursos)
            self.btn_zoom_out.dibujar(pantalla, self.recursos)
            
            if not self.borrador_activo:
                self.btn_delete_sel.dibujar(pantalla, self.recursos)

        for b in self.botones_top:
            b.dibujar(pantalla, self.recursos)

        # Modales
        if self.mostrar_config:
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            pantalla.blit(overlay, (0, 0))

            panel_w, panel_h = 640, 440
            panel_x = (ANCHO - panel_w) // 2
            panel_y = (ALTO - panel_h) // 2
            panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

            pygame.draw.rect(pantalla, (100, 70, 50), panel, border_radius=15)
            pygame.draw.rect(pantalla, (200, 180, 100), panel, 5, border_radius=15)

            titulo = self.recursos.texto("CONFIGURACIÓN DEL NIVEL", 28, (255, 255, 200))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, panel_y + 40)))

            filas_cfg = [
                ("Fondo:",   self.cfg_fondo.split('/')[-1], self.btn_prev_fondo, self.btn_next_fondo),
                ("Suelo:",   self.cfg_suelo.split('/')[-1], self.btn_prev_suelo, self.btn_next_suelo),
                ("Música:",  self.cfg_musica,               self.btn_prev_musica, self.btn_next_musica),
            ]
            for i, (lbl, val, btn_p, btn_n) in enumerate(filas_cfg):
                y = panel_y + 90 + i * 80
                txt_lbl = self.recursos.texto(lbl, 22, (255, 255, 255))
                pantalla.blit(txt_lbl, (panel_x + 30, y + 8))
                
                btn_p.rect.topleft = (panel_x + 170, y); btn_p.dibujar(pantalla, self.recursos)
                
                # Caja de texto (ahora más ancha y con texto más pequeño para que no se desborde)
                box = pygame.Rect(panel_x + 220, y, 220, 40)
                pygame.draw.rect(pantalla, (50, 50, 70), box, border_radius=5)
                
                # Recortamos el texto si es muy largo
                texto_mostrar = val
                while self.recursos.texto(texto_mostrar, 16).get_width() > box.width - 10 and len(texto_mostrar) > 3:
                    texto_mostrar = texto_mostrar[:-4] + "..."
                    
                txt_val = self.recursos.texto(texto_mostrar, 16, (210, 210, 220))
                pantalla.blit(txt_val, txt_val.get_rect(center=box.center))
                
                btn_n.rect.topleft = (panel_x + 450, y); btn_n.dibujar(pantalla, self.recursos)

            self.btn_ok_config.rect.topleft = (ANCHO // 2 - 100, panel_y + panel_h - 70)
            self.btn_ok_config.dibujar(pantalla, self.recursos)

        if self.configurando_habilidad:
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            pantalla.blit(overlay, (0, 0))
            panel = pygame.Rect(ANCHO//2 - 150, 130, 300, 350)
            pygame.draw.rect(pantalla, (40, 50, 75), panel, border_radius=12)
            pygame.draw.rect(pantalla, (100, 150, 220), panel, 3, border_radius=12)
            titulo = self.recursos.texto("Habilidad", 24)
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO//2, 160)))
            
            self.btn_hab_doble.dibujar(pantalla, self.recursos)
            self.btn_hab_super.dibujar(pantalla, self.recursos)
            self.btn_hab_volar.dibujar(pantalla, self.recursos)
            self.btn_hab_vel.dibujar(pantalla, self.recursos)
            self.btn_hab_res.dibujar(pantalla, self.recursos)

        if self.pausado:
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            pantalla.blit(overlay, (0, 0))
            panel = pygame.Rect(ANCHO // 2 - 200, 150, 400, 370)
            pygame.draw.rect(pantalla, (50, 60, 90), panel, border_radius=15)
            pygame.draw.rect(pantalla, (0, 255, 255), panel, 4, border_radius=15)
            titulo = self.recursos.texto("PAUSA", 34, (255, 255, 255))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 180)))
            for b in self.botones_pausa:
                b.dibujar(pantalla, self.recursos)