#!/usr/bin/env python3

"""Grid for Swap"""

import sys
from random import randrange
from itertoolsExt import indexFalse
try:
	from collections.abc import Sequence, MutableSequence
except ImportError:
	from collections import Sequence, MutableSequence

from log import *

RESET_COLOR = '\033[0m'
FG_DCOLORS = ['\033[90m', '\033[91m', '\033[93m', '\033[94m', '\033[92m', '\033[95m', '\033[96m']
# bg colors order: black, red, yellow(=brown), blue, green, magenta, cyan
BG_LCOLORS = ['\033[40m', '\033[101m', '\033[103m', '\033[104m', '\033[102m', '\033[105m', '\033[106m', '\033[47m']
BG_DCOLORS = ['\033[40m', '\033[41m', '\033[43m', '\033[44m', '\033[42m', '\033[45m', '\033[46m', '\033[47m']
fgcolors = lambda i: FG_DCOLORS[i] if i < 7 else '\033[97m'
bgcolors = lambda i: BG_DCOLORS[i] if i < 7 else '\033[97m'

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
		return self.reprDigits()

	def reprDigits(self, color=False):
		"""Return a string represeting grid, with digits and colors"""
		if color:
			return (RESET_COLOR + '\n').join(' '.join(fgcolors(self._grid[i][j]) + \
			str(self._grid[i][j]) for i in range(self.width)) + ' '\
			for j in range(self.height)) + (RESET_COLOR + '\n')
		else: return '\n'.join(' '.join(str(self._grid[i][j])\
			for i in range(self.width)) + ' ' for j in range(self.height)) + '\n'

	def reprBlocks(self):
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

	def isHole(self, x, y):
		return self[x][y] == 0 and any(self[x][j] != 0 for j in range(y))

	def fallStepPos(self, x, y):
		"""Make blocks above pos fall one step"""
		for j in reversed(range(y)):
			self[x][j+1] = self[x][j]
		self[x][j] = 0

	def fallInstant(self, focusX=None):
		"""Make blocks fall instantly."""
		for x in (focusX if focusX != None else range(self.width)):
			for y in reversed(range(self.height)):
				while self.isHole(x, y):
					self.fallStepPos(x, y)

	def fallStep(self, focusX=None):
		"""Make blocks fall one step, return whether it was the last step of fall"""
		isLastStep = True
		for x in (focusX if focusX != None else range(self.width)):
			for y in reversed(range(self.height)):
				if self.isHole(x, y):
					self.fallStepPos(x, y)
					if any(self[x][j] != 0 for j in range(y)):
						isLastStep = False
					break
		return isLastStep

	def lowerHoles(self, focusX=None):
		holes = []
		for x in (focusX if focusX != None else range(self.width)):
			for y in reversed(range(self.height)):
				if self.isHole(x, y):
					holes.append((x, y))
				if self[x][y] == 0: break # Break at any void in column
		return holes

	def combosLine(self, y):
		"""Look for combos in line and return them"""
		comboGroup = []
		comboCount = 1

		#DEBUG('line:', [self[i][y] for i in range(self.width)])
		# Iterate through line
		for x in range(self.width):
			ref = self[x][y]
			#DEBUG('({},{}) ref {} xcombo {}'.format(x, y, ref, comboCount))
			if ref != 0 and x >= 1 and ref == self[x-1][y]:
				comboCount += 1
			if self[x-1][y] != ref:
				if comboCount >= 3:
					combo = Combo([(i, y) for i in range(x-comboCount, x)], self[x-1][y])
					comboGroup.append(combo)
				comboCount = 1
			if x == self.width - 1 and comboCount >= 3:
				combo = Combo([(i, y) for i in range(x-comboCount+1, x+1)], ref)
				comboGroup.append(combo)
		return comboGroup

	def combosColumn(self, x):
		"""Look for combos in column and return them"""
		comboGroup = []
		comboCount = 1

		#DEBUG('column:', [self[x][j] for j in range(self.height)])
		# Iterate through column
		for y in range(self.height):
			ref = self[x][y]
			#DEBUG('({},{}) ref {} ycombo {}'.format(x, y, ref, comboCount))
			if ref != 0 and y >= 1 and ref == self[x][y-1]:
				comboCount += 1
			if ref != self[x][y-1]:
				if comboCount >= 3:
					combo = Combo([(x, j) for j in range(y-comboCount, y)], self[x][y-1])
					comboGroup.append(combo)
				comboCount = 1
			if y == self.height - 1 and comboCount >= 3:
				combo = Combo([(x, j) for j in range(y-comboCount+1, y+1)], ref)
				comboGroup.append(combo)
		return comboGroup

	def combosAll(self):
		"""Return the list of combos found in the whole grid"""
		comboGroup = []

		for x in range(self.width):
			comboGroup.extend(self.combosColumn(x))

		for y in range(self.height):
			comboGroup.extend(self.combosLine(y))

		return comboGroup

	def blockRangeVerticalAround(self, x, y):
		"""Return the range corresponding to the group of blocks around (x, y).

Return a void range if there is no block at (x, y).
"""
		return range(y+1 - indexFalse(self._grid[x][y::-1]),
			y + indexFalse(self._grid[x][y:]))

	def comboHorizontalAround(self, x, y, minLen=3):

		f = lambda e: bool(e) and e == self._grid[x][y]
		p1 = (e[y] for e in self._grid[x::-1])
		p2 = (e[y] for e in self._grid[x:])
		comboRange = range(x+1 - indexFalse(p1, f), x + indexFalse(p2, f))
		if len(comboRange) >= minLen:
			return Combo([(i, y) for i in comboRange], self._grid[x][y])
		return None

	def comboVerticalAround(self, x, y, minLen=3):

		f = lambda e: bool(e) and e == self._grid[x][y]
		p1 = self._grid[x][y::-1]
		p2 = self._grid[x][y:]
		comboRange = range(y+1 - indexFalse(p1, f), y + indexFalse(p2, f))
		if len(comboRange) >= minLen:
			return Combo([(x, j) for j in comboRange], self._grid[x][y])
		return None

	def combosAfterSwap(self, pos):
		"""Test existance of combos around the designated swap position
Return the group of combos found"""
		x, y = pos
		return list(filter(None,
			[self.comboHorizontalAround(x, y),
			self.comboHorizontalAround(x+1, y),
			self.comboVerticalAround(x, y),
			self.comboVerticalAround(x+1, y)]))

	def combosAfterFall(self, formerHole): # TEST
		"""Test existance of combos around a former hole
Return the list of combos found"""
		x, y = formerHole
		def blocksAroundHole():
			yield self.comboVerticalAround(x, y)
			for j in self.blockRangeVerticalAround(x, y):
				yield self.comboHorizontalAround(x, j)

		r = list(filter(None, blocksAroundHole()))
		DEBUG("Combo after fall: %s %s", self.blockRangeVerticalAround(x, y), r)
		return r

	def randomBlock(self):
		totalBlockNb = sum(block != 0 for col in self for block in col)
		chosenBlock = randrange(totalBlockNb)
		curBlock = -1
		for x in range(self.width):
			for y in range(self.height):
				if self[x][y] != 0:
					curBlock += 1
				if curBlock == chosenBlock:
					return (x, y)

	def randomSwap(self):
		randX, randY = self.randomBlock()
		if randX == 0: return (randX, randY)
		if randX == self.width - 1: return (randX - 1, randY)
		return (randX - randrange(2), randY)

