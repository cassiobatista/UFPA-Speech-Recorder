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
# Author Feb 2017:
# Cassio Trindade Batista - cassio.batista.13@gmail.com
# Nelson C. Sampaio Neto  - dnelsonneto@gmail.com


import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
import re
import zipfile
import info

from PyQt4 import QtCore, QtGui


class UFPAConfig(QtGui.QWidget):
	def __init__(self, parent=None):
		super(UFPAConfig, self).__init__()
		self.parent = parent
		self.init_main_screen()

	def init_main_screen(self):
		pass

	def config(self):
		if os.path.exists(os.path.join(info.SRC_DIR_PATH, 'ufpasrconfig')):
			pass


class UFPAZip(QtGui.QMainWindow):

	closed = QtCore.pyqtSignal()
	last_dir = info.ROOT_DIR_PATH

	def __init__(self, parent=None):
		super(UFPAZip, self).__init__()
		self.parent = parent
		self.init_main_screen()

	def init_main_screen(self):
		self.zipdir = QtGui.QLineEdit(self)
		self.zipdir.setReadOnly(True)

		self.zipdir_button = QtGui.QPushButton(u'Procurar')
		self.zipdir_button.setMinimumWidth(150)
		self.zipdir_button.setStatusTip(u'Procurar pasta para ser compactada')
		self.zipdir_button.clicked.connect(self.select_zipdir)

		hb_zipdir = QtGui.QHBoxLayout()
		hb_zipdir.addWidget(QtGui.QLabel(u'Pasta'))
		hb_zipdir.addWidget(self.zipdir)
		hb_zipdir.addWidget(self.zipdir_button)
		hb_zipdir.addSpacing(20)

		gb_zipdir = QtGui.QGroupBox(u'Compactar uma pasta em um arquivo .zip')
		gb_zipdir.setLayout(hb_zipdir)
		# ---------------------

		self.compress_button = QtGui.QPushButton(u'Compactar')
		self.compress_button.setMinimumWidth(130)
		self.compress_button.setMinimumHeight(50)
		self.compress_button.setStatusTip(u'Clique para "zipar" a pasta selecionada')
		self.compress_button.clicked.connect(self.compress)

		self.cancel_button = QtGui.QPushButton(u'Cancelar')
		self.cancel_button.setMinimumWidth(130)
		self.cancel_button.setMinimumHeight(50)
		self.cancel_button.setStatusTip(u'Clique para cancelar/sair')
		self.cancel_button.setShortcut('Ctrl+Q')
		self.cancel_button.clicked.connect(self.close)

		hb_compress = QtGui.QHBoxLayout()
		hb_compress.addStretch()
		hb_compress.addWidget(self.cancel_button)
		hb_compress.addWidget(self.compress_button)

		gb_compress = QtGui.QGroupBox()
		gb_compress.setLayout(hb_compress)
		# ---------------------

		self.vb_layout_main = QtGui.QVBoxLayout()
		self.vb_layout_main.addWidget(gb_zipdir)
		self.vb_layout_main.addWidget(gb_compress)

		wg_central = QtGui.QWidget()
		wg_central.setLayout(self.vb_layout_main)

		self.setCentralWidget(wg_central)

		self.select_zipdir()

	def select_zipdir(self):
		dirname = QtGui.QFileDialog.getExistingDirectory(self,
				u'Selecione a pasta a ser compactada', 
				self.last_dir, QtGui.QFileDialog.ShowDirsOnly)

		dirname = unicode(str(dirname.toUtf8()), 'utf-8')

		if dirname is not u'':
			os.chdir(info.ROOT_DIR_PATH)
			self.last_dir = dirname
			self.zipdir.setText(dirname)

	# https://pymotw.com/2/zipfile/
	# http://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory
	def compress(self):
		try:
			import zlib
			cmode = zipfile.ZIP_DEFLATED
		except ImportError:
			print u'Aviso: Arquivo .zip será criado sem compressão.'
			cmode = zipfile.ZIP_STORED

		if self.zipdir.text() == '':
			QtGui.QMessageBox.warning(self,
						u'Problema ao abrir diretório para compressão.\n', 
						u'Por favor, preencha o campo corretamente.\n' +
						u'Dica: utilize o botão "Procurar" :)\n')
			return

		dirname = unicode(self.zipdir.text().toUtf8(), 'utf-8')
		basename = os.path.basename(dirname)

		try:
			zf = zipfile.ZipFile(basename+'.zip', mode='w', compression=cmode)
			for root, dirs, files in os.walk(dirname):
				ziproot = re.sub('.*'+basename, basename, root)
				for f in files:
					longpath  = unicode(str(os.path.join(root, f)), 'utf-8')
					shortpath = unicode(str(os.path.join(ziproot, f)), 'utf-8')
					zf.write(longpath,
							arcname=shortpath.encode(sys.stdout.encoding))
			zf.close()

			QtGui.QMessageBox.information(self, 
						u'Arquivo zipado com sucesso!',
						u'O arquivo <b>%s.zip</b>' % basename + ' foi criado!')

			self.close()
		except IOError:
			reply = QtGui.QMessageBox.critical(self, 
						u'Erro ao criar arquivo compactado',
						u'Ocorreu algum erro inesperado ao tentar criar o ' +
						u'arquivo <b>%s</b>.' % basename + '\n'
						u'Deseja tentar novamente?\n',
						QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				return
			else:
				self.close()

class UFPAUpload(QtGui.QMainWindow):

	closed = QtCore.pyqtSignal()
	last_dir = info.ROOT_DIR_PATH

	def __init__(self, parent=None):
		super(UFPAUpload, self).__init__()
		self.parent = parent
		self.init_main_screen()

	def init_main_screen(self):
		self.zippath = QtGui.QLineEdit()
		self.zippath.setReadOnly(True)

		self.zippath_button = QtGui.QPushButton(u'Procurar')
		self.zippath_button.setMinimumWidth(150)
		self.zippath_button.setStatusTip(u'Procurar arquivo .zip')
		self.zippath_button.setToolTip(u'Procurar arquivo .zip')
		self.zippath_button.clicked.connect(self.select_zip)

		hb_zippath = QtGui.QHBoxLayout()
		hb_zippath.addWidget(QtGui.QLabel(u'Arquivo'))
		hb_zippath.addWidget(self.zippath)
		hb_zippath.addSpacing(20)
		hb_zippath.addWidget(self.zippath_button)

		gb_zippath = QtGui.QGroupBox(u'Enviar arquivo .zip por email')
		gb_zippath.setLayout(hb_zippath)
		# ---------------------

		self.frommail = QtGui.QLineEdit(self)

		hb_frommail = QtGui.QHBoxLayout()
		hb_frommail.addWidget(QtGui.QLabel(u'De:   '))
		hb_frommail.addWidget(self.frommail)

		gb_frommail = QtGui.QVBoxLayout()
		gb_frommail.addLayout(hb_frommail)
		# ---------------------

		self.tomail = QtGui.QLineEdit()

		self.tomail_button = QtGui.QPushButton(u'Adicionar')
		self.tomail_button.setMinimumWidth(140)
		self.tomail_button.setStatusTip(u'Adicionar email à lista de destinatários')
		self.tomail_button.setToolTip(u'Adicionar email')
		self.tomail_button.clicked.connect(self.add_email)

		hb_tomail = QtGui.QHBoxLayout()
		hb_tomail.addWidget(QtGui.QLabel(u'Para:'))
		hb_tomail.addWidget(self.tomail)
		hb_tomail.addSpacing(10)
		hb_tomail.addWidget(self.tomail_button)

		gb_tomail = QtGui.QVBoxLayout()
		gb_tomail.addLayout(hb_tomail)
		# ---------------------

		self.destin = QtGui.QListWidget()
		self.destin.setStyleSheet('QListWidget:item {' + 
					'border-bottom: 2px dotted black;}')

		hb_destin = QtGui.QHBoxLayout()
		hb_destin.addSpacing(40)
		hb_destin.addWidget(self.destin)

		gb_destin = QtGui.QVBoxLayout()
		gb_destin.addLayout(hb_destin)
		# ---------------------

		self.send_button = QtGui.QPushButton(u'Enviar')
		self.send_button.setMinimumWidth(130)
		self.send_button.setMinimumHeight(50)
		self.send_button.setStatusTip(u'Clique para "zipar" a pasta selecionada')
		self.send_button.clicked.connect(self.send_email)

		self.cancel_button = QtGui.QPushButton(u'Cancelar')
		self.cancel_button.setMinimumWidth(130)
		self.cancel_button.setMinimumHeight(50)
		self.cancel_button.setStatusTip(u'Clique para cancelar/sair')
		self.cancel_button.setShortcut('Ctrl+Q')
		self.cancel_button.clicked.connect(self.close)

		hb_send = QtGui.QHBoxLayout()
		hb_send.addStretch()
		hb_send.addWidget(self.cancel_button)
		hb_send.addWidget(self.send_button)

		gb_send = QtGui.QVBoxLayout()
		gb_send.addLayout(hb_send)
		# ---------------------

		self.vb_layout_main = QtGui.QVBoxLayout()
		self.vb_layout_main.addWidget(gb_zippath)
		self.vb_layout_main.addLayout(gb_frommail)
		self.vb_layout_main.addSpacing(10)
		self.vb_layout_main.addLayout(gb_tomail)
		self.vb_layout_main.addLayout(gb_destin)
		self.vb_layout_main.addLayout(gb_send)

		wg_central = QtGui.QWidget()
		wg_central.setLayout(self.vb_layout_main)

		self.setCentralWidget(wg_central)

	def add_email(self):
		if self.tomail.text() == '':
			QtGui.QMessageBox.warning(self, u'Erro ao adicionar email',
						u'Nenhum email para adicionar à lista.\n' + 
						u'Por favor, preencha o campo "Para".\n')
			return
		elif len(self.tomail.text()) < 10 or not '@' in self.tomail.text():
			QtGui.QMessageBox.warning(self, u'Erro ao adicionar email',
						u'O email indicado não parece válido.\n' + 
						u'Por favor, preencha o campo "Para" corretamente.\n')
			return

		email = unicode(self.tomail.text().toUtf8(), 'utf-8')

		self.tomail.clear()
		self.destin.addItem(email)

	def select_zip(self):
		filename = QtGui.QFileDialog.getOpenFileName(self,
				u'Procurar arquivo compactado (.zip) para upload', 
				self.last_dir, u'(*.zip)')

		filename = unicode(str(filename.toUtf8()), 'utf-8')

		if filename is not u'':
			self.zippath.setText(filename)
			self.last_dir = os.path.dirname(filename)
		pass

	def send_email(self):
		pass

### EOF ###
