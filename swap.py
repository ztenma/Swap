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
from time import time, sleep, strftime
import itertools

import logging
logging.basicConfig(filename='swap.log', filemode='w', level=logging.DEBUG, \
format='%(message)s')
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def timestamp():
	return strftime('%H:%M:%S') + "." + str(time()).split('.')[1][:2]
def DEBUG(msg, *args): logger.debug(timestamp() + " " + msg, *args)
def INFO(msg, *args): logger.info(timestamp() + " " + msg, *args)
def WARN(msg, *args): logger.warning(timestamp() + " " + msg, *args)
def ERROR(msg, *args): logger.error(timestamp() + " " + msg, *args)

try:
	from collections.abc import Sequence, MutableSequence
	print("Imported collections.abc")
except ImportError:
	from collections import Sequence, MutableSequence
	print("Imported collections")

RESET_COLOR = '\033[0m'
FG_DCOLORS = ['\033[90m', '\033[91m', '\033[93m', '\033[94m', '\033[92m', '\033[95m', '\033[96m']
# bg colors order: black, red, yellow(=brown), blue, green, magenta, cyan
BG_LCOLORS = ['\033[40m', '\033[101m', '\033[103m', '\033[104m', '\033[102m', '\033[105m', '\033[106m']
BG_DCOLORS = ['\033[40m', '\033[41m', '\033[43m', '\033[44m', '\033[42m', '\033[45m', '\033[46m']
fgcolors = lambda i: FG_DCOLORS[i] if i < 7 else '\033[97m'
bgcolors = lambda i: BG_DCOLORS[i] if i < 7 else '\033[97m'
SCORES = [2, 5, 20, 80, 200, 500, 1000, 2000, 4000, 6000, 8000, 10000]
scoreIt = lambda x: SCORES[x-3] if x <= 10 else 0

class Game(object):

	def __init__(self):
		self.grid = Grid(15, 20, 4)

		self.state = StateMachine()
		self.state.transition("IA_swap", 2)
		self.lastTime = time()
		self.pause = False

		self.swapperPos = (0, 0)

		self.score = 0
		self.scoreMultiplier = 1

		INFO("Starting Swap")

	# TODO: vérifier actions différées (combos, etc) existent encore avant réalisation
	def update(self):

		currentTime = time()
		dt = currentTime - self.lastTime
		self.lastTime = currentTime

		if self.pause: return

		DEBUG("State %s", self.state.crepr())

		for stateName in tuple(self.state.keys()):

			if stateName == "IA_swap":
				if self.state["IA_swap"].status == "starting":
					#DEBUG("IA_swap/")
					self.swapperPos = self.randomSwapChoice()#randrange(self.grid.width-1), randrange(self.grid.height-1)
				elif self.state["IA_swap"].status == "ending":
					#DEBUG("IA_swap\\")
					self.grid.swap(*self.swapperPos)
					if "fall" not in self.state:
						self.state.transition("fall", .2)
					self.state.transition("IA_swap", 2)

			elif stateName == "fall":
				#DEBUG("Falling %s", "{:.2f}/{:.2f}".format(\
				#	self.state[stateName].elapsedTime, self.state[stateName].duration))
				if self.state["fall"].status == "ending":
					#DEBUG("fall\\")
					isLastStep = self.grid.fallStep()
					if isLastStep:
						comboGroup = self.grid.testComboAll()
						if comboGroup:
							comboNb = sum(1 for name in self.state if name.startswith("combo#"))
							comboGroups = list(self.state[name].data for name in self.state if name.startswith("combo#"))
							#DEBUG("Combo groups %s in %s", comboGroup, comboGroups)
							if not comboGroup in comboGroups:
								self.state.transition("combo#" + str(comboNb), 1, comboGroup)
						else:
							self.scoreMultiplier = 1
						self.state.delete("fall")
					else:
						self.state.transition("fall", .1)

			elif stateName.startswith("combo#"):
				if self.state[stateName].status == "ending":
					#DEBUG("%s\\", stateName)
					#DEBUG("Combos %s\n%s", stateName, self.state[stateName].data)
					endComboGroup = self.grid.testComboAll()
					startComboGroup = self.state[stateName].data

					# TODO: tests
					comboGroup = updateComboGroupLazy(startComboGroup, endComboGroup)
					comboGroupPos = set(itertools.chain.from_iterable(comboGroup))

					for combo in comboGroup:
						self.score += scoreIt(len(combo)) * self.scoreMultiplier
					self.scoreMultiplier += 1
					#DEBUG("Score multiplier %s", self.scoreMultiplier)

					for pos in comboGroupPos: # Remove combos
						self.grid[pos] = 0
					#self.processCombos(self.state[stateName].data)
					self.state.delete(stateName)

		self.state.update(dt)

	def processCombos(self, comboGroup):
		for combo in comboGroup:
			self.score += scoreIt(len(combo)) * self.scoreMultiplier
		self.scoreMultiplier += 1
		#DEBUG("Score multiplier %s", self.scoreMultiplier)
		comboGroupPos = set(itertools.chain.from_iterable(comboGroup))
		for pos in comboGroupPos: # Remove combos
			self.grid[pos] = 0

	def randomSwapChoice(self):
		return self.grid.getRandomSwap()

