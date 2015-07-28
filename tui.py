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
		self.game = swap.Game()

		self.buildUI()
		self.updateUI()

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
		scoreLabel = urwid.Text(str(self.game.score), align='center')
		statsPile = urwid.Pile([scoreCont, urwid.Filler(urwid.AttrMap(scoreLabel, 'stats'), 'top', top=2)])

		columns = urwid.Columns([(32, leftCont), statsPile, (32, rightCont)])

		frame = urwid.Frame(header=header, body=columns)

		self.leftGrid, self.rightGrid = leftGrid, rightGrid
		self.scoreLabel = scoreLabel
		self.palette = palette
		self.frame = frame
		self.mainLoop = urwid.MainLoop(frame, palette, unhandled_input=self.handleInput)

	def updateUI(self):
		self.leftGrid.set_text(self.buildMarkup(self.game.grid))
		self.rightGrid.set_text(self.buildMarkup(self.game.grid))
		self.scoreLabel.set_text(str(self.game.score))

	def handleInput(self, key):
		if key == '+':
			self.scoreLabel.base_widget.set_text("plus")

		elif key in ('q', 'Q'):
			raise urwid.ExitMainLoop()

	def run(self):
		self.mainLoop.set_alarm_in(1, self.update)
		self.mainLoop.run()

	def update(self, loop, userData):
		self.game.update()
		self.updateUI()
		self.mainLoop.set_alarm_in(.04, self.update)

	def buildMarkup(self, grid):
		out = []
		color, chars = None, None
		for y in range(grid.height):
			for x in range(grid.width):
				color, chars = TUI.COLORS[grid[x][y]][0], '  '

				spx, spy = self.game.swapperPos
				if spy == y and spx == x:
					chars = '>>'
				elif spy == y and spx+1 == x:
					chars = '<<'

				out.append((color, chars))
			out.append('\n')
		#out = [[(TUI.COLORS[grid[i][j]][0], '  ')\
		#for i in range(grid.width)] + ['\n'] for j in range(grid.height)]
		return out

if __name__ == '__main__':
	TUI().run()
