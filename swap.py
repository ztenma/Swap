#!/usr/bin/env python3
# -*- coding: Utf-8 -*-

"""
Swap

A puzzle game with a grid of blocks. Form associations of blocks by
swapping blocks to destroy them!

Modes:

Survival
Battle vs CPU/Human
	Stamina (life bar)
	Projectile (throw blocks to opponent)

"""

import sys
from random import randrange
import time
import itertools

RESET_COLOR = '\033[0m'
FG_DCOLORS = ['\033[90m', '\033[91m', '\033[93m', '\033[94m', '\033[92m', '\033[95m', '\033[96m']
BG_LCOLORS = ['\033[40m', '\033[101m', '\033[103m', '\033[104m', '\033[102m', '\033[105m', '\033[106m']
BG_DCOLORS = ['\033[40m', '\033[41m', '\033[43m', '\033[44m', '\033[42m', '\033[45m', '\033[46m']
fgcolors = lambda i: FG_DCOLORS[i] if i < 7 else '\033[97m'
bgcolors = lambda i: BG_DCOLORS[i] if i < 7 else '\033[97m'
SCORES = [10, 100, 500, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000]
scoreIt = lambda x: SCORES[x-3] if x <= 10 else 0#10 ** ((x-2)

class Grid(object):

	def __init__(self, width=None, height=None, nbSymbols=5, data=None):
		"""nbSymbols includes 0 (no block)"""
		if data:
			assert len(data) >= 3 and len(data[0]) >= 3, 'grid too small!'
			self.width = len(data)
			self.height = len(data[0])
			self.nbSymbols = nbSymbols
			self._grid = data
		else:
			assert width >= 3 and height >= 3, 'grid too small!'
			self.width = width
			self.height = height
			self.nbSymbols = nbSymbols
			self._grid = [[0 for _ in range(self.height)] for _ in range(self.width)]
			self.generate()

	def __getitem__(self, pos):
		if not hasattr(pos, '__getitem__'): return self._grid[pos]
		return self._grid[pos[0]][pos[1]]

	def __setitem__(self, pos, val):
		if not hasattr(pos, '__getitem__'): self._grid[pos] = val
		self._grid[pos[0]][pos[1]] = val

	def __repr__(self):
		return self.displayBlocks()
		#return '\n'.join(' '.join(map(str, (self._grid[i][j] for i in range(self.width)))) for j in range(self.height)) + '\n'

	def displayDigits(self):
		"""Return a string represeting grid, with digits and colors"""
		return (RESET_COLOR + '\n').join(' '.join(fgcolors(self._grid[i][j]) + \
		str(self._grid[i][j]) for i in range(self.width)) + ' '\
		for j in range(self.height)) + (RESET_COLOR + '\n')

	def displayBlocks(self):
		"""Return a string represeting grid, with colors blocks"""
		return (RESET_COLOR + '\n').join(''.join(bgcolors(self._grid[i][j]) + '  '\
		for i in range(self.width)) for j in range(self.height)) + (RESET_COLOR + '\n')

	def generate(self):
		"""Generate a valid grid"""
		for x in range(self.width):
			for y in reversed(range(randrange(self.height) + 1, self.height)):
				self._grid[x][y] = self.genBlock(x, y)

	def genBlock(self, x:int, y:int):
		"""Generate a random block based on neighbour blocks"""
		rand = randrange(1, self.nbSymbols)
		while (y <= self.height - 3 and self[x][y+1] == self[x][y+2] == rand) \
		or (x >= 2 and self[x-1][y] == self[x-2][y] == rand):
			rand = randrange(1, self.nbSymbols)
		return rand

	def swap(self, x:int, y:int):
		"""Swap two blocks horizontally"""
		self[x][y], self[x+1][y] = self[x+1][y], self[x][y]

	def fallInstant(self, focusX=None):
		"""Make blocks fall instantly"""
		for x in ((focusX, focusX+1) if focusX != None else range(self.width)):
			for y in reversed(range(self.height)):
				while self[x][y] == 0 and any(self[x][j] != 0 for j in range(y)):
					for j in reversed(range(y)):
						self[x][j+1] = self[x][j]
					self[x][j] = 0

	def fallStep(self, focusX=None):
		"""Make blocks fall one step, return whether it was the last step of fall"""
		isLastStep = True
		for x in ((focusX, focusX+1) if focusX != None else range(self.width)):
			for y in reversed(range(self.height)):
				if self[x][y] == 0 and any(self[x][j] != 0 for j in range(y)):
					for j in reversed(range(y)):
						self[x][j+1] = self[x][j]
					self[x][j] = 0
					if any(self[x][j] != 0 for j in range(y)):
						isLastStep = False
					break
		return isLastStep

	def __testComboLine(self, y):
		"""Look for combos in line and return them"""
		combos = []
		comboCount = 1

		#print('line:', [self[i][y] for i in range(self.width)])
		# Iterate through line
		for x in range(self.width):
			ref = self[x][y]
			#print('({},{}) ref {} xcombo {}'.format(x, y, ref, comboCount))
			if ref != 0 and x >= 1 and ref == self[x-1][y]:
				comboCount += 1
			if self[x-1][y] != ref:
				if comboCount >= 3:
					combos.append([(i, y) for i in range(x-comboCount, x)])
				comboCount = 1
			if x == self.width - 1 and comboCount >= 3:
				combos.append([(i, y) for i in range(x-comboCount+1, x+1)])
		return combos

	def __testComboColumn(self, x):
		"""Look for combos in column and return them"""
		combos = []
		comboCount = 1

		#print('column:', [self[x][j] for j in range(self.height)])
		# Iterate through column
		for y in range(self.height):
			ref = self[x][y]
			#print('({},{}) ref {} ycombo {}'.format(x, y, ref, comboCount))
			if ref != 0 and y >= 1 and ref == self[x][y-1]:
				comboCount += 1
			if ref != self[x][y-1]:
				if comboCount >= 3:
					combos.append([(x, j) for j in range(y-comboCount, y)])
				comboCount = 1
			if y == self.height - 1 and comboCount >= 3:
				combos.append([(x, j) for j in range(y-comboCount+1, y+1)])
		return combos

	def testComboSwap(self, x, y):
		"""Test existance of combos at the designated swap position
Return set of positions of blocks combinated"""
		combos = []

		combos.extend(self.__testComboLine(y))
		combos.extend(self.__testComboColumn(x))
		combos.extend(self.__testComboColumn(x+1))

		return combos

	def testComboAll(self):
		"""Test existance of combos in the whole grid
Return set of positions of blocks combinated"""
		combos = []

		for x in range(self.width):
			combos.extend(self.__testComboColumn(x))

		for y in range(self.height):
			combos.extend(self.__testComboLine(y))

		return combos

