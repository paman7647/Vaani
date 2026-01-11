# Read the Docs Deployment Guide

## ✅ Setup Complete

Your Vaani documentation is now ready for Read the Docs deployment!

### Files Configured

1. **`.readthedocs.yaml`** - RTD v2 configuration
   - Build OS: Ubuntu 22.04
   - Python: 3.11
   - Sphinx config: `docs/conf.py`
   - Dependencies: `docs/requirements.txt`

2. **`docs/requirements.txt`** - Documentation dependencies
   - sphinx>=7.0.0
   - pydata-sphinx-theme>=0.14.0

3. **`docs/conf.py`** - Sphinx configuration
   - Theme: pydata-sphinx-theme
   - Extensions: autodoc, autosummary, napoleon, intersphinx
   - Mocked imports for heavy dependencies

### Build Status

✅ **Local build: SUCCESS (0 warnings)**
- All title underlines fixed
- Duplicate object warnings resolved
- Import errors handled via autodoc_mock_imports
- HTML output: `docs/_build/html`

### Next Steps: Deploy to Read the Docs

#### 1. Push to GitHub

```bash
git add .
git commit -m "Add Read the Docs configuration and fix documentation warnings"
git push origin main
```

#### 2. Import Project on Read the Docs

1. Go to https://readthedocs.org/dashboard/
2. Click **"Import a Project"**
3. Connect your GitHub repository
4. Select **vaani** (or your repo name)
5. Click **"Next"**

#### 3. Configure Project (if needed)

RTD will auto-detect `.readthedocs.yaml`. Verify these settings:
- **Name**: vaani (or your preferred slug)
- **Repository URL**: Your GitHub repo URL
- **Default branch**: main (or master)
- **Default version**: latest

#### 4. Trigger First Build

- RTD will automatically trigger the first build
- Monitor progress at: `https://readthedocs.org/projects/vaani/builds/`
- Build time: ~2-5 minutes

#### 5. Access Your Docs

Once built, your documentation will be available at:
- **Latest**: https://vaani.readthedocs.io/en/latest/
- **Stable**: https://vaani.readthedocs.io/en/stable/ (after first release tag)

### Documentation Structure

```
docs/
├── _build/html/          # Local build output (gitignored)
├── _static/              # Static assets
├── conf.py               # Sphinx configuration
├── index.rst             # Documentation home
├── requirements.txt      # Doc dependencies
├── modules/              # API reference
│   ├── core.rst
│   ├── intelligence.rst
│   ├── voice.rst
│   ├── integrations.rst
│   ├── config.rst
│   └── utils.rst
├── development/          # Developer guides
├── architecture.rst      # System design
├── installation.rst      # Setup instructions
├── usage.rst             # User guide
└── ...                   # Additional guides
```

### Maintenance

#### Update Documentation

1. Edit `.rst` files or module docstrings
2. Test locally:
   ```bash
   .venv/bin/python -m sphinx -b html docs docs/_build/html
   ```
3. Commit and push changes
4. RTD will auto-rebuild on push

#### Add New Modules

1. Create module with proper docstrings
2. Add to appropriate `docs/modules/*.rst` file:
   ```rst
   .. autosummary::
      :toctree: <category>
      :template: autosummary/module.rst

      Vaani.new_package.new_module
   ```
3. Rebuild and push

#### Troubleshooting

**Build fails on RTD but succeeds locally?**
- Check Python version matches (3.11)
- Verify all deps in `docs/requirements.txt`
- Check `autodoc_mock_imports` in `conf.py`

**Import errors during build?**
- Add missing packages to `autodoc_mock_imports`
- Avoid runtime-only imports in module-level code

**Badge not updating?**
- Clear cache: RTD project settings → Advanced → "Wipe"
- Wait 5-10 minutes for CDN propagation

### Badge & Links

The README now includes a Read the Docs badge:

[![Documentation Status](https://readthedocs.org/projects/vaani/badge/?version=latest)](https://vaani.readthedocs.io/en/latest/?badge=latest)

### Support

- Read the Docs docs: https://docs.readthedocs.io/
- Sphinx docs: https://www.sphinx-doc.org/
- PyData theme: https://pydata-sphinx-theme.readthedocs.io/

---

**Status**: ✅ Ready for deployment
**Last Updated**: 2026-01-12
