"""Sistema de animación por secuencia + divisor propio de spritesheets."""
import pygame


class DivisorSpritesheet:
    """Corta una spritesheet en una lista de Surfaces (frames)."""

    @staticmethod
    def dividir(ruta, ancho_frame, alto_frame, columnas, filas=1):
        hoja = pygame.image.load(ruta).convert_alpha()
        frames = []
        for fila in range(filas):
            for col in range(columnas):
                rect = pygame.Rect(
                    col * ancho_frame, fila * alto_frame,
                    ancho_frame, alto_frame
                )
                frames.append(hoja.subsurface(rect).copy())
        return frames

    @staticmethod
    def dividir_fila(ruta, ancho_frame, alto_frame, fila, columnas):
        return DivisorSpritesheet.dividir(
            ruta, ancho_frame, alto_frame, columnas, filas=fila + 1
        )[fila * columnas:(fila + 1) * columnas]


