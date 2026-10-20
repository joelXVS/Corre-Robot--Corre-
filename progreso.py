"""Persistencia JSON + reglas de desbloqueo por estadísticas."""
import json
import os
import pygame


class Progreso:
    RUTA = "progreso.json"

    DEFAULTS = {
        "vol_musica": 0.5,
        "vol_sfx": 0.5,
        "fps": 60,
        "calidad": "media",
        "pantalla_completa": False,
        "personaje_seleccionado": 0,
        "nivel_max_desbloqueado": 0,
        "teclas": {
            "izquierda": pygame.K_LEFT,
            "derecha":   pygame.K_RIGHT,
            "salto":     pygame.K_SPACE,
            "pausa":     pygame.K_ESCAPE,
            "reiniciar": pygame.K_r,
        },
        "estadisticas": {
            "total_completados": 0,
            "niveles_completados": [],
            "baterias_recogidas": 0,
            "engranajes_recogidos": 0,
            "codigos_recogidos": 0,
            "codigo_secreto_encontrado": False,
            "puntuacion_maxima": 0,
            "fragmentos_secretos": [],
        },
    }

    CONDICIONES = {
        "Atlas":    lambda s: True,
        "MIO":      lambda s: s["total_completados"] >= 5,
        "Nyx":      lambda s: s["total_completados"] >= 15,
        "Vega":     lambda s: (s["baterias_recogidas"] + s["engranajes_recogidos"]) >= 1000,
        "Xperia51": lambda s: s["codigo_secreto_encontrado"],
    }

    def __init__(self):
        self.datos = self._cargar()
        if "vol_musica" not in self.datos:
            v = self.datos.pop("volumen", 0.5)
            self.datos["vol_musica"] = v
            self.datos["vol_sfx"] = v
            self.guardar()
        # asegurar teclas
        if "teclas" not in self.datos:
            self.datos["teclas"] = dict(self.DEFAULTS["teclas"])
            self.guardar()

    # ---------- Carga / guardado ----------
    def _cargar(self):
        if os.path.exists(self.RUTA):
            try:
                with open(self.RUTA, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                for k, v in self.DEFAULTS.items():
                    datos.setdefault(k, v)
                for k, v in self.DEFAULTS["estadisticas"].items():
                    datos["estadisticas"].setdefault(k, v)
                return datos
            except (json.JSONDecodeError, OSError):
                pass
        return json.loads(json.dumps(self.DEFAULTS))

    def guardar(self):
        try:
            with open(self.RUTA, "w", encoding="utf-8") as f:
                json.dump(self.datos, f, indent=2, ensure_ascii=False)
        except OSError as e:
            print(f"[Progreso] No se pudo guardar: {e}")

    # ---------- Accesos ----------
    @property
    def vol_musica(self): return self.datos["vol_musica"]
    @vol_musica.setter
    def vol_musica(self, v):
        self.datos["vol_musica"] = float(v); self.guardar()

    @property
    def vol_sfx(self): return self.datos["vol_sfx"]
    @vol_sfx.setter
    def vol_sfx(self, v):
        self.datos["vol_sfx"] = float(v); self.guardar()

    @property
    def fps(self): return self.datos["fps"]
    @fps.setter
    def fps(self, v):
        self.datos["fps"] = int(v); self.guardar()

    @property
    def calidad(self): return self.datos["calidad"]
    @calidad.setter
    def calidad(self, v):
        self.datos["calidad"] = str(v); self.guardar()

    @property
    def pantalla_completa(self): return self.datos["pantalla_completa"]
    @pantalla_completa.setter
    def pantalla_completa(self, v):
        self.datos["pantalla_completa"] = bool(v); self.guardar()

    def resetear(self):
        self.datos = json.loads(json.dumps(self.DEFAULTS))
        self.guardar()

    @property
    def personaje_seleccionado(self): return self.datos["personaje_seleccionado"]
    @personaje_seleccionado.setter
    def personaje_seleccionado(self, v):
        self.datos["personaje_seleccionado"] = int(v); self.guardar()

    @property
    def nivel_max_desbloqueado(self): return self.datos["nivel_max_desbloqueado"]
    def desbloquear_hasta(self, indice):
        if indice > self.datos["nivel_max_desbloqueado"]:
            self.datos["nivel_max_desbloqueado"] = int(indice); self.guardar()

    @property
    def stats(self): return self.datos["estadisticas"]

    # ---------- Teclas ----------
    @property
    def teclas(self): return self.datos["teclas"]

    def tecla(self, accion):
        return self.teclas.get(accion, self.DEFAULTS["teclas"].get(accion, pygame.K_SPACE))

    def set_tecla(self, accion, key):
        self.teclas[accion] = int(key); self.guardar()

    # ---------- Registro de eventos ----------
    def registrar_nivel_completado(self, indice_nivel, puntaje):
        s = self.stats
        s["total_completados"] += 1
        if indice_nivel not in s["niveles_completados"]:
            s["niveles_completados"].append(indice_nivel)
        s["puntuacion_maxima"] = max(s["puntuacion_maxima"], puntaje)
        self.guardar()

    def registrar_bateria(self):
        self.stats["baterias_recogidas"] += 1; self.guardar()

    def registrar_engranaje(self):
        self.stats["engranajes_recogidos"] += 1; self.guardar()

    def registrar_codigo(self):
        self.stats["codigos_recogidos"] += 1; self.guardar()

    def registrar_fragmento(self, fragmento, total_secretos):
        if not fragmento: return
        if fragmento not in self.stats["fragmentos_secretos"]:
            self.stats["fragmentos_secretos"].append(fragmento)
        if len(self.stats["fragmentos_secretos"]) >= total_secretos:
            self.stats["codigo_secreto_encontrado"] = True
        self.guardar()

    @property
    def codigo_formateado(self):
        frags = self.stats["fragmentos_secretos"]
        return "".join(sorted(frags)) if frags else ""

    def esta_desbloqueado(self, meta_personaje):
        cond = self.CONDICIONES.get(meta_personaje["nombre"])
        return cond(self.stats) if cond else True