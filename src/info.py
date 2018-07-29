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
# Cassio Trindade Batista  - cassio.batista.13@gmail.com
#
# Last edited on February, 2017


import sys
import os
import platform
import logging

DEBUG = False

SYS_OS = platform.system().lower()
SYS_HOME_PATH = 'HOMEPATH' if SYS_OS == 'windows' else 'HOME'

SRC_DIR_PATH  = unicode(str(os.path.abspath(os.path.dirname(
			os.path.realpath(__file__)))), 'utf-8')
ROOT_DIR_PATH = unicode(str(os.path.abspath(os.path.join(
			SRC_DIR_PATH, os.pardir))), 'utf-8')

LOGFILE = os.path.join(ROOT_DIR_PATH, 'ufpalog.log')

MAIL = {'cassio':u'cassio.batista.13@gmail.com',
		'nelson':u'dnelsonneto@gmail.com'}

TITLE = u'UFPA Speech Recorder'

INFO =  TITLE + '<br>' \
		u'<br>' + \
		u'Autores:' + \
		u'<br>' + \
		u'Cassio Trindade Batista' + \
		u'<br>' + \
		u'Nelson Cruz Sampaio Neto' + \
		u'<br><br>' + \
		u'Contato:' + \
		u'<br>' + \
		u'<a href=mailto:{0}>{0}</a>'.format(MAIL['cassio']) + \
		u'<br>' + \
		u'<a href=mailto:{0}>{0}</a>'.format(MAIL['nelson']) + \
		u'<br><br>' + \
		u'Copyleft 2017' + \
		u'<br>' + \
		u'Grupo FalaBrasil' + \
		u'<br>' + \
		u'Instituto de Ciências Exatas e Naturais' + \
		u'<br>' + \
		u'Universidade Federal do Pará'

def img_path(img):
	return os.path.join(SRC_DIR_PATH, 'images', img)

# http://stackoverflow.com/questions/11232230/logging-to-two-files-with-different-settings
def get_logger():
	logging.disable(logging.NOTSET)
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

	handler = logging.FileHandler(LOGFILE)
	handler.setFormatter(formatter)

	logger = logging.getLogger('UFPA Logger')
	logger.addHandler(handler)
	logger.setLevel(logging.DEBUG)

	return logger

### EOF ###
