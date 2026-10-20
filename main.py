"""Motor de la aplicación: escenas, progreso, sonidos, loop."""
import json
import os
import pygame

from ajustes import *
from recursos import Recursos
from progreso import Progreso
from sound import Sonidos


class Main:
    RUTA_NIVELES = "levels"
    RUTA_NIVELES_JSON = "levels/niveles.json"

    def __init__(self):
        pygame.init()
        try: pygame.mixer.init()
        except pygame.error: pass

        self.progreso = Progreso()
        self.recursos = Recursos()
        self.sonidos = Sonidos(volumen=self.progreso.vol_sfx)

        self.ajustes = {
            "fps": self.progreso.fps,
            "ancho": ANCHO, "alto": ALTO,
            "titulo": TITULO,
            "volumen_musica": self.progreso.vol_musica,
            "volumen_sfx": self.progreso.vol_sfx,
        }

        flags = pygame.SCALED
        if self.progreso.pantalla_completa:
            flags |= pygame.FULLSCREEN

        self.pantalla = pygame.display.set_mode((ANCHO, ALTO), flags)
        pygame.display.set_caption(TITULO)
        self.reloj = pygame.time.Clock()
        self.corriendo = True

        self.niveles_cfg = self._cargar_niveles_cfg()
        self.niveles = [cfg["archivo"] for cfg in self.niveles_cfg]
        self.ruta_niveles = self.RUTA_NIVELES
        self.total_secretos = sum(1 for cfg in self.niveles_cfg if cfg.get("codigo_secreto"))

        self.nivel_prueba = None
        self._musica_actual = None
        self.return_scene = "lobby"

        self.puntaje_actual = 0
        self.puntuaciones = []
        self.indice_nivel = 0

        from scenes.lobby import EscenaLobby
        from scenes.level_selector import EscenaNiveles
        from scenes.settings import EscenaAjustes
        from scenes.credits import EscenaCreditos
        from scenes.character_selector import EscenaPersonajes
        from scenes.juego import EscenaJuego
        from scenes.victory import EscenaVictoria
        from scenes.defeat import EscenaDerrota
        from scenes.loading import EscenaCargando
        from scenes.my_levels import EscenaMisNiveles
        from scenes.editor import EscenaEditor
        from scenes.how_to_play import EscenaComoJugar

        self.escenas = {
            "lobby":       EscenaLobby(self),
            "niveles":     EscenaNiveles(self),
            "ajustes":     EscenaAjustes(self),
            "creditos":    EscenaCreditos(self),
            "personajes":  EscenaPersonajes(self),
            "juego":       EscenaJuego(self),
            "victoria":    EscenaVictoria(self),
            "derrota":     EscenaDerrota(self),
            "cargando":    EscenaCargando(self),
            "mis_niveles": EscenaMisNiveles(self),
            "editor":      EscenaEditor(self),
            "como_jugar":  EscenaComoJugar(self),
        }
        self.escena_actual = "lobby"
        self.escenas[self.escena_actual].entrar()

    def _cargar_niveles_cfg(self):
        if os.path.exists(self.RUTA_NIVELES_JSON):
            try:
                with open(self.RUTA_NIVELES_JSON, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                niveles = datos.get("niveles", [])
                if niveles: return niveles
            except (json.JSONDecodeError, OSError): pass
        archivos = sorted(f for f in os.listdir(self.RUTA_NIVELES) if f.endswith(".txt"))
        return [{"archivo": a, "nombre": f"Nivel {i+1}"} for i, a in enumerate(archivos)]

    # ---------- Música ----------
    def musica(self, ruta_relativa, loop=True):
        """No reinicia si la misma pista ya está reproduciéndose."""
        if self._musica_actual == ruta_relativa:
            try:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1 if loop else 0)
            except pygame.error:
                pass
            return
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(ruta_relativa)
            pygame.mixer.music.set_volume(self.progreso.vol_musica)
            pygame.mixer.music.play(-1 if loop else 0)
            self._musica_actual = ruta_relativa
        except (pygame.error, FileNotFoundError):
            self._musica_actual = None

    def detener_musica(self):
        try: pygame.mixer.music.stop()
        except pygame.error: pass
        self._musica_actual = None

    # ---------- Puentes ----------
    @property
    def personaje_seleccionado(self): return self.progreso.personaje_seleccionado
    @personaje_seleccionado.setter
    def personaje_seleccionado(self, v): self.progreso.personaje_seleccionado = v

    @property
    def nivel_max_desbloqueado(self): return self.progreso.nivel_max_desbloqueado
    @nivel_max_desbloqueado.setter
    def nivel_max_desbloqueado(self, v): self.progreso.desbloquear_hasta(v)

    # ---------- Escenas ----------
    ESCENAS_LIMPIAN_PRUEBA = ("lobby", "niveles", "editor", "mis_niveles")

    def cambiar_escena(self, nombre):
        self.escenas[self.escena_actual].salir()
        if nombre in self.ESCENAS_LIMPIAN_PRUEBA:
            self.nivel_prueba = None
            if "juego" in self.escenas:
                self.escenas["juego"].limpiar_prueba()
        self.escena_actual = nombre
        self.escenas[nombre].entrar()

    def ejecutar(self):
        while self.corriendo:
            fps = self.ajustes.get("fps", 60)
            dt = self.reloj.tick(fps) / 1000.0
            eventos = pygame.event.get()
            for e in eventos:
                if e.type == pygame.QUIT:
                    self.corriendo = False; break

            escena = self.escenas[self.escena_actual]
            escena.manejar_eventos(eventos)
            escena.actualizar(dt)
            escena.dibujar(self.pantalla)
            pygame.display.flip()

        self.progreso.guardar()
        self.detener_musica()
        pygame.quit()


if __name__ == "__main__":
    Main().ejecutar()