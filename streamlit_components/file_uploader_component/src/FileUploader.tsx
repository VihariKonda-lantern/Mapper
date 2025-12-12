import React, { useRef, useState } from "react";
import { UploadCloud, CheckCircle } from "lucide-react";

interface FileUploaderProps {
  label: string;
  sublabel?: string;
  accept?: string;
  onFileSelect: (file: File | null) => void;
  selectedFileName?: string;
  selectedFileSize?: number;
  compact?: boolean;
}

const FileUploader: React.FC<FileUploaderProps> = ({
  label,
  sublabel = "Drag & drop or browse",
  accept = ".csv,.txt,.xlsx",
  onFileSelect,
  selectedFileName,
  selectedFileSize,
  compact = false,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleClick = () => {
    inputRef.current?.click();
  };

  // Success State (File Selected)
  if (selectedFileName) {
    const fileSizeKb = selectedFileSize ? selectedFileSize / 1024 : 0;
    const fileSizeMb = fileSizeKb / 1024;
    const sizeStr = fileSizeKb > 1024 ? `${fileSizeMb.toFixed(1)} MB` : `${fileSizeKb.toFixed(1)} KB`;

    if (compact) {
      return (
        <div
          className="file-uploader-success-compact"
          onClick={handleClick}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            ref={inputRef}
            type="file"
            accept={accept}
            onChange={handleChange}
            style={{ display: "none" }}
          />
          <div className="file-uploader-content">
            <div className="file-uploader-icon success">
              <CheckCircle size={16} />
            </div>
            <div className="file-uploader-info">
              <p className="file-uploader-name">{selectedFileName}</p>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div
        className="file-uploader-success"
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleChange}
          style={{ display: "none" }}
        />
        <div className="file-uploader-content">
          <div className="file-uploader-icon success large">
            <CheckCircle size={20} />
          </div>
          <div className="file-uploader-info">
            <p className="file-uploader-name">{selectedFileName}</p>
            <p className="file-uploader-size">{sizeStr} • Ready to process</p>
          </div>
        </div>
      </div>
    );
  }

  // Empty State (Compact)
  if (compact) {
    return (
      <div
        className={`file-uploader-empty-compact ${isDragging ? "dragging" : ""}`}
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleChange}
          style={{ display: "none" }}
        />
        <div className="file-uploader-content">
          <div className="file-uploader-icon">
            <UploadCloud size={16} />
          </div>
          <div className="file-uploader-info">
            <p className="file-uploader-label">{label}</p>
          </div>
        </div>
      </div>
    );
  }

  // Empty State (Full / Main)
  return (
    <div
      className={`file-uploader-empty ${isDragging ? "dragging" : ""}`}
      onClick={handleClick}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleChange}
        style={{ display: "none" }}
      />
      <div className="file-uploader-content">
        <div className="file-uploader-icon large">
          <UploadCloud size={28} />
        </div>
        <p className="file-uploader-label">{label}</p>
        <p className="file-uploader-sublabel">{sublabel}</p>
        <p className="file-uploader-hint">Limit 200MB per file • {accept.toUpperCase()}</p>
      </div>
    </div>
  );
};

export default FileUploader;

