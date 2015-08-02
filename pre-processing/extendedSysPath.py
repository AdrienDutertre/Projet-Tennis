# -*- coding: utf-8 -*-

import os, sys

# Obtention répertoire courant
currentDir = os.path.dirname(__file__)

# Obtention chemins relatifs aux modules que l'on souhaite rendre accessibles
configDir = os.path.join(currentDir, '../Config')

# S'ils ne sont pas déjà dans le PATH python on les rajoute
if configDir not in sys.path:
	sys.path.insert(0, configDir)