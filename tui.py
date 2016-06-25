#!/usr/bin/env python3
# -*- coding: Utf-8 -*-

"""Textual User Interface for Swap"""

import sys
from time import time
from random import randrange
from itertoolsExt import flatten
import urwid

import swap
from log import *

class TUI(object):
	COLORS = [('k', 'black'), ('r', 'dark red'), ('w', 'brown'), ('b', 'dark blue'),
	('g', 'dark green'), ('m', 'dark magenta'), ('c', 'dark cyan'), ('z', 'light gray')]

	def __init__(self):
		self.GAME_DT = .05
		self.UI_DT = .1
		self.timer = self.UI_DT
		self.last_time = time()
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
		scoreLabel = urwid.Text('_%s | %s_' % (self.game.players[0].score, self.game.players[1].score), align='center')

		multiplierTitle = urwid.AttrMap(urwid.Text('Multiplier', align='center'), 'title')
		multiplierCont = urwid.Filler(multiplierTitle, 'top', top=2)
		multiplierLabel = urwid.Text('%s | %s' % (self.game.players[0].scoreMultiplier, self.game.players[1].scoreMultiplier), align='center')

		stateTitle = urwid.AttrMap(urwid.Text('State', align='center'), 'title')
		stateCont = urwid.Filler(stateTitle, 'top', top=2)
		stateLabel = urwid.Text('%s\n%s' % (self.game.players[0].stateMachine.vcrepr(), self.game.players[1].stateMachine.vcrepr()), align='left')

		statsPile = urwid.Pile([scoreCont,
			urwid.Filler(urwid.AttrMap(scoreLabel, 'stats'), 'top', top=1),
			multiplierCont,
			urwid.Filler(urwid.AttrMap(multiplierLabel, 'stats'), 'top', top=1),
			stateCont,
			urwid.Filler(urwid.AttrMap(stateLabel, 'stats'), 'top', top=1)
			])

		columns = urwid.Columns([(12*2+2, leftCont), statsPile, (12*2+2, rightCont)])

		frame = urwid.Frame(header=header, body=columns)

		self.leftGrid, self.rightGrid = leftGrid, rightGrid
		self.scoreLabel = scoreLabel
		self.multiplierLabel = multiplierLabel
		self.stateLabel = stateLabel
		self.palette = palette
		self.frame = frame
		self.mainLoop = urwid.MainLoop(frame, palette, unhandled_input=self.handleInput)

	def handleInput(self, key):
		#DEBUG("input %s", self.mainLoop.screen.get_input())
		if key == ' ':
			self.game.pause = not self.game.pause
		elif key in ('up', 'right', 'down', 'left'):
			self.game.processInputEvent(key)
		elif key == "x":
			self.game.processInputEvent("swap")
		elif key == '+':
			self.scoreLabel.base_widget.set_text("test")
		elif key in ('q', 'Q'):
			raise urwid.ExitMainLoop()

	def run(self):
		self.mainLoop.set_alarm_in(1, self.update)
		self.mainLoop.set_alarm_in(1, self.updateDebugUI)
		self.mainLoop.run()

	def updateUI(self):
		self.leftGrid.set_text(self.buildMarkup(self.game.players[0]))
		self.rightGrid.set_text(self.buildMarkup(self.game.players[1]))
		self.scoreLabel.set_text('%s | %s' % (self.game.players[0].score, self.game.players[1].score))
		self.multiplierLabel.set_text('x%s | x%s' % (self.game.players[0].scoreMultiplier, self.game.players[1].scoreMultiplier))

	def update(self, loop, userData):
		
		if not self.game.pause:
			self.game.update()
			if self.timer <= 0:
				self.updateUI()
				self.timer = self.UI_DT
			# Timing
			t = time()
			self.timer -= t - self.last_time
			self.last_time = t
			
		# Schedule update
		self.mainLoop.set_alarm_in(self.GAME_DT, self.update)

	def updateDebugUI(self, loop, userData):
		if not self.game.pause:
			self.stateLabel.set_text('%s\n%s' % (self.game.players[0].stateMachine.vcrepr(), self.game.players[1].stateMachine.vcrepr()))
		self.mainLoop.set_alarm_in(.2, self.updateDebugUI)

	def buildMarkup(self, player):
		out = []
		color, chars = None, None
		comboGroups = self.game.getComboGroups(player)
		#DEBUG("Markup combo groups: %s", comboGroups)
		for y in range(player.grid.height):
			for x in range(player.grid.width):
				color, chars = TUI.COLORS[player.grid[x][y]][0], [' ', ' ']

				for cg in comboGroups:
					for block in set(flatten(cg)):
						if block.pos == (x, y):
							chars = ['*', '*']

				spx, spy = player.swapperPos
				if spy == y and spx == x:
					chars[0] = '['
				elif spy == y and spx+1 == x:
					chars[1] = ']'

				out.append((color, ''.join(chars)))
			out.append('\n')
		return out

if __name__ == '__main__':
	TUI().run()
