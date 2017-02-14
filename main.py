#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 
#
# UFPA Speech Recorder
#
# Copyright 2017: PPGCC UFPA
# Programa de Pós-Graduação em Ciência da Computação
# Universidade Federal do Pará
#
# Authors Jan 2017:
# Cassio Trindade Batista - cassio.batista.13@gmail.com
# Nelson C. Sampaio Neto  - dnelsonneto@gmail.com

# References:
# [1] http://stackoverflow.com/questions/35887523/qmessagebox-change-text-of-standard-button


import sys
sys.path.insert(0, 'src')
import os

try:
	from PyQt4 import QtCore, QtGui
except ImportError:
	print u'Erro: PyQt4 não instalado'
	sys.exit()

try:
	import pyaudio
except ImportError:
	print u'Warning: PyAudio não instalado'
	import pip
	pip.main(['install', 'pyaudio'])

from ufpareg import UFPARegister

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)

	# Yes/No Dialog question translation
	translator = QtCore.QTranslator(app)
	translator.load('qt_%s' % 
			'pt_BR', #QtCore.QLocale.system().name() can be used as well
			QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
	app.installTranslator(translator)

	reg = UFPARegister()
	reg.move(300,200) # try to centralize
	reg.setMaximumSize(1200, 390) # define initial size
	reg.setWindowTitle(u'UFPA Speech Recorder')
	reg.setWindowIcon(QtGui.QIcon(os.path.join('images', 'ufpa.png')))
	reg.show()

	sys.exit(app.exec_())

### EOF ###
