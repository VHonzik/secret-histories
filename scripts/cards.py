#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import json
import math
import os
import re
import scripts.constants as constants

from pathlib import Path
from PIL import Image, ImageDraw, PngImagePlugin, ImageFont
from scripts.constants import mmToPixel

cardsPath = constants.rootPath / "cards"

titleFontPath = os.path.join(constants.assetsPath, 'LinLibertine_RB.ttf')
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

# Calculated measurements in px
cardSize = (mmToPixel(constants.physicalCardSize[0]), mmToPixel(constants.physicalCardSize[1]))
centerX = math.floor(cardSize[0] * 0.5)

titleY = mmToPixel(61)
smallIconSize = (mmToPixel(5),mmToPixel(5))

rightIconsXOffset = mmToPixel(2.6)

verbSize = smallIconSize
verbX = cardSize[0] - verbSize[0] - rightIconsXOffset
verbStartY = mmToPixel(4)
verbOffsetY = mmToPixel(1) + verbSize[1]

textY = math.floor(cardSize[1] - mmToPixel(16))
textYLong =  math.floor(cardSize[1] - mmToPixel(14))

aspectXRight = rightIconsXOffset
aspectY =  cardSize[1] - mmToPixel(2.5) - smallIconSize[1]
aspectTextSpace = mmToPixel(0.3)
aspectSpace = mmToPixel(1.5)

inlineIconSize = (mmToPixel(4),mmToPixel(4))

def sanitizeName(name):
  s = str(name).strip().replace(" ", "_")
  s = re.sub(r"(?u)[^-\w.]", "", s)
  return s

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

