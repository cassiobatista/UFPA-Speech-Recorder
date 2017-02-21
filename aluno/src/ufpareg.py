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
		self.config()

	def config(self):
		if os.path.exists(os.path.join(info.SRC_DIR_PATH, 'ufpasrconfig')):
			pass

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

		self.group = QtGui.QComboBox()
		self.group.addItem(u'')
		self.group.addItem(u'Experimental')
		self.group.addItem(u'Controle')

		hb_applier = QtGui.QHBoxLayout()
		hb_applier.addWidget(QtGui.QLabel('Aplicador'))
		hb_applier.addWidget(self.applier)
		hb_applier.addSpacing(50) # --
		hb_applier.addWidget(QtGui.QLabel('Grupo'))
		hb_applier.addWidget(self.group)

		gb_applier = QtGui.QGroupBox(u'Campos para o(a) aplicador(a)')
		gb_applier.setLayout(hb_applier)
		# -------------

		self.school = QtGui.QLineEdit()
		self.school.setStatusTip(u'Ex.:  "Escola Estadual de Ensino ' + 
					u'Fundamental e Médio Doutor Freitas"')
		self.school.setMinimumWidth(500)

		hb_school = QtGui.QHBoxLayout()
		hb_school.addWidget(QtGui.QLabel('Escola'))
		hb_school.addWidget(self.school)
		# -------------

		self.student = QtGui.QLineEdit()
		self.student.setStatusTip(u'Ex.:  "Cassio Trindade Batista"')
		self.student.setMinimumWidth(500)

		hb_student = QtGui.QHBoxLayout()
		hb_student.addWidget(QtGui.QLabel('Aluno'))
		hb_student.addWidget(self.student)
		# -------------

		self.city = QtGui.QLineEdit()
		self.city.setStatusTip(u'Ex.:  "Belo Horizonte"')
		self.city.setMinimumWidth(250)

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
		hb_location.addWidget(QtGui.QLabel('Cidade'))
		hb_location.addWidget(self.city)
		hb_location.addSpacing(150) # --
		hb_location.addWidget(QtGui.QLabel('Estado'))
		hb_location.addWidget(self.state)
		# -------------

		self.gender_m = QtGui.QRadioButton(u'M')
		self.gender_m.setStatusTip(u'Masculino')
		self.gender_f = QtGui.QRadioButton(u'F')
		self.gender_f.setStatusTip(u'Feminino')

		self.age = QtGui.QComboBox()
		self.age.addItem(u'')
		for age in range(4, 16):
			self.age.addItem(str(age))

		self.grade = QtGui.QComboBox()
		self.grade.addItem(u'')
		self.grade.addItem(u'Pré-escola')
		for fund in xrange(1, 10):
			self.grade.addItem(str(fund) + u' º ano (ensino fundamental)')
		for med in xrange(1, 4):
			self.grade.addItem(str(med) + u' º série (ensino médio)')

		hb_compl = QtGui.QHBoxLayout()
		hb_compl.addWidget(QtGui.QLabel(u'Gênero'))
		hb_compl.addWidget(self.gender_m)
		hb_compl.addWidget(self.gender_f)
		hb_compl.addSpacing(50) # --
		hb_compl.addWidget(QtGui.QLabel(u'Idade'))
		hb_compl.addWidget(self.age)
		hb_compl.addSpacing(50) # --
		hb_compl.addWidget(QtGui.QLabel(u'Série'))
		hb_compl.addWidget(self.grade)
		hb_compl.addStretch()

		vb_form = QtGui.QVBoxLayout()
		vb_form.addLayout(hb_school)
		vb_form.addSpacing(20)
		vb_form.addLayout(hb_student)
		vb_form.addSpacing(20)
		vb_form.addLayout(hb_location)
		vb_form.addSpacing(20)
		vb_form.addLayout(hb_compl)

		gb_form = QtGui.QGroupBox(u'Campos para o(a) aluno(a)')
		gb_form.setLayout(vb_form)
		# -------------

		self.start = QtGui.QPushButton('Cadastrar')
		self.start.setStatusTip(u'Cadastrar criança e iniciar ' +
					u'a gravação de áudio')
		self.start.setShortcut('Ctrl+Space')
		self.start.setMinimumSize(150,50)
		self.start.setDefault(True)
		self.start.setAutoDefault(True)
		self.start.clicked.connect(self.register)

		hb_start = QtGui.QHBoxLayout()
		hb_start.addStretch()
		hb_start.addWidget(self.start)

		gb_start = QtGui.QGroupBox()
		gb_start.setLayout(hb_start)
		# -------------

		self.vb_layout_main = QtGui.QVBoxLayout()
		self.vb_layout_main.addWidget(gb_applier)
		self.vb_layout_main.addWidget(gb_form)
		self.vb_layout_main.addWidget(gb_start)

		wg_central = QtGui.QWidget()
		wg_central.setLayout(self.vb_layout_main)
		self.setCentralWidget(wg_central)

		if info.DEBUG:
			self.applier.setText(u'Nelson Cruz Sampaio Neto')
			self.group.setCurrentIndex(1)
			self.school.setText(u'Universidade Federal do Pará')
			self.student.setText(u'Cassio Trindade Batista')
			self.city.setText(u'Belém')
			self.state.setCurrentIndex(14)
			self.gender_m.setChecked(True)
			self.age.setCurrentIndex(3)
			self.grade.setCurrentIndex(2)

	def open_reg(self):
		filename = QtGui.QFileDialog.getOpenFileName(self,
				u'Abrir arquivo de texto contendo as informações da criança', 
				self.last_dir, u'(*.txt)')

		filename = unicode(str(filename.toUtf8()), 'utf-8')

		if filename is u'':
			return 

		with open(filename, 'r') as info_reg:
			reg = info_reg.read().splitlines()

		if reg.pop(0) != 'Dados do Aplicador':
			QtGui.QMessageBox.critical(self,
						u'Erro ao carregar dados do aplicador',
						u'O arquivo <b>%s</b> ' % filename + 
						u'não está de acordo com formato gerado pelo ' +
						u' UFPA Speech Recorder!\n')
			return

		data = []
		for i in xrange(2):
			data.append(reg.pop(0))

		reg.pop(0) # discard blank line
		if reg.pop(0) != 'Dados do Aluno':
			QtGui.QMessageBox.critical(self,
						u'Erro ao carregar dados do aluno',
						u'O arquivo de <b>%s</b> ' % filename + 
						u'não está de acordo com formato gerado pelo ' + 
						u'UFPA Speech Recorder!\n')
			return

		while len(reg):
			data.append(reg.pop(0))

		register = {}
		while len(data):
			field, value = data.pop(0).split(': ')
			register[field] = unicode(value, 'utf-8')

		self.applier.setText(register['Aplicador'])
		self.group.setCurrentIndex(self.group.findText(register['Grupo']))
		self.school.setText(register['Escola'])
		self.student.setText(register['Aluno'])
		self.city.setText(register['Cidade'])
		self.state.setCurrentIndex(self.state.findText(register['Estado']))
		self.age.setCurrentIndex(self.age.findText(register['Idade']))
		self.grade.setCurrentIndex(self.grade.findText(register['Série']))
		if register['Gênero'] == u'Masculino':
			self.gender_m.setChecked(True)
		elif register['Gênero'] == u'Feminino':
			self.gender_f.setChecked(True)

		self.last_dir = os.path.dirname(filename)

	def init_menu(self):
		act_exit = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'x.png')), u'&Sair', self)
		act_exit.setShortcut('Ctrl+Q')
		act_exit.setStatusTip(u'Fechar UFPA Speech Recorder')
		act_exit.triggered.connect(self.quit_app)

		act_open = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'open.png')), u'&Abrir', self)
		act_open.setShortcut('Ctrl+O')
		act_open.setStatusTip(u'Carregar o registro de uma criança já cadastrada')
		act_open.triggered.connect(self.open_reg)

		act_about = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'about.png')), u'&Sobre', self)
		act_about.setShortcut('Ctrl+I')
		act_about.setStatusTip(u'Sobre o UFPA Speech Recorder')
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
		#act_cloud.triggered.connect(self.upload)

		self.statusBar()
	
		toolbar = self.addToolBar('Standard')
		toolbar.addAction(act_exit)
		toolbar.addAction(act_open)
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
		group   = unicode(self.group.currentText().toUtf8(), 'utf-8')
		school  = unicode(self.school.text().toUtf8(), 'utf-8')
		student = unicode(self.student.text().toUtf8(), 'utf-8')
		city    = unicode(self.city.text().toUtf8(), 'utf-8')
		state   = unicode(self.state.currentText().toUtf8(), 'utf-8')
		age     = unicode(self.age.currentText().toUtf8(), 'utf-8')
		grade   = unicode(self.grade.currentText().toUtf8(), 'utf-8')

		if self.gender_f.isChecked():
			gender = u'Feminino'
		elif self.gender_m.isChecked():
			gender = u'Masculino'
		else:
			gender = u''

		if  len(applier)     < 10 \
			or len(school)   < 10 \
			or len(student)  < 10 \
			or len(city)     < 4  \
			or group  == u'' \
			or state  == u'' \
			or age    == u'' \
			or grade  == u'' \
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
			if not os.path.exists(student.split()[0].lower() + self.uid):
				os.mkdir(student.split()[0].lower() + self.uid)
			os.chdir(student.split()[0].lower() + self.uid)

			with open('1NFO.me.txt', 'w') as f:
				f.write(u'Dados do Aplicador\n')
				f.write(u'Aplicador: '  + applier  + '\n')
				f.write(u'Grupo: '      + group    + '\n')
				f.write('\n')
				f.write(u'Dados do Aluno\n')
				f.write(u'Aluno: '  + student  + '\n')
				f.write(u'ID: '     + self.uid.replace('_','') + '\n')
				f.write(u'Escola: ' + school   + '\n')
				f.write(u'Idade: '  + age      + '\n')
				f.write(u'Cidade: ' + city     + '\n')
				f.write(u'Estado: ' + state    + '\n')
				f.write(u'Gênero: ' + gender   + '\n')
				f.write(u'Série: '  + grade    + '\n')

			self.module = UFPAModule(self, state, school, student, self.uid)
			self.module.closed.connect(self.show)
			self.module.setWindowTitle(info.TITLE)
			self.module.move(200,150)
			self.module.show()
			self.module.setWindowIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'ufpa.png')))
			self.module.show()

	def clear(self):
		self.applier.clear()
		self.group.setCurrentIndex(0)
		self.school.clear()
		self.student.clear()
		self.city.clear()
		self.state.setCurrentIndex(0)
		self.age.setCurrentIndex(0)
		self.grade.setCurrentIndex(0)

		self.gender_f.setChecked(False)
		self.gender_m.setChecked(False)


