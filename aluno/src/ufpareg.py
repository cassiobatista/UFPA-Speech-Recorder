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

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import pyaudio
import threading
import zipfile

from PyQt4 import QtCore, QtGui
from datetime import datetime

import info
from ufparead import UFPARead
from ufparepeat import UFPARepeat
from ufpatools import UFPAZip, UFPAUpload


class UFPARegister(QtGui.QMainWindow):

	uid = datetime.now().strftime('_%Y%m%d-%H%M%S')
	last_dir = info.ROOT_DIR_PATH
	regloaded = False

	def __init__(self, logger):
		super(UFPARegister, self).__init__()
		self.logger = logger

		def rec_demo():
			p = pyaudio.PyAudio()
			stream = p.open(input=True, 
						format=pyaudio.paInt16, channels=1, rate=44100,
						frames_per_buffer=1024)

			for i in xrange(5):
				snd_data = stream.read(1024)

			del(snd_data)
			stream.stop_stream()
			stream.close()
			p.terminate()

		self.init_main_screen()
		self.init_menu()
		threading.Thread(target=rec_demo).start()

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
		#hb_applier.addWidget(QtGui.QLabel(u'Nome Completo\n\t(Aplicador)'.expandtabs(4)))
		hb_applier.addWidget(QtGui.QLabel(u'\tNome\nCompleto'.expandtabs(4)))
		hb_applier.addWidget(self.applier)
		hb_applier.addSpacing(50) # --
		hb_applier.addWidget(QtGui.QLabel(u'Grupo'))
		hb_applier.addWidget(self.group)

		#gb_applier = QtGui.QGroupBox(u'Campos para o(a) aplicador(a)')
		gb_applier = QtGui.QGroupBox(u'Aplicador(a):')
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
		#hb_student.addWidget(QtGui.QLabel('Nome Completo\n\t(Aluno)'.expandtabs(8)))
		hb_student.addWidget(QtGui.QLabel('\tNome\nCompleto'.expandtabs(4)))
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

		self.radio_group = QtGui.QButtonGroup()
		self.gender_m = QtGui.QRadioButton(u'M')
		self.gender_m.setStatusTip(u'Masculino')
		self.gender_f = QtGui.QRadioButton(u'F')
		self.gender_f.setStatusTip(u'Feminino')
		self.radio_group.addButton(self.gender_m)
		self.radio_group.addButton(self.gender_f)

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
		hb_compl.addWidget(QtGui.QLabel(u'Sexo'))
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

		gb_form = QtGui.QGroupBox(u'Aluno(a):')
		gb_form.setLayout(vb_form)
		# -------------

		tip = u'Cadastrar criança e iniciar o módulo "Ler"'
		self.read_button = QtGui.QToolButton()
		self.read_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
		self.read_button.setStatusTip(tip)
		self.read_button.setToolTip(tip)
		self.read_button.setMinimumSize(150,110)
		self.read_button.setIcon(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'read.png')))
		self.read_button.setIconSize(QtCore.QSize(80,80))
		self.read_button.setText(u'1. Cadastrar e "Ler"')
		self.read_button.clicked.connect(self.register)

		tip = u'Iniciar o módulo "Repetir" para uma criança já cadastrada'
		self.repeat_button = QtGui.QToolButton()
		self.repeat_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
		self.repeat_button.setStatusTip(tip)
		self.repeat_button.setToolTip(tip)
		self.repeat_button.setIcon(QtGui.QIcon(os.path.join(
						info.SRC_DIR_PATH, 'images', 'ear.png')))
		self.repeat_button.setIconSize(QtCore.QSize(80,80))
		self.repeat_button.setText(u'2. "Ouvir e Repetir"')
		self.repeat_button.setMinimumSize(150,110)
		self.repeat_button.setDisabled(True)
		self.repeat_button.clicked.connect(self.register)

		hb_start = QtGui.QHBoxLayout()
		hb_start.addStretch()
		hb_start.addWidget(self.read_button)
		hb_start.addWidget(self.repeat_button)

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
						u'O arquivo <b>%s</b> ' % os.path.basename(filename) + 
						u'não está de acordo com formato gerado pelo ' +
						u' UFPA Speech Recorder!\n')
			self.logger.error(u'Arquivo de dados incorreto.')
			return

		data = []
		for i in xrange(2):
			data.append(reg.pop(0))

		reg.pop(0) # discard blank line
		if reg.pop(0) != 'Dados do Aluno':
			QtGui.QMessageBox.critical(self,
						u'Erro ao carregar dados do aluno',
						u'O arquivo <b>%s</b> ' % os.path.basename(filename) + 
						u'não está de acordo com formato gerado pelo ' + 
						u'UFPA Speech Recorder!\n')
			self.logger.error(u'Arquivo de dados incorreto.')
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
		self.uid = '_' + register['ID']

		self.last_dir = os.path.dirname(filename)
		self.logger.debug(u'Arquivo com dados já existentes carregado.')

		self.applier.setEnabled(False)
		self.group.setEnabled(False)
		self.school.setEnabled(False)
		self.student.setEnabled(False)
		self.city.setEnabled(False)
		self.state.setEnabled(False)
		self.gender_m.setEnabled(False)
		self.gender_f.setEnabled(False)
		self.age.setEnabled(False)
		self.grade.setEnabled(False)

		self.read_button.setEnabled(False)
		self.repeat_button.setEnabled(True)

		self.regloaded = True

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

		act_clean = QtGui.QAction(QtGui.QIcon(os.path.join(
					info.SRC_DIR_PATH, 'images', 'clean.png')), u'&Limpar', self)
		act_clean.setStatusTip(u'Restaura os campos da interface de cadastro')
		act_clean.triggered.connect(self.clear)

		self.statusBar()
	
		toolbar = self.addToolBar('Standard')
		toolbar.addAction(act_exit)
		toolbar.addAction(act_open)
		toolbar.addAction(act_about)
		#toolbar.addAction(act_cfg)
		toolbar.addAction(act_zip)
		#toolbar.addAction(act_cloud)
		toolbar.addAction(act_clean)

	def closeEvent(self, event):
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

		form_full = False
		if applier   != u'':
			form_full = True
		elif group   != u'':
			form_full = True
		elif school  != u'':
			form_full = True
		elif student != u'':
			form_full = True
		elif city    != u'':
			form_full = True
		elif state   != u'':
			form_full = True
		elif gender  != u'':
			form_full = True
		elif age     != u'':
			form_full = True
		elif grade   != u'':
			form_full = True

		if not form_full:
			QtGui.qApp.quit()

		reply = QtGui.QMessageBox.question(self, u'Fechar UFPA Speech Recorder', 
					u'Todos os dados preenchidos serão perdidos.\n\n' + 
					u'Você deseja realmente sair?\n', 
					QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			QtGui.qApp.quit()
		else:
			event.ignore()

	def quit_app(self):
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

		form_full = False
		if applier   != u'':
			form_full = True
		elif group   != u'':
			form_full = True
		elif school  != u'':
			form_full = True
		elif student != u'':
			form_full = True
		elif city    != u'':
			form_full = True
		elif state   != u'':
			form_full = True
		elif gender  != u'':
			form_full = True
		elif age     != u'':
			form_full = True
		elif grade   != u'':
			form_full = True

		if not form_full:
			QtGui.qApp.quit()

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

	def input_error(self, field):
		msg = u'O campo <b>"%s"</b> não foi corretamente preenchido.' % field
		QtGui.QMessageBox.warning(self, u'Erro nos dados de entrada', 
					msg + 
					u'<br>' +
					u'Por favor, verifique novamente o formulário.' + 
					u'<br>' +
					u'Se o problema persistir, entre em contato conosco:' + 
					u'<br>' +
					u'<a href=mailto:{0}>{0}</a>'.format(info.MAIL['cassio']) +
					u'<br>' +
					u'<a href=mailto:{0}>{0}</a>'.format(info.MAIL['nelson']) +
					u'<br>')
		self.logger.error(u'Erro no preenchimento dos dados')

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

		if len(applier) < 6:
			self.input_error(u'Nome completo do aplicador')
			return
		elif group == u'':
			self.input_error(u'Grupo')
			return
		elif len(school) < 3:
			self.input_error(u'Escola do aluno')
			return
		elif len(student) < 6:
			self.input_error(u'Nome completo do aluno')
			return
		elif len(city) < 3:
			self.input_error(u'Cidade do aluno')
			return
		elif state == u'':
			self.input_error(u'Estado do aluno')
			return
		elif gender == u'':
			self.input_error(u'Sexo do aluno')
			return
		elif age == u'':
			self.input_error(u'Idade do aluno')
			return
		elif grade  == u'':
			self.input_error(u'Série do aluno')
			return
		else:
			# ROOT/state
			if not os.path.exists(os.path.join(info.ROOT_DIR_PATH,
						u"Estado do " + state)):
				os.mkdir(os.path.join(info.ROOT_DIR_PATH,
						u"Estado do " + state))
			os.chdir(os.path.join(info.ROOT_DIR_PATH,
						u"Estado do " + state))

			# ROOT/state/city
			if not os.path.exists(city):
				os.mkdir(city)
			os.chdir(city)

			# ROOT/state/city/school
			if not os.path.exists(school):
				os.mkdir(school)
			os.chdir(school)

			# ROOT/state/city/school/group
			if not os.path.exists(group):
				os.mkdir(group)
			os.chdir(group)

			# not working on Windows
			## ROOT/state/city/school/group/firstname_uid
			#if not os.path.exists(student.split()[0].lower() + self.uid):
			#	os.mkdir(student.split()[0].lower() + self.uid)
			#else:
			#	if self.regloaded:
			#		newid = datetime.now().strftime('_%Y%m%d-%H%M%S') # def new uid
			#		os.rename(student.split()[0].lower() + self.uid, 
			#					student.split()[0].lower() + newid)
			#		self.uid = newid 
			#		self.logger.debug(u'Atualizando o ID')
			#	else:
			#		pass # this condition must never exist. Ever
			#os.chdir(student.split()[0].lower() + self.uid)

			# ROOT/state/city/school/group/firstname_uid
			if not os.path.exists(student.split()[0].lower() + self.uid):
				os.mkdir(student.split()[0].lower() + self.uid)
			os.chdir(student.split()[0].lower() + self.uid)

			if not self.regloaded:
				self.logger.debug(u'Criando arquivo 1NFO.me')
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

				# ROOT/src/state/city/school/group/firstname_uid/leitura
				if not os.path.exists(u'leitura'):
					os.mkdir(u'leitura')
				else:
					pass #overwrite audios from the previous applied reading mod
				os.chdir(u'leitura')

				self.logger.debug(u'Iniciando o módulo de leitura.')

				self.rec = UFPARead(self)
							#self.state, self.school, self.student, self.uid)
				self.rec.closed.connect(self.show)
				self.rec.move(230,30) # try to centralize
				self.rec.setMinimumSize(900, 700) # define initial size
				self.rec.setWindowTitle(info.TITLE)
				self.rec.setWindowIcon(QtGui.QIcon(os.path.join(
							info.SRC_DIR_PATH, 'images', 'ufpa.png')))
				self.rec.show()
			else:
				# ROOT/src/state/city/school/group/firstname_uid/repetição
				if not os.path.exists(u'repetição'):
					os.mkdir(u'repetição')
				else:
					pass #overwrite audios from the previous applied repeating mod
				os.chdir(u'repetição')

				self.logger.debug(u'Iniciando o módulo de repetição.')

				#self.rep = UFPARepeat(self,
				#			self.state, self.school, self.student, self.uid)
				self.rep = UFPARepeat(self)
				self.rep.closed.connect(self.show)
				self.rep.move(230,30) # try to centralize
				self.rep.setMinimumSize(900, 520) # define initial size
				self.rep.setWindowTitle(info.TITLE)
				self.rep.setWindowIcon(QtGui.QIcon(os.path.join(
							info.SRC_DIR_PATH, 'images', 'ufpa.png')))
				self.rep.show()
			self.hide()

	def clear(self, force=True):
		if not force:
			reply = QtGui.QMessageBox.warning(self, u'Limpar campos de registro', 
						u'Todos os dados preenchidos serão apagados.\n',
						QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)

			if reply == QtGui.QMessageBox.Cancel:
				return

		self.applier.setEnabled(True)
		self.group.setEnabled(True)
		self.school.setEnabled(True)
		self.student.setEnabled(True)
		self.city.setEnabled(True)
		self.state.setEnabled(True)
		self.age.setEnabled(True)
		self.grade.setEnabled(True)
		self.gender_m.setEnabled(True)
		self.gender_f.setEnabled(True)

		self.applier.clear()
		self.group.setCurrentIndex(0)
		self.school.clear()
		self.student.clear()
		self.city.clear()
		self.state.setCurrentIndex(0)
		self.age.setCurrentIndex(0)
		self.grade.setCurrentIndex(0)

		self.radio_group.setExclusive(False)
		self.gender_f.setChecked(False)
		self.gender_m.setChecked(False)
		self.radio_group.setExclusive(True)

		self.read_button.setEnabled(True)
		self.repeat_button.setEnabled(False)

		self.logger = info.get_logger()
		self.uid = datetime.now().strftime('_%Y%m%d-%H%M%S')
		self.regloaded = False

### EOF 
