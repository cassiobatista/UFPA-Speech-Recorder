#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 
#
# UFPA Speech Recorder
#
# Copyright 2017: 
# Grupo Falabrasil
# Programa de Pós-Graduação em Ciência da Computação
# Universidade Federal do Pará
#
# Author Jan 2017:
# Cassio Trindade Batista - cassio.batista.13@gmail.com
#
# Last edited on February, 2017

# References:
# [1] http://stackoverflow.com/questions/892199/detect-record-audio-in-python
# [2] http://stackoverflow.com/questions/5630828/how-to-call-one-mainwindow-to-another-mainwindow-in-qt-or-pyqt
# [3] http://stackoverflow.com/questions/12734319/change-rectangular-qt-button-to-round
# [4] https://srinikom.github.io/pyside-docs/PySide/QtCore/Qt.html
# [5] https://docs.python.org/2/howto/logging-cookbook.html
# [6] http://pyqt.sourceforge.net/Docs/PyQt4/new_style_signals_slots.html
# [7] http://stackoverflow.com/questions/14349563/how-to-get-non-blocking-real-time-behavior-from-python-logging-module-output-t


import sys
import os
import time
import random
import shutil

from PyQt4 import QtCore, QtGui
from datetime import datetime

import logging

import StringIO

import threading
import pyaudio
import wave
import struct 
from array import array

import info
from ufpatools import UFPAZip, UFPAUpload, UFPAPlotWave

