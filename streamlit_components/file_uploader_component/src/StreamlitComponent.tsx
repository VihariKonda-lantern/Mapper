import React, { useState, useEffect } from "react";
import { Streamlit } from "streamlit-component-lib";
import FileUploader from "./FileUploader";
import "./styles.css";

interface FileUploaderProps {
  label: string;
  sublabel?: string;
  accept?: string;
  compact?: boolean;
  selectedFileName?: string;
  selectedFileSize?: number;
}

const StreamlitComponent: React.FC = () => {
  const [props, setProps] = useState<FileUploaderProps>({
    label: "Upload File",
    sublabel: "Drag & drop or browse",
    accept: ".csv,.txt,.xlsx",
    compact: false,
  });

  useEffect(() => {
    // Get args from Streamlit (passed via URL or window)
    const getStreamlitArgs = () => {
      // Try to get from window (set by index.tsx)
      if ((window as any).streamlitComponentValue) {
        return (window as any).streamlitComponentValue;
      }
      // Try to get from URL params
      const urlParams = new URLSearchParams(window.location.search);
      const argsParam = urlParams.get("args");
      if (argsParam) {
        try {
          return JSON.parse(decodeURIComponent(argsParam));
        } catch (e) {
          return {};
        }
      }
      return {};
    };

    const args = getStreamlitArgs();
    if (args.label || args.accept) {
      setProps({
        label: args.label || "Upload File",
        sublabel: args.sublabel || "Drag & drop or browse",
        accept: args.accept || ".csv,.txt,.xlsx",
        compact: args.compact || false,
        selectedFileName: args.selectedFileName,
        selectedFileSize: args.selectedFileSize,
      });
    }
    
    // Set component ready
    Streamlit.setComponentReady();
  }, []);

  const handleFileSelect = (file: File | null) => {
    if (file) {
      // Convert file to base64 for Streamlit
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = (reader.result as string).split(",")[1];
        Streamlit.setComponentValue({
          fileName: file.name,
          fileSize: file.size,
          fileType: file.type,
          fileContent: base64,
        });
      };
      reader.readAsDataURL(file);
    } else {
      Streamlit.setComponentValue(null);
    }
  };

  return (
    <div style={{ width: "100%" }}>
      <FileUploader
        label={props.label}
        sublabel={props.sublabel}
        accept={props.accept}
        compact={props.compact}
        selectedFileName={props.selectedFileName}
        selectedFileSize={props.selectedFileSize}
        onFileSelect={handleFileSelect}
      />
    </div>
  );
};

export default StreamlitComponent;

