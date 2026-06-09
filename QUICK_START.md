# 🚀 Quick Start Guide - Green Model Advisor with Authentication

## ⚡ 30 Second Setup

### Terminal 1: Start Backend
```bash
cd c:\games\green-model-advisor
python run.py
```
Wait for: `Uvicorn running on http://0.0.0.0:8000`

### Terminal 2: Start Frontend
```bash
cd c:\games\green-model-advisor\client
npm install  # Only first time
npm run dev
```
You'll see: `VITE v... ready in ... ms`

### Step 3: Open Browser
```
http://localhost:5173
```

## 🔐 Your First Login

### Sign Up (First Time)
1. Click **"Don't have an account? Sign up here"**
2. Fill in:
   - **Full Name**: Your Name
   - **Email**: your@email.com
   - **Password**: min 6 characters
   - **Confirm Password**: same as above
3. Click **Sign Up** ✅

### What You'll See
- Profile avatar with your initial in top-left
- Sidebar with chat history (empty at first)
- Main chat area ready to use

## 💬 Create Your First Chat

1. Type a prompt: `"Explain carbon emissions in AI models"`
2. Click **"📤 Estimate"** (Single Mode)
3. Wait for response...
4. See results with:
   - **Model Used**: Best model auto-selected
   - **Carbon Emission**: CO2 equivalent
   - **Accuracy Score**: Quality percentage

## 📊 View Your Dashboard

1. Click **"📈 Dashboard"** tab
2. See your model performance:
   - Model selection count
   - Carbon efficiency stats
   - Accuracy metrics

## 👤 Check Your Profile

1. Click your **avatar** (top-left corner)
2. See dropdown with:
   - Your email
   - Your name
   - **"View Profile"** button
3. Click **View Profile** to see:
   - Total chats created
   - Total estimates performed
   - Member since date

## 🔄 Test Multi-User Feature

1. Click **Logout** in profile dropdown
2. Click **"Don't have an account? Sign up here"**
3. Sign up as different user: `alice@email.com`
4. Create new chats
5. **Logout** and **login** as first user
6. ✅ **See only your original chats!**

## 🧪 Testing Scenarios

### Scenario 1: Persistent Storage
- ✅ Create chats
- ✅ Close browser completely
- ✅ Reopen → auto-logged in with all data

### Scenario 2: Model Selection
- Try **Single Mode**: Auto-picks best model
- Try **Compare Mode**: Compare 2-3 models side-by-side
- See carbon emissions and accuracy

### Scenario 3: Different Prompts
```
✓ "What is machine learning?"
✓ "How to optimize Python code?"
✓ "Explain blockchain technology"
✓ "Generate a poem about AI"
```

## 🎮 Features to Try

| Feature | How | Expected |
|---------|-----|----------|
| **Single Mode** | Type prompt + click Estimate | Best model auto-selected |
| **Compare Mode** | Select 2+ models + click Compare | Side-by-side comparison |
| **Dashboard** | Click Dashboard tab | Your stats appear |
| **Rename Chat** | Click ✏️ on chat in sidebar | Enter new name |
| **Delete Chat** | Click 🗑️ on chat in sidebar | Chat removed |
| **Profile Stats** | Click avatar → View Profile | Stats modal shows |
| **New Chat** | Click ➕ New Chat | Fresh conversation |

## 📱 Data Stored Per User

```
✓ Your email & password (localStorage)
✓ Your full name (profile)
✓ Your chat history (all conversations)
✓ Your carbon estimates (all API calls)
✓ Your dashboard stats (aggregated)
✓ Login session (auto-remember)
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't sign up | Make sure email format is valid (user@domain.com) |
| Can't log in | Check email and password exactly match signup |
| Data not saving | Check browser's localStorage isn't disabled |
| Backend not responding | Ensure `python run.py` is running on Terminal 1 |
| Frontend not loading | Ensure `npm run dev` is running on Terminal 2 |
| Port already in use | Change port or kill existing process |

## 📚 Full Documentation

- **Setup Guide**: Read `AUTHENTICATION_SETUP.md`
- **Implementation Details**: Read `IMPLEMENTATION_SUMMARY.md`
- **Formulas Used**: Read `FORMULAS_COMPLETE.md`
- **Tech Stack**: Read `TECHNOLOGIES_EXPLAINED.md`
- **Complete Guide**: Read `README.md`

## 💾 Browser Storage (DevTools)

To check your data:
1. Press **F12** to open DevTools
2. Go to **Application** tab
3. Click **LocalStorage**
4. Find `http://localhost:5173`
5. You'll see:
   - `currentUser`: Currently logged in user
   - `users`: All registered users
   - `userData_your@email.com`: Your chats and estimates

## 🎯 Next Steps

1. ✅ Test signup/login flow
2. ✅ Create several chats with different prompts
3. ✅ Try compare mode with multiple models
4. ✅ Check dashboard for your stats
5. ✅ Test logout/login to verify data persistence
6. ✅ Create another user account to test multi-user
7. ✅ Read full documentation for advanced features

## 🚨 Important Notes

- **Browser LocalStorage Only**: Data is on your computer only
- **No Cloud Sync**: Data doesn't sync across devices
- **Clear Storage**: If you clear browser data, everything is deleted
- **Private Data**: Anyone with access to this computer can see it
- **Development Mode**: Not suitable for production use yet

## 🎉 You're Ready!

Your authentication system is fully operational. Start the backend and frontend, sign up, and enjoy using the Green Model Advisor!

**Questions?** Check the documentation files or browser console (F12) for errors.

**Happy Coding!** 🚀
