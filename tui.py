#!/usr/bin/env python3

"""Textual User Interface for Swap"""

from random import randrange
import itertools
import urwid
import swap
from swap import INFO, DEBUG, WARN, ERROR

class TUI(object):
	COLORS = [('k', 'black'), ('r', 'dark red'), ('w', 'brown'), ('b', 'dark blue'),
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

		leftGrid = urwid.Text('')
		leftCont = urwid.LineBox(urwid.Filler(leftGrid, 'top'))

		rightGrid = urwid.Text('')
		rightCont = urwid.LineBox(urwid.Filler(rightGrid, 'top'))

		scoreTitle = urwid.AttrMap(urwid.Text('Score', align='center'), 'title')
		scoreCont = urwid.Filler(scoreTitle, 'top', top=2)
		scoreLabel = urwid.Text(str(self.game.score), align='center')

		multiplierTitle = urwid.AttrMap(urwid.Text('Multiplier', align='center'), 'title')
		multiplierCont = urwid.Filler(multiplierTitle, 'top', top=2)
		multiplierLabel = urwid.Text(str(self.game.scoreMultiplier), align='center')

		stateTitle = urwid.AttrMap(urwid.Text('State', align='center'), 'title')
		stateCont = urwid.Filler(stateTitle, 'top', top=2)
		stateLabel = urwid.Text(self.game.state.vcrepr(), align='left')

		statsPile = urwid.Pile([scoreCont,
			urwid.Filler(urwid.AttrMap(scoreLabel, 'stats'), 'top', top=1),
			multiplierCont,
			urwid.Filler(urwid.AttrMap(multiplierLabel, 'stats'), 'top', top=1),
			stateCont,
			urwid.Filler(urwid.AttrMap(stateLabel, 'stats'), 'top', top=1)
			])

		columns = urwid.Columns([(32, leftCont), statsPile, (32, rightCont)])

		frame = urwid.Frame(header=header, body=columns)

		self.leftGrid, self.rightGrid = leftGrid, rightGrid
		self.scoreLabel = scoreLabel
		self.multiplierLabel = multiplierLabel
		self.stateLabel = stateLabel
		self.palette = palette
		self.frame = frame
		self.mainLoop = urwid.MainLoop(frame, palette, unhandled_input=self.handleInput)

	def handleInput(self, key):
		if key == ' ':
			self.game.pause = not self.game.pause
		elif key in ('up', 'right', 'down', 'left'):
			self.game.moveSwapper(key)
		elif key == "x":
			self.game.swap()
		elif key == '+':
			self.scoreLabel.base_widget.set_text("test")
		elif key in ('q', 'Q'):
			raise urwid.ExitMainLoop()

	def run(self):
		self.mainLoop.set_alarm_in(1, self.update)
		self.mainLoop.set_alarm_in(1, self.updateDebugUI)
		self.mainLoop.run()

	def updateUI(self):
		#self.leftGrid.set_text(self.buildMarkup(self.game.grid))
		self.rightGrid.set_text(self.buildMarkup(self.game.grid))
		self.scoreLabel.set_text(str(self.game.score))
		self.multiplierLabel.set_text('x' + str(self.game.scoreMultiplier))

	def update(self, loop, userData):
		self.game.update()
		if not self.game.pause:
			self.updateUI()
		self.mainLoop.set_alarm_in(.05, self.update)

	def updateDebugUI(self, loop, userData):
		self.stateLabel.set_text(self.game.state.vcrepr())
		self.mainLoop.set_alarm_in(.2, self.updateDebugUI)

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
