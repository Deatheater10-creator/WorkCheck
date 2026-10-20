"""One local JSON draft; no pickle, accounts, or network access."""
import json
import os
from pathlib import Path
import re
import tempfile
from uuid import uuid4
from dataclasses import dataclass

SCHEMA_VERSION = 1
MAX_SAVE_BYTES = 8 * 1024 * 1024
TOPICS = ("Differentiation", "Partial fractions")


def empty_draft():
    return {"schema_version": SCHEMA_VERSION, "topic": "Differentiation", "question": "",
            "lines": [], "revision": 0}


def default_draft_path():
    # Explicit test/development override; the normal Windows app uses LOCALAPPDATA.
    override = os.environ.get("WORKCHECK_DRAFT_PATH")
    if override:
        return Path(override).expanduser().resolve()
    base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    return base / "WorkCheck" / "draft.json"


class DraftInvalid(ValueError):
    pass


class SaveError(OSError):
    pass


def validate_draft(value):
    if not isinstance(value, dict) or type(value.get("schema_version")) is not int or value["schema_version"] != SCHEMA_VERSION:
        raise DraftInvalid("Unknown or damaged draft format.")
    if value.get("topic") not in TOPICS or not isinstance(value.get("question"), str):
        raise DraftInvalid("Invalid question or topic in saved draft.")
    if type(value.get("revision")) is not int or value["revision"] < 0 or not isinstance(value.get("lines"), list):
        raise DraftInvalid("Invalid working structure in saved draft.")
    ids = set()
    for line in value["lines"]:
        if not isinstance(line, dict) or not isinstance(line.get("id"), str) or not re.fullmatch(r"[a-f0-9]{32}", line["id"]):
            raise DraftInvalid("Invalid saved line identifier.")
        if line["id"] in ids or not isinstance(line.get("text"), str):
            raise DraftInvalid("Duplicate or damaged saved working line.")
        ids.add(line["id"])
    # Copy only durable data, preserving raw over-limit maths and line order.
    return {"schema_version": SCHEMA_VERSION, "topic": value["topic"], "question": value["question"],
            "lines": [{"id": line["id"], "text": line["text"]} for line in value["lines"]],
            "revision": value["revision"]}


@dataclass
class LoadResult:
    draft: dict
    message: str
    warning: bool = False


class DraftStore:
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else default_draft_path()

    def _read(self):
        if self.path.stat().st_size > MAX_SAVE_BYTES:
            raise DraftInvalid("The save file exceeds the 8 MiB recovery limit.")
        try:
            with self.path.open("r", encoding="utf-8") as stream:
                return validate_draft(json.load(stream))
        except (ValueError, UnicodeError, RecursionError) as exc:
            raise DraftInvalid("The save file could not be read as a valid draft.") from exc

    def _archive(self):
        backup = self.path.with_name(f"{self.path.stem}.damaged-{uuid4().hex}{self.path.suffix}")
        # Preserve the complete original in the same directory, including oversized files.
        self.path.rename(backup)
        return backup

    def load(self):
        try:
            draft = self._read()
            return LoadResult(draft, "Restored your locally saved draft.")
        except FileNotFoundError:
            return LoadResult(empty_draft(), "No saved draft yet. Your next edits will be saved locally.")
        except DraftInvalid as exc:
            try:
                backup = self._archive()
                message = f"{exc} A recoverable copy was kept as {backup.name}. Starting a fresh draft."
            except OSError:
                message = f"{exc} The original file is still on disk. Recovery could not preserve a separate copy; saving will retry safely."
            return LoadResult(empty_draft(), message, True)
        except OSError:
            return LoadResult(empty_draft(), "The saved draft could not be opened. It is unchanged on disk. You can work here, but saving may fail until access is restored.", True)

    def save(self, draft):
        temporary = None
        try:
            data = validate_draft(draft)
            encoded = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
            if len(encoded) > MAX_SAVE_BYTES:
                raise SaveError("This draft exceeds the 8 MiB save-file limit. It remains intact in memory but is not saved.")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            # Never overwrite an unreadable or invalid original without preserving it.
            try:
                self._read()
            except FileNotFoundError:
                pass
            except DraftInvalid:
                self._archive()
            with tempfile.NamedTemporaryFile(mode="wb", dir=self.path.parent,
                                             prefix=".workcheck-", suffix=".tmp", delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
            temporary = None
        except (OSError, DraftInvalid) as exc:
            raise SaveError(f"Draft not saved: {exc}") from exc
        finally:
            if temporary is not None:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass
