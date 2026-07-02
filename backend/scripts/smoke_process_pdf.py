from __future__ import annotations

import io
import logging
import sys
from pathlib import Path

from fastapi.testclient import TestClient
from PyPDF2 import PdfReader, PdfWriter

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

logging.disable(logging.CRITICAL)
from app.main import app  # noqa: E402
logging.disable(logging.NOTSET)
logging.getLogger().setLevel(logging.WARNING)


def create_booklet_pdf() -> bytes:
    writer = PdfWriter()
    for _ in range(2):
        writer.add_blank_page(width=400, height=200)

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def page_count(pdf_bytes: bytes) -> int:
    return len(PdfReader(io.BytesIO(pdf_bytes)).pages)


def assert_pdf_response(response, expected_pages: int) -> None:
    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("application/pdf")
    assert len(response.content) > 0
    assert page_count(response.content) == expected_pages


def post_pdf(client: TestClient, path: str):
    pdf_bytes = create_booklet_pdf()
    files = {"file": ("booklet.pdf", pdf_bytes, "application/pdf")}
    return client.post(path, files=files)


def main() -> None:
    print("[smoke] backend PDF processing")
    print(f"[smoke] python: {sys.version.split()[0]}")
    print(f"[smoke] backend: {BACKEND_DIR}")

    client = TestClient(app)

    swap_response = post_pdf(client, "/api/process/swap")
    assert_pdf_response(swap_response, expected_pages=2)
    print(f"[smoke] swap: {len(swap_response.content)} bytes, 2 pages")

    scale_response = post_pdf(client, "/api/process/scale")
    assert_pdf_response(scale_response, expected_pages=4)
    print(f"[smoke] scale: {len(scale_response.content)} bytes, 4 pages")


if __name__ == "__main__":
    main()
