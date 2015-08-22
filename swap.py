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
from time import time
from itertoolsExt import flatten

from log import *
from grid import Grid, Combo, Block

SCORES = [2, 5, 20, 80, 200, 500, 1000, 2000, 4000, 6000, 8000]
scoreIt = lambda x: SCORES[x-3] if x <= 10 else 10000

STATES = {'debug': 'D', 'swap': 's', 'AI_swap': 'S', 'fall': 'F', 'combo': 'C'}

class Game(object):

	def __init__(self):
		self.grid = Grid(15, 20, 4)

		self.state = StateMachine()
		self.state.transition("AI_swap", 2) # To enable AI
		self.lastTime = time()
		self.pause = False

		self.swapperPos = (0, 0)

		self.score = 0
		self.scoreMultiplier = 1

		INFO("Starting Swap")

	"""def update(self):

		currentTime = time()
		dt = currentTime - self.lastTime
		self.lastTime = currentTime

		if self.pause: return

		#DEBUG("State %s", self.state.crepr())

		for stateName in tuple(self.state.keys()):

			if stateName == "AI_swap":
				if self.state["AI_swap"].status == "starting":
					self.swapperPos = self.randomSwapChoice()
				elif self.state["AI_swap"].status == "ending":
					self.grid.swap(*self.swapperPos)
					if "fall" not in self.state:
						self.state.transition("fall", .2)
					self.state.transition("AI_swap", .5)

			elif stateName == "fall":
				if self.state["fall"].status == "ending":
					isLastStep = self.grid.fallStep()
					if isLastStep:
						comboGroup = self.grid.getComboAll()
						if comboGroup:
							comboGroups = self.getComboGroups()
							comboNb = len(comboGroups)
							#DEBUG("Combo groups %s in %s", comboGroup, comboGroups)
							if not comboGroup in comboGroups:
								self.state.transition("combo#" + str(comboNb), 1.6, comboGroup)
						else:
							self.scoreMultiplier = 1
						self.state.delete("fall")
					else:
						self.state.transition("fall", .1)

			elif stateName.startswith("combo#"):
				if self.state[stateName].status == "ending":
					#DEBUG("Combos %s\n%s", stateName, self.state[stateName].data)
					endComboGroup = self.grid.getComboAll()
					startComboGroup = self.state[stateName].data

					comboGroup = updateComboGroupMorph(startComboGroup, endComboGroup)
					self.processCombos(comboGroup)

					if "fall" not in self.state:
						self.state.transition("fall", .2)
					self.state.delete(stateName)

		self.state.update(dt)"""

	def update(self): # TODO problème de synchro fall/combo

		currentTime = time()
		dt = currentTime - self.lastTime
		self.lastTime = currentTime

		if self.pause: return

		if any(self.state.isChanging(e) for e in self.state):
			DEBUG("State: %s", self.state.vcrepr())

		for stateName in tuple(self.state.keys()):

			if stateName == "AI_swap":
				if self.state["AI_swap"].status == "starting":
					self.swapperPos = self.randomSwapChoice()
				elif self.state["AI_swap"].status == "ending":
					self.swap()
					self.state.transition("AI_swap", 1.5)

			elif stateName.startswith("fall#"):
				if self.state[stateName].status == "ending":
					pos = self.state[stateName].data
					self.grid.fallStepPos(*pos)
					if self.grid.isHole(*pos):
						self.state.transition(stateName, .2, pos)
					else: # Falling ended
						self.state.delete(stateName)
						sumFalls = sum(1 for name in self.state if name.startswith("fall#"))
						if sumFalls == 0 and not self.checkCombo("fall", pos):
							self.scoreMultiplier = 1

			elif stateName.startswith("combo#"):
				if self.state[stateName].status == "ending":
					#DEBUG("Combos %s\n%s", stateName, self.state[stateName].data)
					endComboGroup = self.grid.getComboAll()
					startComboGroup = self.state[stateName].data

					comboGroup = updateComboGroupLazy(startComboGroup, endComboGroup)
					self.processCombos(comboGroup)

					self.state.delete(stateName)
					self.checkFall()

		self.state.update(dt)

	def checkFall(self, focusX=None): # TODO then rewrite update()
		"""Check whether some blocks have to fall. Return lower holes.

		Creates fall state for each hole found.
		If focusX, then only corresponding columns are checked."""

		lowerHoles = self.grid.getLowerHoles(focusX)
		DEBUG("Lower holes: %s", lowerHoles)
		if lowerHoles:
			for pos in lowerHoles:
				if "fall#" + str(pos[0]) not in self.state:
					self.state.transition("fall#" + str(pos[0]), .2, pos)
		return lowerHoles

	def getComboGroups(self):
		return [self.state[name].data for name in self.state if name.startswith("combo#")]

	def genComboId(self):
		for i in range(100):
			if "combo#" + str(i) not in self.state:
				return i
		raise RuntimeError("Too much combos")

	def checkCombo(self, checkType, pos): # TODO: check if blocks fell
		"""Check whether there are combo above pos. Return combo group.

		Creates combo state."""

		if checkType == "fall":
			comboGroup = self.grid.getComboAfterFall(pos)
		elif checkType == "swap":
			comboGroup = self.grid.getComboAfterSwap(pos)
		else: raise ValueError("Wrong check type: " + str(checkType))

		if comboGroup:
			DEBUG("Initial combo group %s", comboGroup)
			fallingX = [pos[0] for pos in self.grid.getLowerHoles()]
			comboGroup = [combo for combo in comboGroup \
				if not any(cx in fallingX for cx in [cp[0] for cp in combo])]

			comboGroups = self.getComboGroups()
			DEBUG("Combo groups %s not in %s", comboGroup, comboGroups)
			if comboGroup not in comboGroups:
				self.state.transition("combo#" + str(self.genComboId()), 2, comboGroup)
		return comboGroup

	def processCombos(self, comboGroup):
		for combo in comboGroup:
			self.score += scoreIt(len(combo)) * self.scoreMultiplier
			self.scoreMultiplier += 1
		#DEBUG("Score multiplier %s", self.scoreMultiplier)
		comboGroupPos = set(flatten(comboGroup))
		for pos in comboGroupPos: # Remove combos
			self.grid[pos] = 0

	def randomSwapChoice(self):
		return self.grid.getRandomSwap()

	def moveSwapper(self, direction):
		x, y = self.swapperPos
		if direction == 'up': self.swapperPos = (x, max(0, y-1))
		elif direction == 'right': self.swapperPos = (min(x+1, self.grid.width-2), y)
		elif direction == 'down': self.swapperPos = (x, min(y+1, self.grid.height-1))
		elif direction == 'left': self.swapperPos = (max(x-1, 0), y)
		else: raise ValueError("direction must be one of up, right, down, left")

	def swap(self):
		x, y = self.swapperPos
		self.grid.swap(x, y)
		if not self.checkFall([x, x+1]):
			self.checkCombo("swap", (x, y))

	def processInput(self, name):
		if name == "swap": self.swap()
		elif name in ("up", "right", "down", "left"): self.moveSwapper(name)

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

