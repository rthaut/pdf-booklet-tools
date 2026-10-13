import io

from fastapi.testclient import TestClient
from pdf2image import convert_from_bytes
from PIL import Image
from PyPDF2 import PdfReader

from app.main import app
from app.pdf_utils import get_poppler_path

client = TestClient(app)

# Each half of each input page is filled with one of these colors, so the
# output pages can be checked for which input half landed where.
COLORS = {
    "1": (255, 0, 0),
    "2": (0, 255, 0),
    "3": (0, 0, 255),
    "4": (255, 255, 0),
}

PAGE_WIDTH = 600
PAGE_HEIGHT = 400


def make_spread(left: str, right: str) -> Image.Image:
    page = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT))
    half = PAGE_WIDTH // 2
    page.paste(COLORS[left], (0, 0, half, PAGE_HEIGHT))
    page.paste(COLORS[right], (half, 0, PAGE_WIDTH, PAGE_HEIGHT))
    return page


def make_pdf(spreads) -> bytes:
    pages = [make_spread(left, right) for left, right in spreads]
    output = io.BytesIO()
    pages[0].save(output, format="PDF", save_all=True, append_images=pages[1:])
    return output.getvalue()


def nearest_label(pixel) -> str:
    return min(
        COLORS,
        key=lambda label: sum((a - b) ** 2 for a, b in zip(COLORS[label], pixel)),
    )


def render(pdf_bytes: bytes):
    return convert_from_bytes(pdf_bytes, dpi=36, poppler_path=get_poppler_path())


def half_labels(page: Image.Image):
    page = page.convert("RGB")
    width, height = page.size
    left = page.getpixel((width // 4, height // 2))
    right = page.getpixel((3 * width // 4, height // 2))
    return nearest_label(left), nearest_label(right)


def center_label(page: Image.Image) -> str:
    page = page.convert("RGB")
    width, height = page.size
    return nearest_label(page.getpixel((width // 2, height // 2)))


def post_pdf(path: str, pdf_bytes: bytes, filename: str = "booklet.pdf"):
    files = {"file": (filename, pdf_bytes, "application/pdf")}
    return client.post(path, files=files)


def test_fixture_pdf_has_expected_layout():
    pdf_bytes = make_pdf([("1", "2"), ("3", "4")])
    pages = render(pdf_bytes)
    assert [half_labels(page) for page in pages] == [("1", "2"), ("3", "4")]


def test_swap_reorders_halves_into_booklet_order():
    pdf_bytes = make_pdf([("1", "2"), ("3", "4")])

    response = post_pdf("/api/process/swap", pdf_bytes)

    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == "application/pdf"
    assert (
        response.headers["content-disposition"]
        == 'attachment; filename="booklet-swapped.pdf"'
    )
    assert len(PdfReader(io.BytesIO(response.content)).pages) == 2
    pages = render(response.content)
    assert [half_labels(page) for page in pages] == [("4", "1"), ("2", "3")]


def test_scale_splits_each_spread_into_portrait_pages_in_order():
    pdf_bytes = make_pdf([("1", "2"), ("3", "4")])

    response = post_pdf("/api/process/scale", pdf_bytes)

    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == "application/pdf"
    assert (
        response.headers["content-disposition"]
        == 'attachment; filename="booklet-scaled.pdf"'
    )
    assert len(PdfReader(io.BytesIO(response.content)).pages) == 4
    pages = render(response.content)
    assert [center_label(page) for page in pages] == ["1", "2", "3", "4"]
    for page in pages:
        width, height = page.size
        assert height > width


def test_swap_rejects_non_pdf_upload():
    response = post_pdf("/api/process/swap", b"not a pdf", filename="notes.txt")
    assert response.status_code == 500
