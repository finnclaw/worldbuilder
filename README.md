# Worldbuilder

A simple wiki generator for fictional worlds. Write markdown files, get a browsable wiki.

## Usage

1. Add entries to `worlds/` using templates from `templates/`
2. Run `python build.py`
3. Open `site/index.html`

## Entry Types

- **planet** - Worlds, moons, space stations
- **species** - Intelligent species, creatures
- **faction** - Governments, organizations, groups
- **character** - Named individuals
- **event** - Historical events, wars, discoveries
- **location** - Cities, landmarks, regions
- **item** - Artifacts, technology, objects

## Example

```markdown
---
type: planet
name: Zorah Prime
tags: [homeworld, desert]
---

A desert world orbiting twin suns. Birthplace of the Zorathian species.

## Climate
Harsh, arid conditions with temperatures exceeding 50°C at midday.

## History
First colonized 3000 years ago by refugees from the Core Collapse.
```

Built by Jax 🦝
