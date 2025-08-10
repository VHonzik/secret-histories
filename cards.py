#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import math
import re
from PIL import Image, ImageFont, ImageDraw, PngImagePlugin
from fpdf import FPDF
from pathlib import Path
import hashlib

rootPath=Path.cwd()
cardsPath = rootPath / "cards"
assetsPath = rootPath / "assets"
exportPath = rootPath / "export"
exportCardsPath = exportPath / "cards"
exportPageImagesPath = exportPath / "pageImages"
dpi = 300
physicalCardSize = (58, 89) # mm
physicalPageSize = (210, 297) # mm
patchOnly = False

titleFontPath = os.path.join(assetsPath, 'LinLibertine_RB.ttf')
titleFontSize = 100 # px
titleFont = ImageFont.truetype(titleFontPath, size=titleFontSize)

smallTitleFontSize = 60 # px
smallTitleFont = ImageFont.truetype(titleFontPath, size=smallTitleFontSize)

tinyTitleFontSize = 50 # px
tinyTitleFont = ImageFont.truetype(titleFontPath, size=tinyTitleFontSize)

textFontSize = 30 # px
textFont = ImageFont.truetype(titleFontPath, size=textFontSize)

aspectFontSize = 70 # px
aspectFont = ImageFont.truetype(titleFontPath, size=aspectFontSize)

textSpacing = 48 # px

pageCardsOffset = (150, 150) # px
pageCardsSpacing = 1 # px

def mmToPixel(mm):
  inches = mm / 25.4
  return math.floor(inches * dpi)

# Calculated measurements in px
cardSize = (mmToPixel(physicalCardSize[0]), mmToPixel(physicalCardSize[1]))
centerX = math.floor(cardSize[0] * 0.5)

titleY = mmToPixel(61)
smallIconSize = (mmToPixel(5),mmToPixel(5))

rightIconsXOffset = mmToPixel(2.6)

verbSize = smallIconSize
verbX = cardSize[0] - verbSize[0] - rightIconsXOffset
verbStartY = mmToPixel(4)
verbOffsetY = mmToPixel(1) + verbSize[1]

deckSize = smallIconSize
deckX = rightIconsXOffset
deckY = mmToPixel(4)

textY = math.floor(cardSize[1] - mmToPixel(16))
textYLong =  math.floor(cardSize[1] - mmToPixel(14))

aspectXRight = rightIconsXOffset
aspectY =  cardSize[1] - mmToPixel(2.5) - smallIconSize[1]
aspectTextSpace = mmToPixel(0.3)
aspectSpace = mmToPixel(1.5)

pageSize = (mmToPixel(physicalPageSize[0]), mmToPixel(physicalPageSize[1]))
cardsGridDimension = (math.floor(pageSize[0] / cardSize[0]), math.floor(pageSize[1] / cardSize[1]))

inlineIconSize = (mmToPixel(4),mmToPixel(4))

# Tracking
usedArt = set()
cardCount = 0
pageCount = 0

def sanitizeName(name):
  s = str(name).strip().replace(" ", "_")
  s = re.sub(r"(?u)[^-\w.]", "", s)
  return s

def cardAddArt(cardImage, artName, areaName):
  global usedArt
  artImagePath = assetsPath / artName
  usedArt.add(artName.lower())
  with Image.open(artImagePath) as artImage:
    region = (0, 0)
    if areaName == "Tiny":
      ratio = artImage.height / artImage.width
      artImage = artImage.resize((cardSize[0], math.floor(cardSize[0] * ratio)))
      region = (0, -20)
    elif areaName == "No":
      ratio = artImage.height / artImage.width
      artImage = artImage.resize((cardSize[0], math.floor(cardSize[0] * ratio)))
    else:
      artImage = artImage.resize((cardSize[0], cardSize[0]))
    cardImage.paste(artImage, region)

def cardAddBorder(cardImage):
  borderImagePath = assetsPath / ("BorderPatch.png" if patchOnly else "Border.png")
  usedArt.add("Border.png".lower())
  with Image.open(borderImagePath) as borderImage:
    borderImage.convert('RGBA')
    cardImage.alpha_composite(borderImage)

def cardAddArea(cardImage, areaType):
  if areaType == "No":
    return
  areaImagePath = assetsPath / f"{areaType}Area.png"
  usedArt.add(f"{areaType}Area.png".lower())
  with Image.open(areaImagePath) as areaImage:
    areaImage.convert('RGBA')
    cardImage.alpha_composite(areaImage)

def cardAddTitle(cardImageDraw, title):
  font = titleFont
  if cardImageDraw.textlength(title, font=font) > (0.9 * cardSize[0]):
    font = smallTitleFont
  if cardImageDraw.textlength(title, font=font) > (0.9 * cardSize[0]):
    font = tinyTitleFont
  cardImageDraw.multiline_text((centerX, titleY), title, anchor='mm', fill='black', align='center', font=font)

