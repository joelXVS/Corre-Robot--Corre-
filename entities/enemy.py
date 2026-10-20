import pygame
import random
from entities.entity import Entidad
from ajustes import DANIO_ENEMIGO, GRAVEDAD

class Enemigo(Entidad):
    def __init__(self, x, y, ancho=32, alto=32, velocidad=3, animaciones=None):
        super().__init__(x, y, ancho, alto)
        self.animaciones = animaciones or {}
        self.danio = DANIO_ENEMIGO
        self.velocidad = velocidad
        self.vel_x = 0
        self.vel_y = 0
        self.en_suelo = False
        self.mirando_derecha = True
        
        # Distancias de detección y ataque
        self.distancia_deteccion = 250
        self.distancia_ataque = 50
        self.distancia_y_ataque = 40
        
        # Sistema de tiempo para la IA de patrulla
        self.timer_ia = 0.0
        self.estado_ia = "idle" # idle o walk
        
        self.estado_anim = "idle"
        self.animacion = self.animaciones.get("idle", self.animaciones.get("walk"))
        self.cooldown_ataque = 0.0

    def aplicar_efecto(self, robot):
        robot.recibir_danio(self.danio)

    def actualizar(self, dt, solidos, robot):
        if self.cooldown_ataque > 0:
            self.cooldown_ataque -= dt

        dist_real = pygame.math.Vector2(self.rect.center).distance_to(robot.rect.center)
        dist_y = abs(self.rect.centery - robot.rect.centery)
        
        nuevo_estado = "idle"

        # --- 1. Lógica de IA (Agresivo vs Patrulla) ---
        if dist_real < self.distancia_deteccion and dist_y < 100:
            # EL JUGADOR ESTÁ CERCA
            if (dist_real < self.distancia_ataque and dist_y < self.distancia_y_ataque) or self.rect.colliderect(robot.rect):
                # Atacar
                nuevo_estado = "attack"
                self.vel_x = 0
                if self.cooldown_ataque <= 0:
                    self.aplicar_efecto(robot)
                    self.cooldown_ataque = 1.0
            else:
                # Perseguir
                nuevo_estado = "walk"
                self.vel_x = (self.velocidad if robot.rect.centerx > self.rect.centerx else -self.velocidad) * dt * 60
            
            # Reiniciar el timer de patrulla para cuando el jugador se aleje
            self.timer_ia = 0 
        else:
            # EL JUGADOR ESTÁ LEJOS (Modo Patrulla)
            self.timer_ia -= dt
            
            if self.timer_ia <= 0:
                # Elegimos una nueva acción al azar
                # 40% de probabilidad de quedarse quieto, 60% de caminar
                if random.random() < 0.4:
                    self.estado_ia = "idle"
                    self.timer_ia = random.uniform(1.0, 3.0) # Quieto de 1 a 3 segundos
                else:
                    self.estado_ia = "walk"
                    self.timer_ia = random.uniform(1.0, 3.5) # Camina de 1 a 3.5 segundos
                    # Velocidad de patrulla lenta (la mitad de su velocidad real)
                    vel_patrulla = self.velocidad * 0.5
                    self.vel_x = random.choice([-vel_patrulla, vel_patrulla]) * dt * 60

            # Asignar animación y velocidad según el estado de patrulla
            if self.estado_ia == "idle":
                nuevo_estado = "idle"
                self.vel_x = 0
            else:
                nuevo_estado = "walk"

        # Actualizar dirección visual
        if self.vel_x > 0:
            self.mirando_derecha = True
        elif self.vel_x < 0:
            self.mirando_derecha = False

        # --- 2. Detección de borde o pared ---
        if self.vel_x != 0 and self.en_suelo:
            if self.vel_x > 0:
                check_rect = pygame.Rect(self.rect.right, self.rect.bottom, 5, 10)
            else:
                check_rect = pygame.Rect(self.rect.left - 5, self.rect.bottom, 5, 10)
            
            hay_suelo = any(s.colliderect(check_rect) for s, _ in solidos)
            if not hay_suelo:
                self.vel_x *= -1 * dt * 60
                self.mirando_derecha = self.vel_x > 0
                self.timer_ia = 0 # Forzar nueva decisión al llegar a un borde

        # --- 3. Cambiar animación ---
        if nuevo_estado in self.animaciones:
            if self.estado_anim != nuevo_estado:
                self.estado_anim = nuevo_estado
                self.animacion = self.animaciones[nuevo_estado]
                self.animacion.reiniciar()

        # --- 4. Física y Colisiones ---
        self.vel_y = min(self.vel_y + (GRAVEDAD * dt * 60), 20)

        # Mover en X
        self.rect.x += self.vel_x * dt * 60
        for s, _ in solidos:
            if self.rect.colliderect(s):
                if self.vel_x > 0:
                    self.rect.right = s.left
                    self.vel_x = -abs(self.vel_x) * dt * 60
                elif self.vel_x < 0:
                    self.rect.left = s.right
                    self.vel_x = abs(self.vel_x) * dt * 60
                
                self.timer_ia = 0 # Forzar nueva decisión al chocar con una pared
                self.mirando_derecha = self.vel_x > 0

        # Mover en Y
        self.rect.y += self.vel_y * dt * 60
        self.en_suelo = False
        for s, _ in solidos:
            if self.rect.colliderect(s):
                if self.vel_y > 0:
                    self.rect.bottom = s.top
                    self.vel_y = 0
                    self.en_suelo = True
                elif self.vel_y < 0:
                    self.rect.top = s.bottom
                    self.vel_y = 0

        # --- 5. Actualizar animación actual ---
        if self.animacion:
            self.animacion.actualizar(dt)

    def dibujar(self, pantalla, offset=(0, 0)):
        if self.animacion:
            img = self.animacion.frame_actual()
            if not self.mirando_derecha:
                img = pygame.transform.flip(img, True, False)
            pantalla.blit(img, (self.rect.x - offset[0], self.rect.y - offset[1]))
        else:
            pygame.draw.rect(pantalla, (200, 60, 200), (self.rect.x - offset[0], self.rect.y - offset[1], self.rect.width, self.rect.height))