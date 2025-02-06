"use client";

import type React from "react";
import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Book, Maximize, Upload } from "lucide-react";

interface ProcessingOption {
  id: string;
  label: string;
  icon: React.ReactNode;
}

const processingOptions: ProcessingOption[] = [
  {
    id: "swap",
    label: "Reorder booklet pages",
    icon: <Book className="w-6 h-6" />,
  },
  {
    id: "scale",
    label: "Scale to portrait",
    icon: <Maximize className="w-6 h-6" />,
  },
];

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFile(acceptedFiles[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
  });

  const handleProcessing = async () => {
    if (!file || !selectedOption) return;

    setIsProcessing(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/process/" + selectedOption, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Processing failed");

      const blob = await response.blob();

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;

      // Get filename from Content-Disposition header if present
      const contentDisposition = response.headers.get("content-disposition");
      const filename = contentDisposition
        ? contentDisposition.split("filename=")[1].replace(/"/g, "")
        : `processed-${file.name}`;

      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error processing PDF:", error);
      alert("An error occurred while processing the PDF.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-center text-blue-400">
          PDF Booklet Tools
        </h1>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 mb-8 text-center cursor-pointer transition-all duration-300 ease-in-out ${
            isDragActive
              ? "border-blue-400 bg-blue-400 bg-opacity-10"
              : "border-gray-600 hover:border-gray-500"
          }`}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center">
            <Upload className="w-12 h-12 mb-4 text-blue-400" />
            {file ? (
              <p className="text-lg">Selected file: {file.name}</p>
            ) : (
              <p className="text-lg">
                Drag and drop a PDF file here, or click to select a file
              </p>
            )}
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4 mb-8">
          {processingOptions.map((option) => (
            <button
              key={option.id}
              onClick={() => setSelectedOption(option.id)}
              className={`flex flex-col items-center justify-center p-6 rounded-lg transition-all duration-300 ease-in-out ${
                selectedOption === option.id
                  ? "bg-blue-600 text-white"
                  : "bg-gray-800 hover:bg-gray-700"
              }`}
            >
              {option.icon}
              <span className="mt-2 text-sm">{option.label}</span>
            </button>
          ))}
        </div>
        <button
          onClick={handleProcessing}
          disabled={!file || !selectedOption || isProcessing}
          className={`w-full py-3 rounded-lg font-semibold text-lg transition-all duration-300 ease-in-out ${
            !file || !selectedOption || isProcessing
              ? "bg-gray-700 text-gray-500 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700 text-white"
          }`}
        >
          {isProcessing ? "Processing..." : "Process PDF"}
        </button>
      </div>
    </div>
  );
}

export default App;
