"""HUD: iconos + números, sin texto descriptivo."""
class HUD:
    def __init__(self, recursos):
        self.recursos = recursos
        self.iconos = recursos.iconos_hud()

    def dibujar(self, pantalla, robot, puntaje, nivel_actual, total_niveles, es_prueba=False):
        datos = [
            ("vida",    f"{robot.vida}"),
            ("energia", f"{robot.energia}"),
        ]
        
        if not es_prueba:
            datos.append(("puntaje", f"{puntaje}"))
            datos.append(("nivel", f"{nivel_actual}/{total_niveles}"))
            
        x, y = 10, 10
        for icono, valor in datos:
            pantalla.blit(self.iconos[icono], (x, y))
            txt = self.recursos.texto(valor, 20)
            pantalla.blit(txt, (x + 40, y - 6))
            y += 40