class Block(Sequence):
	"""A tuple-like"""
	def __init__(self, pos, color):
		self.pos = pos
		self.color = color

	def __len__(self): return len(self.pos)
	def __getitem__(self, i): return self.pos[i]

	def __eq__(self, other): return self.pos == other.pos and self.color == other.color
	def __hash__(self): return hash(self.pos)
	def __repr__(self):
		#return str(self.pos)
		return "Block({}, {})".format(self.pos, self.color)
	def __str__(self): return str(self.pos)

class Combo(MutableSequence):
	"""A list-like"""

	def __init__(self, blockList, color=None):
		assert isinstance(blockList, Sequence) and len(blockList) > 0, "blockList must be a non-empty sequence"
		if color != None and color > 0:
			self.blockList = [Block(e, color) for e in blockList]
			self.color = color
		else:
			assert all(isinstance(e, Block) for e in blockList), "if no color argument provided, blockList must be a sequence of Block objects"
			self.blockList = blockList[:]
			self.color = blockList[0].color

	def __len__(self): return len(self.blockList)
	def __getitem__(self, i): return self.blockList[i]
	def __setitem__(self, i, v): self.blockList[i] = v
	def __delitem__(self, i): del self.blockList[i]
	def __iadd__(self, e): self.blockList += e
	def append(self, e): self.blockList.append(e)
	def insert(self, i, e): self.blockList.insert(i, e)

	def __eq__(self, other):
		return isinstance(other, Combo) and self.blockList == other.blockList and self.color == other.color
	def __repr__(self):
		orientation = self.orientation()
		ref = self.blockList[0]
		if orientation == 'v':
			return "C{}({},[{}])".format(self.color, ref[0], ','.join(str(e[1]) for e in self.blockList))
		if orientation == 'h':
			return "C{}([{}],{})".format(self.color, ','.join(str(e[0]) for e in self.blockList), ref[1])
		return "C{}[{}]".format(self.color, ','.join(str(b) for b in self.blockList))

	def orientation(self):
		ref = self.blockList[0]
		if all(e[0] == ref[0] for e in self.blockList[1:]): return 'v'
		if all(e[1] == ref[1] for e in self.blockList[1:]): return 'h'
		return '?'
