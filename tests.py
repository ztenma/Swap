#!/usr/bin/env python3
# -*- coding: Utf-8 -*-

"""
Tests for Swap
"""

from time import time, sleep

from swap import *
from itertoolsExt import flatten

def rotateMatrix(mat):
	return [[mat[y][x] for y in range(len(mat))] for x in range(len(mat[0]))]

def test1():
	_grid = rotateMatrix(\
	[[3, 4, 2, 2, 3, 4],
	[3, 0, 1, 4, 0, 3],
	[3, 2, 0, 2, 0, 3],
	[1, 1, 0, 2, 4, 3]])
	grid = Grid(data=_grid, nbSymbols=5)
	print(grid.reprBlocks())
	pos = (2, 1)

	grid.fallInstant()
	print('fallInstant\n' + str(grid))
	grid.swap(*pos)
	print('swap 2,1\n' + str(grid))
	grid.fallInstant(pos[0])
	print('fallInstant\n' + str(grid))

	combos = grid.combosAll()
	combosPos = set(flatten(combos))
	for pos in combosPos: # Remove combos
		grid[pos] = 0
	print('getCombo {}:'.format(pos), combos, '\n' + str(combosPos), len(combosPos))
	print()
	print(grid.reprBlocks())

	grid.fallInstant()
	print('fallInstant\n' + grid.reprBlocks())

def test2():
	grid = Grid(data=[[randrange(4) for _ in range(20)] for _ in range(40)], nbSymbols=4)
	#grid = Grid(40, 20, 4)
	print(grid.reprBlocks())

	score, scoreMultiplier = 0, 1
	combos = True
	while combos:
		lastStep = grid.fallStep()
		print('fallStep', lastStep, '\n' + str(grid))
		print('score:', score)
		input()#sleep(.2)
		if not lastStep: continue

		combos = grid.combosAll()
		combosPos = set(flatten(combos))
		#print(combos, combosPos)
		if combos:
			for combo in combos:
				score += scoreIt(len(combo)) * scoreMultiplier
				#print(len(combo), scoreIt(len(combo)), end=' ')
			#print()
			scoreMultiplier += 1
			for pos in combosPos: # Remove combos
				grid[pos] = 0
			print('combosAll:', combos, '\n' + str(combosPos), len(combosPos))
			print()
			print(grid.reprBlocks())
			input()#sleep(1)

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
	print(grid.reprBlocks())

def test4():
	_grid = rotateMatrix(\
	[[0, 0, 0, 2, 0, 0],
	[0, 0, 0, 4, 0, 0],
	[0, 0, 2, 2, 0, 3],
	[1, 0, 0, 2, 4, 3]])
	grid = Grid(data=_grid, nbSymbols=5)
	print(grid.reprBlocks())

	pos = grid.randomSwap()
	print(pos)
	grid.swap(*pos)
	print(grid.reprBlocks())

def test5():
	_grid = rotateMatrix([\
	[0, 0, 2, 0, 0],
	[0, 0, 3, 2, 2],
	[0, 0, 3, 1, 1],
	[3, 0, 3, 1, 1]])
	"""
	_grid = rotateMatrix([\
	[0, 0, 2, 0, 0],
	[0, 3, 0, 2, 2],
	[0, 3, 1, 1, 1],
	[3, 1, 3, 1, 1]])"""
	grid = Grid(data=_grid, nbSymbols=5)
	print(grid.reprBlocks())
	pos1 = (1, 3)

	comboGroup1 = grid.combosAll()
	comboPos1 = set(flatten(comboGroup1))
	print('getCombo', comboGroup1, '\n' + str(comboPos1), len(comboPos1))

	grid.swap(*pos1)
	print('swap', pos1, '\n' + str(grid))
	grid.fallInstant()
	print('fallInstant\n' + str(grid))

	comboGroup2 = grid.combosAll()
	comboPos2 = set(flatten(comboGroup2))
	print('getCombo {}:'.format(pos1), comboGroup2, '\n' + str(comboPos2), len(comboPos2))
	print()
	print(grid.reprBlocks())
	print()

	comboGroup3 = updateComboGroupMorph(comboGroup1, comboGroup2)
	comboPos3 = set(flatten(comboGroup3))
	print('updateCombo', comboGroup3, '\n' + str(comboPos3), len(comboPos3))

	for pos in comboPos3: # Remove combos
		grid[pos] = 0

	print()
	print(grid.reprBlocks())

def test6():
	_grid = rotateMatrix([\
	[4, 0, 2, 0, 0],
	[5, 0, 3, 2, 2],
	[6, 0, 3, 1, 1],
	[3, 0, 3, 1, 1]])
	grid = Grid(data=_grid, nbSymbols=5)
	print(grid.reprBlocks())

	cg = grid.combosAll()
	print(cg)
	cp = set(flatten(cg))
	print(cp)

