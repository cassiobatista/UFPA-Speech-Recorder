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

	block_mic = True
	mic_ready = False

	text = None
	rec2f = None

	recording = False
	paused = False
	finished = False

	FORMAT = pyaudio.paInt16 # bits per sample (short)
	RATE = 22050 # Hz
	CHUNK_SIZE = 1024
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

	def __init__(self, parent, state, school, name, uid):
		super(UFPARead, self).__init__()

		self.parent = parent
		self.state = state
		self.school = school
		self.name = name
		self.uid = uid

		self.init_main_screen()
		self.init_menu()

	def init_main_screen(self):
		self.rec_button = QtGui.QPushButton()
		self.rec_button.setIcon(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'rec.png')))
		self.rec_button.setIconSize(QtCore.QSize(85,85))
		self.rec_button.setStatusTip(u'Iniciar a gravação de áudio')
		self.rec_button.setToolTip(u'Iniciar gravação')
		self.rec_button.setMinimumSize(90,90)
		self.rec_button.setFlat(True)
		self.rec_button.setStyleSheet('QPushButton:hover:!pressed' + 
					'{background-color: black; border: 3px solid lightgray;}')
		self.rec_button.clicked.connect(self.start_rec)
		self.rec_button.setShortcut(QtCore.Qt.Key_Up)

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
		self.next_button.setShortcut(QtCore.Qt.Key_Right)

		self.newreg_button = QtGui.QPushButton()
		self.newreg_button.setIconSize(QtCore.QSize(65,65))
		self.newreg_button.setStatusTip(u'Cadastrar novo aluno')
		self.newreg_button.setToolTip(u'Novo registro')
		self.newreg_button.setMinimumSize(90,90)
		self.newreg_button.setFlat(True)
		self.newreg_button.setStyleSheet('QPushButton:hover:!pressed' + 
					'{background-color: black; border: 3px solid lightgray;}')
		self.newreg_button.setEnabled(False)
		self.newreg_button.clicked.connect(self.new_reg)

		hb_rec = QtGui.QHBoxLayout()
		hb_rec.addWidget(self.newreg_button)
		hb_rec.addStretch()
		hb_rec.addWidget(self.rec_button)
		hb_rec.addWidget(self.next_button)
		#hb_rec.addSpacing(100)
		hb_rec.addStretch()

		gb_rec = QtGui.QGroupBox()
		gb_rec.setLayout(hb_rec)
		# -------------

		self.vb_layout_main = QtGui.QVBoxLayout()
		self.vb_layout_main.addWidget(gb_rec)

		wg_central = QtGui.QWidget()
		wg_central.setLayout(self.vb_layout_main)
		self.setCentralWidget(wg_central)

	def init_menu(self):
		self.act_exit = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'x.png')), u'', self)
		self.act_exit.setShortcut('Ctrl+Q')
		self.act_exit.setStatusTip(u'Fechar UFPA Speech Recorder')
		self.act_exit.setToolTip(u'Sair')
		self.act_exit.triggered.connect(self.quit_app)

		self.act_about = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'about.png')), u'', self)
		self.act_about.setShortcut('Ctrl+I')
		self.act_about.setStatusTip(u'Sobre o app')
		self.act_about.setToolTip(u'Sobre')
		self.act_about.triggered.connect(self.about)

		self.act_cfg = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'settings.png')), u'', self)
		self.act_cfg.setStatusTip(u'Configurar UFPA Speech Recorder')
		self.act_cfg.setToolTip(u'Configurações')
		#self.act_cfg.triggered.connect(self.config)

		self.act_zip = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'zip.png')), u'', self)
		self.act_zip.setStatusTip(u'Compactar pasta de áudios em um arquivo .zip')
		self.act_zip.setToolTip(u'Compactar')
		self.act_zip.triggered.connect(self.compress)

		self.act_cloud = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'cloud.png')), u'', self)
		self.act_cloud.setStatusTip(u'Fazer upload do áudios compactados para a nuvem')
		self.act_cloud.setToolTip(u'Upload')
		#self.act_cloud.triggered.connect(self.config)

		self.act_add_new = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'add.png')), u'', self)
		self.act_add_new.setShortcut('Ctrl+N')
		self.act_add_new.setStatusTip(u'Adicionar novo registro')
		self.act_add_new.setToolTip(u'Novo registro')
		self.act_add_new.triggered.connect(self.new_reg)

		self.statusBar()
		
		self.tb = QtGui.QToolBar()
		self.tb.addAction(self.act_exit)
		self.tb.addAction(self.act_about)
		self.tb.addAction(self.act_zip)
		self.tb.addAction(self.act_add_new)
		self.tb.setStyleSheet('QToolBar:focus {border:none; outline:none;}')
	
		toolbar = self.addToolBar(self.tb)

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
			reply = QtGui.QMessageBox.question(self, u'Fechar ' + info.TITLE, 
						u'A gravação não foi concluída.\n\n' + 
						u'Você deseja realmente sair?\n', 
						QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.Yes:
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

	@QtCore.pyqtSlot(str)
	def change_color(self, act):
		if act == '_finished':
			self.finished = True
			self.recording = False
			self.paused = False

			self.restore_gui()

			self.rec_button.setIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'rec.png')))
			self.rec_button.setIconSize(QtCore.QSize(80,80))
			self.rec_button.setStatusTip(u'')
			self.rec_button.setToolTip(u'')
			self.rec_button.setEnabled(False)
			self.rec_button.update()

			self.next_button.setStatusTip(u'')
			self.next_button.setToolTip(u'')

			self.newreg_button.setIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'add.png')))
			self.newreg_button.setEnabled(True)

		elif act == '_error':
			self.finished = True
			self.recording = False
			self.paused = False

			self.rec_button.setIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'rec.png')))
			self.rec_button.setIconSize(QtCore.QSize(80,80))
			self.rec_button.setStatusTip(u'Reinicia a gravação desde o início')
			self.rec_button.setToolTip(u'Reiniciar gravação')
			self.rec_button.update()
		else:
			self.block_mic = False
			self.rec2f = threading.Thread(target=self.record_to_file)
			self.rec2f.start()

			# wait for mic
			while not self.mic_ready:
				pass

			self.hide_gui()

	def hide_gui(self):
		void_icon = QtGui.QIcon()

		color = QtGui.QPalette(self.rec_button.palette())
		color.setColor(QtGui.QPalette.Background, QtCore.Qt.transparent)
		color.setColor(QtGui.QPalette.Button, QtCore.Qt.transparent)
		self.rec_button.setIcon(void_icon)
		self.rec_button.setPalette(color)

		color = QtGui.QPalette(self.next_button.palette())
		color.setColor(QtGui.QPalette.Background, QtCore.Qt.transparent)
		color.setColor(QtGui.QPalette.Button, QtCore.Qt.transparent)
		self.next_button.setIcon(void_icon)
		self.next_button.setPalette(color)

		self.newreg_button.setEnabled(False)
		color = QtGui.QPalette(self.newreg_button.palette())
		color.setColor(QtGui.QPalette.Background, QtCore.Qt.transparent)
		color.setColor(QtGui.QPalette.Button, QtCore.Qt.transparent)
		self.newreg_button.setIcon(void_icon)
		self.newreg_button.setPalette(color)

		self.tb.setMaximumHeight(0) # gambiarras

		self.rec_button.setStyleSheet('QPushButton:focus {border:none; outline:none;}')

		self.statusBar().hide()

	def restore_gui(self):
		self.rec_button.setStyleSheet('QPushButton:hover:!pressed' + 
					'{background-color: black; border: 3px solid lightgray;}')
		self.next_button.setIcon(QtGui.QIcon(info.img_path('next.png')))
		self.tb.setMaximumHeight(45)
		self.statusBar().show()

	def start_rec(self):
		if not self.paused and not self.recording: # start recording
			self.finished = False
			self.recording = True

			#self.wshow.setFrameStyle(54) # QTextEdit.frameStyle() returned 54

			self.rec_button.setIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'pause.png')))
			self.rec_button.setIconSize(QtCore.QSize(80,80))
			self.rec_button.setStatusTip(u'Pausar gravação')
			self.rec_button.setToolTip(u'Pausar gravação')
			self.rec_button.update()

			self.bred.setIcon(QtGui.QIcon())
			self.byellow.setIcon(QtGui.QIcon())
			self.bgreen.setIcon(QtGui.QIcon())

			self.hide_gui()

			self.finished = False
		elif not self.paused and self.recording: # pause recording
			self.wshow.clear()

			self.paused = True

			self.rec_button.setIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'resume.png')))
			self.rec_button.setIconSize(QtCore.QSize(80,80))
			self.rec_button.setStatusTip(u'Retomar gravação da última palavra')
			self.rec_button.setToolTip(u'Retomar gravação')
			self.rec_button.update()

			self.restore_gui()
			if self.rec2f is not None:
				self.rec2f.join()
				self.rec2f = None

			while self.mic_ready:
				pass

			self.next_button.setEnabled(True)
		elif self.paused and self.recording: # resume recording
			self.rec_button.setIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'pause.png')))
			self.rec_button.setIconSize(QtCore.QSize(80,80))
			self.rec_button.setToolTip(u'Pausar gravação')
			self.rec_button.update()

			self.hide_gui()

			self.paused = False

			while self.mic_ready:
				pass

			self.next_button.setEnabled(False)

	def wnext(self):
		time.sleep(.25)
		self.rec_button.click()
		self.paused = False

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

		# wait for GUI
		if self.block_mic:
			self.pause_rec(stream)
	
		self.mic_ready = True

		while self.thread.recording:
			if self.paused:
				self.pause_rec(stream)
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
			wf = wave.open(self.text + '.wav', 'wb')
			wf.setnchannels(self.CHANNELS)
			wf.setsampwidth(sample_width)
			wf.setframerate(self.RATE)
			wf.writeframes(data)
			wf.close()

		del(sample_width, data)
		self.thread.recording = False
		self.block_mic = True

### EOF ###
