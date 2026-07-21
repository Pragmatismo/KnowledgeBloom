# Knowledge in Bloom

A canvas-based learning garden with modular lesson packs and mini-games built around a spaced repetition learning system. 

## Gameplay

Play learning mini-games to earn flowers and Garden Points while building knowledge through lessons and revision. Plant the flowers you earn, spend Garden Points on increasingly elaborate garden decorations, and arrange both across your garden rows to make the space your own.

The first four mini-games are:

- **Flashcards:** Learn new material and review existing questions with multiple-choice or typed answers.
- **Memory Cards:** Turn over cards to match each question with its answer before the garden timer runs out.
- **Falling Answers:** Move a basket beneath the correct falling answer to catch it before it reaches the meadow.
- **Memory Racer:** Select answers as quickly as possible and try to win the race.

## Run

```bash
python server.py
```

Open <http://localhost:8000>


## GPT and Codex 

I created the idea through a long conversation with chatGPT then added all the different elements piece at at a time through various codex promps and planning. 

## Included Dev Tools 

In the choose a seed pack selection page is a tool for creating your own seed packs, this allows you to easily edit the json files containing all the question and answer information, links to media, etc. 

Enabling debug-mode in the settings menu (found via the guide page) will enable three red boxes on the main screen which advance time 1, 6, or 24 hours to let you test the learning progress without having to wait - this is done by setting all dates in that users history back by the given time. 

Debug mode also shows a button which gives access to the flower sprite editor - this is a simple tool for positioning the flower sprites to align them properly (most image gen tools get close but not perfect when making sprite sheets) simply line up each frame of the sprite on the red cross and save it - this will create a correctly aligened spritesheet and save it in the assets/flowers folder. There is an example prompt for generating suitible sprite sheets in the assets/flowers folder. 
