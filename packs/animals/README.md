# Basic Animals pack

A 25-item introductory animal-identification pack for Knowledge in Bloom.

## Current artwork

The files in `assets/images/` are deliberately obvious placeholders. Each is labelled
with the animal it should depict, so the pack can be loaded and tested immediately
without introducing photographs whose licence or attribution has not been verified.

Replace each placeholder with a suitable photograph while keeping the same filename.
When replacing an image, update the corresponding `question.credit` object in
`items.json`.

## Pack behaviour

- Every prompt uses: **Name this animal.**
- Supports multiple choice, typed answers, category games and media-only presentation.
- Explicit distractors are included for every item.
- The canonical progress keys are `animals_basic:<item_id>`.
