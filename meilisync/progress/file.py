import json
from pathlib import Path

import aiofiles

from meilisync.enums import ProgressType
from meilisync.progress import Progress


class File(Progress):
    type = ProgressType.file

    def __init__(
        self,
        path: str = "progress.json",
    ):
        super().__init__(path=path)
        self.path = path

    async def set(self, **kwargs):
        parent = Path(self.path).parent
        if parent != Path(""):
            parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(self.path, "w") as f:
            await f.write(json.dumps(kwargs))

    async def get(self):
        try:
            async with aiofiles.open(self.path) as f:
                return json.loads(await f.read())
        except json.JSONDecodeError:
            return None
        except FileNotFoundError:
            return None