class Cards:
  def __init__(self, patchOnly=False):
    self.patchOnly = patchOnly
    self.usedArt = set()
    self.list = []

  def cardAddArt(self, cardImage, artName, areaName):
    artImagePath = constants.assetsPath / artName
    self.usedArt.add(artName.lower())
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

  def cardAddBorder(self, cardImage):
    borderImagePath = constants.assetsPath / ("BorderPatch.png" if self.patchOnly else "Border.png")
    self.usedArt.add("Border.png".lower())
    with Image.open(borderImagePath) as borderImage:
      borderImage.convert('RGBA')
      cardImage.alpha_composite(borderImage)

  def cardAddArea(self, cardImage, areaType):
    if areaType == "No":
      return
    areaImagePath = constants.assetsPath / f"{areaType}Area.png"
    self.usedArt.add(f"{areaType}Area.png".lower())
    with Image.open(areaImagePath) as areaImage:
      areaImage.convert('RGBA')
      cardImage.alpha_composite(areaImage)

  def cardAddTitle(self, cardImageDraw, title):
    font = titleFont
    if cardImageDraw.textlength(title, font=font) > (0.9 * cardSize[0]):
      font = smallTitleFont
    if cardImageDraw.textlength(title, font=font) > (0.9 * cardSize[0]):
      font = tinyTitleFont
    cardImageDraw.multiline_text((centerX, titleY), title, anchor='mm', fill='black', align='center', font=font)

  def cardAddText(self, cardImage, cardImageDraw, text, i, n):
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
      iconPath = constants.assetsPath / f"{icon}.png"
      self.usedArt.add(f"{icon}.png".lower())
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

  def cardAddVerb(self, cardImage, verb, i):
    verbImagePath = constants.assetsPath / f"{verb}.png"
    self.usedArt.add(f"{verb}.png".lower())
    with Image.open(verbImagePath) as verbImage:
      verbImage = verbImage.resize((smallIconSize[0], smallIconSize[0]))
      region = (verbX, verbStartY + i * verbOffsetY)
      cardImage.paste(verbImage, region)

  def cardAddAspect(self, cardImage, cardImageDraw, aspect, startX):
    aspectImagePath = constants.assetsPath / aspectIcon(aspect)
    self.usedArt.add(aspectIcon(aspect).lower())
    with Image.open(aspectImagePath) as aspectImage:
      aspectImage = aspectImage.resize((smallIconSize[0], smallIconSize[0]))
      region = (startX, aspectY)
      cardImage.paste(aspectImage, region)

    if isinstance(aspect, list):
      textY = math.floor(aspectY + smallIconSize[1] * 0.5)
      text = str(aspect[1])
      cardImageDraw.text((startX + smallIconSize[0] + aspectTextSpace, textY), text, anchor='lm', fill='black', font=aspectFont)

  def cardAddAspects(self, cardImage, cardImageDraw, aspects):
    totalWidth = 0
    for aspect in aspects:
      totalWidth = totalWidth + aspectWidth(cardImageDraw, aspect)
    totalWidth = totalWidth + (len(aspects)-1) * aspectSpace

    startX = math.floor(cardSize[0] - totalWidth - aspectXRight)
    for (_, aspect) in enumerate(aspects):
      self.cardAddAspect(cardImage, cardImageDraw, aspect, startX)
      startX = math.floor(startX + aspectWidth(cardImageDraw, aspect) + aspectSpace)

  def createCardImage(self, cardJson, cardJsonPath, cardJsonMd5):
    (cardPath, upToDate, cardImage, amount) = self.checkCardExists(cardJson, cardJsonPath, cardJsonMd5)

    if not upToDate:
      print(f"\t{cardJsonPath.stem} ✔️")
      cardImage = Image.new('RGBA', cardSize, '#ffffff00')
      cardImageDraw = ImageDraw.Draw(cardImage)

      if not self.patchOnly:
        self.cardAddArt(cardImage, cardJson['art'], cardJson['area'])
      self.cardAddBorder(cardImage)
      self.cardAddArea(cardImage, cardJson['area'])
      self.cardAddTitle(cardImageDraw, cardJson['title'])
      for i in range(len(cardJson['text'])):
        self.cardAddText(cardImage, cardImageDraw, cardJson['text'][i], i, len(cardJson['text']))

      if not self.patchOnly:
        for i in range(len(cardJson['verbs'])):
          self.cardAddVerb(cardImage, cardJson['verbs'][i], i)

      if len(cardJson['aspects']) > 0:
        self.cardAddAspects(cardImage, cardImageDraw, cardJson['aspects'])

      info = PngImagePlugin.PngInfo()
      info.add_itxt("md5", cardJsonMd5)
      cardImage.save(cardPath, pnginfo=info)
    else:
      print(f"\t{cardJsonPath.stem} ✖️")
    self.list.append((cardImage,amount,cardPath))

  def checkCardExists(self, cardJson, cardJsonPath, cardJsonMd5):
    cardJsonFilename = cardJsonPath.stem
    cardJsonParentName = cardJsonPath.parent.name
    cardPath = constants.exportCardsPath / cardJsonParentName
    if not cardPath.exists():
      os.makedirs(cardPath)
    cardImageName = sanitizeName(cardJsonFilename)
    cardPath = cardPath / f"{cardJson['amount']}-{cardImageName}.png"

    upToDate = False
    cardImage=None
    if (cardPath.exists()):
      cardImage = Image.open(cardPath)
      if ('md5' in cardImage.info and cardImage.info['md5'] == cardJsonMd5):
        upToDate = True

    return (cardPath, upToDate, cardImage, cardJson['amount'])

  def create(self):
    if not constants.exportPath.exists():
      os.makedirs(constants.exportPath)

    if not constants.exportCardsPath.exists():
      os.makedirs(constants.exportCardsPath)

    print(f"Creating cards with dimensions {cardSize[0]}x{cardSize[1]} px")
    print("Processing cards...")
    for (root, _, files) in os.walk(cardsPath):
      for cardJsonFileName in files:
        cardJsonPath = Path(root) / cardJsonFileName
        cardJsonMd5 = hashlib.md5(open(cardJsonPath, 'rb').read()).hexdigest()
        with open(cardJsonPath, 'r') as cardJsonFile:
          cardJson = json.load(cardJsonFile)
          self.createCardImage(cardJson, cardJsonPath, cardJsonMd5)

  def checkAssetsUsed(self):
    unusedArt = []
    for assetFile in constants.assetsPath.glob("*.png"):
      if not (assetFile.name.lower() in self.usedArt):
        unusedArt.append(assetFile.name)
    if len(unusedArt) > 0:
      print(f"{len(unusedArt)} assets not used in any card ⚠️:")
      for art in unusedArt:
        print(f"\t\t{constants.assetsPath / art}")
    else:
      print(f"\t All {len(self.usedArt)} assets were used ✔️ ")

  def iterate(self):
    for (cardImage, amount, cardPath) in self.list:
      yield (cardImage, amount, cardPath)
