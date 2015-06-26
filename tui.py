#!/usr/bin/env python3

"""Textual User Interface for Swap"""

from random import randrange
import itertools
import urwid
import swap

class TUI(object):
	COLORS = [('k', 'black'), ('w', 'brown'), ('b', 'dark blue'), ('r', 'dark red'),
	('g', 'dark green'), ('m', 'dark magenta'), ('c', 'dark cyan'), ('z', 'light gray')]

	def __init__(self):
		self.score = 0
		self.scoreMultiplier = 1
		self.grid = swap.Grid(15, 20, 4)

		self.buildUI()

		self.leftGrid.set_text(self.buildMarkup(self.grid))
		self.rightGrid.set_text(self.buildMarkup(self.grid))

	def buildUI(self):
		urwid.set_encoding("UTF-8")

		palette = [('title', 'white,bold', 'black'),('stats', 'white', 'white')]
		palette.extend((name, 'white', style) for name, style in TUI.COLORS)

		header = urwid.AttrMap(urwid.Text('Swap', align='center'), 'title')

		leftGrid = urwid.Text('0 1 2 3\n0 1 2 3\n4 5 6 7\n0 1 2 3\n0 1 2 3\n')
		leftCont = urwid.LineBox(urwid.Filler(leftGrid, 'top'))

		rightGrid = urwid.Text('0 1 2 3\n0 1 2 3\n4 5 6 7\n0 1 2 3\n0 1 2 3\n')
		rightCont = urwid.LineBox(urwid.Filler(rightGrid, 'top'))

		scoreTitle = urwid.AttrMap(urwid.Text('Score', align='center'), 'title')
		scoreCont = urwid.Filler(scoreTitle, 'top', top=2)
		scoreLabel = urwid.Text(str(self.score), align='center')
		statsPile = urwid.Pile([scoreCont, urwid.Filler(urwid.AttrMap(scoreLabel, 'stats'), 'top', top=2)])

		columns = urwid.Columns([(32, leftCont), statsPile, (32, rightCont)])

		frame = urwid.Frame(header=header, body=columns)

		self.leftGrid, self.rightGrid = leftGrid, rightGrid
		self.scoreLabel = scoreLabel
		self.palette = palette
		self.frame = frame
		self.mainLoop = urwid.MainLoop(frame, palette, unhandled_input=self.handleInput)

	def handleInput(self, key):
		if key == '+':
			TUI.i += 1
			self.scoreLabel.base_widget.set_text(str(self.score))

		elif key in ('q', 'Q'):
			raise urwid.ExitMainLoop()

	def run(self):
		self.mainLoop.set_alarm_in(1, self.step)
		self.mainLoop.run()

	def step(self, loop, user_data):
		self.updateGame()

		self.scoreLabel.set_text(str(self.score))
		self.leftGrid.set_text(self.buildMarkup(self.grid))

	def buildMarkup(self, grid):
		out = [[(TUI.COLORS[grid[i][j]][0], '  ')\
		for i in range(grid.width)] + ['\n'] for j in range(grid.height)]
		#print(out)
		return out

	def updateGame(self):

		lastStep = self.grid.fallStep()
		if not lastStep:
			self.alarm = self.mainLoop.set_alarm_in(.2, self.step)
			return

		randPos = randrange(self.grid.width-1), randrange(self.grid.height-1)
		self.grid.swap(*randPos)

		combos = self.grid.testComboAll()
		combosPos = set(itertools.chain.from_iterable(combos))
		if combos:
			for combo in combos:
				self.score += swap.scoreIt(len(combo)) * self.scoreMultiplier
			self.scoreMultiplier += 1
			for pos in combosPos: # Remove combos
				self.grid[pos] = 0
			self.alarm = self.mainLoop.set_alarm_in(1, self.step)
		else:
			self.alarm = self.mainLoop.set_alarm_in(.2, self.step)

if __name__ == '__main__':
	TUI().run()