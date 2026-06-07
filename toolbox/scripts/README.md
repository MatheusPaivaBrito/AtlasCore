# Toolbox Scripts

General-purpose development scripts can live here.

Use this folder for scripts that are not tied to a specific database seed and are not automated tests.

Examples:

- local maintenance helpers;
- project inspection scripts;
- one-off data repair utilities for development environments.

Scripts that mutate service-owned data should usually live under `toolbox/seeds/<service>/` or a future service-specific toolbox folder.
