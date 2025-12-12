# Setup Instructions for Streamlit Components

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Python 3.8+

## Step 1: Install Node Dependencies

```bash
cd streamlit_components/file_uploader_component
npm install
```

## Step 2: Build the Component

```bash
npm run build
```

This will create a `dist/` folder with the compiled component.

## Step 3: Test Locally (Optional)

For development with hot reload:

```bash
npm start
```

This starts a dev server on port 3001. The component will automatically connect to it during development.

## Step 4: Use in Streamlit

The component is ready to use! See the integration example in `app/main.py` or use the Python wrapper:

```python
from streamlit_components.file_uploader_component.python_wrapper import file_uploader

result = file_uploader(
    label="Upload Claims File",
    sublabel="Drag & drop or browse",
    accept=".csv,.txt,.xlsx",
    compact=False,
    key="claims_file"
)
```

## Troubleshooting

### Component not loading
- Make sure `dist/` folder exists
- Check that `npm run build` completed successfully
- Verify the path in `python_wrapper.py` is correct

### Import errors
- Run `npm install` to ensure all dependencies are installed
- Check Node.js version: `node --version` (should be 16+)

### Build errors
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check TypeScript errors: `npm run build` will show them

## For Databricks Deployment

1. Build the component: `npm run build`
2. Ensure `dist/` folder is included in your deployment package
3. Test locally first before deploying to Databricks
4. If it doesn't work on Databricks, we'll fallback to the CSS-based approach