class UFPAModule(QtGui.QMainWindow):

	closed = QtCore.pyqtSignal()

	def __init__(self, parent, state, school, student, uid):
		super(UFPAModule, self).__init__()
		self.parent = parent
		self.state = state
		self.school = school
		self.student = student
		self.uid = uid

		self.init_main_screen()
		self.init_menu()

	def init_main_screen(self):
		book = QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images','read.png'))
		self.read_button = QtGui.QPushButton()
		self.read_button.setAutoFillBackground(True)
		self.read_button.setIcon(book)
		self.read_button.setStatusTip(u'Iniciar o módulo de leitura')
		self.read_button.setToolTip(u'Leitura')
		self.read_button.setIconSize(QtCore.QSize(220,220))
		self.read_button.setAutoDefault(True)
		self.read_button.clicked.connect(self.read_module)

		headphone = QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images','listen.png'))
		self.repeat_button = QtGui.QPushButton()
		self.repeat_button.setAutoFillBackground(True)
		self.repeat_button.setIcon(headphone)
		self.repeat_button.setStatusTip(u'Iniciar o módulo de repetição')
		self.repeat_button.setToolTip(u'Repetição')
		self.repeat_button.setIconSize(QtCore.QSize(210,220))
		self.repeat_button.setEnabled(False)
		self.repeat_button.setAutoDefault(True)
		self.repeat_button.clicked.connect(self.repeat_module)

		hb_buttons = QtGui.QHBoxLayout()
		hb_buttons.addWidget(self.read_button)
		hb_buttons.addWidget(self.repeat_button)

		gb_buttons = QtGui.QGroupBox(u'Qual módulo você deseja utilizar agora?')
		gb_buttons.setLayout(hb_buttons)

		self.vb_layout_main = QtGui.QVBoxLayout()
		self.vb_layout_main.addWidget(gb_buttons)

		wg_central = QtGui.QWidget()
		wg_central.setLayout(self.vb_layout_main)

		self.setCentralWidget(wg_central)

	def init_menu(self):
		act_exit = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'x.png')), u'&Sair', self)
		act_exit.setShortcut('Ctrl+Q')
		act_exit.setStatusTip(u'Fechar')
		act_exit.triggered.connect(self.close)

		self.statusBar()

		menubar = self.menuBar() 
		file_menu = menubar.addMenu(u'&Opções')
		file_menu.addAction(act_exit)

	def read_module(self):
		self.rec = UFPARecord(self.parent, 
					self.state, self.school, self.student, self.uid)
		self.rec.closed.connect(self.show)
		self.rec.move(230,30) # try to centralize
		self.rec.setMinimumSize(900, 700) # define initial size
		self.rec.setWindowTitle(info.TITLE)
		self.rec.setWindowIcon(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'ufpa.png')))
		self.rec.show()
		self.parent.hide()
		self.close()

	def repeat_module(self):
		QtGui.QMessageBox.information(self, u'Módulo de repetição', u'Coming soon')


### EOF 
