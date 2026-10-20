import os
import json
import random
import pygame
from scenes.scene import Escena
from ui.hud import HUD
from ui.button import Boton
from level import Nivel
from entities.robot import Robot
from entities.obstacle import Obstaculo
from entities.enemy import Enemigo
from entities.door import Puerta
from entities.items import Bateria, Engranaje, CodigoPy, CodigoSecreto
from ajustes import TAM_TILE, COLOR_FONDO, COLOR_SUELO, ANCHO, ALTO


class EscenaJuego(Escena):
    NOMBRE_UI = None

    def __init__(self, juego):
        super().__init__(juego)
        self.hud = HUD(self.recursos)
        self.nivel = None
        self.robot = None
        self.solidos = []
        self.items = []
        self.obstaculos = []
        self.enemigos = []
        self.puerta = None
        self.fondo = None
        self.tile_suelo = None
        self.cam_x = 0
        self.cooldown_bat_baja = 0.0
        self._cfg_prueba = None
        self._musica_pausada = False

        self.pausado = False
        self.botones_pausa = []

        self.transicion = 0.0
        self.accion_final = None
        self._ultima_pos_x = 0

    def limpiar_prueba(self):
        self._cfg_prueba = None

    def entrar(self):
        if self.juego.nivel_prueba:
            self._cfg_prueba = self.juego.nivel_prueba
            self.juego.nivel_prueba = None
            self._cargar_desde_cfg(self._cfg_prueba)
        elif self._cfg_prueba:
            self._cargar_desde_cfg(self._cfg_prueba)
        else:
            self.cargar_nivel(self.juego.indice_nivel)
        self._configurar_pausa()

    def salir(self):
        self.juego.detener_musica()
        if self._musica_pausada:
            try: pygame.mixer.music.unpause()
            except pygame.error: pass
            self._musica_pausada = False

    def _configurar_pausa(self):
        if self._cfg_prueba is not None:
            texto_volver = "Volver al editor" if self.juego.return_scene == "editor" else "Volver a Mis Niveles"
            self.botones_pausa = [
                Boton((ANCHO // 2 - 110, 200, 220, 50), "Reanudar", self._toggle_pausa),
                Boton((ANCHO // 2 - 110, 270, 220, 50), "Reiniciar", self._reiniciar_nivel),
                Boton((ANCHO // 2 - 110, 340, 220, 50), texto_volver,
                      lambda: self.juego.cambiar_escena(self.juego.return_scene)),
            ]
        else:
            texto_volver = "Volver a Niveles" if self.juego.return_scene == "niveles" else "Salir al Lobby"
            self.botones_pausa = [
                Boton((ANCHO // 2 - 110, 200, 220, 50), "Reanudar", self._toggle_pausa),
                Boton((ANCHO // 2 - 110, 270, 220, 50), "Reiniciar", self._reiniciar_nivel),
                Boton((ANCHO // 2 - 110, 340, 220, 50), texto_volver,
                    lambda: self.juego.cambiar_escena(self.juego.return_scene if self.juego.return_scene else "lobby")),
            ]

    def cargar_nivel(self, indice):
        self.juego.indice_nivel = indice
        self._cargar_desde_cfg(self.juego.niveles_cfg[indice])
        
    def _reiniciar_nivel(self):
        cfg = self._cfg_prueba if self._cfg_prueba else self.juego.niveles_cfg[self.juego.indice_nivel]
        self._cargar_desde_cfg(cfg)
        self.pausado = False
        self.juego.sonidos.reproducir("start")

    def _toggle_pausa(self):
        self.pausado = not self.pausado
        if self.pausado:
            try: pygame.mixer.music.pause()
            except pygame.error: pass
            self._musica_pausada = True
        else:
            if self._musica_pausada:
                try: pygame.mixer.music.unpause()
                except pygame.error: pass
                self._musica_pausada = False

    def _puntuar(self, cantidad):
        self.juego.puntaje_actual = max(0, self.juego.puntaje_actual + cantidad)

    def manejar_eventos(self, eventos):
        if self.transicion > 0: return

        if self.pausado:
            for e in eventos:
                for b in self.botones_pausa:
                    if b.manejar_evento(e):
                        self.juego.sonidos.reproducir("click")
            return

        pausa_key = self.juego.progreso.tecla("pausa")
        reiniciar_key = self.juego.progreso.tecla("reiniciar")
        salto_key = self.juego.progreso.tecla("salto")

        for e in eventos:
            if e.type == pygame.KEYDOWN:
                if e.key == pausa_key:
                    self._toggle_pausa(); return
                if e.key == reiniciar_key:
                    self._reiniciar_nivel(); return
                if e.key == salto_key or e.key in (pygame.K_UP, pygame.K_w):
                    if not self.robot.en_suelo and self.robot.saltos_disponibles > 0:
                        self.robot.saltar()
                        self.juego.sonidos.reproducir("salto")
                        self._puntuar(2)

    def actualizar(self, dt):
        if not self.nivel or self.pausado: return

        if self.transicion > 0:
            self.transicion -= dt
            self.robot.actualizar(dt, self.solidos)
            
            if self.transicion > 1.0 and (self.puerta and self.robot.colisiona_con(self.puerta)):
                self.robot.alpha = max(0, self.robot.alpha - int(300 * dt))
                
            if self.puerta:
                self.puerta.actualizar(dt)
                
            if self.transicion <= 0:
                self.juego.cambiar_escena(self.accion_final)
            return

        teclas = pygame.key.get_pressed()
        izq = self.juego.progreso.tecla("izquierda")
        der = self.juego.progreso.tecla("derecha")
        salto = self.juego.progreso.tecla("salto")

        if teclas[izq]:
            self.robot.mover_izquierda()
        elif teclas[der]:
            self.robot.mover_derecha()
        else:
            self.robot.detener()

        if teclas[salto]:
            if self.robot.en_suelo:
                self.robot.saltar()
                self.juego.sonidos.reproducir("salto")
                self._puntuar(2)

        vida_antes = self.robot.vida
        self.robot.actualizar(dt, self.solidos)
        
        # --- REFUERZO DE LÍMITES ---
        if self.robot.rect.left < 0:
            self.robot.rect.left = 0
            self.robot.vel_x = 0
        elif self.robot.rect.right > self.nivel.ancho_px:
            self.robot.rect.right = self.nivel.ancho_px
            self.robot.vel_x = 0

        distancia = abs(self.robot.rect.x - self._ultima_pos_x)
        if distancia >= TAM_TILE:
            self._puntuar(2)
            self._ultima_pos_x = self.robot.rect.x

        for item in self.items:
            if item.recogido: continue
            item.actualizar(dt)
            if self.robot.colisiona_con(item):
                item.recoger(self.robot)
                self._procesar_recogida(item)

        for obs in self.obstaculos:
            if self.robot.colisiona_con(obs): obs.aplicar_efecto(self.robot)
        
        for en in self.enemigos:
            en.actualizar(dt, self.solidos, self.robot)
            if self.robot.colisiona_con(en): en.aplicar_efecto(self.robot)
            
        if self.robot.vida < vida_antes:
            self.juego.sonidos.reproducir(f"danio00{random.randint(1, 5)}")
            self._puntuar(-50)

        self._actualizar_camara()

        if self.puerta:
            self.puerta.actualizar(dt)
            if self.robot.colisiona_con(self.puerta) and not self.puerta.animando:
                self.puerta.animar()
                self.juego.sonidos.reproducir("door")
                self.transicion = 2.5
                self.robot.vel_x = 0
                self.robot.vel_y = 0
                
                self.robot.rect.centerx = self.puerta.rect.centerx
                
                if self._cfg_prueba is not None:
                    self.accion_final = self.juego.return_scene
                else:
                    self.accion_final = "victoria"
                    self._siguiente_nivel()
                return

        if self.robot.vida <= 0 or self.robot.energia <= 0:
            self.robot.morir()
            if self.transicion == 0:
                self.juego.detener_musica()
                self._puntuar(-200)
                self.juego.sonidos.reproducir("derrota")
                self.transicion = 2.0
                self.accion_final = "derrota"        

    def _procesar_recogida(self, item):
        p = self.juego.progreso
        s = self.juego.sonidos
        if isinstance(item, Bateria):
            p.registrar_bateria(); s.reproducir("bateria_recargada"); self._puntuar(10)
        elif isinstance(item, Engranaje):
            p.registrar_engranaje(); s.reproducir("engranaje"); self._puntuar(5)
        elif isinstance(item, CodigoSecreto):
            p.registrar_fragmento(item.fragmento, self.juego.total_secretos); s.reproducir("codigo_secreto")
        elif isinstance(item, CodigoPy):
            p.registrar_codigo(); s.reproducir("codigo"); self._puntuar(25)

    def _actualizar_camara(self):
        objetivo = self.robot.rect.centerx - self.juego.ajustes["ancho"] // 2
        max_cam = max(0, self.nivel.ancho_px - self.juego.ajustes["ancho"])
        self.cam_x = max(0, min(objetivo, max_cam))

    def _siguiente_nivel(self):
        self._puntuar(100)
        if self._cfg_prueba is not None: return
        completado = self.juego.indice_nivel
        self.juego.progreso.registrar_nivel_completado(completado, self.juego.puntaje_actual)
        siguiente = completado + 1
        if siguiente >= len(self.juego.niveles):
            self.juego.nivel_max_desbloqueado = len(self.juego.niveles) - 1
            self.juego.escenas["victoria"].es_victoria_total = True
        else:
            self.juego.nivel_max_desbloqueado = siguiente
            self.juego.indice_nivel = siguiente
            self.juego.escenas["victoria"].es_victoria_total = False
        
        self.juego.sonidos.reproducir("victoria")

    def _blit_fondo_infinito(self, pantalla, img, offset_x):
        w = img.get_width()
        x = -(int(offset_x) % w)
        while x < pantalla.get_width():
            pantalla.blit(img, (x, 0)); x += w

    def _cargar_desde_cfg(self, cfg):
        ruta = cfg["archivo"]
        if not os.path.isabs(ruta):
            ruta = os.path.join(self.juego.ruta_niveles, ruta)

        self.nivel = Nivel(ruta, config=cfg)
        self.solidos = self.nivel.rects_solidos() # Ya viene como lista de (Rect, char)
        self.items, self.obstaculos, self.enemigos = [], [], []
        self.transicion = 0.0
        self.pausado = False
        self._musica_pausada = False
        self._ultima_pos_x = 0

        pos_r = self.nivel.posiciones_de("P")
        x, y = pos_r[0] if pos_r else (0, 0)
        meta = self.juego.recursos.meta_personaje(self.juego.personaje_seleccionado)
        anims = self.juego.recursos.anim_robot(self.juego.personaje_seleccionado)
        self.robot = Robot(x, y, anims, vida_max=meta["vida_maxima"], energia_max=meta["energia_maxima"])
        self._ultima_pos_x = self.robot.rect.x
        
        self.robot.limite_izq = 0
        self.robot.limite_der = self.nivel.ancho_px

        self.puerta = None
        for x, y in self.nivel.posiciones_de("*"):
            anim = self.juego.recursos.anim_puerta()
            self.puerta = Puerta(x, y, TAM_TILE, TAM_TILE, animacion=anim)
            break

        habilidades_codigo = {}
        ruta_json = ruta.replace(".txt", ".json")
        if os.path.exists(ruta_json):
            try:
                with open(ruta_json, 'r') as f:
                    datos = json.load(f)
                    habilidades_codigo = datos.get("codigos", {})
            except Exception:
                pass

        for x, y in self.nivel.posiciones_de("B"): 
            self.items.append(Bateria(x, y, self.juego.recursos.anim_item("bateria")))
        for x, y in self.nivel.posiciones_de("E"): 
            self.items.append(Engranaje(x, y, self.juego.recursos.anim_item("engranaje")))
        
        for x, y in self.nivel.posiciones_de("C"): 
            col = x // TAM_TILE
            fila = y // TAM_TILE
            r_ed = fila - 1 
            habilidad = habilidades_codigo.get(f"{r_ed},{col}", "habilidad")
            self.items.append(CodigoPy(x, y, self.juego.recursos.anim_item("codigo"), habilidad=habilidad))
            
        for x, y in self.nivel.posiciones_de("?"): 
            self.items.append(CodigoSecreto(x, y, self.juego.recursos.anim_item("codigo_secreto")))
        
        for simbolo in ('{', '}', 'm', ',', '[', ']', '.', '-', '^', '>', '~', '<'):
            for x, y in self.nivel.posiciones_de(simbolo): 
                img = self.juego.recursos.obtener_bloque(simbolo)
                self.obstaculos.append(Obstaculo(x, y, TAM_TILE, TAM_TILE, tipo=simbolo, imagen=img))
        
        # Cargar enemigos (coches)
        for x, y in self.nivel.posiciones_de("N"): 
            anims = self.juego.recursos.anim_enemigo("enemigo001")
            self.enemigos.append(Enemigo(x, y, TAM_TILE, TAM_TILE, velocidad=3, animaciones=anims))
            
        for x, y in self.nivel.posiciones_de("K"): 
            anims = self.juego.recursos.anim_enemigo("enemigo002")
            self.enemigos.append(Enemigo(x, y, TAM_TILE, TAM_TILE, velocidad=2, animaciones=anims))
            
        for x, y in self.nivel.posiciones_de("H"):
            anims = self.juego.recursos.anim_enemigo("enemigo003")
            self.enemigos.append(Enemigo(x, y, TAM_TILE, TAM_TILE, velocidad=4, animaciones=anims))

        self.fondo = self.juego.recursos.fondo_nivel(cfg.get("fondo"))
        self.tile_suelo = self.juego.recursos.tile_suelo(cfg.get("suelo"))

        self.juego.detener_musica()
        if cfg.get("musica"):
            ruta_musica = f"assets/sonidos/{cfg['musica']}"
            if os.path.exists(ruta_musica):
                self.juego.musica(ruta_musica, loop=True)

        self.cam_x = 0

    def dibujar(self, pantalla):
        pantalla.fill(COLOR_FONDO)
        if not self.nivel: return
        if self.fondo: self._blit_fondo_infinito(pantalla, self.fondo, self.cam_x * 0.5)
        offset = (self.cam_x, 0)
        ancho_visible = pantalla.get_width()

        # Dibujar sólidos
        for s, char in self.solidos:
            dx = s.x - self.cam_x
            if -TAM_TILE < dx < ancho_visible + TAM_TILE:
                img_bloque = self.juego.recursos.obtener_bloque(char)
                if img_bloque:
                    pantalla.blit(img_bloque, (dx, s.y))
                else:
                    pygame.draw.rect(pantalla, COLOR_SUELO, (dx, s.y, s.width, s.height))

        if self.puerta: self.puerta.dibujar(pantalla, offset)
        for it in self.items: it.dibujar(pantalla, offset)
        for ob in self.obstaculos: ob.dibujar(pantalla, offset)
        for en in self.enemigos: en.dibujar(pantalla, offset)
        self.robot.dibujar(pantalla, offset)
        self.hud.dibujar(pantalla, self.robot, self.juego.puntaje_actual,
                         self.juego.indice_nivel + 1, len(self.juego.niveles), es_prueba=(self._cfg_prueba is not None))

        if self.pausado:
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            pantalla.blit(overlay, (0, 0))
            for b in self.botones_pausa:
                b.dibujar(pantalla, self.recursos)