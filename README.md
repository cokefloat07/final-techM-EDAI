# 🌱 Green Model Advisor

**Smart AI Model Selection & Carbon Emission Tracking Platform**

A full-stack application that automatically selects the best-performing AI models while monitoring their carbon footprint and energy consumption. Built with a modern tech stack combining FastAPI backend and React frontend.

---

## 📋 Overview

Green Model Advisor helps you:
- **Compare multiple LLM models** (Google Gemini, Mistral, NVIDIA Qwen) based on accuracy and performance
- **Track carbon emissions** and energy consumption in real-time using CodeCarbon
- **Auto-select optimal models** based on accuracy, carbon footprint, and context
- **Evaluate code quality** using custom metrics and validation
- **Visualize performance metrics** through an interactive dashboard
- **Manage conversation context** for improved model recommendations

---

## 🛠️ Technology Stack

### **Backend**
- **FastAPI 0.104.1** - Modern async Python web framework with auto-documentation
- **SQLAlchemy 2.0.23** - SQL toolkit and ORM for database operations
- **SQLite** - Lightweight database for estimates and conversations
- **Pydantic 2.5.0** - Data validation and serialization
- **Pytorch** - Used Pytorch for good orchestration

### **AI/ML Models**
- **Google Gemini 2.0 Flash** - Advanced text generation via `google-generativeai` 0.3.0
- **Mistral 7B** - Open-source model via OpenRouter API
- **NVIDIA Qwen 2.5 Coder** - Specialized code generation via NVIDIA NIM

### **Carbon & Performance Tracking**
- **CodeCarbon 2.2.1** - Real-time carbon emissions tracking for code execution
- **NumPy 1.24.3** - Numerical computing for performance calculations

### **Frontend**
- **React 19.2.0** - Component-based UI library
- **Vite (Rolldown) 7.2.5** - Lightning-fast build tool and dev server
- **Vanilla CSS** - Custom styling for UI components

### **Development & DevOps**
- **Python 3.8+** with virtual environment
- **Node.js + npm** - JavaScript package management
- **Uvicorn 0.24.0** - ASGI server for FastAPI

### **Utilities**
- **python-dotenv 1.0.0** - Environment variable management
- **requests 2.31.0** - HTTP client for API calls
- **aiofiles 23.2.1** - Async file operations
- **python-multipart 0.0.6** - Multipart form data support
- **uuid 1.30** - Unique identifier generation

---

## 🤖 AI Technologies Used

### **LLM Integration**
The application integrates with **three production-ready LLM providers**:

1. **Google Gemini 2.0 Flash** (`google-generativeai`)
   - Advanced reasoning and code generation
   - Excellent accuracy on programming tasks
   - Default model for code generation tasks

2. **Mistral 7B via OpenRouter** (API-based)
   - Open-source, fast inference
   - Good balance of speed and quality
   - Cost-effective alternative

3. **NVIDIA Qwen 2.5 Coder** (NVIDIA NIM)
   - Specialized for code generation
   - Optimized performance on coding tasks
   - Enterprise-grade reliability

### **Smart Model Selection Algorithm**
Custom deterministic selector that evaluates models using:
- **Carbon emissions** (kg CO₂)
- **Code quality metrics** (accuracy 0-100)
- **Prompt analysis** (domain, complexity, task type)
- **Historical performance** (per-model success rates)

Scoring formula: `score = carbon + (1 - accuracy_normalized)`
- Lower score = better choice
- Balances environmental impact with output quality
- Implemented using pure Python logic (no ML algorithms)

### **Code Quality Evaluation**
Custom evaluator analyzes generated code for:
- Completeness (does it solve the problem?)
- Code structure (organization and readability)
- Functionality (does it work correctly?)
- Efficiency (performance optimization)
- Documentation (comments and clarity)

Returns accuracy score: **0-100%**

### **How Model Selection Works (No ML Required)**
The project uses a **pure deterministic algorithm** (not machine learning):

1. **Prompt Analysis** - Analyzes task type, domain, complexity, technical level
2. **Score Calculation** - Evaluates each model:
   - Carbon emissions from CodeCarbon
   - Code quality accuracy (0-100)
   - Historical success rate
   - Prompt compatibility
3. **Best Model Selection** - Returns model with lowest combined score

Other components:
- Carbon estimation: **Physics-based** via CodeCarbon (real CPU/GPU measurements)
- Accuracy evaluation: **Rule-based metrics** (code analysis + execution)
- Context management: **Simple history tracking** of conversations

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+ with pip
- Node.js 16+ with npm
- API Keys:
  - `GOOGLE_API_KEY` - Google Gemini API
  - `OPENROUTER_API_KEY` - OpenRouter (Mistral)
  - `NVIDIA_NIM_API_KEY` - NVIDIA NIM
  - `NVIDIA_NIM_URL` - NVIDIA NIM endpoint

### **Installation**

1. **Clone and enter directory**
```bash
cd green-model-advisor
```

2. **Backend Setup**
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd client
npm install
```

4. **Environment Variables**
Create `.env` file in root directory:
```
GOOGLE_API_KEY=your_google_key
OPENROUTER_API_KEY=your_openrouter_key
NVIDIA_NIM_API_KEY=your_nvidia_key
NVIDIA_NIM_URL=your_nvidia_endpoint
DATABASE_URL=sqlite:///./carbon_estimates.db
```

### **Running the Application**

**Terminal 1 - Backend (Port 8000)**
```bash
python run.py
```

**Terminal 2 - Frontend (Port 5173)**
```bash
cd client
npm run dev
```

Visit `http://localhost:5173` in your browser.

