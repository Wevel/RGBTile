# To run, open the KiCad scripting console and type: exec(open("F:/Git/RGBTile/Hardware/HexTile/Load.py").read())
# Can all make a function:
# def Run():
# 	exec(open("F:/Git/RGBTile/Hardware/HexTile/Load.py").read())
# Then use Run()

# Based on https://github.com/gregdavill/GlassUnicorn/blob/master/ref/led_32x32_array_place.py

import os
import sys
import numpy as np
import math

import pcbnew

sys.path.append("F:/Git/RGBTile/Hardware/HexTile")
import HexPlacement as hexagon
	
class HexVector:
	def __init__(self, q:int, r:int) -> None:
		self.q = q
		self.r = r

	def __str__(self) -> str:
		return f"[{self.q}, {self.r}]"

	def GetHexXYPos(self, subHexRadius:float) -> "Vector2":
		angleRad = np.pi / 180.0 * 60.0

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

		return Vector2((self.q * dqX) + (self.r * drX), (self.q * dqY) + (self.r * drY))

class Vector2:
	def __init__(self, x:float, y:float) -> None:
		self.x = x
		self.y = y

	def __str__(self) -> str:
		return f"({self.x}, {self.y})"

	def __add__(self, other:"Vector2") -> "Vector2":
		return Vector2(self.x + other.x, self.y + other.y)

	def Rotate(self, angle:float) -> "Vector2":
		return Vector2((self.x * np.cos(angle)) - (self.y * np.sin(angle)), (self.x * np.sin(angle)) + (self.y * np.cos(angle)))

	def GetPolar (self) -> tuple[float,float]:
		alpha = np.arctan2(self.y, self.x) - (0.5 * np.pi)
		r = np.sqrt(self.x**2 + self.y**2)
		return alpha, r

