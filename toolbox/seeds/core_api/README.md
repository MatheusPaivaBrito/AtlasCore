# Core API Seeds

Core API seeds populate the database owned by `core_api`.

## Library Seed

```bash
make seed-core
```

The seed is idempotent. It uses stable natural keys:

- `library.code`;
- `shelf(library_id, code)`;
- `section(shelf_id, code)`;
- `book.isbn`;
- `reader.email`;
- rental pairs for sample rental history.

Run migrations before running the seed:

```bash
make migrate
make seed-core
```
