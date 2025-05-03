#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import math

from PIL import Image
from scripts.constants import exportPath
from scripts.cards import Cards

exportDeckImagesPath = exportPath / "deckImages"
deckColumns = 10
deckRows = 7

deckSize = (4096, 4096) # px

cardWidths =  [407, 405, 407, 406, 408, 406, 405, 406, 410, 409] # px
cardHeights = [585, 579, 583, 582, 583, 582, 584] # px
cardSpacing = 3

PILES_CARDS = {
  "Hours": [
    "Hours-0",
    "Hours-1",
    "Hours-2",
    "Hours-3",
    "Hours-4",
    "Hours-5",
    "Hours-6",
    "Hours-7",
    "Hours-8",
    "Hours-9"
  ]
}

class Piles:
  def __init__(self):
    self.piles = {}

  def sortCardsToPiles(self, cards):
    print("Sorting cards into piles...")
    for (cardImage, cardAmount, cardPath) in cards:
      pileKey = cardPath.parent.name + "-" + cardPath.stem.split("-")[1]
      for (pileName, pileCards) in PILES_CARDS.items():
        if not (pileName in self.piles):
          self.piles[pileName] = []
        for pileCard in pileCards:
          if pileCard == pileKey:
            print(f"\tCard {pileKey} is {cardAmount}x in pile {pileName}.")
            for _ in range(cardAmount):
              self.piles[pileName].append(cardImage)

  def createPileImages(self):
    print("Creating pile images...")
    for (pileName, pileImages) in self.piles.items():
      columns = min(len(pileImages), deckColumns)
      rows = (len(pileImages) / deckColumns) + 1
      if rows > deckRows:
        raise Exception(f"Too many cards in pile {pileName}")
      deckImage = Image.new('RGB', deckSize, 'white')
      currentCardIndex = (0,0)
      for cardImage in pileImages:
        resizedImage = cardImage.resize((cardWidths[currentCardIndex[0]], cardHeights[currentCardIndex[1]]))
        region = (math.floor(sum(cardWidths[:currentCardIndex[0]]) + currentCardIndex[0]*cardSpacing),
                  math.floor(sum(cardHeights[:currentCardIndex[1]]) + currentCardIndex[1]*cardSpacing))
        deckImage.paste(resizedImage, region)
        currentCardIndex = (currentCardIndex[0] + 1, currentCardIndex[1])
        if currentCardIndex[0] == columns:
          currentCardIndex = (0, currentCardIndex[1]+1)
      deckImage.save(f"{exportDeckImagesPath}\\{pileName}.jpg")

  def create(self, cards):
    self.sortCardsToPiles(cards)
    self.createPileImages()



def main():
  """ Main program """
  if not exportPath.exists():
    os.makedirs(exportPath)

  if not exportDeckImagesPath.exists():
    os.makedirs(exportDeckImagesPath)

  cards = Cards()
  cards.create()

  piles = Piles()
  piles.create(cards.iterate())


if __name__ == "__main__":
  main()