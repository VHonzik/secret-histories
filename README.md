# Secret Histories

Unofficial print&play card boardgame for 2-3 players based on the [Cultist Simulator](https://store.steampowered.com/app/718670/Cultist_Simulator/) video game. Average play time is somewhere between 2-3 hours.

## Game description

Secret Histories is card-heavy boardgame designed for 3 players. The main mechanics, borrowing from BoardGameGeek terminology, are:
- Race: Players race to achieve immortality through an occult ritual. Whoever performs an ascension ritual first wins the game. Players need to gather occult lore, influences and ingredients of the right principle and strength.
- Action Points/Action drafting: There are 4 types of actions a player can do: Work, Study, Dream and Talk. But they can only do 3 unique ones each round. Additionally, some actions are picked from a shared limited pool.
- Hand Management/Push Your Luck/Player Elimination: Players fall under effects of powerful yet temporary "influences." And not all of them are good. As seasons change, they must careful manage their mental state or risk loosing their hard earned resources. You can always play it safe but takes time that you don't always have. And if that wasn't enough, the authorities don't take kindly to the occult activities either.
- Hidden Information: Many key pieces for final ritual are obtained secretly. Victory won't come out of the blue but it is not always clear how close an individual player is.
- Temporary Cards: Influences are fickle in their nature.
- Auction: Some end-game pieces for the ascension are auctioned among the player. Prepare to pay a hefty price for the final piece of the puzzle.

## I want to play right now!

Check out [Github releases](https://github.com/VHonzik/secret-histories/releases) with PDFs that you can print and play.

## I want the latest the greatest version

 If you want to help with testing the latest version up-to-date, you will need to do some work yourself. First of all, you will need [python 3](https://www.python.org/downloads/) installed with following packages: [FPDF](https://pypi.org/project/fpdf/) and [Pillow](https://pypi.org/project/pillow/). From the root of this repo run:
- `python cards.py`

This will take around 2 minutes and generate `export/SecretHistories.pdf`. Afterwards you can roughly follow instructions in [README for Github releases](Release.template.docx). Tokens art is in the `assets` folder.

## Digital version

I have made a work in progress [Tabletop Simulator mod of this game](https://steamcommunity.com/sharedfiles/filedetails/?id=3479818565). It is currently very behind the main, sitting at version 0.3.

## Licensing

I do not own the rights for Cultist Simulator game, its assets and the excellent fictional world it takes place in. This is a fan project to try and play with my boardgame group of friends. The majority of assets for the cards were ripped out of the PC game and occasionally modified to suit this boardgame needs. On the other hand, they are also available publicly at the [Cultist Simulator wiki](https://cultistsimulator.fandom.com/). If you are from Weather Factory and reading this, let's figure out a kickstarter!