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
import zipfile
import info

from PyQt4 import QtCore, QtGui

class UFPAConfig(QtGui.QWidget):
	def __init__(self, last_dir):
		super(UFPAConfig, self).__init__()
		self.last_dir = last_dir

	def config(self):
		if os.path.exists(os.path.join(info.SRC_DIR_PATH, 'ufpasrconfig')):
			pass

class UFPAZip(QtGui.QWidget):

	closed = QtCore.pyqtSignal()
	last_dir = info.ROOT_DIR_PATH

	def __init__(self, parent=None):
		super(UFPACompress, self).__init__()
		self.parent = parent
		self.init_main_screen()

	def init_main_screen(self):
		self.zipdir = QtGui.QLineEdit()
		self.zipdir.setReadOnly(True)

		self.zipdir_button = QtGui.QPushButton('Procurar')
		self.zipdir_button.setMinimumWidth(150)
		self.zipdir_button.setStatusTip(u'Procurar pasta para ser compactada')
		self.zipdir_button.clicked.connect(self.select_zipdir)

		hb_zipdir = QtGui.QHBoxLayout()
		hb_zipdir.addWidget(QtGui.QLabel('Pasta'))
		hb_zipdir.addWidget(self.zipdir)
		hb_zipdir.addWidget(self.zipdir_button)
		hb_zipdir.addSpacing(20)

		gb_zipdir = QtGui.QGroupBox()
		gb_zipdir.setLayout(hb_zipdir)
		# ---------------------

		self.compress_button = QtGui.QPushButton('Compactar')
		self.compress_button.setMinimumWidth(150)
		self.compress_button.setMinimumHeight(150)
		self.compress_button.setStatusTip(u'Clique para "zipar" a pasta selecionada')
		self.compress_button.clicked.connect(self.compress)

		hb_compress = QtGui.QHBoxLayout()
		hb_compress.addStretch()
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

	def select_zipdir(self):
		dirname = QtGui.QFileDialog.getExistingDirectory(self,
				u'Selecionar pasta contendo arquivos a serem compactados', 
				self.last_dir, QtGui.QFileDialog.ShowDirsOnly)

		dirname = unicode(str(dirname.toUtf8()), 'utf-8')

		if dirname is not u'':
			os.chdir(info.ROOT_DIR_PATH)
			self.last_dir = dirname
			dirname = dirname.replace(info.ROOT_DIR_PATH + u'/', u'')
			self.zip_dir.setText(dirname)

	# https://pymotw.com/2/zipfile/
	def compress(self):
		try:
			import zlib
			compress = zipfile.ZIP_DEFLATED
		except ImportError:
			compress = zipfile.ZIP_STORED

		if self.zip_dir.text() == '':
			QtGui.QMessageBox.warning(self,
						u'Problema ao abrir diretório para compressão', 
						u'Por favor, preencha o campo corretamente.\n' +
						u'Dica: utilize o botão "Procurar" :)\n')
			return

		zipname = unicode(self.zip_dir.text().toUtf8(), 'utf-8')

		zf = zipfile.ZipFile(zipname + u'.zip', mode='w', compression=compress)
		for root, dirs, files in os.walk(zipname):
			for f in files:
				zf.write(os.path.join(root, f))
		zf.close()

class UFPAUpload(QtGui.QWidget):
	def __init__(self, last_dir):
		super(UFPAUpload, self).__init__()
		self.last_dir = last_dir

	def send_email(self):
		pass

### EOF ###
