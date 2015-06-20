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
SCORES = [10, 100, 500, 2000, 5000, 10000, 15000, 20000]
scoreIt = lambda x: SCORES[x-3] #10 ** ((x-2)

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

	# Return a string represeting grid, with digits and colors
	def displayDigits(self):
		return (RESET_COLOR + '\n').join(' '.join(fgcolors(self._grid[i][j]) + \
		str(self._grid[i][j]) for i in range(self.width)) + ' '\
		for j in range(self.height)) + (RESET_COLOR + '\n')

	# Return a string represeting grid, with colors blocks
	def displayBlocks(self):
		return (RESET_COLOR + '\n').join(''.join(bgcolors(self._grid[i][j]) + '  '\
		for i in range(self.width)) for j in range(self.height)) + (RESET_COLOR + '\n')

	# Generate a valid grid
	def generate(self):
		for x in range(self.width):
			for y in reversed(range(randrange(self.height) + 1, self.height)):
				self._grid[x][y] = self.genBlock(x, y)

	# Generate a random block based on neighbour blocks
	def genBlock(self, x:int, y:int):
		rand = randrange(1, self.nbSymbols)
		while (y <= self.height - 3 and self[x][y+1] == self[x][y+2] == rand) \
		or (x >= 2 and self[x-1][y] == self[x-2][y] == rand):
			rand = randrange(1, self.nbSymbols)
		return rand

	# Swap two blocks horizontally
	def swap(self, x:int, y:int):
		self[x][y], self[x+1][y] = self[x+1][y], self[x][y]

	# Make blocks fall instantly
	def fallInstant(self, focusX=None):
		for x in ((focusX, focusX+1) if focusX != None else range(self.width)):
			for y in reversed(range(self.height)):
				if self[x][y] == 0:
					#print('zéro: ({},{})'.format(x, y), 'col:', [self[x][j] for j in range(self.height)])
					while self[x][y] == 0 and not all(self[x][j] == 0 for j in range(y)):
						for j in reversed(range(y)):
							self[x][j+1] = self[x][j]
							#print('move:', self[x][j2])
						self[x][j] = 0#genBlock(x, y)
					#print('->', [self[x][j] for j in range(self.height)])

	# Make blocks fall one step, return whether it was the last step of fall
	def fallStep(self, focusX=None):
		isLastStep = True
		for x in ((focusX, focusX+1) if focusX != None else range(self.width)):
			for y in reversed(range(self.height)):
				if self[x][y] == 0 and any(self[x][j] != 0 for j in range(y)):
					#print('zéro: ({},{})'.format(x, y), 'col:', [self[x][j] for j in range(self.height)])
					for j in reversed(range(y)):
						self[x][j+1] = self[x][j]
						#print('move:', self[x][j2])
					self[x][j] = 0
					if any(self[x][j] != 0 for j in range(y)):
						isLastStep = False
					break
				#print('->', [self[x][j] for j in range(self.height)])
		return isLastStep

	# Test existance of combos at the designated swap position
	# Return set of positions of blocks combinated
	"""def testCombo(self, x, y): # TODO
		ref = self[x][y]
		if ref == 0: continue
		print('ref:', ref)

		comboPos = set()
		comboCount = 1
		# Iterate through line
		print('line:', [self[i][y] for i in range(self.width)])
		for i in range(self.width):
			print('({0},{1}): {2} c{3}'.format(i, y, self[i][y], comboCount), end='\n')
			if self[i][y] == ref:
				comboCount += 1
			if i == self.width - 1 or self[i+1][y] != ref:
				if comboCount >= 3:
					print('blocks:', [(k, y) for k in range(i+1-comboCount, i+1)])
					comboPos.update([(k, y) for k in range(i+1-comboCount, i+1)])
				break

		comboCount = 1
		# Iterate through column
		print('column:', self[x][:])
		for j in range(self.height):
			print('({0},{1}): {2} c{3}'.format(x, j, self[x][j], comboCount), end='\n')
			if self[x][j] == ref:
				comboCount += 1
			if j == self.height - 1 or self[x][j+1] != ref:
				if comboCount >= 3:
					print('blocks:', [(x, k) for k in range(j+1-comboCount, j+1)])
					comboPos.update([(x, k) for k in range(j+1-comboCount, j+1)])
				break

		return comboPos"""

	# Test existance of combos in the whole grid
	# Return set of positions of blocks combinated
	def testComboAll(self):
		comboCount = 1
		combos = []

		for x in range(self.width):
			for y in range(self.height):
				ref = self[x][y]
				if ref == 0: continue

				#print('({},{}) ref {} ycombo {}'.format(x, y, ref, comboCount))
				if y >= 1 and ref == self[x][y-1]:
					comboCount += 1
				if ref != self[x][y-1]:
					if comboCount >= 3:
						blocks = [(x, j) for j in range(y-comboCount, y)]
						#print('blocks:', blocks)
						combos.append(blocks)
						#print('ycombo:', comboCount)
					comboCount = 1
				if y == self.height - 1 and comboCount >= 3:
					blocks = [(x, j) for j in range(y-comboCount+1, y+1)]
					#print('blocks:', blocks)
					combos.append(blocks)

			comboCount = 1

		for y in range(self.height):
			for x in range(self.width):
				ref = self[x][y]
				if ref == 0: continue

				#print('({},{}) ref {} xcombo {}'.format(x, y, ref, comboCount))
				if x >= 1 and ref == self[x-1][y]:
					comboCount += 1
				if self[x-1][y] != ref:
					if comboCount >= 3:
						blocks = [(i, y) for i in range(x-comboCount, x)]
						#print('blocks:', blocks)
						combos.append(blocks)
						#print('xcombo:', comboCount)
					comboCount = 1
				if x == self.width - 1 and comboCount >= 3:
					blocks = [(i, y) for i in range(x-comboCount+1, x+1)]
					#print('blocks:', blocks)
					combos.append(blocks)
			comboCount = 1

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

	grid.fallInstant()
	print('fallInstant\n' + str(grid))
	grid.swap(2, 1)
	print('swap 2,1\n' + str(grid))
	grid.fallInstant(2)
	print('fallInstant\n' + str(grid))

def test2():
	_grid = [[randrange(3) for _ in range(20)] for _ in range(40)]
	grid = Grid(data=_grid, nbSymbols=3)
	#grid = Grid(40, 20, 6)
	print('init\n' + str(grid))
	input()

	score = 0
	combos = True
	while combos:
		lastStep = grid.fallStep()
		print('fallStep', lastStep, '\n' + str(grid))
		print(score)
		#input()
		time.sleep(.5)
		if not lastStep: continue

		combos = grid.testComboAll()
		combosPos = set(itertools.chain.from_iterable(combos))
		print(combos, combosPos)
		if combos:
			for combo in combos:
				score += scoreIt(len(combo))
				print(len(combo), scoreIt(len(combo)), end=' ')
			print()
			for pos in combosPos: # Remove combos
				grid[pos] = 0
			print('testCombo1All:', combos, '\n' + str(combosPos), len(combosPos), '\n' + str(grid))
			time.sleep(.5)

if __name__ == '__main__':
	#print("\033[104mkuro\033[00mmatsu")
	test2()
