#!/usr/bin/env python3
# -*- coding: Utf-8 -*-

"""
Tests for Swap
"""

from swap import *

def rotateMatrix(mat):
	return [[mat[y][x] for y in range(len(mat))] for x in range(len(mat[0]))]

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
		lastStep = grid.fallStep()
		print('fallStep', lastStep, '\n' + str(grid))
		print('score:', score)
		input()#sleep(.2)
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
	print('init\n' + str(grid))
	return grid

def test4():
	_grid = rotateMatrix(\
	[[0, 0, 0, 2, 0, 0],
	[0, 0, 0, 4, 0, 0],
	[0, 0, 2, 2, 0, 3],
	[1, 0, 0, 2, 4, 3]])
	grid = Grid(data=_grid, nbSymbols=5)
	print('init\n' + str(grid))

	pos = grid.getRandomSwap()
	print(pos)
	grid.swap(*pos)
	print(grid)

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
	print(str(grid))
	pos1 = (1, 3)

	comboGroup1 = grid.testComboAll()
	comboPos1 = set(itertools.chain.from_iterable(comboGroup1))
	print('testCombo', comboGroup1, '\n' + str(comboPos1), len(comboPos1))

	grid.swap(*pos1)
	print('swap', pos1, '\n' + str(grid))
	grid.fallInstant()
	print('fallInstant\n' + str(grid))

	comboGroup2 = grid.testComboAll()
	comboPos2 = set(itertools.chain.from_iterable(comboGroup2))
	print('testCombo {}:'.format(pos1), comboGroup2, '\n' + str(comboPos2), len(comboPos2))
	print()
	print(grid)
	print()

	comboGroup3 = updateComboGroupLazy(comboGroup1, comboGroup2)
	comboPos3 = set(itertools.chain.from_iterable(comboGroup3))
	print('updateCombo', comboGroup3, '\n' + str(comboPos3), len(comboPos3))

	for pos in comboPos3: # Remove combos
		grid[pos] = 0

	print()
	print(grid)

def test6():
	_grid = rotateMatrix([\
	[4, 0, 2, 0, 0],
	[5, 0, 3, 2, 2],
	[6, 0, 3, 1, 1],
	[3, 0, 3, 1, 1]])
	grid = Grid(data=_grid, nbSymbols=5)
	print(str(grid))

	cg = grid.testComboAll()
	print(cg)
	cp = set(itertools.chain.from_iterable(cg))
	print(cp)

def test7():
	_grid = rotateMatrix([\
	[3, 0, 0, 2, 0],
	[3, 0, 0, 4, 0],
	[2, 3, 2, 2, 0],
	[1, 1, 4, 2, 4]])
	grid = Grid(data=_grid, nbSymbols=5)
	print(str(grid))
	pos1 = (1, 3)

	comboGroup1 = grid.testComboAll()
	comboPos1 = set(itertools.chain.from_iterable(comboGroup1))
	print('testCombo', comboGroup1, '\n' + str(comboPos1), len(comboPos1))

	grid.swap(*pos1)
	print('swap', pos1, '\n' + str(grid))
	grid.fallInstant()
	print('fallInstant\n' + str(grid))

	comboGroup2 = grid.testComboAll()
	comboPos2 = set(itertools.chain.from_iterable(comboGroup2))
	print('testCombo {}:'.format(pos1), comboGroup2, '\n' + str(comboPos2), len(comboPos2))
	print()
	print(grid)
	print()

	comboGroup3 = updateComboGroup(comboGroup1, comboGroup2)
	comboPos3 = set(itertools.chain.from_iterable(comboGroup3))
	print('updateCombo', comboGroup3, '\n' + str(comboPos3), len(comboPos3))

	#for pos in comboPos3: # Remove combos
	#	grid[pos] = 0

if __name__ == '__main__':
	#print("\033[104mkuro\033[00mmatsu")
	test5()
