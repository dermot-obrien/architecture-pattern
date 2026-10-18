# portfolio

Keeps a repository's architecture patterns current as a managed portfolio: finds every pattern by the signature in its front matter, writes an inventory page, tags what needs conversion or deprecation, archives what is agreed with `git mv`, and turns a backlog into placeholders.

- What an agent reads: [SKILL.md](SKILL.md)
- The signature and the portfolio block: [references/signature.md](references/signature.md)
- Backlog forms and matching: [references/backlog.md](references/backlog.md)
- The guide for people: [docs/portfolio.md](../../docs/portfolio.md)

Tests, standard library only:

```bash
python -m unittest discover -s skills/portfolio/tests
```
