# Knowledge in Bloom

A canvas-based prototype learning garden. Packs and mini-games are discovered from their folders, learning progress grows flower sprite sheets, and layouts are saved by the included zero-dependency server.

## Gameplay

Play learning mini-games to earn flowers and Garden Points while building knowledge through introductions and spaced reviews. Plant the flowers you earn, spend Garden Points on increasingly elaborate garden decorations, and arrange both across your garden rows to make the space your own.

The three working mini-games are:

- **Flashcards:** Learn new material and review existing questions with multiple-choice or typed answers.
- **Memory Cards:** Turn over cards to match each question with its answer before the garden timer runs out.
- **Falling Answers:** Move a basket beneath the correct falling answer to catch it before it reaches the meadow.

## Run

```bash
python server.py
```

Open <http://localhost:8000>. Add folders containing `icon.png` beneath `packs/` or `minigames/` and refresh to discover them. Garden state is written to the ignored `garden-save.json` file.
