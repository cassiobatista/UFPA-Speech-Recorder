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
from collections import deque

import info
from ufpatools import UFPAZip, UFPAUpload

class UFPARepeat(QtGui.QMainWindow):

	closed = QtCore.pyqtSignal()

	thread = None
	block_mic = True
	mic_ready = False

	text = None

	recording = False
	paused = False
	finished = False

	THRESHOLD = 600
	FORMAT = pyaudio.paInt16 # bits per sample (short)
	RATE = 22050 # Hz
	CHUNK_SIZE = 1024
	CHANNELS = 1 # mono
	WINDOW_SIZE = 6
	SILENCE_CHUNK = 20

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

	def __init__(self, parent, state, school, name, uid):
		super(UFPARepeat, self).__init__()

		self.parent = parent
		self.state = state
		self.school = school
		self.name = name
		self.uid = uid

		self.init_main_screen()
		self.init_menu()
		self.statusBar()

	def init_main_screen(self):
		self.wav_dir = QtGui.QLineEdit()
		self.wav_dir.setReadOnly(True)

		self.wav_button = QtGui.QPushButton('Procurar')
		self.wav_button.setMinimumWidth(150)
		self.wav_button.setStatusTip(u'Procurar a lista de palavras')
		self.wav_button.clicked.connect(self.select_wavdir)

		hb_wlist = QtGui.QHBoxLayout()
		hb_wlist.addWidget(QtGui.QLabel('Pasta de áudios'))
		hb_wlist.addWidget(self.wav_dir)
		hb_wlist.addWidget(self.wav_button)
		hb_wlist.addSpacing(20)

		gb_wlist = QtGui.QGroupBox()
		gb_wlist.setLayout(hb_wlist)
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

		self.prev_button = QtGui.QPushButton()
		self.prev_button.setIcon(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'previous.png')))
		self.prev_button.setIconSize(QtCore.QSize(65,65))
		self.prev_button.setStatusTip(u'Gravar a palavra anterior')
		self.prev_button.setToolTip(u'Palavra anterior')
		self.prev_button.setMinimumSize(90,90)
		self.prev_button.setFlat(True)
		self.prev_button.setStyleSheet('QPushButton:hover:!pressed' + 
					'{background-color: black; border: 3px solid lightgray;}')
		self.prev_button.setEnabled(False)
		self.prev_button.clicked.connect(self.wprev)

		self.rec_button = QtGui.QPushButton()
		self.rec_button.setIcon(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'rec.png')))
		self.rec_button.setIconSize(QtCore.QSize(85,85))
		self.rec_button.setStatusTip(u'Iniciar a gravação de áudio')
		self.rec_button.setToolTip(u'Iniciar gravação')
		self.rec_button.setShortcut('Ctrl+Space')
		self.rec_button.setMinimumSize(90,90)
		self.rec_button.setFlat(True)
		self.rec_button.setStyleSheet('QPushButton:hover:!pressed' + 
					'{background-color: black; border: 3px solid lightgray;}')
		self.rec_button.clicked.connect(self.start_rec)

		self.next_button = QtGui.QPushButton()
		self.next_button.setIcon(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'next.png')))
		self.next_button.setIconSize(QtCore.QSize(65,65))
		self.next_button.setStatusTip(u'Passar para a próxima palavra')
		self.next_button.setToolTip(u'Próxima palavra')
		self.next_button.setMinimumSize(90,90)
		self.next_button.setFlat(True)
		self.next_button.setStyleSheet('QPushButton:hover:!pressed' + 
					'{background-color: black; border: 3px solid lightgray;}')
		self.next_button.setEnabled(False)
		self.next_button.clicked.connect(self.wnext)

		hb_rec = QtGui.QHBoxLayout()
		hb_rec.addStretch()
		hb_rec.addWidget(self.prev_button)
		hb_rec.addWidget(self.rec_button)
		hb_rec.addWidget(self.next_button)
		hb_rec.addStretch()

		gb_rec = QtGui.QGroupBox()
		gb_rec.setLayout(hb_rec)
		# -------------

		self.vb_layout_main = QtGui.QVBoxLayout()
		self.vb_layout_main.addWidget(gb_wlist)
		self.vb_layout_main.addWidget(gb_wshow)
		self.vb_layout_main.addWidget(gb_semaphore)
		self.vb_layout_main.addWidget(gb_rec)

		wg_central = QtGui.QWidget()
		wg_central.setLayout(self.vb_layout_main)
		self.setCentralWidget(wg_central)

	def init_menu(self):
		act_exit = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'x.png')), '&Sair', self)
		act_exit.setShortcut('Ctrl+Q')
		act_exit.setStatusTip(u'Fechar UFPA Speech Recorder')
		act_exit.triggered.connect(self.quit_app)

		act_about = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'about.png')), '&Sobre', self)
		act_about.setShortcut('Ctrl+I')
		act_about.setStatusTip('Sobre o app')
		act_about.triggered.connect(self.about)

		act_cfg = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'settings.png')), u'&Configurações', self)
		act_cfg.setStatusTip(u'Configurar UFPA Speech Recorder')
		#act_cfg.triggered.connect(self.config)

		act_zip = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'zip.png')), u'&Compactar', self)
		act_zip.setStatusTip(u'Compactar pasta de áudios em um arquivo .zip')
		act_zip.triggered.connect(self.compress)
		act_cloud = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'cloud.png')), u'&Upload', self)

		act_cloud.setStatusTip(u'Fazer upload do áudios compactados para a nuvem')
		#act_cloud.triggered.connect(self.config)

		act_add_new = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'add.png')), '&Novo Registro', self)
		act_add_new.setShortcut('Ctrl+N')
		act_add_new.setStatusTip(u'Adicionar novo registro')
		act_add_new.triggered.connect(self.new_reg)

		self.statusBar()
	
		toolbar = self.addToolBar('Standard')
		toolbar.addAction(act_exit)
		toolbar.addAction(act_about)
		#toolbar.addAction(act_cfg)
		toolbar.addAction(act_zip)
		#toolbar.addAction(act_cloud)
		toolbar.addAction(act_add_new)

	def remove_data(self):
		state_path = os.path.join(info.ROOT_DIR_PATH, u'Estado do ' + self.state)

		# remove user dir (rm -rf)
		shutil.rmtree(os.path.join(state_path, self.school,
					self.name.split()[0].lower() + self.uid))

		# remove school dir, if empty (rmdir)
		if os.listdir(os.path.join(state_path, self.school)) == []:
			os.rmdir(os.path.join(state_path, self.school))

		# remove state dir, if empty (rmdir)
		if os.listdir(state_path) == []:
			 os.rmdir(state_path)

	def closeEvent(self, event):
		if self.finished:
			QtGui.qApp.quit()
		else:
			reply = QtGui.QMessageBox.question(self, u'Fechar app', 
						u'A reprodução não foi concluída.\n\n' + 
						u'Você deseja realmente sair?\n', 
						QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.Yes:
				if self.thread is not None:
					self.thread.i = 5000
					self.recording = False
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
			reply = QtGui.QMessageBox.question(self, u'Fechar app', 
						u'A reprodução não foi concluída.\n\n' + 
						u'Você deseja realmente sair?\n', 
						QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.Yes:
				if self.thread is not None:
					self.thread.i = 5000
					self.recording = False
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
		reply = QtGui.QMessageBox.question(self, u'Cadastrar novo contato',
					u'Deseja realizar um novo cadastro?\n',
					QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			self.hide()
			if not info.DEBUG:
				self.parent.clear()
			self.parent.show()
		else:
			return

	def select_wavdir(self):
		dirname = QtGui.QFileDialog.getExistingDirectory(self,
				u'Selecione a pasta com os áudios a serem repetidos', 
				self.last_dir, QtGui.QFileDialog.ShowDirsOnly)

		dirname = unicode(str(dirname.toUtf8()), 'utf-8')

		if dirname is not u'':
			os.chdir(info.ROOT_DIR_PATH)
			self.last_dir = dirname
			self.zipdir.setText(dirname)


	@QtCore.pyqtSlot(str)
	def change_color(self, act):
		if act == '_red':
			color = QtGui.QPalette(self.bred.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.red)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.red)
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
		elif act == '_yellow':
			if info.SYS_OS == 'windows':
				threading.Thread(target=self.record_to_file).start()

			color = QtGui.QPalette(self.bred.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.lightGray)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.lightGray)
			self.bred.setAutoFillBackground(True)
			self.bred.setPalette(color)

			color = QtGui.QPalette(self.byellow.palette())
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.yellow)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.yellow)
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
		elif act == '_green':
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
			color.setColor(QtGui.QPalette.Background, QtCore.Qt.green)
			color.setColor(QtGui.QPalette.Button, QtCore.Qt.green)
			self.bgreen.setAutoFillBackground(True)
			self.bgreen.setPalette(color)

			self.bred.update()
			self.byellow.update()
			self.bgreen.update()
		elif act == '_gray':
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
			self.recording = False
			self.paused = False

			smiley = QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images','smiley.png'))

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
			self.rec_button.setStatusTip(u'Reinicia a gravação desde o início')
			self.rec_button.setToolTip(u'Reiniciar gravação')
			self.rec_button.update()

		elif act == '_error':
			self.finished = True
			self.recording = False
			self.paused = False

			frowny = QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images','frowny.png'))

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
			self.rec_button.setStatusTip(u'Reinicia a gravação desde o início')
			self.rec_button.setToolTip(u'Reiniciar gravação')
			self.rec_button.update()
		else:
			self.block_mic = False
			if info.SYS_OS == 'linux':
				threading.Thread(target=self.record_to_file).start()

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
	
			with open(act + '.time.txt', 'w') as f:
				f.write(datetime.now().strftime('Exibição: %X:%f\n'))

	def start_rec(self):
		if self.wav_dir.text() == '':
			QtGui.QMessageBox.warning(self,
						u'Problema ao abrir pasta de áudios *.wav', 
						u'É preciso selecionar uma pasta contendo áudios.\n' +
						u'Por favor, preencha o campo corretamente.\n' +
						u'Dica: utilize o botão "Procurar" :)\n')
			return

		if not self.paused and not self.recording: # start recording
			self.recording = True
			self.wav_button.setEnabled(False)

			# create logger
			self.logger = logging.getLogger()

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
			self.thread = LogThread(unicode(self.wav_dir.text(),'utf-8'), self) 
			self.thread.start()

			self.rec_button.setIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'pause.png')))
			self.rec_button.setIconSize(QtCore.QSize(80,80))
			self.rec_button.setStatusTip(u'Pausar gravação')
			self.rec_button.setToolTip(u'Pausar gravação')
			self.rec_button.update()

			self.bred.setIcon(QtGui.QIcon())
			self.byellow.setIcon(QtGui.QIcon())
			self.bgreen.setIcon(QtGui.QIcon())

			self.finished = False
		elif not self.paused and self.recording: # pause recording
			self.thread.paused = True

			self.paused = True
			self.thread.recording = False

			self.rec_button.setIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'resume.png')))
			self.rec_button.setIconSize(QtCore.QSize(80,80))
			self.rec_button.setStatusTip(u'Retomar gravação da última palavra')
			self.rec_button.setToolTip(u'Retomar gravação')
			self.rec_button.update()

			self.bred.setIcon(QtGui.QIcon())
			self.byellow.setIcon(QtGui.QIcon())
			self.bgreen.setIcon(QtGui.QIcon())

			while self.mic_ready:
				pass

			self.prev_button.setEnabled(True)
			self.next_button.setEnabled(True)
		elif self.paused and self.recording: # resume recording
			self.rec_button.setIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'pause.png')))
			self.rec_button.setIconSize(QtCore.QSize(80,80))
			self.rec_button.setToolTip(u'Pausar gravação')
			self.rec_button.update()

			self.bred.setIcon(QtGui.QIcon())
			self.byellow.setIcon(QtGui.QIcon())
			self.bgreen.setIcon(QtGui.QIcon())

			self.paused = False
			self.thread.paused = False

			self.text = None

			while self.mic_ready:
				pass

			self.prev_button.setEnabled(False)
			self.next_button.setEnabled(False)

	def wprev(self):
		self.thread.wprev()

		time.sleep(.25)
		self.rec_button.click()

		self.paused = False
		self.thread.paused = False

	def wnext(self):
		self.thread.wnext()

		time.sleep(.25)
		self.rec_button.click()

		self.paused = False
		self.thread.paused = False

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

		def init_window(val, maxl):
			return deque([val], maxlen=maxl) 

		p = pyaudio.PyAudio()
		stream = p.open(input=True,
					format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,
					frames_per_buffer=self.CHUNK_SIZE)

		started = None
		stopped = None

		# wait for GUI
		if self.block_mic:
			self.pause_rec(stream)
	
		# Estimate initial silence
		i = 0
		r = array('h')
		initial_silence = []
		while i < 10:
			if self.paused: # paused: wait for resume button
				self.pause_rec(stream)

			snd_data = array('h', stream.read(self.CHUNK_SIZE))
			#if sys.byteorder == 'big':
			#	snd_data.byteswap()
			r.extend(snd_data)
			initial_silence.append(max(snd_data))
			i += 1

		if int(max(initial_silence)) > self.THRESHOLD:
			self.THRESHOLD = int(max(initial_silence)) 
		del(initial_silence)

		self.mic_ready = True

		speech = init_window(False, self.WINDOW_SIZE)
		times  = init_window(None, self.WINDOW_SIZE)
		detected = False
		while self.thread.recording:
			if self.paused:
				self.pause_rec(stream)

			snd_data = array('h', stream.read(self.CHUNK_SIZE))
			times.append(datetime.now())
			r.extend(snd_data)
	
			voiced = (int(max(snd_data)) > self.THRESHOLD)
			speech.append(voiced)
	
			#if not silence and speech_count < self.SPEECH_CHUNK:
			#	speech[speech_count] = True
			#	times[speech_count]  = datetime.now().strftime('%X:%f\n')
			#	speech_count += 1
			#elif silence and all(speech) == False:
			#	speech = [False] * self.SPEECH_CHUNK
			#	times = [None] * self.SPEECH_CHUNK
			#	speech_count = 0
			#elif silence and all(speech):
			#	achei = True
			#	silence = True

			if not detected and all(speech):
				detected = True
				started = times.popleft()
				break

		silence = init_window(False, self.WINDOW_SIZE)
		times   = init_window(None,  self.WINDOW_SIZE)
		detected = False
		while self.thread.recording:
			if self.paused:
				self.pause_rec(stream)

			snd_data = array('h', stream.read(self.CHUNK_SIZE))
			times.append(datetime.now())
			r.extend(snd_data)
	
			unvoiced = (int(max(snd_data)) < self.THRESHOLD)
			silence.append(unvoiced)
	
			if not detected and all(silence):
				detected = True
				stopped = times.popleft()

		click_time = datetime.now()
		del(speech, silence, times)

		if self.text is not None:
			with open(self.text + '.time.txt', 'a') as f:
				if started is not None:
					f.write(started.strftime(u'Início da fala: %X.%f\n'))
				else:
					f.write(u'Início da fala: -- \n')
				if stopped is not None:
					f.write(stopped.strftime(u'Fim da fala: %X.%f\n'))
				else:
					f.write(u'Fim da fala: -- \n')

		with open(self.text + '.time.txt', 'a') as f:
			f.write(click_time.strftime(u'Ocultação: %X.%f\n'))

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
			wf = wave.open(self.text + '.wav', 'wb')
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

	recording = False
	paused = False
	wavlist = None
	error = False

	def __init__(self, wlfile, parent=None):
		self.wlfile = wlfile
		super(LogThread, self).__init__(parent)

	def start(self):
		return super(LogThread, self).start()

	def wnext(self):
		self.i += 1

	def wprev(self):
		self.i -= 1

	def run(self):
		wavlist = f.read().splitlines()
		self.wavlist = [wav.lower() for wav in wavlist]
		self.i = 0

		wcolors = ['_red', '_yellow', '_green']
		while self.i < len(self.wavlist):
			for c in wcolors:
				if self.paused:
					break
				time.sleep(.5)
				logging.info(c)
				time.sleep(.5)

			if self.paused:
				logging.info('_gray')
				while self.paused:
					pass
				continue

			if self.i < 0:
				self.i = 0

			try:
				logging.info(unicode(self.wavlist[self.i], 'utf-8'))
				self.recording = True
			except UnicodeError:
				print u'A codificação do arquivo txt ou da palavra não é UTF-8'
				self.error = True
				break

			while self.recording:
				pass

		if self.error:
			logging.info('_error')
		else:
			logging.info('_finished')

### EOF ###