class UFPARepeat(QtGui.QMainWindow):

	closed = QtCore.pyqtSignal()

	thread = None
	block_mic = True
	mic_ready = False

	text = None
	rec2f = None

	recording = False
	paused = False
	finished = False

	FORMAT = pyaudio.paInt16 # bits per sample (short)
	RATE = 22050 # Hz
	CHUNK_SIZE = 1024 # buffer size
	CHANNELS = 1 # mono

	last_dir = info.ROOT_DIR_PATH

	def compress(self):
		self.czip = UFPAZip(self)
		self.czip.closed.connect(self.show)
		self.czip.move(230,30) # try to centralize
		self.czip.setMinimumSize(800, 200) # define initial size
		self.czip.setWindowTitle(info.TITLE)
		self.czip.setWindowIcon(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'ufpa.png')))
		self.czip.show()

	def analise(self):
		self.wav = UFPAPlotWave(self)
		self.wav.closed.connect(self.show)
		self.wav.move(100,30) # try to centralize
		self.wav.setMinimumSize(1200, 600) # define initial size
		self.wav.setWindowTitle(info.TITLE)
		self.wav.setWindowIcon(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'ufpa.png')))
		self.wav.show()

	#def __init__(self, parent, state, school, name, uid):
	def __init__(self, parent=None):
		super(UFPARepeat, self).__init__()
		self.parent = parent

		self.init_main_screen()
		self.init_menu()
		self.setFocusPolicy(QtCore.Qt.NoFocus)

	def init_main_screen(self):
		self.txt_check = QtGui.QCheckBox(u'Carregar lista interna de palavras')
		self.txt_check.setChecked(True)
		self.txt_check.clicked.connect(self.clear_txt)

		self.txt_label = QtGui.QLabel(u'Lista de Palavras')
		self.txt_label.setEnabled(False)

		self.txt_file = QtGui.QLineEdit()
		self.txt_file.setReadOnly(True)
		self.txt_file.setEnabled(False)

		self.txt_button = QtGui.QPushButton('Procurar')
		self.txt_button.setMinimumWidth(150)
		#self.txt_button.setStatusTip(u'Procurar a lista de palavras')
		self.txt_button.setToolTip(u'Procurar a lista de palavras')
		self.txt_button.setEnabled(False)
		self.txt_button.clicked.connect(self.open_wlist_file)

		hb_wlist = QtGui.QHBoxLayout()
		hb_wlist.addSpacing(22)
		hb_wlist.addWidget(self.txt_label)
		hb_wlist.addWidget(self.txt_file)
		hb_wlist.addWidget(self.txt_button)
		hb_wlist.addSpacing(20)

		vb_wlist = QtGui.QVBoxLayout()
		vb_wlist.addWidget(self.txt_check)
		vb_wlist.addLayout(hb_wlist)
		vb_wlist.addSpacing(40)
		# -------------

		region = QtGui.QRegion(
					QtCore.QRect(0, 0, 180, 180), QtGui.QRegion.Ellipse)

		self.bred = QtGui.QPushButton(u'')
		self.bred.setMask(region)
		self.bred.setFixedHeight(180)
		self.bred.setFixedWidth(180)
		self.bred.setFlat(True)
		self.bred.setEnabled(False)

		color = QtGui.QPalette(self.bred.palette())
		color.setColor(QtGui.QPalette.Background, QtCore.Qt.lightGray)
		color.setColor(QtGui.QPalette.Button, QtCore.Qt.lightGray)
		self.bred.setAutoFillBackground(True)
		self.bred.setPalette(color)
		self.bred.update()

		self.byellow = QtGui.QPushButton(u'')
		self.byellow.setMask(region)
		self.byellow.setFixedHeight(180)
		self.byellow.setFixedWidth(180)
		self.byellow.setFlat(True)
		self.byellow.setEnabled(False)

		color = QtGui.QPalette(self.byellow.palette())
		color.setColor(QtGui.QPalette.Background, QtCore.Qt.lightGray)
		color.setColor(QtGui.QPalette.Button, QtCore.Qt.lightGray)
		self.byellow.setAutoFillBackground(True)
		self.byellow.setPalette(color)
		self.byellow.update()

		self.bgreen = QtGui.QPushButton(u'')
		self.bgreen.setMask(region)
		self.bgreen.setFixedHeight(180)
		self.bgreen.setFixedWidth(180)
		self.bgreen.setFlat(True)
		self.bgreen.setEnabled(False)

		color = QtGui.QPalette(self.bgreen.palette())
		color.setColor(QtGui.QPalette.Background, QtCore.Qt.lightGray)
		color.setColor(QtGui.QPalette.Button, QtCore.Qt.lightGray)
		self.bgreen.setAutoFillBackground(True)
		self.bgreen.setPalette(color)
		self.bgreen.update()

		hb_semaphore = QtGui.QHBoxLayout()
		hb_semaphore.addWidget(self.bred)
		hb_semaphore.addWidget(self.byellow)
		hb_semaphore.addWidget(self.bgreen)

		gb_semaphore = QtGui.QGroupBox()
		gb_semaphore.setLayout(hb_semaphore)
		# -------------

		self.newreg_button = QtGui.QPushButton()
		self.newreg_button.setMinimumSize(80,80)
		self.newreg_button.setFlat(True)
		self.newreg_button.setStyleSheet('QPushButton:hover:!pressed' + 
					'{background-color: black; border: 3px solid lightgray;}')
		self.newreg_button.setEnabled(False)
		self.newreg_button.clicked.connect(self.new_reg)

		self.play_button = QtGui.QToolButton()
		self.play_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
		self.play_button.setIcon(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'play.png')))
		self.play_button.setIconSize(QtCore.QSize(65,65))
		self.play_button.setToolTip(u'Iniciar módulo "Ouvir e Repetir"')
		self.play_button.setMinimumSize(120,90)
		self.play_button.setText(u'Iniciar Módulo')
		self.play_button.setStyleSheet('QPushButton:hover:!pressed' + 
					'{background-color: black; border: 3px solid lightgray;}')
		self.play_button.clicked.connect(self.play)

		self.rec_button = QtGui.QPushButton()
		self.rec_button.setIcon(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'rec.png')))
		self.rec_button.setIconSize(QtCore.QSize(80,80))
		self.rec_button.setToolTip(u'Iniciar gravação')
		self.rec_button.setMinimumSize(90,90)
		self.rec_button.setFlat(True)
		self.rec_button.setStyleSheet('QPushButton:hover:!pressed' + 
					'{background-color: black; border: 3px solid lightgray;}')
		self.rec_button.setEnabled(False)
		self.rec_button.clicked.connect(self.start_rec)
		self.rec_button.setShortcut(QtCore.Qt.Key_Up)

		self.next_button = QtGui.QPushButton()
		self.next_button.setIcon(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'next.png')))
		self.next_button.setIconSize(QtCore.QSize(60,60))
		#self.next_button.setStatusTip(u'Passar para a próxima palavra')
		self.next_button.setToolTip(u'Próxima palavra')
		self.next_button.setMinimumSize(90,90)
		self.next_button.setFlat(True)
		self.next_button.setStyleSheet('QPushButton:hover:!pressed' + 
					'{background-color: black; border: 3px solid lightgray;}')
		self.next_button.setEnabled(False)
		self.next_button.clicked.connect(self.wnext)
		self.next_button.setShortcut(QtCore.Qt.Key_Right)

		hb_rec = QtGui.QHBoxLayout()
		hb_rec.addWidget(self.newreg_button)
		hb_rec.addSpacing(115)
		hb_rec.addStretch()
		hb_rec.addWidget(self.rec_button)
		hb_rec.addWidget(self.next_button)
		hb_rec.addStretch()
		hb_rec.addWidget(self.play_button)

		gb_rec = QtGui.QGroupBox()
		gb_rec.setLayout(hb_rec)
		# -------------

		self.vb_layout_main = QtGui.QVBoxLayout()
		self.vb_layout_main.addLayout(vb_wlist)
		self.vb_layout_main.addWidget(gb_semaphore)
		self.vb_layout_main.addWidget(gb_rec)

		wg_central = QtGui.QWidget()
		wg_central.setLayout(self.vb_layout_main)
		self.setCentralWidget(wg_central)

	def init_menu(self):
		self.act_exit = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'x.png')), u'', self)
		self.act_exit.setShortcut('Ctrl+Q')
		#self.act_exit.setStatusTip(u'Fechar UFPA Speech Recorder')
		self.act_exit.setToolTip(u'Sair')
		self.act_exit.triggered.connect(self.quit_app)

		self.act_about = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'about.png')), u'', self)
		self.act_about.setShortcut('Ctrl+I')
		#self.act_about.setStatusTip(u'Sobre o app')
		self.act_about.setToolTip(u'Sobre')
		self.act_about.triggered.connect(self.about)

		self.act_cfg = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'settings.png')), u'', self)
		#self.act_cfg.setStatusTip(u'Configurar UFPA Speech Recorder')
		self.act_cfg.setToolTip(u'Configurações')
		#self.act_cfg.triggered.connect(self.config)

		self.act_zip = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'zip.png')), u'', self)
		#self.act_zip.setStatusTip(u'Compactar pasta de áudios em um arquivo .zip')
		self.act_zip.setToolTip(u'Compactar')
		self.act_zip.triggered.connect(self.compress)

		self.act_cloud = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'cloud.png')), u'', self)
		#self.act_cloud.setStatusTip(u'Fazer upload do áudios compactados para a nuvem')
		self.act_cloud.setToolTip(u'Upload')
		#self.act_cloud.triggered.connect(self.config)

		self.act_add_new = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'add.png')), u'', self)
		self.act_add_new.setShortcut('Ctrl+N')
		#self.act_add_new.setStatusTip(u'Adicionar novo registro')
		self.act_add_new.setToolTip(u'Novo registro')
		self.act_add_new.triggered.connect(self.new_reg)

		self.sb = self.statusBar()
		self.sb.setSizeGripEnabled(False)
		#self.sb.setStyleSheet('QStatusBar {border: 0px;}')

		act_analise = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'waveform.png')), u'&Analisar', self)
		#act_analise.setStatusTip(u'Analisa os sinais de voz')
		act_analise.setStatusTip(u'Analisar')
		act_analise.triggered.connect(self.analise)
		
		self.tb = QtGui.QToolBar()
		self.tb.addAction(self.act_exit)
		self.tb.addAction(self.act_about)
		self.tb.addAction(self.act_zip)
		self.tb.addAction(self.act_add_new)
		self.tb.addAction(act_analise)
		self.tb.setStyleSheet('QToolBar:focus {border:none; outline:none;}')
	
		toolbar = self.addToolBar(self.tb)

	def closeEvent(self, event):
		if self.finished:
			QtGui.qApp.quit()
		else:
			reply = QtGui.QMessageBox.question(self, u'Fechar ' + info.TITLE, 
						u'A gravação não foi concluída.\n\n' + 
						u'Você deseja realmente sair?\n', 
						QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.Yes:
				if self.thread is not None:
					self.thread.i = 5000
					self.thread.paused = False
					self.thread.recording = False
					self.block_mic = False
					self.paused = False

				QtGui.qApp.quit()
			else:
				event.ignore()

	def quit_app(self):
		if self.finished:
			QtGui.qApp.quit()
		else:
			reply = QtGui.QMessageBox.question(self, u'Fechar ' + info.TITLE, 
						u'A gravação não foi concluída.\n\n' + 
						u'Você deseja realmente sair?\n', 
						QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.Yes:
				if self.thread is not None:
					self.thread.i = 5000
					self.paused = False
					self.thread.paused = False
					self.thread.recording = False
					self.block_mic = False

				QtGui.qApp.quit()
			else:
				return

	def about(self):
		QtGui.QMessageBox.information(self, u'Sobre o app', info.INFO)
		return

	def new_reg(self):
		reply = QtGui.QMessageBox.warning(self, u'Cadastrar novo contato',
					u'Desejar cadastrar uma nova criança?\n',
					QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			if self.thread is not None:
				self.thread.i = 5000
				self.paused = False
				self.thread.paused = False
				self.thread.recording = False
				self.block_mic = False
			self.hide()
			if not info.DEBUG:
				self.parent.clear()
			self.parent.show()
		else:
			return

	def open_wlist_file(self):
		filename = QtGui.QFileDialog.getOpenFileName(self,
				u'Abrir arquivo de texto contendo lista de palavras', 
				self.last_dir, u'(*.txt)')

		filename = unicode(str(filename.toUtf8()), 'utf-8')

		if filename is not u'':
			self.txt_file.setText(filename)
			self.last_dir = os.path.dirname(filename)

	@QtCore.pyqtSlot(str)
	def change_color(self, act):
		if act == '_gray':
			color = QtGui.QPalette(self.bred.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.lightGray)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.lightGray)
			self.bred.setAutoFillBackground(True)
			self.bred.setPalette(color)

			color = QtGui.QPalette(self.byellow.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.lightGray)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.lightGray)
			self.byellow.setAutoFillBackground(True)
			self.byellow.setPalette(color)

			color = QtGui.QPalette(self.bgreen.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.lightGray)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.lightGray)
			self.bgreen.setAutoFillBackground(True)
			self.bgreen.setPalette(color)

			self.bred.update()
			self.byellow.update()
			self.bgreen.update()
		elif act == '_finished':
			self.finished = True
			self.paused = False

			smiley = QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images','smiley.png'))

			print 'finished'
			color = QtGui.QPalette(self.bred.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.blue)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.blue)
			self.bred.setAutoFillBackground(True)
			self.bred.setPalette(color)
			self.bred.setIcon(smiley)
			self.bred.setIconSize(QtCore.QSize(220,220))

			color = QtGui.QPalette(self.byellow.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.blue)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.blue)
			self.byellow.setAutoFillBackground(True)
			self.byellow.setPalette(color)
			self.byellow.setIcon(smiley)
			self.byellow.setIconSize(QtCore.QSize(220,220))

			color = QtGui.QPalette(self.bgreen.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.blue)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.blue)
			self.bgreen.setAutoFillBackground(True)
			self.bgreen.setPalette(color)
			self.bgreen.setIcon(smiley)
			self.bgreen.setIconSize(QtCore.QSize(220,220))

			self.bred.update()
			self.byellow.update()
			self.bgreen.update()

			self.rec_button.setIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'rec.png')))
			self.rec_button.setIconSize(QtCore.QSize(80,80))
			#self.rec_button.setStatusTip(u'')
			self.rec_button.setToolTip(u'')
			self.rec_button.setEnabled(False)
			self.rec_button.update()

			#self.next_button.setStatusTip(u'')
			self.next_button.setToolTip(u'')

			self.newreg_button.setIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'add.png')))
			self.newreg_button.setIconSize(QtCore.QSize(65,65))
			self.newreg_button.setEnabled(True)
			#self.newreg_button.setStatusTip(u'Cadastrar um novo aluno')
			self.newreg_button.setToolTip(u'Novo registro')
		elif act == '_error':
			self.finished = True
			self.paused = False

			frowny = QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images','frowny.png'))

			print 'error'
			color = QtGui.QPalette(self.bred.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.red)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.red)
			self.bred.setAutoFillBackground(True)
			self.bred.setPalette(color)
			self.bred.setIcon(frowny)
			self.bred.setIconSize(QtCore.QSize(220,220))

			color = QtGui.QPalette(self.byellow.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.red)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.red)
			self.byellow.setAutoFillBackground(True)
			self.byellow.setPalette(color)
			self.byellow.setIcon(frowny)
			self.byellow.setIconSize(QtCore.QSize(220,220))

			color = QtGui.QPalette(self.bgreen.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.red)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.red)
			self.bgreen.setAutoFillBackground(True)
			self.bgreen.setPalette(color)
			self.bgreen.setIcon(frowny)
			self.bgreen.setIconSize(QtCore.QSize(220,220))

			self.bred.update()
			self.byellow.update()
			self.bgreen.update()

			self.rec_button.setIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'rec.png')))
			self.rec_button.setIconSize(QtCore.QSize(80,80))
			#self.rec_button.setStatusTip(u'Reinicia a gravação desde o início')
			self.rec_button.setToolTip(u'Reiniciar gravação')
			self.rec_button.update()
		elif act == '_green':
			# wait for mic
			while not self.mic_ready:
				pass

			color = QtGui.QPalette(self.bred.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.green)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.green)
			self.bred.setAutoFillBackground(True)
			self.bred.setPalette(color)

			color = QtGui.QPalette(self.byellow.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.green)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.green)
			self.byellow.setAutoFillBackground(True)
			self.byellow.setPalette(color)

			color = QtGui.QPalette(self.bgreen.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.green)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.green)
			self.bgreen.setAutoFillBackground(True)
			self.bgreen.setPalette(color)

			self.bred.update()
			self.byellow.update()
			self.bgreen.update()

			self.paused = False
			self.block_mic = False
		else:
			self.block_mic = True
			self.rec2f = threading.Thread(target=self.record_to_file)
			self.rec2f.start()

			color = QtGui.QPalette(self.bred.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.yellow)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.yellow)
			self.bred.setAutoFillBackground(True)
			self.bred.setPalette(color)

			color = QtGui.QPalette(self.byellow.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.yellow)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.yellow)
			self.byellow.setAutoFillBackground(True)
			self.byellow.setPalette(color)

			color = QtGui.QPalette(self.bgreen.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.yellow)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.yellow)
			self.bgreen.setAutoFillBackground(True)
			self.bgreen.setPalette(color)

			self.sb.showMessage(act)
			self.text = act

			self.bred.update()
			self.byellow.update()
			self.bgreen.update()

	def play(self):
		if self.txt_file.text() == '' and self.txt_check.isChecked() == False:
			QtGui.QMessageBox.warning(self,
						u'Problema ao carregar arquivo *.txt', 
						u'É preciso carregar uma lista de palavras.\n' +
						u'Caso contrário, deixe a opção acima marcada.\n')
			return

		self.txt_button.setEnabled(False)
		self.txt_check.setEnabled(False)
		self.txt_label.setEnabled(False)
		self.txt_file.setEnabled(False)

		logging.disable(logging.NOTSET)

		# create logger
		# http://stackoverflow.com/a/16966965
		self.logger = logging.getLogger()
		map(self.logger.removeHandler, self.logger.handlers[:])
		map(self.logger.removeFilter,  self.logger.filters[:])

		# create buffers
		self.log_buff = LogBuffer()
		self.log_buff.bufferMessage.connect(self.change_color)

		# create stream handlers
		log_handler = logging.StreamHandler(self.log_buff)
		log_handler.setLevel(logging.INFO)

		# set handlers up
		self.logger.setLevel(logging.INFO)
		self.logger.addHandler(log_handler)

		# define and start threads
		self.thread = LogThread(unicode(self.txt_file.text(),'utf-8'), self) 
		self.thread.start()

		self.bred.setIcon(QtGui.QIcon())
		self.byellow.setIcon(QtGui.QIcon())
		self.bgreen.setIcon(QtGui.QIcon())

		self.play_button.setEnabled(False)
		self.play_button.setText(u'')
		self.play_button.setStyleSheet('QToolButton {border: 0px;}')
		color = QtGui.QPalette(self.play_button.palette())
		color.setColor(QtGui.QPalette.Background, QtCore.Qt.transparent)
		color.setColor(QtGui.QPalette.Button, QtCore.Qt.transparent)
		self.play_button.setAutoFillBackground(True)
		self.play_button.setPalette(color)
		self.play_button.setIcon(QtGui.QIcon())

		self.paused = True

		self.rec_button.setEnabled(True)
		self.next_button.setEnabled(False)

	def start_rec(self):
		if not self.recording and self.paused: # record!
			self.block_mic = True
			self.recording = True
			self.paused = False

			self.thread.paused = False
			self.thread.blocked = False

			self.sb.showMessage(u'')

			self.rec_button.setIcon(QtGui.QIcon(
						os.path.join(info.SRC_DIR_PATH, 'images', 'pause.png')))
			self.rec_button.setIconSize(QtCore.QSize(80,80))

			self.next_button.setEnabled(False)
		elif not self.paused and self.recording: # pause
			self.thread.paused = True
			self.paused = True
			self.thread.recording = False
			self.thread.blocked = False

			if self.rec2f is not None:
				if self.rec2f.is_alive():
					self.rec2f.join()
				self.rec2f = None

			self.rec_button.setIcon(QtGui.QIcon(
						os.path.join(info.SRC_DIR_PATH, 'images', 'resume.png')))
			self.rec_button.setIconSize(QtCore.QSize(80,80))
			self.rec_button.setEnabled(False)

			self.sb.showMessage(u'')
			while self.mic_ready:
				pass

			self.rec_button.setEnabled(True)
			self.next_button.setEnabled(True)
		elif self.paused and self.recording: # resume
			self.recording = False
			self.thread.paused = False
			self.thread.recording = False
			self.thread.blocked = False

			while self.mic_ready:
				pass

			self.rec_button.setIcon(QtGui.QIcon(
						os.path.join(info.SRC_DIR_PATH, 'images', 'rec.png')))
			self.rec_button.setIconSize(QtCore.QSize(80,80))


			self.next_button.setEnabled(False)

	def wnext(self):
		self.block_mic = True
		self.thread.wnext()

		self.thread.paused = False

		self.rec_button.setIcon(QtGui.QIcon(
					os.path.join(info.SRC_DIR_PATH, 'images', 'rec.png')))
		self.rec_button.setIconSize(QtCore.QSize(80,80))
		self.rec_button.setEnabled(False)

		time.sleep(.25)

		self.paused = True
		self.recording = False

		self.rec_button.setEnabled(True)
		self.next_button.setEnabled(False)

	def clear_txt(self):
		self.txt_file.clear()
		self.txt_label.setEnabled(not self.txt_check.isChecked())
		self.txt_file.setEnabled(not self.txt_check.isChecked())
		self.txt_button.setEnabled(not self.txt_check.isChecked())

	def pause_rec(self, stream):
		stream.stop_stream()
		while self.paused or self.block_mic:
			pass
		stream.start_stream()

	def record(self):
		"""
		Record a word or words from the microphone and return the data 
		as an array of signed shorts.
		"""

		p = pyaudio.PyAudio()
		stream = p.open(input=True, 
					format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,
					frames_per_buffer=self.CHUNK_SIZE)

		self.mic_ready = True

		# wait for GUI
		if self.block_mic:
			self.pause_rec(stream)

		# record!
		r = array('h')
		while self.thread.recording:
			if self.paused:
				break
				#self.pause_rec(stream)

			snd_data = array('h', stream.read(self.CHUNK_SIZE))
			r.extend(snd_data)

		sample_width = p.get_sample_size(self.FORMAT)
		stream.stop_stream()
		stream.close()
		p.terminate()
	
		self.mic_ready = False
		return sample_width, r

	def record_to_file(self):
		"""
		Records from the microphone and outputs the resulting data to a file
		"""
		sample_width, data = self.record()
		data = struct.pack('<' + ('h'*len(data)), *data)
	
		if self.text is not None:
			wf = wave.open(unicode(self.text, 'utf-8') + '.wav', 'wb')
			wf.setnchannels(self.CHANNELS)
			wf.setsampwidth(sample_width)
			wf.setframerate(self.RATE)
			wf.writeframes(data)
			wf.close()

		del(sample_width, data)
		self.thread.recording = False
		self.block_mic = True