def rotateMatrix(mat):
	w, h = len(mat), len(mat[0])
	return [[mat[y][x] for y in range(w)] for x in range(h)]


def test1():
	_grid = rotateMatrix(\
	[[3, 4, 2, 2, 3, 4],
	[3, 0, 1, 4, 0, 3],
	[3, 2, 0, 2, 0, 3],
	[1, 1, 0, 2, 4, 3]])
	grid = Grid(data=_grid, nbSymbols=5)
	print('init\n' + str(grid))
	pos = (2, 1)

	grid.fallInstant()
	print('fallInstant\n' + str(grid))
	grid.swap(*pos)
	print('swap 2,1\n' + str(grid))
	grid.fallInstant(pos[0])
	print('fallInstant\n' + str(grid))

	combos = grid.testComboAll()
	combosPos = set(itertools.chain.from_iterable(combos))
	for pos in combosPos: # Remove combos
		grid[pos] = 0
	print('testCombo {}:'.format(pos), combos, '\n' + str(combosPos), len(combosPos), '\n' + str(grid))

	grid.fallInstant()
	print('fallInstant\n' + str(grid))

def test2():
	grid = Grid(data=[[randrange(4) for _ in range(20)] for _ in range(40)], nbSymbols=4)
	#grid = Grid(40, 20, 4)
	print('init\n' + str(grid))

	score, scoreMultiplier = 0, 1
	combos = True
	while combos:
		lastStep = grid.fall(step=True)
		print('fallStep', lastStep, '\n' + str(grid))
		print('score:', score)
		time.sleep(.2)
		if not lastStep: continue

		combos = grid.testComboAll()
		combosPos = set(itertools.chain.from_iterable(combos))
		#print(combos, combosPos)
		if combos:
			for combo in combos:
				score += scoreIt(len(combo)) * scoreMultiplier
				#print(len(combo), scoreIt(len(combo)), end=' ')
			#print()
			scoreMultiplier += 1
			for pos in combosPos: # Remove combos
				grid[pos] = 0
			print('testComboAll:', combos, '\n' + str(combosPos), len(combosPos), '\n' + str(grid))
			time.sleep(1)

