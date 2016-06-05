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

SCORES = [2, 3, 5, 10, 20, 50, 100, 200, 400, 600, 800]
scoreIt = lambda x: SCORES[x-3] if x <= 10 else 1000

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

	def update(self):

		currentTime = time()
		dt = currentTime - self.lastTime
		self.lastTime = currentTime

		if self.pause: return

		#if any(self.state.isChanging(e) for e in self.state):
		#	DEBUG("State: %s", self.state.vcrepr())

		for stateName in tuple(self.state.keys()):

			if stateName == "AI_swap":
				if self.state["AI_swap"].status == "starting":
					self.swapperPos = self.grid.randomSwap()
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
						lowerHoles = self.grid.lowerHoles([pos[0]])
						if lowerHoles:
							self.state.transition(stateName, .2, lowerHoles[0])
						else:
							self.state.delete(stateName)
							sumFalls = sum(1 for name in self.state if name.startswith("fall#"))
							comboGroup = self.checkCombo("fall", pos)
							if sumFalls == 0 and not comboGroup:
								self.scoreMultiplier = 1

			elif stateName.startswith("combo#"):
				if self.state[stateName].status == "ending":
					#DEBUG("Combos %s\n%s", stateName, self.state[stateName].data)
					comboGroup = self.state[stateName].data

					comboGroup = self.updateComboGroupLazy(comboGroup)
					self.processCombos(comboGroup)

					self.state.delete(stateName)
					#DEBUG("After delete combo: %s", self.getComboGroups())
					self.checkFall()

		self.state.update(dt)

	def checkFall(self, focusX=None):
		"""Check whether some blocks have to fall. Return lower holes.

		Creates fall state for each hole found.
		If focusX, then only corresponding columns are checked."""

		lowerHoles = self.grid.lowerHoles(focusX)
		#DEBUG("Lower holes: %s", lowerHoles)
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

	def checkCombo(self, checkType, pos):
		"""Check whether there are combos. Return combo group.

		Creates combo state."""

		if checkType == "fall":
			comboGroup = self.grid.combosAfterFall(pos)
		elif checkType == "swap":
			comboGroup = self.grid.combosAfterSwap(pos)
		else: raise ValueError("Wrong check type: " + str(checkType))

		if comboGroup:
			#DEBUG("Found combo group %s\nComboGroups: %s", comboGroup, self.getComboGroups())
			fallingX = [pos[0] for pos in self.grid.lowerHoles()]

			# Filter already found combos and update old combo groups
			oldStates = [self.state[name] for name in self.state if name.startswith("combo#")]
			for state in oldStates: # every state
				oldComboGroup = state.data
				
				oci = 0 # old combo index
				while oci < len(oldComboGroup): # every stored combo
					
					nci = 0 # new combo index
					while nci < len(comboGroup): # every current combo
						#DEBUG('Current combo group: %s', comboGroup)
						if any(p[0] in fallingX for p in comboGroup[nci]):
							DEBUG('Filter#1 combo: %s', comboGroup[nci])
							comboGroup.pop(nci)
							continue
						# If any common block
						if comboGroup[nci] and sum(p in oldComboGroup[oci] for p in comboGroup[nci]) > 1:
							if oldComboGroup[oci] != comboGroup[nci]:
								DEBUG('Update old combo: %s -> %s', oldComboGroup[oci], comboGroup[nci])
								oldComboGroup[oci] = comboGroup[nci] # Update old combo
							else:
								DEBUG('Filter#2 combo: %s', comboGroup[nci])
							comboGroup.pop(nci)
							continue
						nci += 1
					oci += 1

			DEBUG("Add combo group %s", comboGroup)
			if comboGroup:
				self.state.transition("combo#" + str(self.genComboId()), 2, comboGroup)

		return comboGroup

	def processCombos(self, comboGroup):
		if not len(comboGroup): return
		comboGroupPos = set(flatten(comboGroup))
		DEBUG('Score combos: %s %s', scoreIt(len(comboGroupPos)) * self.scoreMultiplier, comboGroup)
		
		self.score += scoreIt(len(comboGroupPos)) * self.scoreMultiplier
		self.scoreMultiplier += 1
		
		for pos in comboGroupPos: # Remove combos
			self.grid[pos] = 0

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
		self.checkFall([x, x+1])
		self.checkCombo("swap", (x, y))

	def processInput(self, name):
		if name == "swap": self.swap()
		elif name in ("up", "right", "down", "left"): self.moveSwapper(name)

	def updateComboGroupLazy(self, comboGroup):
		"""Computes the final combo group based on combo state start and end, using
the lazy startegy.

Lazy:
include any combo from start state that remains in end state"""

		newComboGroup = []
		for combo in comboGroup:
			orientation = combo.orientation()
			if orientation == 'h': comboTest = self.grid.comboHorizontalAround(*combo[0])
			elif orientation == 'v': comboTest = self.grid.comboVerticalAround(*combo[0])
			else: raise NotImplemented
			if combo == comboTest:
				newComboGroup.append(combo)
		return newComboGroup

	def updateComboGroupMorph(self, comboGroup1, comboGroup2): # TODO
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
		self[toStateName] = State(toStateName, duration, data)
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
		return ' '.join(filter(self.isChanging, self))

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

	def __init__(self, name=None, duration=None, data=None):
		self.name = name
		self.status = "starting"
		self.duration = duration
		self.elapsedTime = 0
		self.data = data # Data conveyed by the state

	def __repr__(self):
		return "State({self.status},{self.elapsedTime:.2f}/{self.duration:.2f},{self.data})".format(self=self)

if __name__ == '__main__':
	pass
