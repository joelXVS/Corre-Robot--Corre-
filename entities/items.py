"""Base de ítems recogibles"""

from entities.entity import Entidad

class Coleccionable(Entidad):
    def __init__(self, x, y, ancho, alto, animacion=None, sonido=None):
        super().__init__(x, y, ancho, alto)
        self.animacion = animacion
        self.sonido = sonido
        self.recogido = False

    def recoger(self, robot):
        """Cada subclase define su efecto concreto."""
        raise NotImplementedError

    def _reproducir_sonido(self):
        if self.sonido is not None:
            self.sonido.play()

    def dibujar(self, pantalla, offset=(0, 0)):
        if self.recogido:
            return
        super().dibujar(pantalla, offset)
        
from ajustes import ENERGIA_BATERIA

class Bateria(Coleccionable):
    def __init__(self, x, y, animacion=None, sonido=None):
        super().__init__(x, y, 24, 24, animacion, sonido)
        self.valor = ENERGIA_BATERIA

    def recoger(self, robot):
        robot.energia = min(robot.energia + self.valor, robot.energia_max)
        self.recogido = True
        self._reproducir_sonido()
        
from ajustes import REPARACION_ENGRANAJE

class Engranaje(Coleccionable):
    def __init__(self, x, y, animacion=None, sonido=None):
        super().__init__(x, y, 24, 24, animacion, sonido)
        self.valor = REPARACION_ENGRANAJE

    def recoger(self, robot):
        robot.vida = min(robot.vida + self.valor, robot.vida_max)
        self.recogido = True
        self._reproducir_sonido()
        
from ajustes import DURACION_HABILIDAD

class CodigoPy(Coleccionable):
    """Otorga una habilidad temporal (ej. 'doble_salto')."""

    def __init__(self, x, y, animacion=None, sonido=None,
                 habilidad="doble_salto"):
        super().__init__(x, y, 24, 24, animacion, sonido)
        self.habilidad = habilidad

    def recoger(self, robot):
        robot.otorgar_habilidad(self.habilidad, DURACION_HABILIDAD)
        self.recogido = True
        self._reproducir_sonido()

class CodigoSecreto(Coleccionable):
    """Muestra fragmentos de un desbloqueable"""

    def __init__(self, x, y, animacion=None, sonido=None):
        super().__init__(x, y, 24, 24, animacion, sonido)
        self.fragmento = None

    def recoger(self, robot):
        self.recogido = True
        self._reproducir_sonido()