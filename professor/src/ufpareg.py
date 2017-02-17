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
# Author Jan 2017:
# Cassio Trindade Batista - cassio.batista.13@gmail.com
# Nelson C. Sampaio Neto  - dnelsonneto@gmail.com


import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
from datetime import datetime

from PyQt4 import QtCore, QtGui

import info
from ufparec import UFPARecord
from ufpatools import UFPAZip, UFPAUpload

import zipfile


class UFPARegister(QtGui.QMainWindow):

	uid = datetime.now().strftime('_%Y%m%d-%H%M%S')
	last_dir = info.ROOT_DIR_PATH

	def __init__(self):
		super(UFPARegister, self).__init__()
		self.init_main_screen()
		self.init_menu()

	def config(self):
		QtGui.QMessageBox.information(self, u'Configurações', u'Coming soon.')
		return

	def compress(self):
		self.czip = UFPAZip(self)
		self.czip.closed.connect(self.show)
		self.czip.move(230,30) # try to centralize
		self.czip.setMinimumSize(800, 200) # define initial size
		self.czip.setWindowTitle(info.TITLE)
		self.czip.setWindowIcon(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'ufpa.png')))
		self.czip.show()

	def upload(self):
		QtGui.QMessageBox.information(self, u'Upload', u'Coming soon.')
		return
		self.up = UFPAUpload(self)
		self.up.closed.connect(self.show)
		self.up.move(230,30) # try to centralize
		self.up.setMinimumSize(800, 300) # define initial size
		self.up.setWindowTitle(info.TITLE)
		self.up.setWindowIcon(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'ufpa.png')))
		self.up.show()

	def init_main_screen(self):
		self.applier = QtGui.QLineEdit()
		self.applier.setStatusTip(u'Ex.:  "Nelson Cruz Sampaio Neto"')
		self.applier.setMinimumWidth(500)

		hb_applier = QtGui.QHBoxLayout()
		hb_applier.addWidget(QtGui.QLabel(u'Aplicador(a)'))
		hb_applier.addWidget(self.applier)
		## -------------

		self.school = QtGui.QLineEdit()
		self.school.setStatusTip(u'Ex.:  "Escola Estadual de Ensino ' + 
					u'Fundamental e Médio Doutor Freitas"')
		self.school.setMinimumWidth(500)

		hb_school = QtGui.QHBoxLayout()
		hb_school.addWidget(QtGui.QLabel(u'Escola'))
		hb_school.addSpacing(20)
		hb_school.addWidget(self.school)
		## -------------

		self.city = QtGui.QLineEdit()
		self.city.setStatusTip(u'Ex.:  "Belo Horizonte"')
		self.city.setMinimumWidth(300)

		states = [u'Acre', u'Alagoas', u'Amapá', u'Amazonas', u'Bahia',
					u'Ceará', u'Distrito Federal', u'Espírito Santo', u'Goiás', 
					u'Maranhão', u'Mato Grosso', u'Mato Grosso do Sul', 
					u'Minas Gerais', u'Pará', u'Paraíba', u'Paraná',
					u'Pernambuco', u'Piauí', u'Rio de Janeiro', 
					u'Rio Grande do Norte', u'Rio Grande do Sul', u'Rondônia',
					u'Roraima', u'Santa Catarina', u'São Paulo', u'Sergipe',
					u'Tocantins']

		self.state = QtGui.QComboBox()
		self.state.addItem(u'')
		for st in states:
			self.state.addItem(st)

		hb_location = QtGui.QHBoxLayout()
		hb_location.addWidget(QtGui.QLabel(u'Cidade'))
		hb_location.addSpacing(15)
		hb_location.addWidget(self.city)
		hb_location.addSpacing(30) # --
		hb_location.addWidget(QtGui.QLabel(u'Estado'))
		hb_location.addWidget(self.state)
		# -------------

		self.radio_group = QtGui.QButtonGroup()
		self.gender_m = QtGui.QRadioButton(u'M')
		self.gender_m.setStatusTip(u'Masculino')
		self.gender_f = QtGui.QRadioButton(u'F')
		self.gender_f.setStatusTip(u'Feminino')
		self.radio_group.addButton(self.gender_m)
		self.radio_group.addButton(self.gender_f)

		self.age = QtGui.QComboBox()
		self.age.addItem(u'')
		for age in range(17, 90):
			self.age.addItem(str(age))

		hb_compl = QtGui.QHBoxLayout()
		hb_compl.addWidget(QtGui.QLabel(u'Gênero'))
		hb_compl.addSpacing(12) # --
		hb_compl.addWidget(self.gender_m)
		hb_compl.addWidget(self.gender_f)
		hb_compl.addSpacing(50) # --
		hb_compl.addWidget(QtGui.QLabel(u'Idade'))
		hb_compl.addWidget(self.age)
		hb_compl.addStretch()
		# -------------

		vb_form = QtGui.QVBoxLayout()
		vb_form.addSpacing(10)
		vb_form.addLayout(hb_applier)
		vb_form.addSpacing(18)
		vb_form.addLayout(hb_school)
		vb_form.addSpacing(18)
		vb_form.addLayout(hb_location)
		vb_form.addSpacing(18)
		vb_form.addLayout(hb_compl)

		gb_form = QtGui.QGroupBox(u'Dados do(a) Aplicador(a)')
		gb_form.setLayout(vb_form)
		# ------------- #

		self.start = QtGui.QPushButton('Cadastrar')
		self.start.setStatusTip(u'Cadastrar professor(a) e iniciar ' +
					u'a gravação de áudio')
		self.start.setShortcut('Ctrl+Space')
		self.start.setMinimumSize(150,50)
		self.start.setDefault(True)
		self.start.setAutoDefault(False)
		self.start.clicked.connect(self.register)

		hb_start = QtGui.QHBoxLayout()
		hb_start.addStretch()
		hb_start.addWidget(self.start)

		gb_start = QtGui.QGroupBox()
		gb_start.setLayout(hb_start)
		# -------------

		self.vb_layout_main = QtGui.QVBoxLayout()
		self.vb_layout_main.addWidget(gb_form)
		self.vb_layout_main.addWidget(gb_start)

		wg_central = QtGui.QWidget()
		wg_central.setLayout(self.vb_layout_main)

		self.setCentralWidget(wg_central)

		if info.DEBUG:
			self.applier.setText(u'Nelson Cruz Sampaio Neto')
			self.school.setText(u'Escola Estadual de Ensino Fundamental e ' +
						u'Médio Professor Doutor Freitas')
			self.city.setText(u'Santa Rosa do Purus')
			self.state.setCurrentIndex(1)
			self.gender_m.setChecked(True)
			self.age.setCurrentIndex(1)

	def init_menu(self):
		act_exit = QtGui.QAction(QtGui.QIcon(os.path.join(info.SRC_DIR_PATH,
					'images', 'x.png')), u'&Sair', self)
		act_exit.setShortcut('Ctrl+Q')
		act_exit.setStatusTip(u'Fechar UFPA Speech Recorder')
		act_exit.triggered.connect(self.quit_app)

		act_about = QtGui.QAction(QtGui.QIcon(os.path.join(info.SRC_DIR_PATH,
					'images', 'about.png')), u'&Sobre', self)
		act_about.setShortcut('Ctrl+I')
		act_about.setStatusTip(u'Sobre o UFPA Speech Recorder')
		act_about.triggered.connect(self.about)

		act_cfg = QtGui.QAction(QtGui.QIcon(os.path.join(info.SRC_DIR_PATH,
					'images', 'settings.png')), u'&Configurações', self)
		act_cfg.setStatusTip(u'Configurar UFPA Speech Recorder')
		act_cfg.triggered.connect(self.config)

		act_zip = QtGui.QAction(QtGui.QIcon(os.path.join(info.SRC_DIR_PATH,
					'images', 'zip.png')), u'&Compactar', self)
		act_zip.setStatusTip(u'Compactar pasta de áudios em um arquivo .zip')
		act_zip.triggered.connect(self.compress)

		act_cloud = QtGui.QAction(QtGui.QIcon(os.path.join(info.SRC_DIR_PATH,
					'images', 'cloud.png')), u'&Upload', self)
		act_cloud.setStatusTip(u'Fazer upload do áudios compactados para a nuvem')
		act_cloud.triggered.connect(self.upload)

		self.statusBar()
	
		toolbar = self.addToolBar('Standard')
		toolbar.addAction(act_exit)
		toolbar.addAction(act_about)
		#toolbar.addAction(act_cfg)
		toolbar.addAction(act_zip)
		#toolbar.addAction(act_cloud)

	def closeEvent(self, event):
		reply = QtGui.QMessageBox.question(self, u'Fechar UFPA Speech Recorder', 
					u'Todos os dados preenchidos serão perdidos.\n\n' + 
					u'Você deseja realmente sair?\n', 
					QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			QtGui.qApp.quit()
		else:
			event.ignore()

	def quit_app(self):
		reply = QtGui.QMessageBox.question(self, u'Fechar UFPA Speech Recorder', 
					u'Todos os dados preenchidos serão perdidos.\n\n' +
					u'Você deseja realmente sair?\n',
					QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			QtGui.qApp.quit()
		else:
			return

	def about(self):
		QtGui.QMessageBox.information(self, u'Sobre o app', info.INFO)
		return

	def register(self):
		applier = unicode(self.applier.text().toUtf8(), 'utf-8')
		school  = unicode(self.school.text().toUtf8(), 'utf-8')
		city    = unicode(self.city.text().toUtf8(), 'utf-8')
		state   = unicode(self.state.currentText().toUtf8(), 'utf-8')
		age     = unicode(self.age.currentText().toUtf8(), 'utf-8')

		if self.gender_f.isChecked():
			gender = u'Feminino'
		elif self.gender_m.isChecked():
			gender = u'Masculino'
		else:
			gender = u''

		if  len(applier)     < 10 \
			or len(school)   < 10 \
			or len(city)     < 4  \
			or state  == u'' \
			or age    == u'' \
			or gender == u'':
			QtGui.QMessageBox.information(self, u'Erro nos dados de entrada', 
					u'Alguma informação não foi devidamente preenchida.\n' + 
					u'Por favor, verifique novamente o formulário.\n' + 
					u'Se o problema persistir, entre em contato com o Nelson.')
			return
		else:
			# path: src/state
			if not os.path.exists(os.path.join(info.ROOT_DIR_PATH,
						u"Estado do " + state)):
				os.mkdir(os.path.join(info.ROOT_DIR_PATH,
						u"Estado do " + state))
			os.chdir(os.path.join(info.ROOT_DIR_PATH,
						u"Estado do " + state))

			# path: src/state/school
			if not os.path.exists(school):
				os.mkdir(school)
			os.chdir(school)

			# path: src/state/school/firstname_uid
			os.mkdir(applier.split()[0].lower() + self.uid)
			os.chdir(applier.split()[0].lower() + self.uid)

			with open('1NFO.me.txt', 'w') as f:
				f.write(u'Dados do Aplicador\n')
				f.write(u'Nome: '   + applier + '\n')
				f.write(u'Escola: ' + school  + '\n')
				f.write(u'Idade: '  + age     + '\n')
				f.write(u'Cidade: ' + city    + '\n')
				f.write(u'Estado: ' + state   + '\n')
				f.write(u'Gênero: ' + gender  + '\n')

			self.rec = UFPARecord(self, state, school, applier, self.uid)
			self.rec.closed.connect(self.show)
			self.rec.move(230,30) # try to centralize
			self.rec.setMinimumSize(900, 700) # define initial size
			self.rec.setWindowTitle(info.TITLE)
			self.rec.setWindowIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'ufpa.png')))
			self.rec.show()
			self.hide()

	def clear(self):
		self.applier.clear()
		self.school.clear()
		self.city.clear()
		self.state.setItemText(0, u'')
		self.state.setCurrentIndex(0)
		self.age.setItemText(0, u'')
		self.age.setCurrentIndex(0)

		self.radio_group.setExclusive(False)
		self.gender_f.setChecked(False)
		self.gender_m.setChecked(False)
		self.radio_group.setExclusive(True)

### EOF ###