def updateComboGroupLazy(comboGroup1, comboGroup2):
	"""Computes the final combo group based on combo state start and end, using
	the lazy startegy.

	Lazy:
	include any combo from start state that remains in end state"""

	comboGroup3 = []

	for combo2 in comboGroup2:
		if combo2 in comboGroup1:
			comboGroup3.append(combo2)
	return comboGroup3

def updateComboGroupMorph(comboGroup1, comboGroup2): # TODO: extensive tests
	"""Computes the final combo group based on combo state start and end, using
	the morph startegy.

	Morph:
	- compute the difference between the two sets of combo positions,
	- include any combo from end state that has at least one position in common
	with the difference set"""

	# We compute the lists of blocks involved in each combo group
	comboPos1 = set(itertools.chain.from_iterable(comboGroup1))
	comboPos2 = set(itertools.chain.from_iterable(comboGroup2))
	diffPos = comboPos1.intersection(comboPos2)
	DEBUG("cp: %s %s", comboPos1, comboPos2)
	DEBUG("diffPos: %s", diffPos)
	comboGroup3 = []

	for combo2 in comboGroup2:
		for pos in diffPos:
			if pos in combo2:
				comboGroup3.append(combo2)
	return comboGroup3

class StateMachine(dict):
	"""Represents a dynamic concurrent state machine"""

	def __init__(self):
		dict.__init__(self)

	def transition(self, toStateName, duration=None, data=None, fromStateName=None):
		"""Transition to another state. If specified, it replaces the state
		named fromStateName."""
		if fromStateName:
			del self[fromStateName]
		self[toStateName] = State(duration, data)
		#DEBUG("Transition\n%s", repr(self))

	def delete(self, stateName):
		"""Delete a state"""
		del self[stateName]

	def update(self, dt):
		"""Update all the states in the machine"""

		for state in self.values():
			if state.elapsedTime != None and state.elapsedTime + dt >= state.duration:
				state.status = "ending"
			elif state.status == "starting" and state.elapsedTime != 0:
				state.status = "ongoing"

			if state.elapsedTime is not None:
				state.elapsedTime += dt

		#DEBUG("Update\n%s", repr(self))

	def crepr(self, onlyChanging=False):
		"""A compact representation"""
		shortenStatus = lambda s: {'starting': '/', 'ongoing': '', 'ending': '\\'}[s]
		isChanging = lambda s: self[s].status in ("starting", "ending")
		if not onlyChanging: return '{' + ', '.join("{}{}".format(name, shortenStatus(self[name].status)) for name in self) + '}'
		return '{' + ', '.join("{}{}".format(name, shortenStatus(self[name].status)) for name in self if isChanging(name)) + '}'

	def vcrepr(self, onlyChanging=False):
		"""A very compact representation"""
		shortenName = lambda s: {'debug': 'D ', 'IA_swap': 'S ', 'fall': 'F ', 'combo': 'C '}[s.split('#')[0]]
		isChanging = lambda s: self[s].status in ("starting", "ending")
		if not onlyChanging: return ''.join("{}".format(shortenName(name)) for name in self)
		return ''.join("{}".format(shortenName(name)) for name in self if isChanging(name))

	def trepr(self):
		"""A representation of progression of states"""
		return '[' + ', '.join("{} {:.2f}/{:.2f}".format(name,
			self[name].elapsedTime, self[name].duration) for name in self) + ']'

