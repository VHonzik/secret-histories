#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import math
from PIL import Image
from fpdf import FPDF
from scripts.constants import mmToPixel, exportPath
from scripts.cards import Cards, cardSize

physicalPageSize = (210, 297) # mm

pageCardsOffset = (150, 150) # px
pageCardsSpacing = 1 # px

exportPageImagesPath = exportPath / "pageImages"

# Calculated measurements in px
pageSize = (mmToPixel(physicalPageSize[0]), mmToPixel(physicalPageSize[1]))
cardsGridDimension = (math.floor(pageSize[0] / cardSize[0]), math.floor(pageSize[1] / cardSize[1]))

def createPDFPageImages(cards):
  currentPageIndex = 0
  currentPageImage = Image.new('RGB', pageSize, 'white')
  currentPageCardIndex = (0,0)

  cardImages = cards.iterate()
  for (cardImage, cardAmount, _) in cardImages:
    currentCardAmount = cardAmount
    while (currentCardAmount > 0):
      region = (pageCardsOffset[0] + currentPageCardIndex[0] * (cardSize[0] + pageCardsSpacing), pageCardsOffset[1] + currentPageCardIndex[1] * (cardSize[1] + pageCardsSpacing))
      currentPageImage.paste(cardImage, region)
      currentPageCardIndex = (currentPageCardIndex[0] + 1, currentPageCardIndex[1])
      currentCardAmount = currentCardAmount - 1
      if currentPageCardIndex[0] == cardsGridDimension[0]:
        currentPageCardIndex = (0, currentPageCardIndex[1]+1)
        if currentPageCardIndex[1] == cardsGridDimension[1]:
          currentPageCardIndex = (0, 0)
          currentPageImage.save(f"{exportPageImagesPath}\\page-{currentPageIndex}.png")
          currentPageIndex = currentPageIndex + 1
          currentPageImage = Image.new('RGB', pageSize, 'white')
          print("\tStarting new page {0}".format(currentPageIndex))
  if currentPageCardIndex[0] != 0 or currentPageCardIndex[1] != 0:
    currentPageImage.save(f"{exportPageImagesPath}\\page-{currentPageIndex}.png")

def createPdfFromImagesInFolder():
  with open(f"{exportPath}\\SecretHistories.pdf", "w") as _:
    pass
  pdf = FPDF(unit = "mm", format = [physicalPageSize[0], physicalPageSize[1]])
  for pagePath in exportPageImagesPath.glob("*.png"):
    print("\tAdding page {0} to pdf.".format(pagePath.stem))
    pdf.add_page()
    pdf.image(str(pagePath), 0, 0, physicalPageSize[0], physicalPageSize[1])
  pdf.output(f"{exportPath}\\SecretHistories.pdf", "F")

def main():
  """ Main program """
  if not exportPath.exists():
    os.makedirs(exportPath)

  if not exportPageImagesPath.exists():
    os.makedirs(exportPageImagesPath)

  cards = Cards()
  cards.create()

  print("Page size in pixels {0}".format(pageSize))
  print("Page will fit {0}x{1} cards".format(cardsGridDimension[0], cardsGridDimension[1]))

  print("Creating pages for PDF...")
  createPDFPageImages(cards)

  print("Creating PDF...")
  createPdfFromImagesInFolder()

  print("Checking art...")
  #cards.checkAssetsUsed()

  return 0

if __name__ == "__main__":
  main()