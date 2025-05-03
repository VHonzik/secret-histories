#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
from pathlib import Path

rootPath=Path.cwd()

assetsPath = rootPath / "assets"
exportPath = rootPath / "export"
exportCardsPath = exportPath / "cards"

dpi = 300
physicalCardSize = (58, 89) # mm

def mmToPixel(mm):
  inches = mm / 25.4
  return math.floor(inches * dpi)
