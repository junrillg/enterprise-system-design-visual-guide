# Maintenance

## Content conventions

- Define the business invariant, authoritative owner, and guarantee boundary.
- Record failure behavior and recovery alongside the successful path.
- Use generic domain examples and distinguish design choices from product guarantees.
- Keep primary-source attribution near relevant technical claims.
- Update SVG diagrams and Mermaid definitions together.

## Validation

From the repository root, with Python 3.10+:

```bash
python3 check_notes.py
python3 -m unittest -v test_failures
```

The integrity check validates relative paths, diagram structure, reference sections, and concept coverage. The tests cover selected transactional crash windows and state transitions; they do not validate a deployed distributed system.

## Generated references

Rebuild diagrams with `python3 build_diagrams.py`. To rebuild the offline reference, install the pinned Node dependency with `npm install`, then run `npm run build:reader`.

The generated HTML is self-contained and requires no installation or network access to read. SVGs are the primary rendered diagrams; Mermaid files are editable companion definitions.
