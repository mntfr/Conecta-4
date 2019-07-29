import numpy as np
import pygame
import sys
import math
import random

AZUL = (0, 0, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
AMARILLO = (255, 255, 0)

NUMRENGLONES = 6
NUMCOLUMNAS = 7

JUGADOR = 0
IA = 1

VACIO = 0
PIEZAJUGADOR = 1
PIEZA_IA = 2

TAMVENTANA = 4

def crearTablero():
	tablero = np.zeros((NUMRENGLONES,NUMCOLUMNAS))
	return tablero

def soltarPieza(tablero, renglon, columna, pieza):
	tablero[renglon][columna] = pieza

def movimientoValido(tablero, columna):
	return tablero[NUMRENGLONES-1][columna] == 0

def getRenglonValido(tablero, columna):
	for r in range(NUMRENGLONES):
		if tablero[r][columna] == 0:
			return r

def checarEmpate(tablero):
	if 0 in tablero:
		return False
	return True

def imprimirTablero(tablero):
	print(np.flip(tablero, 0))

def checarVictoria(tablero, pieza):
	# Check horizontal locations for win
	for c in range(NUMCOLUMNAS-3):
		for r in range(NUMRENGLONES):
			if tablero[r][c] == pieza and tablero[r][c+1] == pieza and tablero[r][c+2] == pieza and tablero[r][c+3] == pieza:
				return True

	# Check vertical locations for win
	for c in range(NUMCOLUMNAS):
		for r in range(NUMRENGLONES-3):
			if tablero[r][c] == pieza and tablero[r+1][c] == pieza and tablero[r+2][c] == pieza and tablero[r+3][c] == pieza:
				return True

	# Check positively sloped diaganols
	for c in range(NUMCOLUMNAS-3):
		for r in range(NUMRENGLONES-3):
			if tablero[r][c] == pieza and tablero[r+1][c+1] == pieza and tablero[r+2][c+2] == pieza and tablero[r+3][c+3] == pieza:
				return True

	# Check negatively sloped diaganols
	for c in range(NUMCOLUMNAS-3):
		for r in range(3, NUMRENGLONES):
			if tablero[r][c] == pieza and tablero[r-1][c+1] == pieza and tablero[r-2][c+2] == pieza and tablero[r-3][c+3] == pieza:
				return True

def esMoviementoFinal(tablero):
	return checarVictoria(tablero, PIEZAJUGADOR) or checarVictoria(tablero, PIEZA_IA) or len(getMovimientosValidos(tablero)) == 0

def minimax(tablero, profundidad, alpha, beta, maximizando):
	movimientosPosibles = getMovimientosValidos(tablero)
	esFinal = esMoviementoFinal(tablero)
	if profundidad == 0 or esFinal:
		if esFinal:
			if checarVictoria(tablero, PIEZA_IA):
				return (None, 100000000000000)
			elif checarVictoria(tablero, PIEZAJUGADOR):
				return (None, -10000000000000)
			else: 
				return (None, 0)
		else: # 
			return (None, puntPosicion(tablero, PIEZA_IA))

	if maximizando:
		valor = -math.inf
		columna = random.choice(movimientosPosibles)
		for col in movimientosPosibles:
			renglon = getRenglonValido(tablero, col)
			copiaTablero = tablero.copy()
			soltarPieza(copiaTablero, renglon, col, PIEZA_IA)
			nuevaPuntuacion = minimax(copiaTablero, profundidad-1, alpha, beta, False)[1]
			if nuevaPuntuacion > valor:
				valor = nuevaPuntuacion
				columna = col
			alpha = max(alpha, valor)
			if alpha >= beta:
				break
		return columna, valor

	else:
		valor = math.inf
		columna = random.choice(movimientosPosibles)
		for col in movimientosPosibles:
			renglon = getRenglonValido(tablero, col)
			copiaTablero = tablero.copy()
			soltarPieza(copiaTablero, renglon, col, PIEZAJUGADOR)
			nuevaPuntuacion = minimax(copiaTablero, profundidad-1, alpha, beta, True)[1]
			if nuevaPuntuacion < valor:
				valor = nuevaPuntuacion
				columna = col
			beta = min(beta, valor)
			if alpha >= beta:
				break
		return columna, valor

def getMovimientosValidos(tablero):
	posicionesValidas = []
	for col in range(NUMCOLUMNAS):
		if movimientoValido(tablero, col):
			posicionesValidas.append(col)
	return posicionesValidas

def escogerMejorMovimiento(tablero, pieza):
	posValidas = getMovimientosValidos(tablero)
	mejorPuntuacion = -10000

	for col in posValidas:
		renglon = getRenglonValido(tablero, col)
		tableroTemporal = tablero.copy()
		soltarPieza(tableroTemporal, renglon, col, pieza)
		score = score_position(tableroTemporal, pieza)
		if score > mejorPuntuacion:
			mejorPuntuacion = score
			mejorColumna = col

	return mejorColumna

def evaluarVentana(window, pieza):
	puntuacion = 0
	piezaDeOponente = PIEZAJUGADOR
	if pieza == PIEZAJUGADOR:
		piezaDeOponente = PIEZA_IA

	if window.count(pieza) == 4:
		puntuacion += 100
	elif window.count(pieza) == 3 and window.count(VACIO) == 1:
		puntuacion += 5
	elif window.count(pieza) == 2 and window.count(VACIO) == 2:
		puntuacion += 2

	if window.count(piezaDeOponente) == 3 and window.count(VACIO) == 1:
		puntuacion -= 4

	return puntuacion

def puntPosicion(tablero, turno):
	puntuacion = 0

	# puntuacion centro
	colCentro = [int(i) for i in list(tablero[:, NUMCOLUMNAS//2])]
	contCentro = colCentro.count(turno)
	puntuacion += contCentro * 3

	# posicion Horizontal
	for r in range(NUMRENGLONES):
		renglon = [int(i) for i in list(tablero[r,:])]
		for c in range(NUMCOLUMNAS-3):
			ventana = renglon[c:c+TAMVENTANA]
			puntuacion += evaluarVentana(ventana, turno)

	# puntuacion Vertical
	for c in range(NUMCOLUMNAS):
		columna = [int(i) for i in list(tablero[:,c])]
		for r in range(NUMRENGLONES-3):
			ventana = columna[r:r+TAMVENTANA]
			puntuacion += evaluarVentana(ventana, turno)

	# puntuacion diagonales
	for r in range(NUMRENGLONES-3):
		for c in range(NUMCOLUMNAS-3):
			ventana = [tablero[r+i][c+i] for i in range(TAMVENTANA)]
			puntuacion += evaluarVentana(ventana, turno)

	for r in range(NUMRENGLONES-3):
		for c in range(NUMCOLUMNAS-3):
			ventana = [tablero[r+3-i][c+i] for i in range(TAMVENTANA)]
			puntuacion += evaluarVentana(ventana, turno)

	return puntuacion

def dibujarTablero(tablero):
	for c in range(NUMCOLUMNAS):
		for r in range(NUMRENGLONES):
			pygame.draw.rect(pantalla, AZUL, (c*TAMCUADROS, r*TAMCUADROS+TAMCUADROS, TAMCUADROS, TAMCUADROS))
			pygame.draw.circle(pantalla, NEGRO, (int(c*TAMCUADROS+TAMCUADROS/2), int(r*TAMCUADROS+TAMCUADROS+TAMCUADROS/2)), RADIO)
	
	for c in range(NUMCOLUMNAS):
		for r in range(NUMRENGLONES):		
			if tablero[r][c] == 1:
				pygame.draw.circle(pantalla, ROJO, (int(c*TAMCUADROS+TAMCUADROS/2), largo-int(r*TAMCUADROS+TAMCUADROS/2)), RADIO)
			elif tablero[r][c] == 2: 
				pygame.draw.circle(pantalla, AMARILLO, (int(c*TAMCUADROS+TAMCUADROS/2), largo-int(r*TAMCUADROS+TAMCUADROS/2)), RADIO)
	pygame.display.update()

tablero = crearTablero()
imprimirTablero(tablero)
juegoTerminado = False
turno = 1

pygame.init()

TAMCUADROS = 100

ancho = NUMCOLUMNAS * TAMCUADROS
largo = (NUMRENGLONES+1) * TAMCUADROS

tam = (ancho, largo)

RADIO = int(TAMCUADROS/2 - 5)

pantalla = pygame.display.set_mode(tam)
dibujarTablero(tablero)
pygame.display.update()

myFuente = pygame.font.SysFont("monospace", 18)

#Aqui se especifica quien empieza
turno = IA
#la profundidad esta relacionada con la dificultad
#teoricamente si el primero turno es la IA 
#y la profunidad es 6 no hay manera de ganarle
PROFUNDIDAD = 6

while not juegoTerminado:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.MOUSEMOTION:
			pygame.draw.rect(pantalla, NEGRO, (0, 0, ancho, TAMCUADROS))
			posx = event.pos[0]
			if turno == JUGADOR:
				pygame.draw.circle(pantalla, ROJO, (posx, int(TAMCUADROS/2)), RADIO)

		pygame.display.update()

		if event.type == pygame.MOUSEBUTTONDOWN:
			pygame.draw.rect(pantalla, NEGRO, (0,0, ancho, TAMCUADROS))
			if turno == JUGADOR:
				posx = event.pos[0]
				columna = int(math.floor(posx/TAMCUADROS))

				if movimientoValido(tablero, columna):
					renglon = getRenglonValido(tablero, columna)
					soltarPieza(tablero, renglon, columna, PIEZAJUGADOR)

					if checarVictoria(tablero, PIEZAJUGADOR):
						mensaje = myFuente.render("Jugador 1 GANA!", 1, ROJO)
						pantalla.blit(mensaje, (40,10))
						juegoTerminado = True

					turno += 1
					turno = turno % 2

					imprimirTablero(tablero)
					dibujarTablero(tablero)


	#Turno inteligencia artificial
	if turno == IA and not juegoTerminado:			
		columna, puntuacion = minimax(tablero, PROFUNDIDAD, -math.inf, math.inf, True)

		if movimientoValido(tablero, columna):
			renglon = getRenglonValido(tablero, columna)
			soltarPieza(tablero, renglon, columna, PIEZA_IA)

			if checarVictoria(tablero, PIEZA_IA):
				mensaje = myFuente.render("Gano la computadora", 1, AMARILLO)
				pantalla.blit(mensaje, (40,10))
				juegoTerminado = True	


			imprimirTablero(tablero)
			dibujarTablero(tablero)

			turno += 1
			turno = turno % 2

	if checarEmpate(tablero):
		mensaje = myFuente.render("Empate", 1, AZUL)
		pantalla.blit(mensaje, (40,10))
		juegoTerminado = True
			
	if juegoTerminado:
		pygame.time.wait(3000)