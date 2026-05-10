# -*- coding: utf-8 -*-
import sys
from fenlight.resources.lib.modules.router import routing, sys_exit_check
# from modules.kodi_utils import logger

routing(sys)
if sys_exit_check(): sys.exit(1)
