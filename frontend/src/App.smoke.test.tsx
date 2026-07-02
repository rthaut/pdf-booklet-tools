import { afterEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import App from "./App";

function createPdfFile(name = "booklet.pdf") {
  const pdfBytes = new Uint8Array([
    0x25, 0x50, 0x44, 0x46, 0x2d, 0x31, 0x2e, 0x34, 0x0a, 0x25, 0xe2, 0xe3,
    0xcf, 0xd3, 0x0a,
  ]);

  return new File([pdfBytes], name, { type: "application/pdf" });
}

function createPdfResponse() {
  return {
    ok: true,
    headers: {
      get: (header: string) =>
        header.toLowerCase() === "content-disposition"
          ? 'attachment; filename="booklet-swapped.pdf"'
          : "application/pdf",
    },
    blob: async () => new Blob(["processed-pdf"], { type: "application/pdf" }),
  } as Response;
}

describe("PDF processing smoke path", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("uploads a PDF, selects an option, posts FormData, and downloads the result", async () => {
    const fetchMock = vi
      .spyOn(window, "fetch")
      .mockResolvedValue(createPdfResponse());
    const createObjectUrlMock = vi
      .spyOn(window.URL, "createObjectURL")
      .mockReturnValue("blob:processed-pdf");
    const revokeObjectUrlMock = vi
      .spyOn(window.URL, "revokeObjectURL")
      .mockImplementation(() => undefined);
    const anchorClickMock = vi
      .spyOn(HTMLAnchorElement.prototype, "click")
      .mockImplementation(() => undefined);

    const { container } = render(<App />);
    const input = container.querySelector('input[type="file"]');
    const file = createPdfFile();

    expect(input).toBeInstanceOf(HTMLInputElement);

    fireEvent.change(input as HTMLInputElement, {
      target: { files: [file] },
    });
    fireEvent.click(screen.getByRole("button", { name: /reorder booklet pages/i }));

    const processButton = screen.getByRole("button", {
      name: /process pdf/i,
    }) as HTMLButtonElement;
    await waitFor(() => expect(processButton.disabled).toBe(false));
    fireEvent.click(processButton);

    await waitFor(() => expect(fetchMock).toHaveBeenCalledOnce());

    const [url, request] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/process/swap");
    expect(request).toMatchObject({ method: "POST" });
    expect(request?.body).toBeInstanceOf(FormData);
    expect((request?.body as FormData).get("file")).toBe(file);

    await waitFor(() => expect(anchorClickMock).toHaveBeenCalledOnce());
    const downloadLink = anchorClickMock.mock.instances[0] as HTMLAnchorElement;
    expect(downloadLink.href).toBe("blob:processed-pdf");
    expect(downloadLink.download).toBe("booklet-swapped.pdf");
    expect(createObjectUrlMock).toHaveBeenCalledWith(expect.any(Blob));
    expect(revokeObjectUrlMock).toHaveBeenCalledWith("blob:processed-pdf");
  });
});
