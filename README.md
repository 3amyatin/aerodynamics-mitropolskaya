# Sail Aerodynamics — Seminar by N. Mitropolskaya

Transcription and illustrated article based on Natalia Mitropolskaya's seminar on sail aerodynamics for the yacht club [Equipage](https://equipage.club), March 16, 2026.

Video: [youtu.be/MXJhzNGrsMo](https://youtu.be/MXJhzNGrsMo)

## Seminar Contents

1. Aerodynamic force and the mechanism of its generation
2. Flow and body parameters
3. Components of aerodynamic force (lift, drag, FD, heeling)
4. Determination methods: Navier-Stokes equations, CFD, wind tunnels
5. Circulation theory (Kutta-Joukowski theorem) and limitations of its interpretation
6. Bernoulli's law: capabilities and limitations
7. Analysis of 9 popular explanations of lift (what is correct and what is not)
8. Aerodynamic coefficients, airfoil polar, VPP
9. Laminar and turbulent flows, Reynolds number
10. Boundary layer, its separation and flow stall

## PDF Generation

```
just setup  # install Chromium (once)
just pdf    # generate PDF from Markdown
just test   # run integrity tests
just check  # verify image references
```

The PDF includes: table of contents with bookmarks, headers/footers with section title and page numbering, KaTeX formulas, 50 illustrations from slides.

## Dependencies

- [pandoc](https://pandoc.org/) — Markdown to HTML conversion
- [uv](https://docs.astral.sh/uv/) — Python dependency management
- [playwright](https://playwright.dev/python/) + Chromium — HTML to PDF rendering
- [pymupdf](https://pymupdf.readthedocs.io/) — headers/footers, bookmarks (TOC), text overlay
- [pytest](https://pytest.org/) — article integrity tests
