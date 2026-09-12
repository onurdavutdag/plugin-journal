# Third-party notices

This plugin adapts material from other open-source projects. Each adapted file carries a
one-line provenance header naming its source; the licence text for each source is reproduced
here in full, as the licence requires.

## k-dense-ai/scientific-agent-skills — MIT

Source: https://github.com/k-dense-ai/scientific-agent-skills (skills `scientific-slides` v1.8
and `pptx-posters` v2.2, fetched 2026-09-12).

Adapted into `skills/journalsunum/` — the `references/journalsunum-r-*.md` files, the
`references/journalsunum-poster-manifest-ornek.json` template, and every script under
`scripts/`. Adaptation here means: trimmed to this package's four presentation types,
descriptions translated to Turkish, calls re-wired to this package's own agents, and files
renamed to this package's naming rule. The upstream rendering path (Nano Banana Pro image
generation) and the LaTeX/Beamer material were not taken.

The upstream authors ask that a project which the skills materially contributed to cite:

> Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). Scientific Agent
> Skills: A Library of Procedural Knowledge for Research Agents. arXiv:2609.00065.
> https://doi.org/10.48550/arXiv.2609.00065

```
MIT License

Copyright (c) 2025 K-Dense Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Not included on purpose

The `pptx` skill this package's `journalsunum-s-pptx` agent drives is **Anthropic's
proprietary skill** (`anthropics/skills@pptx`, licence in its own `LICENSE.txt`). Its terms
forbid retaining copies outside Anthropic's services and creating derivative works, so
nothing from it is reproduced here. It is a machine-level dependency the user installs
separately (`npx skills add anthropics/skills@pptx -g`); see the root README's Requirements.
