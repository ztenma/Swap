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
from state import State, StateMachine


SCORES = [2, 3, 5, 10, 20, 50, 100, 200, 400, 600, 800]
scoreIt = lambda x: SCORES[x-3] if x <= 10 else 1000


class Player(object):
	
	def __init__(self, type_, name):
		assert type_ in ('Human', 'AI'), 'Player type must be among (Human, AI)!'
		self.type = type_ # Human, AI
		self.name = name
		
		self.score = 0
		self.scoreMultiplier = 1
		self.swapperPos = (0, 0)
		
		self.grid = Grid(12, 20, 4)
		
		self.stateMachine = StateMachine()

class Game(object):

	def __init__(self):
		self.players = [Player('Human', 'Human'), Player('AI', 'BOT')]
		self.humanPlayerId = listFind(self.players, 'Human', key=lambda e: e.type)
		self.humanPlayer = self.players[self.humanPlayerId]
		
		self.lastTime = time()
		self.pause = False

		INFO("Starting Swap")
		
		for player in self.players:
			if player.type == 'AI':
				player.stateMachine.transition("AI_swap", 2) # To enable AI
			player.stateMachine.transition("block", 4)

	def update(self):

		currentTime = time()
		dt = currentTime - self.lastTime
		self.lastTime = currentTime

		if self.pause: return

		for player in self.players:
			#if any(player.stateMachine.isChanging(e) for e in player.stateMachine):
			#	DEBUG("State: %s", player.stateMachine.vcrepr())
		
			self.stepStateMachine(player)
			player.stateMachine.update(dt)

	def stepStateMachine(self, player):
		
		for stateName in tuple(player.stateMachine.keys()):

			if stateName == "AI_swap":
				if player.stateMachine["AI_swap"].status == "starting":
					player.swapperPos = player.grid.randomSwap()
				elif player.stateMachine["AI_swap"].status == "ending":
					self.swap(player)
					player.stateMachine.transition("AI_swap", 1.5)
					
			elif stateName == "block":
				if player.stateMachine["block"].status == "ending":
					player.grid.spawnBlock()
					self.checkAndFall(player)
					player.stateMachine.transition("block", .5)

			elif stateName.startswith("fall#"):
				if player.stateMachine[stateName].status == "ending":
					pos = player.stateMachine[stateName].data
					player.grid.fallStepPos(*pos)
					if player.grid.isHole(*pos):
						player.stateMachine.transition(stateName, .2, pos)
					else: # Falling ended
						lowerHoles = player.grid.lowerHoles([pos[0]])
						if lowerHoles:
							player.stateMachine.transition(stateName, .2, lowerHoles[0])
						else:
							player.stateMachine.delete(stateName)
							sumFalls = sum(1 for name in player.stateMachine if name.startswith("fall#"))
							comboGroup = self.checkAndCombo(player, "fall", pos)
							if sumFalls == 0 and not comboGroup:
								player.scoreMultiplier = 1

			elif stateName.startswith("combo#"):
				if player.stateMachine[stateName].status == "ending":
					#DEBUG("Combos %s\n%s", stateName, player.stateMachine[stateName].data)
					comboGroup = player.stateMachine[stateName].data

					comboGroup = updateComboGroupLazy(player, comboGroup)
					self.processCombos(player, comboGroup)

					player.stateMachine.delete(stateName)
					#DEBUG("After delete combo: %s", self.getComboGroups(player))
					self.checkAndFall(player)

	def checkAndFall(self, player, focusX=None):
		"""Check whether some blocks have to fall. Return lower holes.

		Creates fall state for each hole found.
		If focusX, then only corresponding columns are checked."""

		lowerHoles = player.grid.lowerHoles(focusX)
		#DEBUG("Lower holes: %s", lowerHoles)
		for pos in lowerHoles:
			if "fall#" + str(pos[0]) not in player.stateMachine:
				player.stateMachine.transition("fall#" + str(pos[0]), .2, pos)
		return lowerHoles

	def getComboGroups(self, player):
		return [player.stateMachine[name].data for name in player.stateMachine if name.startswith("combo#")]

	def genComboId(self, player):
		for i in range(100):
			if "combo#" + str(i) not in player.stateMachine:
				return i
		raise RuntimeError("Too much combos")

	def checkAndCombo(self, player, checkType, pos):
		"""Check whether there are combos. Return combo group.

		Creates combo state."""

		if checkType == "fall":
			comboGroup = player.grid.combosAfterFall(pos)
		elif checkType == "swap":
			comboGroup = player.grid.combosAfterSwap(pos)
		else: raise ValueError("Wrong check type: " + str(checkType))

		if comboGroup:
			#DEBUG("Found combo group %s\nComboGroups: %s", comboGroup, self.getComboGroups(player))
			fallingX = [pos[0] for pos in player.grid.lowerHoles()]

			# Filter already found combos and update old combo groups
			oldStates = [player.stateMachine[name] for name in player.stateMachine if name.startswith("combo#")]
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
				player.stateMachine.transition("combo#" + str(self.genComboId(player)), 2, comboGroup)

		return comboGroup

	def processCombos(self, player, comboGroup):
		if not len(comboGroup): return
		comboGroupPos = set(flatten(comboGroup))
		DEBUG('Score combos: %s %s', scoreIt(len(comboGroupPos)) * player.scoreMultiplier, comboGroup)
		
		player.score += scoreIt(len(comboGroupPos)) * player.scoreMultiplier
		player.scoreMultiplier += 1
		
		for pos in comboGroupPos: # Remove combos
			player.grid[pos] = 0

	def processInputEvent(self, name):
		player = self.humanPlayer
		if name == "swap":
			self.swap(player)
		elif name in ("up", "right", "down", "left"):
			self.moveSwapper(player, name)
			
	def swap(self, player):
		x, y = player.swapperPos
		player.grid.swap(x, y)
		self.checkAndFall(player, [x, x+1])
		self.checkAndCombo(player, "swap", (x, y))
		
	def moveSwapper(self, player, direction):
		assert direction in ('up', 'right', 'down', 'left'), "direction must be one of up, right, down, left"
		x, y = player.swapperPos
		if direction == 'up': player.swapperPos = (x, max(0, y-1))
		elif direction == 'right': player.swapperPos = (min(x+1, player.grid.width-2), y)
		elif direction == 'down': player.swapperPos = (x, min(y+1, player.grid.height-1))
		elif direction == 'left': player.swapperPos = (max(x-1, 0), y)

def updateComboGroupLazy(player, comboGroup):
		"""Computes the final combo group based on combo state start and end, using
the lazy startegy.

Lazy:
include any combo from start state that remains in end state"""

		newComboGroup = []
		for combo in comboGroup:
			orientation = combo.orientation()
			if orientation == 'h': comboTest = player.grid.comboHorizontalAround(*combo[0])
			elif orientation == 'v': comboTest = player.grid.comboVerticalAround(*combo[0])
			else: raise NotImplemented
			if combo == comboTest:
				newComboGroup.append(combo)
		return newComboGroup

def updateComboGroupMorph(comboGroup1, comboGroup2):
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

def listFind(lst, val, key=(lambda x: x)):
	for i,e in enumerate(lst):
		if key(e) == val:
			return i
	return None

if __name__ == '__main__':
	pass
