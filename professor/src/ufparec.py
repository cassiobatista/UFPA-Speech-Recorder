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
import random
import shutil

from PyQt4 import QtCore, QtGui
from ufpatools import UFPAZip, UFPAUpload

import logging
import StringIO

import threading
import pyaudio
import wave
import struct 
from collections import deque
from array import array

import info


class UFPARecord(QtGui.QMainWindow):

	closed = QtCore.pyqtSignal()

	thread = None
	block_mic = True
	mic_ready = False

	recording = False
	paused = False
	finished = False

	THRESHOLD = 600
	FORMAT = pyaudio.paInt16 # bits per sample (short)
	RATE = 22050 # Hz
	FRAMES_PER_BUFFER = 1024
	CHANNELS = 1 # mono
	WINDOW_SIZE = 6

	last_dir = info.ROOT_DIR_PATH

	def __init__(self, parent, state, school, applier, uid):
		super(UFPARecord, self).__init__()

		self.parent = parent
		self.state = state
		self.school = school
		self.applier = applier
		self.uid = uid

		self.init_main_screen()
		self.init_menu()
		self.statusBar()

	def compress(self):
		self.czip = UFPAZip(self)
		self.czip.closed.connect(self.show)
		self.czip.move(230,30) # try to centralize
		self.czip.setMinimumSize(800, 200) # define initial size
		self.czip.setWindowTitle(info.TITLE)
		self.czip.setWindowIcon(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'ufpa.png')))
		self.czip.show()


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
		self.txt_button.setStatusTip(u'Procurar a lista de palavras')
		self.txt_button.setEnabled(False)
		self.txt_button.clicked.connect(self.open_wlist_file)

		hb_wlist = QtGui.QHBoxLayout()
		hb_wlist.addWidget(self.txt_label)
		hb_wlist.addWidget(self.txt_file)
		hb_wlist.addWidget(self.txt_button)
		hb_wlist.addSpacing(20)

		vb_wlist = QtGui.QVBoxLayout()
		vb_wlist.addWidget(self.txt_check)
		vb_wlist.addLayout(hb_wlist)
		# -------------

		self.wshow = QtGui.QLabel()
		self.wshow.setMinimumWidth(800)
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
		self.prev_button.setShortcut(QtCore.Qt.Key_Left)
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
		self.rec_button.setShortcut(QtCore.Qt.Key_Up)
		self.rec_button.setMinimumSize(90,90)
		self.rec_button.setFlat(True)
		self.rec_button.setStyleSheet('QPushButton:hover:!pressed' + 
					'{background-color: black; border: 3px solid lightgray;}')
		self.rec_button.clicked.connect(self.start_rec)

		hb_rec = QtGui.QHBoxLayout()
		hb_rec.addStretch()
		hb_rec.addWidget(self.prev_button)
		hb_rec.addWidget(self.rec_button)
		hb_rec.addSpacing(100)
		hb_rec.addStretch()

		gb_rec = QtGui.QGroupBox()
		gb_rec.setLayout(hb_rec)
		# -------------

		self.vb_layout_main = QtGui.QVBoxLayout()
		self.vb_layout_main.addLayout(vb_wlist)
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
					self.applier.split()[0].lower() + self.uid))

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
			reply = QtGui.QMessageBox.question(self, u'Fechar ' + info.TITLE, 
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
			reply = QtGui.QMessageBox.question(self, u'Fechar ' + info.TITLE, 
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

	def clear_txt(self):
		self.txt_file.clear()
		self.txt_label.setEnabled(not self.txt_check.isChecked())
		self.txt_file.setEnabled(not self.txt_check.isChecked())
		self.txt_button.setEnabled(not self.txt_check.isChecked())

	def start_rec(self):
		if self.txt_file.text() == '' and self.txt_check.isChecked() == False:
			QtGui.QMessageBox.warning(self,
						u'Problema ao carregar arquivo *.txt', 
						u'É preciso carregar uma lista de palavras.\n' +
						u'Caso contrário, deixe a opção acima marcada.\n')
			return

		if not self.paused and not self.recording: # start recording
			self.recording = True
			self.txt_check.setEnabled(False)
			self.txt_label.setEnabled(False)
			self.txt_button.setEnabled(False)
			self.txt_file.setEnabled(False)

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
		elif not self.paused and self.recording: # pause recording
			self.thread.paused = True

			self.text = unicode(self.wshow.text().toUtf8(), 'utf-8')
			self.wshow.clear()

			if len(self.text) > 1:
				self.thread.wprev(1)
				time.sleep(.25)

			self.paused = True
			self.thread.recording = False

			self.rec_button.setIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'resume.png')))
			self.rec_button.setIconSize(QtCore.QSize(80,80))
			self.rec_button.setStatusTip(u'Retomar gravação da última palavra')
			self.rec_button.setToolTip(u'Retomar gravação')
			self.rec_button.update()

			self.prev_button.setEnabled(True)

			self.bred.setIcon(QtGui.QIcon())
			self.byellow.setIcon(QtGui.QIcon())
			self.bgreen.setIcon(QtGui.QIcon())

			time.sleep(.25)
		elif self.paused and self.recording: # resume recording
			self.rec_button.setIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'pause.png')))
			self.rec_button.setIconSize(QtCore.QSize(80,80))
			self.rec_button.setToolTip(u'Pausar gravação')
			self.rec_button.update()

			self.bred.setIcon(QtGui.QIcon())
			self.byellow.setIcon(QtGui.QIcon())
			self.bgreen.setIcon(QtGui.QIcon())

			self.prev_button.setEnabled(False)

			self.paused = False
			self.thread.paused = False

	def wprev(self):
		self.thread.wprev(1)

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
					frames_per_buffer=self.FRAMES_PER_BUFFER)

		# wait for GUI
		if self.block_mic:
			self.pause_rec(stream)
	
		# Estimate initial silence
		i = 0
		r = array('h')
		initial_silence = []
		frame_count = 0
		while i < 10:
			if self.paused: # paused: wait for resume button
				self.pause_rec(stream)

			snd_data = array('h', stream.read(self.FRAMES_PER_BUFFER))
			frame_count += 1
			r.extend(snd_data)
			initial_silence.append(max(snd_data))
			i += 1

		if int(max(initial_silence)) > self.THRESHOLD:
			self.THRESHOLD = int(max(initial_silence)) 
		del(initial_silence)

		self.mic_ready = True

		speech = init_window(False, self.WINDOW_SIZE)
		while self.thread.recording:
			if self.paused:
				self.pause_rec(stream)

			snd_data = array('h', stream.read(self.FRAMES_PER_BUFFER))
			frame_count += 1
			r.extend(snd_data)
	
			voiced = (int(max(snd_data)) > self.THRESHOLD)
			speech.append(voiced)
			if all(speech):
				break

		silence = init_window(False, self.WINDOW_SIZE)
		while self.thread.recording:
			if self.paused:
				self.pause_rec(stream)

			snd_data = array('h', stream.read(self.FRAMES_PER_BUFFER))
			frame_count += 1
			r.extend(snd_data)
	
			unvoiced = (int(max(snd_data)) < self.THRESHOLD)
			silence.append(unvoiced)
			if all(silence):
				break

		del(speech, silence)
	
		sil_sample = (frame_count+1-self.WINDOW_SIZE)*self.FRAMES_PER_BUFFER

		sample_width = p.get_sample_size(self.FORMAT)
		stream.stop_stream()
		stream.close()
		p.terminate()
	
		self.mic_ready = False
		return sample_width, r, sil_sample
	
	def record_to_file(self):
		"""
		Records from the microphone and outputs the resulting data to a file
		"""
		sample_width, data, sil_sample = self.record()
		data = struct.pack('<' + ('h'*len(data)), *data)
	
		path = str(self.wshow.text().toUtf8())
		if path is not '':
			wf = wave.open(unicode(path, 'utf-8') + '.wav', 'wb')
			wf.setnchannels(self.CHANNELS)
			wf.setsampwidth(sample_width)
			wf.setframerate(self.RATE)
			wf.writeframes(data)
			wf.close()

			with open(unicode(path, 'utf-8') + '.ss.txt', 'wb') as fs:
				fs.write('%d' % sil_sample)

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
	wordlist = None
	error = False

	def __init__(self, wlfile, parent=None):
		self.wlfile = wlfile
		super(LogThread, self).__init__(parent)

	def start(self):
		return super(LogThread, self).start()

	def wprev(self, idx):
		self.i -= idx

	def get_wlist(self):
		return [ 'Vida', 'Tubo', 'Fale', 'Mina', 'Juba', 'Paga', 'Cama',\
				'Gelo', 'Remo', 'Casa', 'Morre', 'Galho', 'Massa', 'Aqui',\
				'Pasto', 'Carta', 'Cinto', 'Tempo', 'Lavam', 'Anão', 'Prato',\
				'Claro', 'Pedaço', 'Mágico', 'Dominó' ]

	def run(self):
		self.i = 0
		if self.wlfile == u'':
			self.wordlist = self.get_wlist()
		else:
			with open(self.wlfile, 'r') as f:
				self.wordlist = f.read().splitlines()

		random.shuffle(self.wordlist)

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

			self.i += 1

		if self.error:
			logging.info('_error')
		else:
			logging.info('_finished')

### EOF ###
