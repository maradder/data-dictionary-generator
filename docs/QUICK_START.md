# Quick Start Guide - Data Dictionary Generator

## 🚀 Get Started in 3 Minutes

### Step 1: Start the Backend (Terminal 1)

```bash
cd backend
uvicorn main:app --reload
```

✅ Backend running at: **http://localhost:8000**
📚 API docs available at: **http://localhost:8000/docs**

### Step 2: Start the Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

✅ Frontend running at: **http://localhost:5173**

### Step 3: Upload Sample Data

1. Open **http://localhost:5173** in your browser
2. Click the **"⬆️ Upload New"** button in the top right
3. Drag and drop the **`sample-data.json`** file (located in the root directory)
4. Fill in the form:
   - **Name**: "User Analytics Data"
   - **Description**: "Sample customer data with PII, nested structures, and statistics"
   - ✅ **Generate AI descriptions**: Keep checked
5. Click **"Create Dictionary"**
6. Wait 1-2 minutes for processing ⏳

### Step 4: Explore Your Data Dictionary

After upload completes, you'll see:

**📊 Overview Tab**
- Total fields detected: ~40
- Records analyzed: 10
- File size and version info
- Quick statistics cards

**🔍 Fields Tab (Click to explore!)**
- Search for any field (try "email" or "order")
- Sort columns by clicking headers
- Click "Details →" on any row to see:
  - Full statistics (min, max, mean, median)
  - PII warnings
  - Sample values
  - AI-generated descriptions
  - Null percentages

**📝 Versions Tab**
- View version history
- Compare versions (after uploading multiple versions)

### Step 5: Test Key Features

#### Export to Excel
1. Click **"📥 Export Excel"** button
2. Excel file downloads with formatted data dictionary
3. Open to see professional formatting with:
   - Field names, types, descriptions
   - Statistics and sample values
   - PII indicators
   - Color-coded null percentages

#### Browse All Dictionaries
1. Click **"📚 Dictionaries"** in the top nav
2. See all uploaded dictionaries
3. Pagination controls at bottom
4. Click any card to view details

#### Search Fields
1. In the Fields tab, use the search box
2. Try searching:
   - "email" - finds email field
   - "order" - finds all order-related fields
   - "address" - finds address fields
3. Results filter in real-time

#### View Field Details
1. Click "Details →" on any field in the table
2. Modal opens with comprehensive information:
   - **Type Info**: Data type, semantic type, nullable
   - **PII Warning**: If field contains sensitive data
   - **Quality Metrics**: Null %, cardinality, distinct count
   - **Statistics**: Min, max, mean, median (for numbers)
   - **Sample Values**: Up to 10 examples
   - **AI Description**: Automatically generated explanation

## 🎯 What to Test

### For Data Engineers
- [x] Upload JSON files (supports .json, .jsonl, .ndjson)
- [x] View all detected fields with nesting
- [x] Check PII auto-detection
- [x] Export to Excel with formatting

### For Data Analysts
- [x] Search for specific fields
- [x] View data quality metrics
- [x] Read AI-generated field descriptions
- [x] Export formatted reports

### For Data Scientists
- [x] View statistical distributions
- [x] Check percentiles and outliers
- [x] Analyze cardinality
- [x] Inspect sample values

## 🧪 Advanced Testing

### Upload Multiple Versions
1. Edit `sample-data.json` (add/remove a field)
2. Go back to dictionary detail page
3. Click **"⬆️ New Version"**
4. Upload modified file
5. View version comparison in Versions tab

### Test with Your Own Data
Replace `sample-data.json` with your own JSON file:
- Any structure (nested or flat)
- Arrays supported
- Max file size: 500MB
- Formats: .json, .jsonl, .ndjson

### Check PII Detection
The sample file includes:
- **Email**: john.doe@example.com (should flag as PII)
- **Phone**: +1-555-123-4567 (should flag as PII)
- **SSN**: 123-45-6789 (should flag as PII)
- **Credit Card**: Last 4 digits (should flag as PII)

Look for red **PII** badges in the field table!

## 📱 UI Features

### Navigation
- **Header**: Click logo to go home
- **Tabs**: Switch between Overview, Fields, Versions
- **Breadcrumbs**: "← Back" button on detail pages

### Responsive Design
- Desktop: Full 3-column layout
- Tablet: 2-column grid
- Mobile: Single column (optimized but best on desktop)

### Dark Mode Support
- UI supports dark mode theme
- Automatically respects system preference
- CSS variables for easy customization

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version (need 3.11+)
python --version

# Reinstall dependencies
cd backend
pip install -r requirements.txt

# Check port 8000 is free
lsof -ti:8000
```

### Frontend won't start
```bash
# Check Node version (need 18+)
node --version

# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check port 5173 is free
lsof -ti:5173
```

### Upload fails
- **Check file size**: Must be < 500MB
- **Check file format**: Must be valid JSON
- **Check backend logs**: Look for error messages
- **Check CORS**: Frontend must be on localhost:5173

### No AI descriptions
- **Check OpenAI API key**: Set in backend `.env`
- **Check rate limits**: OpenAI API may be rate-limited
- **Toggle off**: Uncheck "Generate AI descriptions" to skip

### Fields not showing
- **Check backend processing**: Look for errors in backend logs
- **Refresh page**: Sometimes React Query cache needs refresh
- **Check browser console**: Look for frontend errors

## 🎓 Next Steps

1. **Read the sample data README**: `SAMPLE_DATA_README.md` for details on test data
2. **Check backend docs**: Navigate to `http://localhost:8000/docs` for API documentation
3. **Explore the code**:
   - Frontend: `frontend/src/`
   - Backend: `backend/`
4. **Customize**: Update colors, add features, modify components

## 📞 Need Help?

- **Backend issues**: Check backend logs in terminal
- **Frontend issues**: Check browser console (F12)
- **API issues**: Check `http://localhost:8000/docs` for API status

---

**Enjoy exploring your data with AI-powered insights! 🎉**
