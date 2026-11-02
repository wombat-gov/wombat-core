# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
This release is the coordinated WAFPass → WOMBATpass rebrand and is versioned as
a minor release at the project owner's request; treat the rename as breaking and
pin exact versions.

## [1.2.0] - 2026-11-02

### Breaking changes

- Renamed the distribution from `wafpass-core` to **`wombat-core`**.
- Renamed the import package from `wafpass` to **`wombat`**.
- Renamed the CLI from `wafpass` to **`wombat`**.
- Renamed the repository from `WAF2p/wafpass-core` to
  `wombat-gov/wombat-core`.
- Environment variables now use the `WOMBAT_*` prefix instead of `WAFPASS_*`.

Legacy compatibility is intentionally retained for one migration window:

- `pip install wafpass-core` still resolves through package metadata where
  available.
- `import wafpass` is served by the compatibility shim in `wafpass/__init__.py`.
- The `wafpass` console script remains as a deprecated alias for `wombat`.
- `WAFPASS_*` environment variables are promoted to `WOMBAT_*` by
  `wombat.compat.promote_legacy_env()`.

These aliases are deprecated and will be removed in a future release.

### Changed

- All user-facing branding and documentation now use WOMBATpass.
- Package metadata, repository URLs, and release names point at the
  `wombat-gov` organisation.
- Version reported by the CLI, reporters, PDFs and state files is `1.2.0`.

### Migration

1. Replace `pip install wafpass-core` with `pip install wombat-core`.
2. Replace `import wafpass` with `import wombat`.
3. Replace the `wafpass` CLI with `wombat`.
4. Rename `WAFPASS_*` environment variables to `WOMBAT_*`.
5. Update CI, scripts and pins that reference `WAF2p/wafpass-core` to
   `wombat-gov/wombat-core`.
6. Pin `wombat-core==1.2.0` if you need reproducible builds.

### Companion releases

- `wombat-server` 1.2.0
- `wombat-dashboard` 1.2.0
- `wombat-mcp` 0.2.0
- `wombat-action` 0.2.0
