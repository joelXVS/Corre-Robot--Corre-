"""Jugador: movimiento, salto, daño, energía, reparación y habilidades."""
import pygame
from entities.entity import Entidad
from ajustes import (
    GRAVEDAD, FUERZA_SALTO, VELOCIDAD_ROBOT,
    VIDA_MAXIMA, ENERGIA_MAXIMA, USO_ENERGIA_SALTO,
    SUPER_SALTO, SUPER_VELOCIDAD, RESISTENCIA
)


class Robot(Entidad):
    def __init__(self, x, y, animaciones, vida_max=None, energia_max=None):
        super().__init__(x, y, 32, 40)
        self.vida_max = vida_max if vida_max is not None else VIDA_MAXIMA
        self.vida = self.vida_max
        self.energia_max = energia_max if energia_max is not None else ENERGIA_MAXIMA
        self.energia = self.energia_max

        self.en_suelo = False
        self.mirando_derecha = True
        self.invulnerable = 0.0
        self.habilidades = {}
        self.saltos_disponibles = 1
        
        # Sistema de estados
        self.estado = "idle" # idle, caminar, salto, daño, muerte
        self.timer_danio = 0.0
        self.muerto = False

        self.animaciones = animaciones
        self.animacion = animaciones["idle"]
        self.alpha = 255
        
        # Limites del nivel
        self.limite_izq = 0
        self.limite_der = 99999

    # ---------- Acciones ----------
    def mover_izquierda(self):
        if self.muerto or self.timer_danio > 0: return
        self.mirando_derecha = False
        vel = VELOCIDAD_ROBOT + (SUPER_VELOCIDAD if "super_velocidad" in self.habilidades else 0)
        
        if self.rect.left > self.limite_izq:
            self.vel_x = -vel
        else:
            self.vel_x = 0

    def mover_derecha(self):
        if self.muerto or self.timer_danio > 0: return
        self.mirando_derecha = True
        vel = VELOCIDAD_ROBOT + (SUPER_VELOCIDAD if "super_velocidad" in self.habilidades else 0)
        
        if self.rect.right < self.limite_der:
            self.vel_x = vel
        else:
            self.vel_x = 0

    def detener(self):
        if self.muerto or self.timer_danio > 0: return
        self.vel_x = 0

    def saltar(self):
        if self.muerto or self.timer_danio > 0: return
        if "volar" in self.habilidades:
            self.vel_y = -5
            return
        
        fuerza = FUERZA_SALTO
        if "super_salto" in self.habilidades:
            fuerza += SUPER_SALTO
            
        if self.en_suelo or self.saltos_disponibles > 0:
            self.vel_y = fuerza
            self.energia = max(0, self.energia - USO_ENERGIA_SALTO)
            if not self.en_suelo:
                self.saltos_disponibles -= 1
            self.en_suelo = False

    # ---------- Efectos ----------
    def recibir_danio(self, cantidad):
        if self.invulnerable > 0 or self.muerto:
            return
        self.vida = max(0, self.vida - cantidad)
        self.invulnerable = 1.0
        
        if self.vida <= 0 or self.energia <= 0:
            self.morir()
        else:
            self.estado = "daño"
            self.animacion = self.animaciones["daño"]
            self.animacion.reiniciar()
            self.timer_danio = 0.5
            self.vel_x = 0
    
    def morir(self):
        if self.muerto: return
        self.vida = 0
        self.muerto = True
        self.estado = "muerte"
        self.animacion = self.animaciones["muerte"]
        self.animacion.reiniciar()
        self.vel_x, self.vel_y = 0, 0

    def otorgar_habilidad(self, nombre, duracion):
        nombre = nombre.lower()
        self.habilidades[nombre] = duracion
        if nombre == "doble_salto":
            self.saltos_disponibles = 2
        elif nombre == "resistencia":
            self.vida_max += RESISTENCIA
            self.vida += RESISTENCIA

    # ---------- Update ----------
    def actualizar(self, dt, solidos):
        if self.muerto:
            self.vel_y = min(self.vel_y + (GRAVEDAD * dt * 60), 20)
            self.rect.y += self.vel_y * dt * 60
            
            for s, _ in solidos:
                if self.rect.colliderect(s):
                    if self.vel_y > 0:
                        self.rect.bottom = s.top
                        self.vel_y = 0
            self.animacion.actualizar(dt)
            return

        if self.timer_danio > 0:
            self.timer_danio -= dt
            if self.timer_danio <= 0:
                self.estado = "idle"

        # Física de vuelo / planeo
        if self.en_suelo:
            self.vel_y = 0
        else:
            if "volar" in self.habilidades and not self.timer_danio > 0:
                self.vel_y = min(self.vel_y + (GRAVEDAD * 0.2 * dt * 60), 2)
            else:
                self.vel_y = min(self.vel_y + (GRAVEDAD * dt * 60), 20)

        # Movimiento en X
        self.rect.x += self.vel_x * dt * 60
        for s, _ in solidos:
            if self.rect.colliderect(s):
                if self.vel_x > 0:
                    self.rect.right = s.left
                elif self.vel_x < 0:
                    self.rect.left = s.right

        # Movimiento en Y
        self.rect.y += self.vel_y * dt * 60
        self.en_suelo = False
        for s, _ in solidos:
            if self.rect.colliderect(s):
                if self.vel_y > 0:
                    self.rect.bottom = s.top
                    self.vel_y = 0
                    self.en_suelo = True
                    self.saltos_disponibles = 2 if "doble_salto" in self.habilidades else 1
                elif self.vel_y < 0:
                    self.rect.top = s.bottom
                    self.vel_y = 0

        if self.invulnerable > 0:
            self.invulnerable -= dt

        for nombre in list(self.habilidades.keys()):
            self.habilidades[nombre] -= dt
            if self.habilidades[nombre] <= 0:
                del self.habilidades[nombre]
                if nombre == "doble_salto":
                    self.saltos_disponibles = 1
                elif nombre == "resistencia":
                    self.vida_max -= RESISTENCIA
                    self.vida = min(self.vida, self.vida_max)

        self._actualizar_animacion()
        self.animacion.actualizar(dt)

    def _actualizar_animacion(self):
        if self.muerto:
            return
        
        if self.timer_danio > 0:
            nombre = "daño"
        elif not self.en_suelo and self.vel_y != 0:
            nombre = "salto"
        elif self.vel_x != 0:
            nombre = "caminar"
        else:
            nombre = "idle"
            
        if self.estado != nombre:
            self.estado = nombre
            nueva_anim = self.animaciones.get(nombre, self.animaciones["idle"])
            if nueva_anim is not self.animacion:
                self.animacion = nueva_anim
                self.animacion.reiniciar()

    def dibujar(self, pantalla, offset=(0, 0)):
        img = self.animacion.frame_actual()
        
        if self.alpha < 255:
            img.set_alpha(self.alpha)
            
        if not self.mirando_derecha:
            img = pygame.transform.flip(img, True, False)
        # Parpadeo al ser invulnerable (pero si está muerto no parpadea)
        if not self.muerto and self.invulnerable > 0 and int(self.invulnerable * 20) % 2 == 0:
            return
        pantalla.blit(img, (self.rect.x - offset[0], self.rect.y - offset[1]))