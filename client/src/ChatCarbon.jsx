import React, { useState, useEffect } from "react";
import "./ChatCarbon.css";
import Dashboard from "./Dashboard";

const ChatCarbon = () => {
  // API Configuration
  const API_BASE_URL = "http://localhost:8000";
  
  // State Management
  const [input, setInput] = useState("");
  const [selectedModels, setSelectedModels] = useState(["gemini-2.0-flash"]);
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [theme, setTheme] = useState("light");
  const [loading, setLoading] = useState(false);
  const [availableModels, setAvailableModels] = useState([]);
  const [showComparison, setShowComparison] = useState(false);
  const [comparisonResults, setComparisonResults] = useState(null);
  const [allEstimates, setAllEstimates] = useState([]);
  // Working models with free APIs
  const MODEL_WHITELIST = [
    "gemini-2.0-flash",           // Google Gemini
    "mistral-7b-openrouter",      // OpenRouter (Free)
    "nvidia-qwen-coder"           // NVIDIA NIM Qwen 2.5 Coder (Free)
  ];
  const [selectedMode, setSelectedMode] = useState("single"); // 'single', 'compare', 'dashboard'
    // Detect prompt type (image or text)
    const detectPromptType = (prompt) => {
      // Simple heuristic: look for keywords
      const imageKeywords = ["image", "picture", "photo", "draw", "generate an image", "show me", "visualize", "create a picture", "generate a photo", "generate a drawing"];
      const lowerPrompt = prompt.toLowerCase();
      return imageKeywords.some(k => lowerPrompt.includes(k)) ? "image" : "text";
    };
  const [apiStatus, setApiStatus] = useState({});
  const [error, setError] = useState("");
  
  // Fetch available models on mount
  useEffect(() => {
    fetchAvailableModels();
  }, []);
  
  // Fetch available models
  const fetchAvailableModels = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/models`);
      const data = await response.json();

      // Extract model names from the configuration
      let modelNames = Object.keys(data.models);
      // Only use whitelisted models that are available
      const filteredModels = modelNames.filter(m => MODEL_WHITELIST.includes(m) && data.models[m].api_available);
      setAvailableModels(filteredModels);
      setApiStatus(data.api_status);
      setSelectedModels(filteredModels.slice(0, 3));
    } catch (err) {
      console.error("Failed to fetch models:", err);
      setError("Failed to load available models");
      setAvailableModels([]);
    }
  };
  
  // Single model estimation
  const handleSingleEstimate = async () => {
    if (!input.trim()) return;
    
    setLoading(true);
    setError("");
    
    try {
      // Detect prompt type
      const promptType = detectPromptType(input);

      if (promptType === "image") {
        setError("Image generation will be available soon.");
        setLoading(false);
        return;
      }

      // Use only whitelisted models
      const filteredModels = availableModels;
      if (filteredModels.length === 0) {
        setError("No supported text generation models are available.");
        setLoading(false);
        return;
      }

      console.log("Available models:", filteredModels);
      
      // Compare models for carbon and accuracy
      let bestModel = filteredModels[0];
      let bestResult = null;
      let bestScore = Number.POSITIVE_INFINITY;
      let comparisonResults = [];

      for (const modelName of filteredModels) {
        try {
          const payload = {
            prompt: input,
            model_name: modelName,
            evaluate_accuracy: true,
            auto_select_model: true,
            simulate: false
          };
          console.log(`Requesting estimate for ${modelName}:`, payload);
          
          const response = await fetch(`${API_BASE_URL}/estimate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          
          console.log(`Response from ${modelName}:`, response.status);
          
          if (!response.ok) {
            const errorText = await response.text();
            console.error(`Error from ${modelName}:`, errorText);
            continue;
          }
          
          const result = await response.json();
          console.log(`Result from ${modelName}:`, result);
          
          const carbon = result.carbon_emitted_kgco2 || result.carbon_emitted_grams || 0;
          let accuracy = result.accuracy_scores?.overall_accuracy || result.overall_accuracy || 0;
          // Normalize accuracy from 0-100 to 0-1 for scoring
          const accuracyNormalized = accuracy > 1 ? accuracy / 100 : accuracy;
          // Score: lower carbon is better, higher accuracy is better (so subtract accuracy)
          // Formula: carbon + (1 - accuracy_normalized) = lower score is better
          const score = carbon + (1 - accuracyNormalized);  // Lower score = better (lower carbon + higher accuracy)
          // Store original accuracy (0-100) for display
          const accuracyDisplay = accuracy > 1 ? accuracy : accuracy * 100;
          comparisonResults.push({ model: modelName, carbon, accuracy: accuracyDisplay });
          
          console.log(`${modelName} - Carbon: ${carbon}, Accuracy: ${accuracy}, Score: ${score}`);
          
          if (score < bestScore) {
            bestScore = score;
            bestModel = modelName;
            bestResult = result;
          }
        } catch (modelError) {
          console.error(`Error calling ${modelName}:`, modelError);
          continue;
        }
      }

      if (!bestResult) {
        setError("No successful results from any model. Please check your API keys and ensure models are available.");
        setLoading(false);
        return;
      }

      console.log("Best model selected:", bestModel, "Result:", bestResult);
      
      // Show comparison results
      setComparisonResults(comparisonResults);
      setShowComparison(true);

      // Create or update active chat
      let chatId = activeChatId;
      if (!chatId) {
        const newChat = {
          id: Date.now(),
          title: input.slice(0, 30) + "...",
          messages: []
        };
        setChats([...chats, newChat]);
        chatId = newChat.id;
        setActiveChatId(chatId);
      }

      // Add message to chat
      const message = {
        id: Date.now(),
        type: "estimate",
        prompt: input,
        model: bestModel,
        carbon: bestResult.carbon_emitted_kgco2 || bestResult.carbon_emitted_grams || 0,
        energy: bestResult.energy_consumed_kwh || 0,
        tokens: bestResult.total_tokens || 0,
        accuracy: bestResult.accuracy_scores || bestResult.overall_accuracy || {},
        response_text: bestResult.response_text || "",
        timestamp: new Date().toLocaleTimeString()
      };

      setChats(prev => prev.map(c =>
        c.id === chatId
          ? { ...c, messages: [...c.messages, message] }
          : c
      ));

      // Add to all estimates for dashboard
      console.log("Adding to allEstimates:", bestResult);
      setAllEstimates(prev => [...prev, bestResult]);

      setInput("");

    } catch (err) {
      console.error("Error in handleSingleEstimate:", err);
      setError(err.message || "An unexpected error occurred");
    } finally {
      setLoading(false);
    }
  };
  
  // Compare multiple models
  const handleCompareModels = async () => {
    if (!input.trim() || selectedModels.length < 2) {
      setError("Select at least 2 models to compare");
      return;
    }
    
    setLoading(true);
    setError("");
    
    try {
      const payload = {
        prompt: input,
        models: selectedModels,
        evaluate_accuracy: true
      };
      console.log("Sending comparison request:", payload);
      
      const response = await fetch(`${API_BASE_URL}/compare-models`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      
      console.log("Comparison response status:", response.status);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("Backend error:", errorData);
        throw new Error(errorData.detail || `Comparison failed: ${response.status}`);
      }
      
      const result = await response.json();
      console.log("Comparison result:", result);
      setComparisonResults(result);
      setShowComparison(true);
      
      // Add to chat
      let chatId = activeChatId;
      if (!chatId) {
        const newChat = {
          id: Date.now(),
          title: input.slice(0, 30) + "...",
          messages: []
        };
        setChats([...chats, newChat]);
        chatId = newChat.id;
        setActiveChatId(chatId);
      }
      
      const message = {
        id: Date.now(),
        type: "comparison",
        prompt: input,
        models: selectedModels,
        results: result,
        timestamp: new Date().toLocaleTimeString()
      };
      
      setChats(prev => prev.map(c => 
        c.id === chatId 
          ? { ...c, messages: [...c.messages, message] }
          : c
      ));
      
      setInput("");
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  const activeChat = chats.find(c => c.id === activeChatId);
  
  const handleNewChat = () => {
    const newChat = {
      id: Date.now(),
      title: "New Chat",
      messages: []
    };
    setChats([...chats, newChat]);
    setActiveChatId(newChat.id);
    setShowComparison(false);
  };
  
  const deleteChat = (id) => {
    setChats(chats.filter(c => c.id !== id));
    if (id === activeChatId) setActiveChatId(null);
  };
  
  const renameChat = (id) => {
    const name = prompt("Enter new chat title:");
    if (!name?.trim()) return;
    setChats(chats.map(c =>
      c.id === id ? { ...c, title: name } : c
    ));
  };
  
  // Format carbon for display
  const formatCarbon = (kg) => {
    if (!kg && kg !== 0) return "N/A";
    const value = typeof kg === 'string' ? parseFloat(kg) : kg;
    if (isNaN(value)) return "N/A";
    if (value < 0.000001) return "≈ 0 g";
    if (value < 0.001) return (value * 1000000).toFixed(2) + " μg";
    if (value < 1) return (value * 1000).toFixed(4) + " g";
    return value.toFixed(6) + " kg";
  };
  
  const formatEnergy = (kwh) => {
    if (!kwh && kwh !== 0) return "N/A";
    const value = typeof kwh === 'string' ? parseFloat(kwh) : kwh;
    if (isNaN(value)) return "N/A";
    if (value < 0.000001) return "≈ 0 J";
    if (value < 0.001) return (value * 3600000).toFixed(2) + " J";
    return (value * 3600).toFixed(2) + " kJ";
  };
  
  const getCarbonColor = (kg) => {
    if (kg < 0.000001) return "#4CAF50"; // Green
    if (kg < 0.00001) return "#8BC34A"; // Light Green
    if (kg < 0.0001) return "#CDDC39"; // Lime
    if (kg < 0.001) return "#FBC02D"; // Yellow
    return "#FF6F00"; // Orange
  };
  
  // Copy to clipboard function
  const copyToClipboard = (text, msgId) => {
    navigator.clipboard.writeText(text).then(() => {
      // Show visual feedback
      const btn = document.querySelector(`[data-copy-btn="${msgId}"]`);
      if (btn) {
        btn.textContent = "✓ Copied!";
        btn.classList.add("copied");
        setTimeout(() => {
          btn.textContent = "📋 Copy";
          btn.classList.remove("copied");
        }, 2000);
      }
    }).catch(err => {
      console.error("Failed to copy:", err);
    });
  };
  
  return (
    <div className={`container ${theme}`}>
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo-section">
          <h1>🌍 Green Model Advisor</h1>
          <p>Carbon-Aware AI</p>
        </div>
        
        <button className="new-chat-btn" onClick={handleNewChat}>
          ➕ New Chat
        </button>
        
        {/* Model Status */}
        <div className="api-status">
          <h3>🤖 Model Status</h3>
          <div className="status-items">
            <div className="status-item active">
              🟢 gemini-2.0-flash
            </div>
            <div className="status-item active">
              🟢 mistral-7b-openrouter
            </div>
            <div className="status-item active">
              🟢 nvidia-qwen-coder
            </div>
          </div>
        </div>
        
        {/* Chat History */}
        <div className="chat-history">
          <h3>📋 Chats</h3>
          {chats.map(chat => (
            <div
              key={chat.id}
              className={`chat-item ${chat.id === activeChatId ? "active" : ""}`}
              onClick={() => setActiveChatId(chat.id)}
            >
              <span>{chat.title}</span>
              <div className="chat-actions">
                <button 
                  className="icon-btn" 
                  onClick={(e) => {
                    e.stopPropagation();
                    renameChat(chat.id);
                  }}
                >
                  ✏️
                </button>
                <button 
                  className="icon-btn" 
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteChat(chat.id);
                  }}
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
        
        {/* Theme Toggle */}
        <div className="theme-toggle">
          <button 
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          >
            {theme === "light" ? "🌙 Dark" : "☀️ Light"}
          </button>
        </div>
      </aside>
      
      {/* Main Content */}
      <main className="main-content">
        {/* Mode Selection */}
        <div className="mode-selector">
          <button 
            className={`mode-btn ${selectedMode === "single" ? "active" : ""}`}
            onClick={() => {
              setSelectedMode("single");
              setShowComparison(false);
            }}
          >
            📊 Single Model
          </button>
          <button 
            className={`mode-btn ${selectedMode === "compare" ? "active" : ""}`}
            onClick={() => setSelectedMode("compare")}
          >
            ⚖️ Compare Models
          </button>
          <button 
            className={`mode-btn ${selectedMode === "dashboard" ? "active" : ""}`}
            onClick={() => setSelectedMode("dashboard")}
          >
            📈 Dashboard
          </button>
        </div>
        
        {/* Dashboard - Only show in Dashboard Mode */}
        {selectedMode === "dashboard" && <Dashboard estimates={allEstimates} />}
        
        {/* Chat Messages - Hide in Dashboard Mode */}
        {selectedMode !== "dashboard" && activeChat && (
          <div className="chat-container">
            <div className="messages">
              {activeChat.messages.map(msg => (
                <div key={msg.id} className={`message message-${msg.type}`}>
                  <div className="message-header">
                    <strong>{msg.model || msg.models?.join(", ")}</strong>
                    <span className="timestamp">{msg.timestamp}</span>
                  </div>
                  
                  <div className="message-prompt">
                    <strong>Q:</strong> {msg.prompt}
                  </div>
                  
                  {msg.type === "estimate" && (
                    <div className="estimate-container">
                      <div className="metrics-container">
                        <div className="result-item">
                          <span>Carbon:</span>
                          <strong style={{ color: getCarbonColor(msg.carbon) }}>
                            {formatCarbon(msg.carbon)}
                          </strong>
                        </div>
                        <div className="result-item">
                          <span>Energy:</span>
                          <strong>{formatEnergy(msg.energy)}</strong>
                        </div>
                        <div className="result-item">
                          <span>Tokens:</span>
                          <strong>{msg.tokens}</strong>
                        </div>
                        {msg.accuracy && msg.accuracy.overall_accuracy && (
                          <div className="result-item">
                            <span>Accuracy:</span>
                            <strong>{msg.accuracy.overall_accuracy.toFixed(1)}%</strong>
                          </div>
                        )}
                      </div>
                      {msg.response_text && (
                        <div className="message-response">
                          <div className="message-response-header">
                            <strong style={{color: '#333'}}>📝 Response:</strong>
                            <button 
                              className="copy-btn"
                              data-copy-btn={msg.id}
                              onClick={() => copyToClipboard(msg.response_text, msg.id)}
                            >
                              📋 Copy
                            </button>
                          </div>
                          <p>{msg.response_text}</p>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {msg.type === "comparison" && (
                    <div className="comparison-results">
                      {msg.results?.results && Array.isArray(msg.results.results) ? (
                        msg.results.results.map((result, idx) => (
                          <div key={idx} className="comparison-item">
                            <h4>{result?.model_name || "Unknown"}</h4>
                            {result?.error ? (
                              <div style={{ color: "#d32f2f" }}>Error: {result.error}</div>
                            ) : (
                              <div className="result-grid">
                                <div>Carbon: {formatCarbon(result?.carbon_emitted_kgco2)}</div>
                                <div>Energy: {formatEnergy(result?.energy_consumed_kwh)}</div>
                                {result?.accuracy_scores && (
                                  <div>Accuracy: {(result.accuracy_scores?.overall_accuracy || 0).toFixed(1)}%</div>
                                )}
                              </div>
                            )}
                          </div>
                        ))
                      ) : (
                        <div>No comparison results available</div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Empty State - Show when no chat in Single/Compare mode */}
        {selectedMode !== "dashboard" && !activeChat && (
          <div className="empty-state">
            <h2>🚀 Start a New Chat</h2>
            <p>Create a new chat to compare models and track carbon emissions</p>
          </div>
        )}
        
        {/* Input Area - Hide in Dashboard Mode */}
        {selectedMode !== "dashboard" && (
        <div className="input-section">
          {error && <div className="error-message">{error}</div>}
          
          {/* Model Selection - Only show in Compare mode */}
          {selectedMode === "compare" && (
            <div className="model-selector">
              <label>Select Models to Compare:</label>
              <div className="model-list">
                {availableModels.length === 0 ? (
                  <div className="no-models-message" style={{color: "#d32f2f"}}>
                    No supported text generation models are available. Please check your API keys or backend configuration.
                  </div>
                ) : (
                  availableModels.map(model => (
                    <button
                      key={model}
                      className={`model-tag ${selectedModels.includes(model) ? "selected" : ""}`}
                      onClick={() => {
                        if (selectedModels.includes(model)) {
                          setSelectedModels(selectedModels.filter(m => m !== model));
                        } else {
                          setSelectedModels([...selectedModels, model]);
                        }
                      }}
                    >
                      {model}
                    </button>
                  ))
                )}
              </div>
            </div>
          )}
          
          {selectedMode === "single" && (
            <div style={{padding: "10px", textAlign: "center", color: "#666"}}>
              <p>✨ Best model will be automatically selected based on accuracy & carbon efficiency</p>
            </div>
          )}
          
          {/* Input Box */}
          <div className="input-box">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Enter your prompt here..."
              rows="3"
              disabled={loading}
            />
            <div className="input-actions">
              {selectedMode === "single" ? (
                <button
                  className="send-btn"
                  onClick={handleSingleEstimate}
                  disabled={loading || !input.trim()}
                >
                  {loading ? "⏳ Processing..." : "📤 Estimate"}
                </button>
              ) : (
                <button
                  className="send-btn"
                  onClick={handleCompareModels}
                  disabled={loading || !input.trim() || selectedModels.length < 2}
                >
                  {loading ? "⏳ Comparing..." : "⚖️ Compare"}
                </button>
              )}
            </div>
          </div>
          
          {/* Model Comparison Results (Single Mode) */}
          {selectedMode === "single" && showComparison && comparisonResults && comparisonResults.length > 0 && (
            <div className="model-comparison-box" style={{
              marginTop: "20px",
              padding: "15px",
              backgroundColor: theme === "light" ? "#f5f5f5" : "#2a2a2a",
              borderRadius: "8px",
              border: `2px solid ${theme === "light" ? "#e0e0e0" : "#444"}`
            }}>
              <h3 style={{marginTop: 0}}>📊 Model Comparison:</h3>
              <div style={{display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "10px"}}>
                {comparisonResults.map((result, idx) => (
                  <div key={idx} style={{
                    padding: "10px",
                    backgroundColor: theme === "light" ? "#fff" : "#333",
                    borderRadius: "6px",
                    border: `1px solid ${theme === "light" ? "#ddd" : "#555"}`,
                    textAlign: "center"
                  }}>
                    <div style={{fontWeight: "bold", marginBottom: "8px"}}>{result.model}</div>
                    <div style={{fontSize: "0.9em", color: theme === "light" ? "#666" : "#aaa"}}>
                      <div>Carbon: {formatCarbon(result.carbon)}</div>
                      <div>Accuracy: {typeof result.accuracy === 'number' ? result.accuracy.toFixed(1) : 'N/A'}%</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        )}
      </main>
    </div>
  );
};

export default ChatCarbon;
