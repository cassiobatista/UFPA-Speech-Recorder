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
# Cassio Trindade Batista  - cassio.batista.13@gmail.com
# Nelson Cruz Sampaio Neto - dnelsonneto@gmail.com
#
# Last edited on February, 2017


import sys
import os
import platform

DEBUG = False

SYS_OS = platform.system().lower()
SYS_HOME_PATH = 'HOMEPATH' if SYS_OS == 'windows' else 'HOME'

SRC_DIR_PATH  = unicode(str(os.path.abspath(os.path.dirname(
			os.path.realpath(__file__)))), 'utf-8')
ROOT_DIR_PATH = unicode(str(os.path.abspath(os.path.join(
			SRC_DIR_PATH, os.pardir))), 'utf-8')

MODULE = u'Módulo do Aplicador'

TITLE = u'UFPA Speech Recorder' + ' - ' + MODULE

INFO =  TITLE + '\n' \
		u'\n' + \
		u'Autores:\n' + \
		u'Cassio Trindade Batista\n' + \
		u'Nelson Cruz Sampaio Neto\n' + \
		u'\n' + \
		u'Contato:\n' + \
		u'cassio.batista.13@gmail.com\n' + \
		u'dnelsonneto@gmail.com\n' + \
		u'\n' + \
		u'Copyright 2017\n' + \
		u'Grupo FalaBrasil\n' + \
		u'Instituto de Ciências Exatas e Naturais\n' + \
		u'Universidade Federal do Pará\n'

def img_path(img):
	return os.path.join(SRC_DIR_PATH, 'images', img)

### EOF ###
