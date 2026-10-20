import os
import pygame

# Cache global: (nombre, tamaño) -> lista de Surfaces o None
_SPRITE_CACHE = {}


def _cargar_frames_sprite(nombre, tamano):
    """Carga assets/spritesheets/ui_btn_{nombre}.png como tira horizontal de
    frames cuadrados (alto = ancho_frame). Los escala a `tamano` (w, h).
    Devuelve None si no existe o falla."""
    clave = (nombre, tamano)
    if clave in _SPRITE_CACHE:
        return _SPRITE_CACHE[clave]

    ruta = f"assets/spritesheets/ui_btn_{nombre}.png"
    if not os.path.exists(ruta):
        _SPRITE_CACHE[clave] = None
        return None

    try:
        img = pygame.image.load(ruta).convert_alpha()
    except pygame.error:
        _SPRITE_CACHE[clave] = None
        return None

    fw = img.get_height()
    if fw <= 0:
        _SPRITE_CACHE[clave] = None
        return None

    n = max(1, img.get_width() // fw)
    frames = []
    for i in range(n):
        sub = img.subsurface((i * fw, 0, fw, fw)).copy()
        frames.append(pygame.transform.smoothscale(sub, tamano))

    _SPRITE_CACHE[clave] = frames
    return frames


class BotonIcono:
    """Botón con icono vectorial o spritesheet animado.

    - Si `sprite_nombre` está definido y existe assets/spritesheets/ui_btn_<nombre>.png,
      se usa el spritesheet (animado). En caso contrario, se usa `icono_fn`.
    - `sprite_frames` permite pasar frames pre-cargados manualmente.
    """

    def __init__(self, rect, icono_fn, al_click=None,
                 color=(70, 130, 200), habilitado=True, es_cerrar=False,
                 sprite_nombre=None, sprite_frames=None,
                 sprite_fps=8, sprite_escala=0.7):
        self.rect = pygame.Rect(rect)
        self.icono_fn = icono_fn
        self.al_click = al_click
        self.color = color
        self.habilitado = habilitado
        self.es_cerrar = es_cerrar
        self._hover_t = 0.0

        self._sprite_fps = sprite_fps
        self._sprite_escala = sprite_escala
        self._sprite_idx = 0
        self._sprite_t = 0.0
        self._sprite_frames = sprite_frames

        if self._sprite_frames is None and sprite_nombre:
            tam = (max(1, int(self.rect.width * sprite_escala)),
                   max(1, int(self.rect.height * sprite_escala)))
            self._sprite_frames = _cargar_frames_sprite(sprite_nombre, tam)

    # ---------- Eventos ----------
    def manejar_evento(self, e):
        if not self.habilitado:
            return False
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.rect.collidepoint(e.pos):
                if self.al_click:
                    self.al_click()
                return True
        return False

    # ---------- Update ----------
    def actualizar(self, dt):
        objetivo = 1.0 if (self.habilitado and
                           self.rect.collidepoint(pygame.mouse.get_pos())) else 0.0
        self._hover_t += (objetivo - self._hover_t) * min(1.0, dt * 12)

        if self._sprite_frames and len(self._sprite_frames) > 1:
            self._sprite_t += dt
            if self._sprite_t >= 1.0 / self._sprite_fps:
                self._sprite_t = 0.0
                self._sprite_idx = (self._sprite_idx + 1) % len(self._sprite_frames)

    # ---------- Dibujo ----------
    def dibujar(self, pantalla, recursos=None):
        escala = 1.0 + 0.08 * self._hover_t
        w = int(self.rect.width * escala)
        h = int(self.rect.height * escala)
        r = pygame.Rect(0, 0, w, h)
        r.center = self.rect.center

        if not self.habilitado:
            base = (70, 70, 85)
        elif self.es_cerrar:
            base = (220, 60, 60)
        else:
            base = self.color
        boost = int(55 * self._hover_t)
        color = (min(255, base[0] + boost),
                 min(255, base[1] + boost),
                 min(255, base[2] + boost))

        # Sombra
        sombra = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(sombra, (0, 0, 0, 110), sombra.get_rect(), border_radius=16)
        pantalla.blit(sombra, (r.x, r.y + 5))

        # Cuerpo
        pygame.draw.rect(pantalla, color, r, border_radius=16)
        pygame.draw.rect(pantalla, (245, 245, 245), r, 3, border_radius=16)

        # Icono (sprite o vector)
        if self._sprite_frames:
            frame = self._sprite_frames[self._sprite_idx]
            pantalla.blit(frame, frame.get_rect(center=r.center))
        else:
            self.icono_fn(pantalla, r)


# ============================================================
#  ÍCONOS VECTORIALES (fallback si no hay spritesheet)
# ============================================================

def icono_play(pantalla, r):
    cx, cy = r.center
    s = min(r.width, r.height) // 3
    pygame.draw.polygon(pantalla, (255, 255, 255),
                        [(cx - s // 2, cy - s),
                         (cx - s // 2, cy + s),
                         (cx + s, cy)])


def icono_editor(pantalla, r):
    cx, cy = r.center
    s = min(r.width, r.height) // 3
    for i in range(3):
        pygame.draw.rect(pantalla, (255, 255, 255),
                         (cx - s, cy - s + i * (s // 2 + 2), s * 2, s // 3),
                         border_radius=2)


def icono_x(pantalla, r):
    cx, cy = r.center
    s = min(r.width, r.height) // 4
    pygame.draw.line(pantalla, (255, 255, 255),
                     (cx - s, cy - s), (cx + s, cy + s), 4)
    pygame.draw.line(pantalla, (255, 255, 255),
                     (cx + s, cy - s), (cx - s, cy + s), 4)


def icono_niveles(pantalla, r):
    cx, cy = r.center
    s = min(r.width, r.height) // 4
    for i in range(3):
        pygame.draw.rect(pantalla, (255, 255, 255),
                         (cx - s, cy - s + i * (s // 2 + 2), s * 2, s // 3),
                         border_radius=2)


def icono_personajes(pantalla, r):
    cx, cy = r.center
    s = min(r.width, r.height) // 3
    # Cabeza
    pygame.draw.circle(pantalla, (255, 255, 255), (cx, cy - s // 3), s // 2, 3)
    # Cuerpo (trapecio)
    puntos = [
        (cx - s, cy + s),
        (cx - s // 2, cy + s // 4),
        (cx + s // 2, cy + s // 4),
        (cx + s, cy + s)
    ]
    pygame.draw.polygon(pantalla, (255, 255, 255), puntos, 3)


def icono_ajustes(pantalla, r):
    cx, cy = r.center
    s = min(r.width, r.height) // 3
    pygame.draw.circle(pantalla, (255, 255, 255), (cx, cy), s, 3)
    pygame.draw.circle(pantalla, (255, 255, 255), (cx, cy), s // 3)


def icono_creditos(pantalla, r):
    cx, cy = r.center
    s = min(r.width, r.height) // 4
    pygame.draw.circle(pantalla, (255, 255, 255), (cx, cy), s, 2)
    pygame.draw.line(pantalla, (255, 255, 255),
                     (cx, cy - s), (cx, cy + 1), 2)
    pygame.draw.circle(pantalla, (255, 255, 255),
                       (cx, cy + s // 2 + 2), 2)


def icono_mis_niveles(pantalla, r):
    """Stack de capas (niveles propios apilados)."""
    cx, cy = r.center
    s = min(r.width, r.height) // 4
    for i in range(3):
        offset = (i - 1) * 3
        pygame.draw.rect(pantalla, (255, 255, 255),
                         (cx - s + offset, cy - s + offset, s * 2, s * 2),
                         2, border_radius=2)


def icono_como_jugar(pantalla, r):
    """Ícono de Gamepad."""
    cx, cy = r.center
    s = min(r.width, r.height) // 3
    rect = pygame.Rect(cx - s, cy - s // 2, s * 2, s)
    pygame.draw.rect(pantalla, (255, 255, 255), rect, 3, border_radius=5)
    # Cruz direccional
    pygame.draw.line(pantalla, (255, 255, 255), (cx - s // 2, cy), (cx - s // 4, cy), 2)
    pygame.draw.line(pantalla, (255, 255, 255), (cx - s // 2 - s // 8, cy + s // 8), (cx - s // 2 - s // 8, cy - s // 8), 2)
    # Botones
    pygame.draw.circle(pantalla, (255, 255, 255), (cx + s // 2, cy - s // 4), 2)
    pygame.draw.circle(pantalla, (255, 255, 255), (cx + s // 2 + s // 4, cy), 2)