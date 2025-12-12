# Integration Example

Here's how to integrate the React file uploader component into your Streamlit app:

## Option 1: Use the Python Wrapper (Recommended)

```python
import sys
import os

# Add the streamlit_components directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'streamlit_components'))

from file_uploader_component.python_wrapper import file_uploader

# In your Streamlit app
result = file_uploader(
    label="Upload Claims File",
    sublabel="Drag & drop or browse",
    accept=".csv,.txt,.xlsx",
    compact=False,
    selected_file_name=st.session_state.get("claims_file_name"),
    selected_file_size=st.session_state.get("claims_file_size"),
    key="claims_file"
)

if result:
    # Decode the base64 file content
    import base64
    file_content = base64.b64decode(result['fileContent'])
    file_name = result['fileName']
    
    # Create a file-like object for Streamlit
    import io
    file_obj = io.BytesIO(file_content)
    file_obj.name = file_name
    
    # Use it like a regular uploaded file
    st.session_state.claims_file_obj = file_obj
```

## Option 2: Direct Component Usage

```python
import streamlit.components.v1 as components
import os

# Path to the component
component_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "streamlit_components",
    "file_uploader_component",
    "dist"
)

file_uploader = components.declare_component(
    "file_uploader",
    path=component_path
)

# Use it
result = file_uploader(
    label="Upload Claims File",
    sublabel="Drag & drop or browse",
    accept=".csv,.txt,.xlsx",
    compact=False,
    selectedFileName=st.session_state.get("claims_file_name"),
    selectedFileSize=st.session_state.get("claims_file_size"),
    key="claims_file"
)
```

## Fallback to Native Streamlit

If the React component doesn't work (e.g., on Databricks), you can easily fallback:

```python
USE_REACT_COMPONENT = os.path.exists(component_path)

if USE_REACT_COMPONENT:
    result = file_uploader(...)  # React component
else:
    uploaded_file = st.file_uploader(...)  # Native Streamlit
```