def PlaceComponents():
	def GenerateHexPositions(hexRadius:float, intRadius:int) -> tuple[list[HexVector],float]:#tuple[np.ndarray,float,int,float]: # centerX:float, centerY:float,
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

		# def getPoint(q:int, r:int) -> tuple[float, float]:
		# 	return (centerX + (q * dqX) + (r * drX), centerY + (q * dqY) + (r * drY))

		hexPoints = []
		for q in range(-intRadius, intRadius + 1):
			for r in range(-intRadius, intRadius + 1):
				s = - q - r
				if len(hexPoints) < numLEDs and abs(s) <= intRadius:
					hexPoints.append(HexVector(q, r))
		
		def sortKey(pos:HexVector):
			return pos.q + pos.r

		hexPoints.sort(key=sortKey)

		return hexPoints, subHexRadius

	pcb = pcbnew.GetBoard()

	initialX = 120.0
	initialY = 70.0
	boardRadius = 50.0
	ledRadius = 3

	def addTrack(start:Vector2, end:Vector2, width:float, layer=pcbnew.F_Cu):
		track = pcbnew.PCB_TRACK(pcb)
		track.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(float(initialX + start.x)), pcbnew.FromMM(float(initialY + start.y))))
		track.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(float(initialX + end.x)), pcbnew.FromMM(float(initialY + end.y))))
		track.SetWidth(pcbnew.FromMM(float(width)))  # type: ignore
		track.SetLayer(layer)
		pcb.Add(track)

	def addTrackArc(start:Vector2, end:Vector2, radius:float, width:float, layer=pcbnew.F_Cu):
		deltaX = end.x - start.x
		deltaY = end.y - start.y
		distance = np.sqrt(deltaX**2 + deltaY**2)

		if np.abs(radius) - (0.5 * distance) > 0:
			radiusSquared = radius * radius
			angle = np.arccos((2.0 * radiusSquared - (distance * distance)) / (2.0 * radiusSquared))
			offset = radius * (1.0 - np.cos(0.5 * angle))
			mid = Vector2(start.x + (0.5 * deltaX) - (offset * deltaY / distance), start.y + (0.5 * deltaY) + (offset * deltaX / distance))
			# mid = (start[0] + (0.5 * deltaX), start[1] + (0.5 * deltaY))

			# addTack(start, mid, width, layer)
			# addTack(mid, end, width, layer)

			track = pcbnew.PCB_ARC(pcb)
			track.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(float(initialX + start.x)), pcbnew.FromMM(float(initialY + start.y))))
			track.SetMid(pcbnew.VECTOR2I(pcbnew.FromMM(float(initialX +mid.x)), pcbnew.FromMM(float(initialY + mid.y))))
			track.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(float(initialX +end.x)), pcbnew.FromMM(float(initialY + end.y))))
			track.SetWidth(pcbnew.FromMM(float(width)))  # type: ignore
			track.SetLayer(layer)
			pcb.Add(track)
		else:
			print(f"Can't add curve with radius '{np.abs(radius)}' between points '{start}' and '{end}'")

	print("Start Placing")
	
	# for t in pcb.GetTracks():
    # 	pcb.Delete(t)

	hexPositions, subHexRadius = GenerateHexPositions(boardRadius, ledRadius)

	inputPinOffset = Vector2(2.45, -1.6)
	outputPinOffset = Vector2(-2.45, 1.6)
	powerPinOffset = Vector2(-2.45, -1.6)
	groundPinOffset = Vector2(2.45, 1.6)

	tan30 = np.tan(30 / 180 * np.pi)
	cos30 = np.cos(30 / 180 * np.pi)
	sin30 = np.sin(30 / 180 * np.pi)

	# Edge power rails
	powerRailRadius = boardRadius - 2.0
	powerRailX = powerRailRadius * cos30
	powerRailY = powerRailRadius * sin30
	addTrack(Vector2(powerRailX, powerRailY), Vector2(powerRailX, -powerRailY), 0.5, pcbnew.F_Cu)
	addTrack(Vector2(powerRailX, -powerRailY), Vector2(0.0, -powerRailRadius), 0.5, pcbnew.F_Cu)
	addTrack(Vector2(0.0, powerRailRadius), Vector2(-powerRailX, powerRailY), 0.5, pcbnew.F_Cu)
	addTrack(Vector2(-powerRailX, powerRailY), Vector2(-powerRailX, -powerRailY), 0.5, pcbnew.F_Cu)

	for i, hexPos in enumerate(hexPositions):
		pos = hexPos.GetHexXYPos(subHexRadius)
		try:
			nPart = pcb.FindFootprintByReference(f"D{i + 1}")
			nPart.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(float(initialX + pos.x)), pcbnew.FromMM(float(initialY + pos.y))))  # Update XY
			nPart.SetOrientationDegrees(0)
			# nPart.SetOrientationDegrees(-alpha * 180.0 / np.pi)
		except Exception as e:
			print(f"Failed to place 'D{i + 1}' with error '{e}'")
		
		# Connection to power rails
		s = - hexPos.q - hexPos.r
		print(hexPositions[i], s)
		if hexPos.q == ledRadius:
			start = pos + groundPinOffset
			addTrack(start, Vector2(powerRailX, start.y - ((powerRailX - start.x) * tan30)), 0.5, pcbnew.F_Cu)
		elif hexPos.r == -ledRadius:
			addTrack(pos + groundPinOffset, Vector2(0.5 * powerRailX, pos.y), 0.5, pcbnew.F_Cu)
		elif hexPos.q == -ledRadius:
			start = pos + powerPinOffset
			addTrack(start, Vector2(-powerRailX, start.y + ((powerRailX + start.x) * tan30)), 0.5, pcbnew.F_Cu)
		elif hexPos.r == ledRadius:
			addTrack(pos + powerPinOffset, Vector2(-0.5 * powerRailX, pos.y), 0.5, pcbnew.F_Cu)

		if i != len(hexPositions) - 1:
			hexPos2 = hexPositions[i + 1]
			pos2 = hexPos2.GetHexXYPos(subHexRadius)
			if pos.x < pos2.x:
				xDelta = pos2.x - pos.x
				yDelta = pos2.y - pos.y
				addTrack(pos + powerPinOffset, pos2 + powerPinOffset, 0.5, pcbnew.F_Cu)
				addTrack(pos + groundPinOffset, pos2 + groundPinOffset, 0.5, pcbnew.F_Cu)
				offset = (1.5 / tan30) - 2.45
				addTrack(pos + Vector2(-2.45, 1.6), pos + Vector2(offset, 0), 0.2, pcbnew.F_Cu)
				addTrack(pos + Vector2(offset, 0), pos + Vector2(2.45, 0), 0.2, pcbnew.F_Cu)
				xSize = xDelta - 4.9 - 2.45
				addTrack(pos + Vector2(2.45, 0), pos2 + Vector2(-4.9, -yDelta - (xSize * tan30)), 0.2, pcbnew.F_Cu)
				offset2 = (4.9 + offset) * tan30
				addTrack(pos2 + Vector2(-4.9, -yDelta - (xSize * tan30)), pos2 + Vector2(-4.9, -1.6 + offset2), 0.2, pcbnew.F_Cu)
				addTrack(pos2 + Vector2(-4.9, -1.6 + offset2), pos2 + Vector2(offset, -1.6), 0.2, pcbnew.F_Cu)
				addTrack(pos2 + Vector2(offset, -1.6), pos2 + Vector2(2.45, -1.6), 0.2, pcbnew.F_Cu)
				
	pcbnew.Refresh()
	print('Finished Place')

if __name__ == "__main__":
	PlaceComponents()
	