def cardAddText(cardImage, cardImageDraw, text, i, n):
  inlineSpaceLength = cardImageDraw.textlength(" ", font=textFont)
  inlineSpaceCount = math.ceil(inlineIconSize[0] / inlineSpaceLength) + 1
  inlineSpaces = " " * inlineSpaceCount
  inlineDashes = "-" * inlineSpaceCount

  parsedText = re.sub(r"\{\w+\}", inlineSpaces, text)
  parsedTextLength = cardImageDraw.textlength(parsedText, font=textFont)
  centerY = textY
  if n >= 5:
    centerY = textYLong
  lineY = centerY + (i - ((n-1) / 2)) * textSpacing

  reservedText = re.sub(r"\{\w+\}", inlineDashes, text)

  inlineIconsMatch = re.finditer(r"\{(\w+)\}", text)
  inlineIcons = []
  for inlineIcon in inlineIconsMatch:
    icon = inlineIcon.group(1)
    iconPath = assetsPath / f"{icon}.png"
    usedArt.add(f"{icon}.png".lower())
    inlineIcons.append({'path': iconPath})

  inlineSpacesRe = "-{" + str(inlineSpaceCount) + "}"
  for i,inlineIcon in enumerate(re.finditer(inlineSpacesRe, reservedText)):
    spanLength = cardImageDraw.textlength(parsedText[:inlineIcon.span()[0]], font=textFont)
    inlineIcons[i]['start'] = math.floor(centerX - parsedTextLength * 0.5 + spanLength + inlineSpaceLength * 0.75)

  for inlineIcon in inlineIcons:
    with Image.open(inlineIcon['path']) as iconImage:
      iconImage.convert('RGBA')
      iconImage = iconImage.resize(inlineIconSize)
      region = (inlineIcon['start'], math.floor(lineY - inlineIconSize[0] * 0.5))
      cardImage.alpha_composite(iconImage, region)

  cardImageDraw.text((centerX, lineY), parsedText, anchor='mm', fill='black', align='center', font=textFont)

def cardAddVerb(cardImage, verb, i):
  verbImagePath = assetsPath / f"{verb}.png"
  usedArt.add(f"{verb}.png".lower())
  with Image.open(verbImagePath) as verbImage:
    verbImage = verbImage.resize((verbSize[0], verbSize[1]))
    region = (verbX, verbStartY + i * verbOffsetY)
    cardImage.paste(verbImage, region)

def cardAddDeck(cardImage, deck):
  deckImagePath = assetsPath / f"{deck}.png"
  usedArt.add(f"{deck}.png".lower())
  with Image.open(deckImagePath) as deckImage:
      deckImage = deckImage.resize((deckSize[0], deckSize[1]))
      region = (deckX, deckY)
      cardImage.paste(deckImage, region)

def aspectWidth(cardImageDraw, aspect):
  # Just icon
  if isinstance(aspect, str):
    return smallIconSize[0]
  # Icon with value
  elif isinstance(aspect, list):
    text = str(aspect[1])
    textWidth = cardImageDraw.textlength(text, font=aspectFont)
    return smallIconSize[0] + textWidth + aspectTextSpace
  else:
    raise Exception('Invalid aspect type')

def aspectIcon(aspect):
  # Just icon
  if isinstance(aspect, str):
    return f"{aspect}.png"
  # Icon with value
  elif isinstance(aspect, list):
    return f"{aspect[0]}.png"
  else:
    raise Exception('Invalid aspect type')

def cardAddAspect(cardImage, cardImageDraw, aspect, startX):
  aspectImagePath = assetsPath / aspectIcon(aspect)
  usedArt.add(aspectIcon(aspect).lower())
  with Image.open(aspectImagePath) as aspectImage:
    aspectImage = aspectImage.resize((smallIconSize[0], smallIconSize[0]))
    region = (startX, aspectY)
    cardImage.paste(aspectImage, region)

  if isinstance(aspect, list):
    textY = math.floor(aspectY + smallIconSize[1] * 0.5)
    text = str(aspect[1])
    cardImageDraw.text((startX + smallIconSize[0] + aspectTextSpace, textY), text, anchor='lm', fill='black', font=aspectFont)

def cardAddAspects(cardImage, cardImageDraw, aspects):
  totalWidth = 0
  for aspect in aspects:
    totalWidth = totalWidth + aspectWidth(cardImageDraw, aspect)
  totalWidth = totalWidth + (len(aspects)-1) * aspectSpace

  startX = math.floor(cardSize[0] - totalWidth - aspectXRight)
  for (_, aspect) in enumerate(aspects):
    cardAddAspect(cardImage, cardImageDraw, aspect, startX)
    startX = math.floor(startX + aspectWidth(cardImageDraw, aspect) + aspectSpace)

def checkCardExists(cardJson, cardJsonPath, cardJsonMd5):
  cardJsonFilename = cardJsonPath.stem
  cardJsonParentName = cardJsonPath.parent.name
  cardPath = exportCardsPath / cardJsonParentName
  if not cardPath.exists():
    os.makedirs(cardPath)
  cardImageName = sanitizeName(cardJsonFilename)
  cardPath = cardPath / f"{cardJson['amount']}-{cardImageName}.png"

  upToDate = False
  if (cardPath.exists()):
    cardImage = Image.open(cardPath)
    if ('md5' in cardImage.info and cardImage.info['md5'] == cardJsonMd5):
      upToDate = True

  return (cardPath, upToDate)