def test7():
	_grid = rotateMatrix([\
	[3, 0, 0, 2, 0],
	[3, 0, 0, 4, 0],
	[2, 3, 2, 2, 0],
	[1, 1, 4, 2, 4]])
	grid = Grid(data=_grid, nbSymbols=5)
	print(grid.reprBlocks())
	pos1 = (1, 3)

	comboGroup1 = grid.combosAll()
	comboPos1 = set(flatten(comboGroup1))
	print('getCombo', comboGroup1, '\n' + str(comboPos1), len(comboPos1))

	grid.swap(*pos1)
	print('swap', pos1, '\n' + str(grid))
	grid.fallInstant()
	print('fallInstant\n' + str(grid))

	comboGroup2 = grid.combosAll()
	comboPos2 = set(flatten(comboGroup2))
	print('getCombo {}:'.format(pos1), comboGroup2, '\n' + str(comboPos2), len(comboPos2))
	print()
	print(grid.reprBlocks())
	print()

	comboGroup3 = updateComboGroupMorph(comboGroup1, comboGroup2)
	comboPos3 = set(flatten(comboGroup3))
	print('updateCombo', comboGroup3, '\n' + str(comboPos3), len(comboPos3))

	#for pos in comboPos3: # Remove combos
	#	grid[pos] = 0

def test8():
	_grid = rotateMatrix([\
	[3, 0, 0, 4, 4, 0],
	[0, 0, 0, 4, 0, 0],
	[1, 0, 2, 3, 4, 2],
	[0, 1, 1, 2, 2, 0]])
	grid = Grid(data=_grid, nbSymbols=5)
	print(grid.reprBlocks())

	print("combos line 3:", grid.combosLine(3))
	print("combos column 3:", grid.combosColumn(3))
	print("combo line around (1, 3):", grid.comboHorizontalAround((1, 3)))
	print("combo column around (3, 2):", grid.comboVerticalAround((3, 2)))
	print("holes:", grid.lowerHoles())

	isLastStep = grid.fallStep()
	grid.swap(3, 2)
	print(grid.reprBlocks())
	print("combos line 3:", grid.combosLine(3))
	print("combos column 3:", grid.combosColumn(3))
	print("combo line around (1, 3):", grid.comboHorizontalAround((1, 3)))
	print("combo column around (3, 2):", grid.comboVerticalAround((3, 2)))
	print("holes:", grid.lowerHoles())

	isLastStep = grid.fallStep()
	print(grid.reprBlocks())
	print("combos all:", grid.combosAll())
	print("holes:", grid.lowerHoles())

	combo = grid.comboHorizontalAround((1, 3))
	print("combo line around (1, 3):", combo)
	for pos in combo: # Remove combos
		grid[pos] = 0
	print(grid.reprBlocks())
	print("combo line around (1, 3):", grid.comboHorizontalAround((1, 3)))
	print("combo column around (3, 2):", grid.comboVerticalAround((3, 2)))
	print("holes:", grid.lowerHoles())

	isLastStep = grid.fallStep()
	print(grid.reprBlocks())
	print("combos all:", grid.combosAll())
	print("combo line around (3, 3):", grid.comboHorizontalAround((3, 3)))
	print("combo column around (3, 3):", grid.comboVerticalAround((3, 3)))
	print("holes:", grid.lowerHoles())

def test9():
	_grid = rotateMatrix([\
	[1, 0, 0, 0, 4],
	[0, 0, 0, 0, 4],
	[1, 0, 4, 4, 4],
	[1, 0, 2, 2, 0]])
	grid = Grid(data=_grid, nbSymbols=5)

	holes1 = grid.lowerHoles()
	print(grid.reprBlocks())
	print("holes:", holes1)

	isLastStep = grid.fallStep()
	holes2 = grid.lowerHoles()
	print(grid.reprBlocks())
	print("holes:", holes2)

	if not holes2:
		for hole in holes1:
			comboGroup = grid.combosAfterFall(hole)
			print("Combos after fall {}:".format(hole), comboGroup)
			for pos in set(flatten(comboGroup)): # Remove combos
				grid[pos] = 0
			print(grid.reprBlocks())

def test10():
	_grid = rotateMatrix([\
	[3, 0, 0, 4, 4, 0],
	[0, 0, 0, 4, 0, 0],
	[0, 0, 2, 4, 4, 0],
	[1, 1, 1, 2, 2, 2]])
	grid = Grid(data=_grid, nbSymbols=5)
	print(grid.reprBlocks())

	print("combo vert (0,0):", grid.comboVerticalAround(0, 0))
	print("combo vert (0,1):", grid.comboVerticalAround(0, 1))
	print("combo vert (0,3):", grid.comboVerticalAround(0, 3))
	print("combo vert (1,0):", grid.comboVerticalAround(1, 0))
	print("combo vert (3,1):", grid.comboVerticalAround(3, 1))
	print("combo vert (3,3):", grid.comboVerticalAround(3, 3))
	print("combo horiz (0,0):", grid.comboHorizontalAround(0, 0))
	print("combo horiz (3,2):", grid.comboHorizontalAround(3, 2))
	print("combo horiz (3,3):", grid.comboHorizontalAround(3, 3))

if __name__ == '__main__':
	#print("\033[104mkuro\033[00mmatsu")
	test9()