class State(object):
	"""Represents a game state

A state can have finite or infinite duration (None value).
A status attribute describe whether the state is starting, ongoing or ending.
If necessary, data can be stored for the purpose of state logic."""

	def __init__(self, duration=None, data=None):
		self.status = "starting" # One of "starting", "ongoing", "ending"
		self.duration = duration
		self.elapsedTime = 0
		self.data = data # Data conveyed by the state

	def __repr__(self):
		return "State({self.status},{self.elapsedTime:.2f}/{self.duration:.2f},{self.data})".format(self=self)

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
		return self.reprBlocks()
		#return '\n'.join(' '.join(map(str, (self._grid[i][j] for i in range(self.width)))) for j in range(self.height)) + '\n'

	def reprDigits(self, color=True):
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

	def testComboLine(self, y):
		"""Look for combos in line and return them"""
		comboGroup = []
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
					combo = Combo([(i, y) for i in range(x-comboCount, x)], self[x-1][y])
					comboGroup.append(combo)
				comboCount = 1
			if x == self.width - 1 and comboCount >= 3:
				combo = Combo([(i, y) for i in range(x-comboCount+1, x+1)], ref)
				comboGroup.append(combo)
		return comboGroup

	def testComboColumn(self, x):
		"""Look for combos in column and return them"""
		comboGroup = []
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
					combo = Combo([(x, j) for j in range(y-comboCount, y)], self[x][y-1])
					comboGroup.append(combo)
				comboCount = 1
			if y == self.height - 1 and comboCount >= 3:
				combo = Combo([(x, j) for j in range(y-comboCount+1, y+1)], ref)
				comboGroup.append(combo)
		return comboGroup

	def testComboSwap(self, x, y):
		"""Test existance of combos at the designated swap position
Return set of positions of blocks combinated"""
		comboGroup = []

		comboGroup.extend(self.testComboLine(y))
		comboGroup.extend(self.testComboColumn(x))
		comboGroup.extend(self.testComboColumn(x+1))

		return comboGroup

	def testComboAll(self):
		"""Test existance of combos in the whole grid
Return set of positions of blocks combinated"""
		comboGroup = []

		for x in range(self.width):
			comboGroup.extend(self.testComboColumn(x))

		for y in range(self.height):
			comboGroup.extend(self.testComboLine(y))

		return comboGroup

	def getRandomBlock(self):
		totalBlockNb = sum(block != 0 for col in self for block in col)
		chosenBlock = randrange(totalBlockNb)
		curBlock = -1
		for x in range(self.width):
			for y in range(self.height):
				if self[x][y] != 0:
					curBlock += 1
				if curBlock == chosenBlock:
					return (x, y)

	def getRandomSwap(self):
		randX, randY = self.getRandomBlock()
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
		assert isinstance(blockList, Sequence), "blockList must be a sequence"
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

	def __eq__(self, other): return self.blockList == other.blockList and self.color == other.color
	def __repr__(self):
		return "Combo({}, ".format(self.color) + repr(self.blockList) + ')'

if __name__ == '__main__':
	pass