---

## 📊 Features

### **Single Model Mode**
- Send prompt to a single selected model
- Get real-time carbon emissions and energy consumption
- View code quality evaluation
- Copy generated responses

### **Compare Mode**
- Run same prompt across all 3 models simultaneously
- Compare carbon footprint vs accuracy
- Identify most efficient model for your task
- View side-by-side metrics

### **Dashboard**
- Aggregate statistics across all requests
- Model performance breakdown
- Carbon usage trends
- Average accuracy per model
- Total energy consumption tracking

### **Model Status Sidebar**
- Real-time availability of all models
- Historical success rates
- Quick model selection

---

## 📈 API Endpoints

### **Core Endpoints**
- `POST /estimate` - Single model estimation with carbon & accuracy
- `POST /compare-models` - Compare multiple models
- `POST /compare` - Alternate comparison endpoint
- `GET /models` - List available models

### **Analysis Endpoints**
- `GET /stats` - Overall statistics
- `GET /stats/models` - Per-model performance
- `POST /analyze-accuracy` - Analyze code quality

### **Database Endpoints**
- `GET /estimates` - Retrieve all estimates
- `DELETE /reset` - Clear database

Full API documentation available at `http://localhost:8000/docs`

---

## 📁 Project Structure

```
green-model-advisor/
├── app/
│   ├── main.py                      # FastAPI app & route definitions
│   ├── estimator.py                 # Carbon estimation logic
│   ├── model_runner.py              # LLM API integration
│   ├── code_quality_evaluator.py   # Code quality scoring
│   ├── model_selector.py            # Smart model selection algorithm
│   ├── context_manager.py           # Conversation context management
│   ├── models.py                    # Pydantic data models
│   ├── database.py                  # SQLAlchemy ORM models
│   ├── config.py                    # Configuration settings
│   └── model_api_client.py          # Multi-provider API client
├── client/
│   ├── src/
│   │   ├── ChatCarbon.jsx           # Main React component
│   │   ├── Dashboard.jsx            # Metrics dashboard
│   │   └── ChatCarbon.css           # Styling
│   └── package.json                 # Node dependencies
├── requirements.txt                 # Python dependencies
├── run.py                          # Entry point
└── README.md                       # This file
```

---

## 🔄 How It Works

### **Single Estimate Flow**
1. User enters prompt and selects model
2. Backend calls selected LLM API
3. CodeCarbon measures carbon emissions in real-time
4. Response is analyzed for code quality (0-100 score)
5. Results stored in SQLite database
6. Frontend displays metrics and response

### **Auto-Select Flow**
1. User sends prompt (model = auto)
2. Backend tests all 3 models in parallel
3. Calculates score: `carbon + (1 - accuracy/100)`
4. Selects model with lowest score
5. Returns best result with full metrics

### **Carbon Tracking**
- **CodeCarbon** measures actual CPU/GPU power consumption
- Converts to kg CO₂ using regional electricity grid data
- Fallback to token-based estimation if CodeCarbon unreliable
- Tracks both instantaneous and cumulative emissions

---

## 📊 Database Schema

### **CarbonEstimate Table**
```sql
- id (Primary Key)
- prompt (Input text)
- model_name (Selected model)
- provider (API provider)
- tokens_input, tokens_output, total_tokens
- energy_consumed_kwh
- carbon_emitted_kgco2
- overall_accuracy (0-100)
- response_text (Generated output)
- estimation_method (codecarbon/token_based)
- created_at (Timestamp)
```

### **Conversation Table**
- Stores conversation history
- User preferences and context
- Model selection history

---

## 🔐 Security Considerations

- ✅ **CORS Enabled** - Frontend-backend communication secured
- ✅ **Environment Variables** - API keys never hardcoded
- ✅ **Input Validation** - Pydantic models validate all inputs
- ✅ **Database Isolation** - SQLite with proper ORM usage

---

## 📈 Performance Metrics

Typical results for code generation prompts:

| Model | Carbon (μg) | Energy (J) | Accuracy | Score |
|-------|------------|-----------|----------|-------|
| Gemini 2.0 Flash | 66-67 | 0.2-0.22 | 75-77% | 0.23 |
| Mistral 7B | 60-65 | 0.18-0.20 | 75-77% | 0.23 |
| NVIDIA Qwen | 66-67 | 0.20-0.22 | 70-73% | 0.27 |

*Note: Actual metrics vary based on prompt length and complexity*

---

## 🐛 Troubleshooting

### **Backend won't start**
```bash
# Clear old database
rm *.db

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### **Models not responding**
- Check API keys in `.env`
- Verify internet connection
- Check individual API service status

### **High carbon emissions**
- Reduce `max_tokens` parameter
- Use shorter prompts
- Consider switching to Mistral (more efficient)

---

## 📝 License & Attribution

This project demonstrates:
- ✅ Real carbon tracking for AI inference
- ✅ Multi-model comparison framework
- ✅ Full-stack modern web development
- ✅ AI model orchestration

Built with focus on sustainability and transparency.

---

## 🤝 Contributing

To improve Green Model Advisor:
1. Test new models
2. Optimize carbon calculations
3. Enhance code quality metrics
4. Improve UI/UX

---

## 📞 Support

For issues or questions:
- Check API key configuration
- Review browser console for errors
- Check backend logs in terminal
- Verify all models are responding

---

**Made with 🌍 for a greener AI future**
