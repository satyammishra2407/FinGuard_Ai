# 🚀 Hugging Face Spaces Deployment Guide

## Deploying FinGuard AI to Hugging Face Spaces

### Prerequisites
- Hugging Face account
- Git installed on your system
- Your Hugging Face access token

### Step-by-Step Deployment

#### 1. Prepare the Repository

```bash
# Navigate to your project directory
cd FinGuard_AI

# Make sure README_HF.md is renamed to README.md for Hugging Face
cp README_HF.md README.md
```

#### 2. Create a New Space on Hugging Face

1. Go to https://huggingface.co/spaces
2. Click on "Create new Space"
3. Fill in the details:
   - **Space name**: `FinGuard.Ai` (or your preferred name)
   - **License**: MIT
   - **SDK**: Streamlit
   - **Space hardware**: CPU basic (free tier)
4. Click "Create Space"

#### 3. Clone Your Space Repository

```bash
# Clone the empty space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/FinGuard.Ai
cd FinGuard.Ai
```

#### 4. Copy Files from FinGuard_AI

```bash
# Copy all necessary files
cp ../FinGuard_AI/app.py .
cp ../FinGuard_AI/config.py .
cp ../FinGuard_AI/database.py .
cp ../FinGuard_AI/detection_algorithms.py .
cp ../FinGuard_AI/ml_models.py .
cp ../FinGuard_AI/data_generator.py .
cp ../FinGuard_AI/setup_database.py .
cp ../FinGuard_AI/requirements.txt .
cp ../FinGuard_AI/README_HF.md ./README.md

# Copy model files (if they exist)
cp -r ../FinGuard_AI/models ./models

# Copy lib files
cp -r ../FinGuard_AI/lib ./lib
```

#### 5. Configure for Hugging Face

Make sure your `requirements.txt` has all dependencies:

```txt
streamlit>=1.30.0
sqlalchemy>=2.0.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
xgboost>=2.0.0
plotly>=5.17.0
pyvis>=0.3.2
seaborn>=0.12.0
matplotlib>=3.7.0
networkx>=3.0
python-dotenv>=1.0.0
faker>=20.0.0
pydantic>=2.0.0
```

#### 6. Commit and Push

```bash
# Initialize git (if needed)
git add .
git commit -m "Initial deployment of FinGuard AI"

# Push to Hugging Face
git push
```

#### 7. Monitor Deployment

1. Go to your Space page: `https://huggingface.co/spaces/YOUR_USERNAME/FinGuard.Ai`
2. Wait for the build to complete (usually 2-5 minutes)
3. Once built, your app will be live!

### Important Notes

#### Database Configuration
- Hugging Face Spaces uses **ephemeral storage**
- The SQLite database (`finguard_ai.db`) will be **reset on each restart**
- Users need to click "Generate Data" button each time the Space restarts
- This is normal for free-tier Spaces

#### Performance Considerations
- Free CPU basic tier is sufficient for demo purposes
- For better performance, consider upgrading to CPU upgrade ($0.03/hour)
- GPU is not required for this application

#### Troubleshooting

**Build Fails:**
- Check `requirements.txt` for typos
- Ensure all imports in `app.py` are available in requirements
- Check the build logs in the Space's "Logs" tab

**App Crashes:**
- Check if database initialization is working
- Verify all file paths are relative (not absolute)
- Check logs for error messages

**Slow Performance:**
- Reduce number of customers in data generation (500 instead of 1000)
- Use pagination for large data displays
- Consider upgrading Space hardware

### Updating Your Deployment

```bash
# Make changes to your local files
# Then push updates:

git add .
git commit -m "Update: description of changes"
git push
```

### Alternative: Direct Git Push Method

If you prefer to work from your local FinGuard_AI directory:

```bash
cd FinGuard_AI

# Rename README for HF
cp README_HF.md README.md

# Add HF remote
git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/FinGuard.Ai

# Push to HF
git push huggingface main
```

### Environment Variables (Optional)

If you need environment variables:

1. Go to your Space settings
2. Click on "Variables and secrets"
3. Add any required variables
4. Restart the Space

### Custom Domain (Optional)

For a custom domain:
1. Go to Space settings
2. Click on "Rename or transfer this Space"
3. Or upgrade to a custom domain through HF Pro

---

## 🎉 Congratulations!

Your FinGuard AI platform is now deployed on Hugging Face Spaces!

Share your Space URL: `https://huggingface.co/spaces/YOUR_USERNAME/FinGuard.Ai`

---

**Need Help?**
- Check Hugging Face Spaces documentation: https://huggingface.co/docs/hub/spaces
- Visit Streamlit documentation: https://docs.streamlit.io/
- Create an issue on GitHub