class LogBuffer(QtCore.QObject, StringIO.StringIO):

	bufferMessage = QtCore.pyqtSignal(str)

	def __init__(self, *args, **kwargs):
		QtCore.QObject.__init__(self)
		StringIO.StringIO.__init__(self, *args, **kwargs)

	def write(self, message):
		message = message.strip('\n')
		if message:
			self.bufferMessage.emit(message)

		StringIO.StringIO.write(self, message)


class LogThread(QtCore.QThread):

	blocked = False
	recording = False
	paused = False
	error = False

	def __init__(self, wlfile, parent=None):
		self.wlfile = wlfile
		super(LogThread, self).__init__(parent)

	def start(self):
		return super(LogThread, self).start()

	def wnext(self):
		self.i += 1

	def get_wlist(self):
		return [ 'vida', 'tubo', 'fale', 'mina', 'juba', 'paga', 'cama',\
					'gelo', 'remo', 'casa', 'morre', 'galho', 'massa', 'aqui',\
					'pasto', 'carta', 'cinto', 'tempo', 'lavam', 'anão',\
					'prato', 'claro', 'pedaço', 'mágico', 'dominó' ]

	def run(self):
		self.i = 0
		if self.wlfile == u'':
			self.wordlist = self.get_wlist()
		else:
			with open(self.wlfile, 'r') as f:
				wordlist = f.read().splitlines()

			self.wordlist = []
			for word in wordlist:
				if word not in self.wordlist:
					self.wordlist.append(word)

		while self.i < len(self.wordlist):
			if self.paused:
				logging.info('_gray')
				while self.paused:
					pass
				continue

			try:
				logging.info(unicode(self.wordlist[self.i],'utf-8').lower())
				self.recording = True
				self.blocked = True
			except UnicodeError:
				print u'A codificação do arquivo txt ou da palavra não é UTF-8'
				self.error = True
				break

			while self.blocked:
				pass

			if not self.paused:
				logging.info('_green')

			while self.recording:
				pass

		if self.error:
			logging.info('_error')
		else:
			logging.info('_finished')

### EOF ###