def test3():
	_grid = rotateMatrix([
[1,1,0,1,2,0,3,2,1,1,0,1,3,0,1,0,1,3,2,3,2,0,1,0,1,1,0,1,3,0,0,0,0,0,0,0,3,1,0,3],
[0,0,1,1,0,3,1,3,0,0,0,2,0,3,3,3,2,1,0,0,1,3,2,3,2,0,3,2,1,2,1,1,2,1,3,1,2,3,0,0],
[3,3,0,3,0,1,2,1,3,3,2,1,2,3,1,1,0,3,0,1,2,0,2,1,0,2,1,1,0,2,0,3,0,1,1,3,1,3,2,2],
[2,3,0,2,1,3,3,0,1,0,1,0,1,0,3,1,1,0,3,0,0,0,0,1,3,3,3,2,2,2,0,2,1,0,3,3,2,0,1,3],
[0,1,0,3,0,0,2,0,0,3,0,3,0,0,2,1,0,0,2,0,2,3,3,3,1,0,3,0,1,3,1,2,3,1,2,1,0,2,2,3],
[3,1,3,1,2,0,2,3,3,1,3,0,3,1,0,3,1,0,3,3,3,2,0,1,2,2,0,1,2,3,0,1,0,2,2,0,2,0,0,0],
[2,2,3,2,0,0,0,1,3,0,3,1,1,0,2,0,2,1,3,2,3,1,3,2,3,3,3,0,3,1,3,0,3,1,1,1,1,0,2,0],
[3,3,3,0,0,1,1,2,1,1,2,2,1,0,2,2,0,1,0,0,2,0,2,3,2,3,1,1,0,1,1,3,1,2,0,1,2,2,0,1],
[1,2,1,3,2,0,2,0,1,2,0,0,0,2,3,1,2,2,1,3,2,0,1,3,2,2,2,1,0,1,3,1,0,3,1,1,3,2,2,0],
[0,2,2,2,1,1,0,2,1,1,1,3,2,3,1,2,3,0,3,1,0,1,3,3,1,2,1,2,0,0,3,2,3,0,0,2,2,1,1,1],
[0,3,2,3,0,0,2,3,0,1,1,0,3,0,0,1,1,3,1,0,1,2,0,1,2,2,2,3,3,1,3,2,3,3,2,0,1,2,0,2],
[2,1,0,3,1,0,3,0,0,1,3,1,0,1,0,2,0,0,1,2,2,2,2,3,2,3,1,1,2,3,0,2,2,0,3,2,0,0,2,2],
[3,0,3,1,0,3,2,0,3,1,2,2,3,3,2,1,2,2,3,2,0,3,2,2,3,1,2,2,0,2,3,2,1,2,0,0,0,1,3,0],
[1,2,0,0,0,0,1,2,1,0,3,3,1,0,2,1,1,2,1,2,0,3,1,2,3,1,3,2,3,0,3,0,0,2,2,3,1,2,3,2],
[1,0,1,0,2,2,0,0,1,1,0,3,3,3,2,2,3,0,1,2,0,0,3,0,2,0,1,3,1,2,3,3,0,3,0,0,1,2,1,2],
[0,0,2,1,3,1,2,3,0,2,1,0,3,1,0,3,3,2,0,0,1,2,3,0,3,2,3,3,1,1,1,0,2,1,2,1,0,2,1,3],
[3,3,3,0,0,1,0,2,0,2,1,3,1,1,3,3,1,0,2,0,3,2,3,0,1,2,0,0,0,1,0,0,2,3,3,2,1,1,0,2],
[1,0,3,1,1,0,1,0,2,3,1,2,3,1,1,2,2,2,1,3,3,1,1,3,1,1,0,2,3,3,3,3,0,1,3,0,1,1,3,0],
[2,1,3,1,2,1,2,1,3,0,3,2,3,1,2,2,0,1,1,1,1,1,1,2,1,3,1,2,3,3,2,0,2,3,2,2,0,3,3,1],
[1,2,3,1,2,1,1,3,0,0,1,0,1,0,1,1,2,1,2,0,0,1,2,2,0,1,1,3,2,3,1,3,2,1,3,2,1,3,2,3]
])
	grid = Grid(data=_grid, nbSymbols=4)
	print('init\n' + str(grid))
	return grid

if __name__ == '__main__':
	#print("\033[104mkuro\033[00mmatsu")
	test2()
