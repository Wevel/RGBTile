import os
import sys
import numpy as np
from enum import Enum
import math

if os.getenv('TERM_PROGRAM') == "vscode":
	import matplotlib.pyplot as plt

# https://www.redblobgames.com/grids/hexagons/
class HexType(Enum):
	FlatTopped = 0
	PointyTopped = 1

def GeneratePositions(centerX:float, centerY:float, hexRadius:float, intRadius:int) -> tuple[np.ndarray,float,int,float]:
	angleRad = np.pi / 180.0 * 60.0

	numLEDs = 0
	for q in range(-intRadius, intRadius + 1):
		for r in range(-intRadius, intRadius + 1):
			s = - q - r
			if  abs(s) <= intRadius:
				numLEDs += 1

	areaScale = 1.5 * np.sqrt(3.0)
	area = areaScale * hexRadius * hexRadius
	smallArea = area / numLEDs
	subHexRadius = np.sqrt(smallArea / areaScale)

	positions = np.zeros((numLEDs, 2))
	# Flat top
	dqX = 3.0 * subHexRadius * np.cos(angleRad)
	dqY = subHexRadius * np.sin(angleRad)
	drX = 0.0
	drY = 2.0 * subHexRadius * np.sin(angleRad)

	# Pointy top
	# dqX = 2.0 * subHexRadius * np.sin(angleRad)
	# dqY = 0.0
	# drX = subHexRadius * np.sin(angleRad)
	# drY = 3.0 * subHexRadius * np.cos(angleRad)

	def getPoint(q:int, r:int) -> tuple[float, float]:
		return (centerX + (q * dqX) + (r * drX), centerY + (q * dqY) + (r * drY))

	hexPoints = []
	for q in range(-intRadius, intRadius + 1):
		for r in range(-intRadius, intRadius + 1):
			s = - q - r
			if len(hexPoints) < numLEDs and abs(s) <= intRadius:
				hexPoints.append((q, r))
	
	def getPolar (pos:tuple[float,float]) -> tuple[float,float]:
		x = pos[0] - centerX
		y = pos[1] - centerY
		alpha = np.arctan2(y, x)
		r = np.sqrt(x**2 + y**2)
		return alpha, r

	def sortKey(p) -> float:
		q = p[0]
		r = p[1]
		s = - q - r
		alpha, _ = getPolar(getPoint(q, r))
		return (max(abs(q), abs(r), abs(s)) * 1000) + alpha

	hexPoints.sort(key=sortKey)

	for i, p in enumerate(hexPoints):
		positions[i,:] = getPoint(p[0], p[1])

	return positions, subHexRadius, numLEDs, np.sqrt((dqX * dqX) + (dqY * dqY))

def getHexagonBoundary(centerX:float, centerY:float, hexRadius:float, hexType:HexType) -> np.ndarray:
	def getPoint(index:int) -> tuple[float, float]:
		angleDeg = 60 * index - (30 if hexType is HexType.PointyTopped else 0)
		angleRad = np.pi / 180 * angleDeg
		return (centerX + hexRadius * np.cos(angleRad), centerY + hexRadius * np.sin(angleRad))

	boundary = np.zeros((7, 2))
	for i in range(7):
		boundary[i, :] = getPoint(i)
	
	return boundary

def plotDifferentSize(boardRadius:float, minLEDRadius:int, maxLEDRadius:int):
	if os.getenv('TERM_PROGRAM') != "vscode":
		return

	ledRadii = []
	ledCounts = []
	ledSpacings = []
	for i in range(minLEDRadius, maxLEDRadius + 1):
		_, _, numLEDs, ledSpacing = GeneratePositions(0.0, 0.0, boardRadius, i)
		ledRadii.append(i)
		ledCounts.append(numLEDs)
		ledSpacings.append(ledSpacing)
	
	plt.figure(figsize=(8.0, 6.0))
	plt.plot(ledRadii, ledCounts)

	plt.figure(figsize=(8.0, 6.0))
	plt.plot(ledRadii, ledSpacings)

def plotArray(boardRadius:float, ledRadius:int):
	if os.getenv('TERM_PROGRAM') != "vscode":
		return

	positions, subHexRadius, numLEDs, ledSpacing = GeneratePositions(0.0, 0.0, boardRadius, ledRadius)

	print(f"{ledRadius}: {numLEDs} {'%.1f' % ledSpacing}mm")

	plt.figure(figsize=(8.0, 6.0))
	plt.axis("equal")
	plt.xlabel("x (mm)")
	plt.ylabel("y (mm)")

	hexagon = getHexagonBoundary(0.0, 0.0, boardRadius, HexType.PointyTopped)

	plt.plot(hexagon[:, 0], hexagon[:, 1])

	for i in range(numLEDs):
		hexagon = getHexagonBoundary(positions[i, 0], positions[i, 1], subHexRadius, HexType.FlatTopped)
		plt.plot(hexagon[:, 0], hexagon[:, 1], "k:")


if __name__ == "__main__":
	plotArray(50.0, 3)
	# plotDifferentSize(50.0, 1, 10)

	if os.getenv('TERM_PROGRAM') == "vscode":
		import matplotlib.pyplot as plt
		plt.show()
