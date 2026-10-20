"""Parser de niveles .txt."""
import pygame
from ajustes import TAM_TILE


class Nivel:
    DEFAULTS = {
        "nombre": "Nivel",
        "fondo": None,
        "suelo": None,
        "musica": None,
        "codigo_secreto": None,
    }

    def __init__(self, ruta, config=None):
        self.ruta = ruta
        with open(ruta, "r", encoding="utf-8") as f:
            lineas = f.read().splitlines()

        self.grilla = list(reversed(lineas))
        self.ancho_px = max((len(l) for l in self.grilla), default=0) * TAM_TILE
        self.alto_px  = len(self.grilla) * TAM_TILE

        cfg = dict(self.DEFAULTS)
        if config:
            cfg.update(config)
        self.config = cfg

    def celda(self, fila, col):
        if 0 <= fila < len(self.grilla):
            linea = self.grilla[fila]
            if 0 <= col < len(linea):
                return linea[col]
        return " "

    def posiciones_de(self, simbolo):
        out = []
        for fila, linea in enumerate(self.grilla):
            for col, c in enumerate(linea):
                if c == simbolo:
                    out.append((col * TAM_TILE, fila * TAM_TILE))
        return out

    def rects_solidos(self):
        rects = []

        solidos_chars = (
            "#", "$", "%", "&", "/", "=",
            "L", "R", "U", "D",
            "q", "w", "e", "r",
            "t", "y", "u", "i", 
            "o", "p", "a", "s",
            "d", "f",
            "g", "h", "j", "k", 
            "l", "ñ", "z", "x",
            "c", "v", "b", "n"
        )
        
        for fila, linea in enumerate(self.grilla):
            for col, c in enumerate(linea):
                if c in solidos_chars:
                    rects.append((
                        pygame.Rect(col * TAM_TILE, fila * TAM_TILE, TAM_TILE, TAM_TILE),
                        c
                    ))
        return rects