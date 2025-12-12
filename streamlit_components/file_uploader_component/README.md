# File Uploader Streamlit Component

A React-based file uploader component for Streamlit that matches the modern React design.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Build the component:
```bash
npm run build
```

3. For development with hot reload:
```bash
npm start
```

## Usage in Streamlit

```python
import streamlit.components.v1 as components

# Load the component
file_uploader = components.declare_component(
    "file_uploader",
    path="./streamlit_components/file_uploader_component/dist"
)

# Use it
result = file_uploader(
    label="Upload Claims File",
    sublabel="Drag & drop or browse",
    accept=".csv,.txt,.xlsx",
    compact=False,
    key="claims_file"
)
```

## Development

- `npm start` - Start dev server on port 3001
- `npm run build` - Build for production
- `npm run build:dev` - Build for development

## Notes

- The component sends file data as base64 to Streamlit
- Make sure to handle file size limits in your Streamlit app
- For Databricks deployment, ensure the dist folder is included

