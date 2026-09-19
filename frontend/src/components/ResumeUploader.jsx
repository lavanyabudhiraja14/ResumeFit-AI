import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, X, AlertCircle } from 'lucide-react';

const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.jpg', '.jpeg', '.png'];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

function formatBytes(bytes) {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export default function ResumeUploader({ onAnalyze, isAnalyzing, error, setError }) {
  const [file, setFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef(null);

  const validateAndSetFile = (selectedFile) => {
    if (!selectedFile) return;

    setError(null);
    const filename = selectedFile.name || '';
    const ext = filename.substring(filename.lastIndexOf('.')).toLowerCase();

    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setError(`Unsupported file format '${ext}'. Please upload PDF, DOCX, JPG, or PNG.`);
      return;
    }

    if (selectedFile.size > MAX_FILE_SIZE) {
      setError(`File size exceeds 10MB limit (${formatBytes(selectedFile.size)}).`);
      return;
    }

    if (selectedFile.size === 0) {
      setError('The selected file is empty.');
      return;
    }

    setFile(selectedFile);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleRemove = (e) => {
    e.stopPropagation();
    setFile(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  const handleAnalyzeClick = () => {
    if (!file || isAnalyzing) return;
    onAnalyze(file);
  };

  return (
    <div className="w-full">
      <input
        ref={inputRef}
        type="file"
        id="resume-file-input"
        className="hidden"
        accept=".pdf,.docx,.jpg,.jpeg,.png"
        onChange={(e) => {
          if (e.target.files && e.target.files[0]) {
            validateAndSetFile(e.target.files[0]);
          }
        }}
      />

      {/* Upload Zone or Selected File View */}
      {!file ? (
        <div
          id="drop-zone"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => inputRef.current?.click()}
          className={`group cursor-pointer rounded-xl border border-dashed transition-all duration-200 p-12 text-center flex flex-col items-center justify-center bg-[#151515] ${
            isDragOver
              ? 'border-[#FF6A00] bg-[#151515]/90 ring-1 ring-[#FF6A00]'
              : 'border-[#242424] hover:border-[#333333] hover:bg-[#181818]'
          }`}
        >
          <div className="w-12 h-12 rounded-full bg-[#111111] border border-[#242424] flex items-center justify-center mb-4 group-hover:border-[#FF6A00]/40 transition-colors">
            <UploadCloud className="w-5 h-5 text-[#A1A1A1] group-hover:text-[#FF6A00] transition-colors" />
          </div>

          <p className="text-base font-medium text-[#F5F5F5] mb-1">
            Drop your resume here
          </p>
          <p className="text-sm text-[#A1A1A1] mb-4">
            or <span className="text-[#FF6A00] hover:underline">click to browse</span>
          </p>

          <div className="text-xs font-mono tracking-wider text-[#666666] uppercase bg-[#111111] px-3 py-1 rounded border border-[#242424]">
            PDF, DOCX, JPG, PNG
          </div>
        </div>
      ) : (
        <div className="rounded-xl border border-[#242424] bg-[#151515] p-6 transition-all">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 min-w-0">
              <div className="w-11 h-11 rounded-lg bg-[#111111] border border-[#242424] flex items-center justify-center flex-shrink-0">
                <FileText className="w-5 h-5 text-[#FF6A00]" />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium text-[#F5F5F5] truncate">
                  {file.name}
                </p>
                <div className="flex items-center gap-2 mt-0.5 text-xs text-[#A1A1A1] font-mono">
                  <span>{formatBytes(file.size)}</span>
                  <span>•</span>
                  <span className="uppercase">{file.name.split('.').pop()}</span>
                </div>
              </div>
            </div>

            <button
              type="button"
              id="remove-file-btn"
              onClick={handleRemove}
              disabled={isAnalyzing}
              className="text-xs text-[#A1A1A1] hover:text-[#F5F5F5] p-2 rounded hover:bg-[#1E1E1E] transition-colors flex items-center gap-1.5"
            >
              <X className="w-4 h-4" />
              <span>Remove</span>
            </button>
          </div>

          {/* Primary CTA Button */}
          <div className="mt-6 pt-5 border-t border-[#242424] flex justify-end">
            <button
              type="button"
              id="analyze-resume-btn"
              onClick={handleAnalyzeClick}
              disabled={isAnalyzing}
              className={`px-6 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-2.5 ${
                isAnalyzing
                  ? 'bg-[#1E1E1E] text-[#A1A1A1] cursor-not-allowed border border-[#333333]'
                  : 'bg-[#FF6A00] text-black hover:bg-[#FF7A1A] font-semibold cursor-pointer shadow-sm hover:shadow-[#FF6A00]/20'
              }`}
            >
              {isAnalyzing && (
                <svg
                  className="animate-spin -ml-1 h-4 w-4 text-[#FF6A00]"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
              )}
              <span>{isAnalyzing ? 'Analyzing...' : 'Analyze Resume'}</span>
            </button>
          </div>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="mt-4 p-3.5 rounded-lg bg-red-950/30 border border-red-900/40 text-red-400 text-xs flex items-center gap-2.5">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
