# Plugins

Plugins transform events before and after Meilisearch writes. They can be registered globally (top-level `plugins`) and per table (`sync[].plugins`).

## Interface

```python
from meilisync.plugin import Plugin
from meilisync.schemas import Event


class Plugin:
    is_global = False

    async def pre_event(self, event: Event):
        return event

    async def post_event(self, event: Event):
        return event
```

- `pre_event` runs **before** the document is sent to Meilisearch. Return the (possibly mutated) event.
- `post_event` runs **after** a successful write.
- `is_global = True` — one instance is created and reused. `False` (default) — a new instance is created per event.

## Config

```yaml
plugins:
  - mypackage.plugins.LowercaseTitle
sync:
  - table: products
    plugins:
      - mypackage.plugins.DropUnpublished
```

Each entry is an import path `module.Class`. The module must be importable from the process environment (install it next to meilisync, or mount it into the Docker image).

## Example

```python
from meilisync.plugin import Plugin


class LowercaseTitle(Plugin):
    is_global = True

    async def pre_event(self, event):
        title = event.data.get("title")
        if isinstance(title, str):
            event.data["title"] = title.lower()
        return event
```

::: meilisync.plugin.Plugin
