# 🖥️ FinGuard AI - Local Setup & Running Guide

## ✅ YOUR APP IS RUNNING!

If you see this in terminal:
```
You can now view your Streamlit app in your browser.
Network URL: http://192.168.29.25:8501
```

**Congratulations! The app is RUNNING successfully!** 🎉

---

## 🌐 How to Access the App

### Option 1: Automatic Browser Open
Just run this file by double-clicking:
```
OPEN_APP.bat
```

### Option 2: Manual URL
Open any browser and go to:
```
http://localhost:8501
```

### Option 3: Network Access (from other devices)
From mobile/tablet on same WiFi:
```
http://192.168.29.25:8501
```

---

## 🚀 Step-by-Step: Running Locally

### Step 1: Open Terminal/PowerShell
```bash
cd C:\Users\pc\OneDrive\Desktop\FinGuard.AI
```

### Step 2: Run Streamlit
```bash
python -m streamlit run app.py
```

### Step 3: Wait for Message
You'll see:
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.29.25:8501
```

### Step 4: Open Browser
- Browser should open automatically
- If not, manually visit: http://localhost:8501

---

## ⚙️ Troubleshooting

### Problem 1: "Port 8501 is already in use"

**Solution A: Kill the existing process**
```powershell
# Find process using port 8501
netstat -ano | findstr :8501

# Kill it (replace PID with actual number)
taskkill /F /PID <PID_NUMBER>

# Then run app again
python -m streamlit run app.py
```

**Solution B: Use different port**
```bash
python -m streamlit run app.py --server.port 8502
```
Then open: http://localhost:8502

---

### Problem 2: "streamlit: command not found"

**Solution:** Use full Python command:
```bash
python -m streamlit run app.py
```

---

### Problem 3: "ModuleNotFoundError"

**Solution:** Install requirements:
```bash
pip install -r requirements.txt
```

---

### Problem 4: Browser doesn't open automatically

**Solution:** Manually open:
1. Open any browser (Chrome, Firefox, Edge)
2. Go to: `http://localhost:8501`

Or double-click: `OPEN_APP.bat`

---

## 🛑 How to Stop the App

### Method 1: In Terminal
Press `Ctrl + C` in the terminal where app is running

### Method 2: Kill Process
```powershell
# Find process
netstat -ano | findstr :8501

# Kill (replace PID)
taskkill /F /PID <PID>
```

---

## 📊 App Features to Test

Once app opens in browser, you can:

1. **Dashboard** 📊
   - View risk metrics
   - See customer distribution charts
   - Check recent alerts

2. **Customer Search** 🔍
   - Search by name or ID
   - View customer profiles
   - See transaction history

3. **Risk Analysis** 📈
   - Behavioral analysis
   - Transaction timing patterns
   - Anomaly detection

4. **Network Analysis** 🕸️
   - Smurfing network detection
   - Interactive graph visualization

5. **Alert Management** 🚨
   - View all alerts
   - Filter by status
   - Take actions

6. **ML Models** 🤖
   - Train risk models
   - View performance metrics

---

## 🔄 Quick Commands Reference

### Start App
```bash
python -m streamlit run app.py
```

### Start on Different Port
```bash
python -m streamlit run app.py --server.port 8502
```

### Check if Running
```bash
netstat -ano | findstr :8501
```

### Stop App
Press `Ctrl + C` in terminal

### Open Browser
Double-click `OPEN_APP.bat` or visit http://localhost:8501

---

## 📝 Normal Behavior

### What You'll See in Terminal:
```
Collecting usage statistics. To deactivate, set browser.gatherUsageStats to False.

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.29.25:8501
```

### This is GOOD! ✅
- App is running
- Open browser to access it
- Keep terminal window open

### This is BAD! ❌
```
Port 8501 is already in use
ModuleNotFoundError: No module named 'streamlit'
Error: Could not find app.py
```

If you see bad messages, check Troubleshooting section above.

---

## 🎯 Next Steps After Local Testing

Once you confirm app works locally:

1. **Push to GitHub** (Already done ✅)
   ```bash
   git add .
   git commit -m "Update"
   git push
   ```

2. **Deploy to Streamlit Cloud**
   - Go to: https://share.streamlit.io/
   - Connect your repo: `satyammishra2407/FinGuard.Ai`
   - Deploy!
   - Access at: https://finguard-ai.streamlit.app/

---

## 💡 Pro Tips

1. **Keep Terminal Open**
   - Don't close terminal while using app
   - App will stop if terminal closes

2. **Auto-reload**
   - Streamlit auto-reloads when you save code changes
   - No need to restart app

3. **Clear Cache**
   - If app behaves weird, press `C` in terminal
   - Or use "Clear cache" in browser (top-right menu)

4. **Check Logs**
   - Terminal shows all errors and logs
   - Useful for debugging

---

## 🆘 Still Having Issues?

1. **Check Python Version**
   ```bash
   python --version
   ```
   Should be 3.8+

2. **Reinstall Dependencies**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Check Database**
   ```bash
   python setup_database.py
   ```

4. **Test Individual Modules**
   ```bash
   python -c "import streamlit; print('OK')"
   ```

---

**Created by:** Satyam Mishra  
**Last Updated:** October 24, 2025  
**License:** MIT

