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
reload(sys)
sys.setdefaultencoding('utf8')

import os
import time

from PyQt4 import QtCore, QtGui
from datetime import datetime

import logging
import StringIO

import threading
import pyaudio
import wave
import struct 
import shutil
from array import array
from collections import deque

import info
from ufpatools import UFPAZip, UFPAUpload

class UFPARecord(QtGui.QMainWindow):

	closed = QtCore.pyqtSignal()

	thread = None
	block_mic = True
	mic_ready = False

	text = None

	recording = False
	paused = False
	finished = False

	FORMAT = pyaudio.paInt16 # bits per sample (short)
	RATE = 22050 # Hz
	CHUNK_SIZE = 1024
	CHANNELS = 1 # mono
	SPEECH_CHUNK = 6
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
		super(UFPARecord, self).__init__()

		self.parent = parent
		self.state = state
		self.school = school
		self.name = name
		self.uid = uid

		self.init_main_screen()
		self.init_menu()
		self.statusBar()

	def init_main_screen(self):
		self.txt_file = QtGui.QLineEdit()
		self.txt_file.setReadOnly(True)
		if info.DEBUG:
			self.txt_file.setText(os.path.join(
						info.ROOT_DIR_PATH, 'exemplo.txt'))

		self.txt_button = QtGui.QPushButton('Procurar')
		self.txt_button.setMinimumWidth(150)
		self.txt_button.setStatusTip(u'Procurar a lista de palavras')
		self.txt_button.clicked.connect(self.open_wlist_file)

		hb_wlist = QtGui.QHBoxLayout()
		hb_wlist.addWidget(QtGui.QLabel('Lista de palavras'))
		hb_wlist.addWidget(self.txt_file)
		hb_wlist.addWidget(self.txt_button)
		hb_wlist.addSpacing(20)

		gb_wlist = QtGui.QGroupBox()
		gb_wlist.setLayout(hb_wlist)
		# -------------

		self.wshow = QtGui.QLabel()
		self.wshow.setFixedWidth(800)
		self.wshow.setFixedHeight(180)
		self.wshow.setStatusTip(u'As palavras da lista serão exibidas aqui')
		self.wshow.setAlignment(QtCore.Qt.AlignCenter)

		hb_wshow = QtGui.QHBoxLayout()
		hb_wshow.addWidget(self.wshow)

		gb_wshow = QtGui.QGroupBox()
		gb_wshow.setLayout(hb_wshow)
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
						u'A gravação não foi concluída.\n\n' + 
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
						u'A gravação não foi concluída.\n\n' + 
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
		if act == '_red':
			self.wshow.clear()

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
				threading.Thread(target=self.record).start()

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

			font = QtGui.QFont(self.wshow.font())
			font.setPointSize(18)
			self.wshow.setFont(font)
			self.wshow.setText(u'Gravação concluída com sucesso. Obrigado!')

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

			font = QtGui.QFont(self.wshow.font())
			font.setPointSize(22)
			self.wshow.setFont(font)
			self.wshow.setText(u'Algum erro inesperado ocorreu.')

			self.rec_button.setIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'rec.png')))
			self.rec_button.setIconSize(QtCore.QSize(80,80))
			self.rec_button.setStatusTip(u'Reinicia a gravação desde o início')
			self.rec_button.setToolTip(u'Reiniciar gravação')
			self.rec_button.update()
		else:
			self.block_mic = False
			if info.SYS_OS == 'linux':
				threading.Thread(target=self.record, args=(act,)).start()

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

			#self.block_mic = False

			self.bred.update()
			self.byellow.update()
			self.bgreen.update()
	
			font = QtGui.QFont(self.wshow.font())
			if len(act) < 15:
				font.setPointSize(66)
			elif len(act) < 30:
				font.setPointSize(44)
			else:
				font.setPointSize(22)
			font.setBold(True)
			self.wshow.setFont(font)
			self.wshow.setText(act)

			with open(act+'.time.txt', 'w') as f:
				f.write(datetime.now().strftime(u'Exibição da palavra: %X:%f\n'))

	def start_rec(self):
		if self.txt_file.text() == '':
			QtGui.QMessageBox.warning(self,
						u'Problema ao carregar arquivo *.txt', 
						u'É preciso carregar uma lista de palavras.\n' +
						u'Por favor, preencha o campo corretamente.\n' +
						u'Dica: utilize o botão "Procurar" :)\n')
			return

		# --- start recording ---
		if not self.paused and not self.recording: 
			self.recording = True
			self.txt_button.setEnabled(False)

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
			self.thread = LogThread(unicode(self.txt_file.text(),'utf-8'), self) 
			self.thread.start()

			self.wshow.setFrameStyle(54) # QTextEdit.frameStyle() returned 54

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
		# --- pause recording ---
		elif not self.paused and self.recording:
			self.thread.paused = True

			self.text = unicode(self.wshow.text().toUtf8(), 'utf-8')
			self.wshow.clear()

			self.paused = True
			self.thread.recording = False

			self.rec_button.setIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'resume.png')))
			self.rec_button.setIconSize(QtCore.QSize(80,80))
			self.rec_button.setStatusTip(u'Retomar gravação da palavra atual')
			self.rec_button.setToolTip(u'Retomar gravação')
			self.rec_button.update()

			self.bred.setIcon(QtGui.QIcon())
			self.byellow.setIcon(QtGui.QIcon())
			self.bgreen.setIcon(QtGui.QIcon())

			while self.mic_ready:
				pass

			self.prev_button.setEnabled(True)
			self.next_button.setEnabled(True)
		# --- resume recording ---
		elif self.paused and self.recording:
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

	def pause_rec(self, stream, timestamps):
		stream.stop_stream()
		timestamps.stop()

		while self.paused or self.block_mic:
			pass
		stream.start_stream()

	# https://people.csail.mit.edu/hubert/pyaudio/docs/
	# TODO: endianness!
	def callback_parent(self):
		def callback(in_data, frame_count, time_info, status):
			self.qtimes.append(datetime.now())
			self.qsamples.append(in_data)
			self.wavlock.acquire()
			self.wavfile.writeframes(in_data)
			self.wavlock.release()
			return (in_data, pyaudio.paContinue)
		return callback

	def record(self, word):
		self.qsamples = deque(maxlen=10)
		self.qtimes = deque(maxlen=4)

		self.wavlock = threading.Lock()

		p = pyaudio.PyAudio()
		stream = p.open(format=self.FORMAT, channels=self.CHANNELS, 
					rate=self.RATE, frames_per_buffer=self.CHUNK_SIZE,
					input=True, start=False,
					stream_callback=self.callback_parent())

		#wavname = os.path.join(tempfile.gettempdir(), 'rec.wav')
		#self.wavfile = wave.open(wavname, 'wb')
		word = unicode(str(word), 'utf-8') 
		self.wavfile = wave.open(word+'.wav', 'wb')
		self.wavfile.setnchannels(self.CHANNELS)
		self.wavfile.setsampwidth(p.get_sample_size(self.FORMAT))
		self.wavfile.setframerate(self.RATE)

		print '0: startstream'
		tstamps = SpeechDetection(self.qsamples, self.qtimes, word)
		tstamps.start()
		stream.start_stream()

		self.mic_ready = True

		# wait for GUI
		if self.block_mic:
			self.pause_rec(stream, tstamps)

		while not self.paused:
			pass

		self.mic_ready = False
		self.thread.recording = False
		self.block_mic = True

		while self.wavlock.locked():
			pass

		self.wavlock.acquire()
		print '0: wavclose'
		self.wavfile.close()
		#print '1: stopstream'
		#stream.stop_stream() # stop strem
		print '2: closestream'
		stream.close() # close stream
		print '3: pyterm'
		p.terminate() # destroy pyaudio obj
		self.wavlock.release()

		tstamps.stop()
		tstamps.join()

		#os.rename(wavname, self.text+'.wav')
	
		self.mic_ready = False
		self.thread.recording = False
		self.block_mic = True