def createCardImage(cardJson, cardJsonPath, cardJsonMd5):
  global cardCount
  (cardPath, upToDate) = checkCardExists(cardJson, cardJsonPath, cardJsonMd5)

  if not upToDate:
    print(f"\t{cardJsonPath.stem} ✔️")
    cardImage = Image.new('RGBA', cardSize, '#ffffff00')
    cardImageDraw = ImageDraw.Draw(cardImage)

    if not patchOnly:
      cardAddArt(cardImage, cardJson['art'], cardJson['area'])
    cardAddBorder(cardImage)
    cardAddArea(cardImage, cardJson['area'])
    cardAddTitle(cardImageDraw, cardJson['title'])
    for i in range(len(cardJson['text'])):
      cardAddText(cardImage, cardImageDraw, cardJson['text'][i], i, len(cardJson['text']))

    if not patchOnly:
      for i in range(len(cardJson['verbs'])):
        cardAddVerb(cardImage, cardJson['verbs'][i], i)
      if 'deck' in cardJson:
        cardAddDeck(cardImage, cardJson['deck'])

    if len(cardJson['aspects']) > 0:
      cardAddAspects(cardImage, cardImageDraw, cardJson['aspects'])

    info = PngImagePlugin.PngInfo()
    info.add_itxt("md5", cardJsonMd5)
    cardImage.save(cardPath, pnginfo=info)
  else:
    print(f"\t{cardJsonPath.stem} ✖️")

  cardCount = cardCount + cardJson['amount']

def createCardImages():
  for (root, _, files) in os.walk(cardsPath):
    for cardJsonFileName in files:
      cardJsonPath = Path(root) / cardJsonFileName
      cardJsonMd5 = hashlib.md5(open(cardJsonPath, 'rb').read()).hexdigest()
      with open(cardJsonPath, 'r') as cardJsonFile:
        cardJson = json.load(cardJsonFile)
        createCardImage(cardJson, cardJsonPath, cardJsonMd5)

def loadCardImage(cardImageFile):
  nameReSearch = re.search("^(\d+)-(.*)", cardImageFile.stem)
  if (nameReSearch):
    amount = int(nameReSearch.group(1))
    cardName = nameReSearch.group(2)
    print("\tFound card {0} with amount {1}".format(cardName, amount))
    return (Image.open(cardImageFile), amount)
  else:
    raise Exception("Failed to parse card file name: '{0}'".format(cardImageFile.stem))

def createPDFPageImages():
  global pageCount
  currentPageIndex = 0
  currentPageImage = Image.new('RGB', pageSize, 'white')
  currentPageCardIndex = (0,0)

  for cardImageFile in exportCardsPath.glob("**/*.png"):
    (cardImage, cardAmount) = loadCardImage(cardImageFile)
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
          pageCount = pageCount + 1
          currentPageIndex = currentPageIndex + 1
          currentPageImage = Image.new('RGB', pageSize, 'white')
          print("\tStarting new page {0}".format(currentPageIndex))
  if currentPageCardIndex[0] != 0 or currentPageCardIndex[1] != 0:
    currentPageImage.save(f"{exportPageImagesPath}\\page-{currentPageIndex}.png")
    pageCount = pageCount + 1

def createPdfFromImagesInFolder():
  pdf = FPDF(unit = "mm", format = [physicalPageSize[0], physicalPageSize[1]])
  for pagePath in exportPageImagesPath.glob("*.png"):
    print("\tAdding page {0} to pdf.".format(pagePath.stem))
    pdf.add_page()
    pdf.image(str(pagePath), 0, 0, physicalPageSize[0], physicalPageSize[1])
  pdf.output(f"{exportPath}\\SecretHistories.pdf", "F")

def checkAssetsUsed():
  unusedArt = []
  for assetFile in assetsPath.glob("*.png"):
    if not (assetFile.name.lower() in usedArt):
      unusedArt.append(assetFile.name)
  if len(unusedArt) > 0:
    print(f"{len(unusedArt)} assets not used in any card ⚠️:")
    for art in unusedArt:
      print(f"\t\t{assetsPath / art}")
  else:
    print(f"\t All {len(usedArt)} assets were used ✔️ ")

def main():
  """ Main program """
  if not exportPath.exists():
    os.makedirs(exportPath)

  if not exportCardsPath.exists():
    os.makedirs(exportCardsPath)

  if not exportPageImagesPath.exists():
    os.makedirs(exportPageImagesPath)

  print(f"Creating cards with dimensions {cardSize[0]}x{cardSize[1]} px")
  print("Processing cards...")
  createCardImages()

  print("Page size in pixels {0}".format(pageSize))
  print("Page will fit {0}x{1} cards".format(cardsGridDimension[0], cardsGridDimension[1]))

  print("Creating pages for PDF...")
  createPDFPageImages()

  print("Creating PDF...")
  createPdfFromImagesInFolder()

  print("Checking art...")
  checkAssetsUsed()

  print(f"Total cards: {cardCount}. Total pages: {pageCount}")

  return 0

if __name__ == "__main__":
  main()