def updateComboGroupMorph(comboGroup1, comboGroup2): # TODO: pas ok
	"""Computes the final combo group based on combo state start and end, using
	the morph startegy.

	Morph:
	- compute the difference between the two sets of combo positions,
	- include any combo from end state that has at least one position in common
	with the difference set"""

	# We compute the lists of blocks involved in each combo group
	comboPos1 = set(flatten(comboGroup1))
	comboPos2 = set(flatten(comboGroup2))
	diffPos = comboPos1.intersection(comboPos2)
	#DEBUG("cp: %s %s", comboPos1, comboPos2)
	#DEBUG("diff pos: %s", diffPos)
	comboGroup3 = []

	for combo2 in comboGroup2:
		for pos in diffPos:
			if pos in combo2:
				comboGroup3.append(combo2)
	DEBUG("morph combo group: %s", comboGroup3)
	return comboGroup3

class StateMachine(dict):
	"""Represents a dynamic concurrent state machine.

	It can hold mutiples states at the same time. States are timed.
	update() update all states statuses."""

	def __init__(self):
		dict.__init__(self)

	def transition(self, toStateName, duration=None, data=None, fromStateName=None):
		"""Transition to another state. If specified, it replaces the state
		named fromStateName."""
		if fromStateName:
			del self[fromStateName]
		#TODO: if duration == 0: # directly call end callback
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

	def _shortenStatus(self, status):
		return {'starting': '/', 'ongoing': '', 'ending': '\\'}[status]

	def _shortenName(self, stateName):
		try:
			stateName = stateName.split('#')
			return STATES[stateName[0]] #+ stateName[1] if len(stateName) > 1 else ''
		except KeyError:
			raise KeyError("state name not registered")

	def isChanging(self, stateName):
		return self[stateName].status == "ending"

	def crepr(self, onlyChanging=False):
		"""A compact representation"""
		if not onlyChanging: return ' '.join("{}{}".format(name, self._shortenStatus(self[name].status)) for name in self)
		return ' '.join("{}{}".format(name, self._shortenStatus(self[name].status)) for name in self if self.isChanging(name))

	def crepr2(self, onlyChanging=False):
		"""A compact representation"""
		if not onlyChanging: return ' '.join(self)
		return ' '.join(filter(lambda e: self.isChanging(e), self))

	def vcrepr(self, onlyChanging=False):
		"""A very compact representation"""
		if not onlyChanging: return ' '.join(map(self._shortenName, self))
		return ' '.join(map(self._shortenName, filter(self.isChanging, self)))

	def trepr(self):
		"""A representation of progression of states"""
		return '[' + ', '.join("{} {:.2f}/{:.2f}".format(name,
			self[name].elapsedTime, self[name].duration) for name in self) + ']'

class State(object): # TODO: add start and end callbacks
	"""Represents a game state

A state can have finite or infinite duration (None value).
A status attribute describe whether the state is starting, ongoing or ending.
If necessary, data can be stored for the purpose of state logic."""

	def __init__(self, duration=None, data=None):
		self.status = "starting"
		self.duration = duration
		self.elapsedTime = 0
		self.data = data # Data conveyed by the state

	def __repr__(self):
		return "State({self.status},{self.elapsedTime:.2f}/{self.duration:.2f},{self.data})".format(self=self)

if __name__ == '__main__':
	pass