# http://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread-in-python
class SpeechDetection(threading.Thread):

	started = None
	stopped = None

	THRESHOLD = 600

	def __init__(self, q, t, w):
		threading.Thread.__init__(self)
		# or super(SpeechDetection, self).__init__()
		self.samples = q
		self.times = t
		self.word = w
		self.event = threading.Event()

	def init_window(self, val):
		return deque([val], maxlen=6) 

	def stop(self):
		self.event.set()
		self.samples.clear()
		self.times.clear()

	def run(self):
		# Estimate initial silence
		initial_silence = []
		for i in xrange(10):
			while not len(self.samples):
				pass

			snd_data = array('h', self.samples.pop())
			initial_silence.append(max(snd_data))

		if int(max(initial_silence)) > self.THRESHOLD:
			self.THRESHOLD = int(max(initial_silence)) 
		del(initial_silence)

		if info.DEBUG:
			print 'thresh:', self.THRESHOLD

		if self.THRESHOLD > 8000:
			print u'Nível de ruído alto demais.'
			self.stop()
			return
	
		speech = self.init_window(False)
		detected = False
		while not self.event.is_set():
			while not len(self.samples):
				pass

			snd_data = array('h', self.samples.popleft())
			voiced = (int(max(snd_data)) > self.THRESHOLD)

			speech.append(voiced)
			if all(speech):
				detected = True
				break

		if detected:
			self.started = self.times.popleft()
			if info.DEBUG:
				sys.stdout.write('started: %s\n' % self.started)

			with open(self.word+'.time.txt', 'a') as f:
				f.write(self.started.strftime('Início da fala: %X.%f\n'))
		else:
			print 'speech not detected'
			#self.stop()
			return

		silence = self.init_window(False)
		detected = False
		while not self.event.is_set():
			while not len(self.samples):
				pass

			snd_data = array('h', self.samples.popleft())
			unvoiced = (int(max(snd_data)) < self.THRESHOLD)

			silence.append(unvoiced)
			if all(silence):
				detected = True
				break

		if detected:
			self.stopped = self.times.popleft()
			if info.DEBUG:
				sys.stdout.write('stopped: %s\n' % self.stopped)

			with open(self.word+'.time.txt', 'a') as f:
				f.write(self.started.strftime('Fim da fala: %X.%f\n'))
		else:
			print 'end point not detected'

		#self.stop()
		return


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
	wordlist = None
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
		with open(self.wlfile, 'r') as f:
			self.wordlist = f.read().splitlines()
			self.i = 0

		wcolors = ['_red', '_yellow', '_green']
		while self.i < len(self.wordlist):
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
				logging.info(unicode(self.wordlist[self.i], 'utf-8'))
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
