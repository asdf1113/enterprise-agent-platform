import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


DOCUMENT_ROOT = Path("data/documents")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


@dataclass(frozen=True)
class DocumentMetadata:
    document_id: str
    document_name: str
    document_type: str
    department: str
    version: str
    effective_date: date
    product: str
    region: str
    allowed_roles: tuple[str, ...]
    source_path: str


@dataclass(frozen=True)
class DocumentSection:
    title: str
    content: str


@dataclass(frozen=True)
class ParsedDocument:
    metadata: DocumentMetadata
    sections: tuple[DocumentSection, ...]


def load_manifest(
    document_root: Path = DOCUMENT_ROOT,
) -> list[DocumentMetadata]:
    manifest_path = document_root / "manifest.json"

    raw_documents = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )

    return [
        DocumentMetadata(
            document_id=item["document_id"],
            document_name=item["document_name"],
            document_type=item["document_type"],
            department=item["department"],
            version=item["version"],
            effective_date=date.fromisoformat(
                item["effective_date"]
            ),
            product=item["product"],
            region=item["region"],
            allowed_roles=tuple(item["allowed_roles"]),
            source_path=item["source_path"],
        )
        for item in raw_documents
    ]


def parse_markdown(
    metadata: DocumentMetadata,
    document_root: Path = DOCUMENT_ROOT,
) -> ParsedDocument:
    source_path = document_root / metadata.source_path
    lines = source_path.read_text(
        encoding="utf-8"
    ).splitlines()

    sections: list[DocumentSection] = []

    current_title: str | None = None
    current_lines: list[str] = []

    for line in lines:
        match = HEADING_PATTERN.match(line)

        if match:
            level = len(match.group(1))
            heading = match.group(2).strip()

            if level == 1:
                continue

            if current_title is not None:
                content = "\n".join(
                    current_lines
                ).strip()

                if content:
                    sections.append(
                        DocumentSection(
                            title=current_title,
                            content=content,
                        )
                    )

            current_title = heading
            current_lines = []
            continue

        if current_title is not None:
            current_lines.append(line)

    if current_title is not None:
        content = "\n".join(current_lines).strip()

        if content:
            sections.append(
                DocumentSection(
                    title=current_title,
                    content=content,
                )
            )

    return ParsedDocument(
        metadata=metadata,
        sections=tuple(sections),
    )


def load_documents(
    document_root: Path = DOCUMENT_ROOT,
) -> list[ParsedDocument]:
    return [
        parse_markdown(metadata, document_root)
        for metadata in load_manifest(document_root)
    ]
