import { API_BASE_URL } from './api';
import React, { useState, useEffect } from "react";
import "./ChatCarbon.css";
import Dashboard from "./Dashboard";
import UserProfile from "./UserProfile";

// Generate UUID for unique identifiers
const generateUUID = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

// Generate smart chat name from prompt
const generateChatNameFromPrompt = (prompt) => {
  if (!prompt) return "New Chat";
  
  // Remove leading/trailing whitespace and special characters
  const cleaned = prompt.trim().replace(/^[^\w\s]+/, '').slice(0, 60);
  
  // Extract first meaningful words
  const words = cleaned.split(/\s+/).slice(0, 5);
  const name = words.join(' ');
  
  return name || "New Chat";
};

// Calculate comprehensive dashboard statistics from chat messages
const calculateDashboardStats = (chats) => {
  const stats = {
    totalChats: chats.length,
    totalEstimates: 0,
    totalCarbonKgCO2: 0,
    totalEnergyKwh: 0,
    averageAccuracy: 0,
    modelsUsed: new Set(),
    estimatesByType: { estimate: 0, comparison: 0 },
    accuracyScores: []
  };
  
  chats.forEach(chat => {
    if (Array.isArray(chat.messages)) {
      chat.messages.forEach(msg => {
        if (msg.carbon !== undefined || msg.energy !== undefined) {
          stats.totalEstimates++;
          
          if (msg.carbon) stats.totalCarbonKgCO2 += msg.carbon;
          if (msg.energy) stats.totalEnergyKwh += msg.energy;
          
          if (msg.accuracy) {
            if (Array.isArray(msg.accuracy)) {
              stats.accuracyScores.push(...msg.accuracy);
            } else {
              stats.accuracyScores.push(msg.accuracy);
            }
          }
          
          if (msg.model) stats.modelsUsed.add(msg.model);
          if (msg.type) {
            stats.estimatesByType[msg.type] = (stats.estimatesByType[msg.type] || 0) + 1;
          }
        }
      });
    }
  });
  
  // Calculate average accuracy
  if (stats.accuracyScores.length > 0) {
    const avgAccuracy = stats.accuracyScores.reduce((a, b) => a + b, 0) / stats.accuracyScores.length;
    stats.averageAccuracy = parseFloat(avgAccuracy.toFixed(2));
  }
  
  stats.modelsUsed = Array.from(stats.modelsUsed);
  
  return stats;
};

// Normalize messages to include required fields for backend
const normalizeMessage = (msg) => {
  return {
    ...msg,
    role: msg.role || "assistant",
    content: msg.content || msg.response || msg.response_text || ""
  };
};

// Normalize all messages in a chat
const normalizeChat = (chat) => {
  return {
    ...chat,
    messages: (chat.messages || []).map(normalizeMessage)
  };
};

// Extract lightweight estimate data for Dashboard display (optimized for performance)
const extractEstimatesForDisplay = (chat) => {
  const messages = chat.messages || [];
  return messages
    .filter(msg => msg.type === "estimate" || msg.type === "comparison")
    .map(msg => {
      // Normalize accuracy to number
      let accuracy = msg.accuracy;
      if (accuracy && typeof accuracy === 'object' && accuracy.overall_accuracy !== undefined) {
        accuracy = parseFloat(accuracy.overall_accuracy) || 0;
      } else if (accuracy !== undefined) {
        accuracy = parseFloat(accuracy) || 0;
      } else {
        accuracy = 0;
      }
      return {
        id: msg.id,
        model: msg.model || "",
        carbon: parseFloat(msg.carbon) || 0,
        energy: parseFloat(msg.energy) || 0,
        accuracy,
        tokens: parseInt(msg.tokens) || 0,
        timestamp: msg.timestamp,
        type: msg.type || "estimate"
      };
    });
};

// Calculate detailed chat statistics - optimized with efficient aggregation
const calculateChatStatistics = (chat) => {
  const messages = chat.messages || [];
  const estimates = extractEstimatesForDisplay(chat);
  
  const stats = {
    total_requests: estimates.length,
    user_prompts: messages.filter(m => m.prompt).map(m => m.prompt),
    models_used: [...new Set(estimates.map(e => e.model).filter(Boolean))],
    total_carbon_emitted_kgco2: parseFloat(estimates.reduce((sum, e) => sum + (e.carbon || 0), 0).toFixed(8)),
    total_energy_consumed_kwh: parseFloat(estimates.reduce((sum, e) => sum + (e.energy || 0), 0).toFixed(8)),
    average_accuracy: estimates.length > 0 
      ? parseFloat((estimates.reduce((sum, e) => sum + (e.accuracy || 0), 0) / estimates.length).toFixed(2))
      : 0,
    total_tokens: estimates.reduce((sum, e) => sum + (e.tokens || 0), 0),
    is_comparison: messages.some(m => m.type === "comparison") ? 1 : 0,
    comparison_models: [],
    comparison_results: {},
    code_generated: null
  };
  
  // Collect comparison data if present
  const comparisonMsg = messages.find(m => m.type === "comparison");
  if (comparisonMsg) {
    if (comparisonMsg.models_compared) {
      stats.comparison_models = comparisonMsg.models_compared;
    }
    if (comparisonMsg.results) {
      stats.comparison_results = comparisonMsg.results;
    }
  }
  
  return stats;
};

const ChatCarbon = ({ user, onLogout }) => {
  // State Management
  const [input, setInput] = useState("");
  const [selectedModels, setSelectedModels] = useState(["gemini-2.0-flash"]);
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [theme, setTheme] = useState("light");
  const [loading, setLoading] = useState(false);
  const [dashboardStats, setDashboardStats] = useState(null);
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
  
  // Load user data on mount
  useEffect(() => {
    loadUserData();
    fetchAvailableModels();
  }, [user]);

  // Save user data whenever chats or estimates change
  useEffect(() => {
    if (user) {
      saveUserData();
    }
  }, [chats, allEstimates]);

  // Recalculate dashboard stats whenever chats change
  useEffect(() => {
    if (chats && chats.length > 0) {
      const stats = calculateDashboardStats(chats);
      setDashboardStats(stats);
      console.log("Dashboard stats updated:", stats);
    }
  }, [chats]);

  const loadUserData = async () => {
    if (user && user.id) {
      try {
        console.log(`Loading chats for user ${user.id}`);
        const response = await fetch(`${API_BASE_URL}/api/chats/${user.id}`);
        
        if (response.status === 404) {
          console.log("No chats found for user (404)");
          setChats([]);
          setAllEstimates([]);
          return;
        }
        
        if (!response.ok) {
          console.error(`Failed to load chats: ${response.status} ${response.statusText}`);
          const errorText = await response.text();
          console.error("Error details:", errorText);
          throw new Error(`HTTP ${response.status}`);
        }
        
        const dbChats = await response.json();
        console.log("Raw API response:", dbChats);
        console.log(`Loaded ${dbChats.length} chats from database`);
        
        // Transform database format to frontend format
        const formattedChats = dbChats.map(chat => {
          let messages = [];
          try {
            // Handle different message formats from backend
            if (Array.isArray(chat.messages)) {
              messages = chat.messages;
            } else if (typeof chat.messages === 'string') {
              messages = JSON.parse(chat.messages);
            } else if (chat.messages === null || chat.messages === undefined) {
              messages = [];
            }
          } catch (msgErr) {
            console.error(`Error parsing messages for chat ${chat.id}:`, msgErr);
            messages = [];
          }
          
          // Enrich messages with stats from database
          const enrichedMessages = messages.map(msg => ({
            ...normalizeMessage(msg),
            // Ensure numeric types for stats
            carbon: parseFloat(msg.carbon) || 0,
            energy: parseFloat(msg.energy) || 0,
            accuracy: msg.accuracy ? parseFloat(msg.accuracy) : 0,
            tokens: msg.tokens ? parseInt(msg.tokens) : 0
          }));
          
          return {
            id: chat.id,
            title: chat.title || "Chat",
            messages: enrichedMessages,
            // Include chat-level stats
            total_requests: chat.total_requests || 0,
            total_carbon_emitted_kgco2: parseFloat(chat.total_carbon_emitted_kgco2) || 0,
            total_energy_consumed_kwh: parseFloat(chat.total_energy_consumed_kwh) || 0,
            average_accuracy: parseFloat(chat.average_accuracy) || 0,
            total_tokens: parseInt(chat.total_tokens) || 0,
            is_comparison: chat.is_comparison || 0,
            models_used: chat.models_used || [],
            comparison_models: chat.comparison_models || [],
            user_prompts: chat.user_prompts || []
          };
        });
        
        console.log("Formatted chats:", formattedChats);
        setChats(formattedChats);
        
        // Calculate comprehensive dashboard statistics
        const stats = calculateDashboardStats(formattedChats);
        setDashboardStats(stats);
        console.log("Dashboard stats calculated:", stats);
        
        // Also load dashboard estimates - now includes properly typed stats
        if (formattedChats.length > 0) {
          const allEstimates = [];
          formattedChats.forEach(chat => {
            if (Array.isArray(chat.messages)) {
              chat.messages.forEach(msg => {
                if (msg.carbon !== undefined || msg.energy !== undefined || msg.accuracy !== undefined) {
                  allEstimates.push(msg);
                }
              });
            }
          });
          setAllEstimates(allEstimates);
          console.log(`Loaded ${allEstimates.length} estimates for dashboard`);
        }
      } catch (err) {
        console.error("Failed to load chats from database:", err);
        // Fall back to localStorage
        console.log("Attempting fallback to localStorage");
        const userData = JSON.parse(localStorage.getItem(`userData_${user.email}`) || '{"chats": [], "estimates": []}');
        const normalizedChats = (userData.chats || []).map(normalizeChat);
        setChats(normalizedChats);
        setAllEstimates(userData.estimates || []);
        
        // Calculate stats from fallback data
        if (normalizedChats && normalizedChats.length > 0) {
          const stats = calculateDashboardStats(normalizedChats);
          setDashboardStats(stats);
        }
      }
    } else {
      console.log("No user or user.id available");
    }
  };

  const saveUserData = async () => {
    if (!user || !user.id) {
      console.log("Cannot save: No user ID");
      return;
    }
    
    if (chats.length === 0) {
      console.log("No chats to save");
      return;
    }
    
    try {
      console.log(`Saving ${chats.length} chats for user ${user.id}`);
      
      for (const chat of chats) {
        if (!chat.id || !chat.title) continue;
        
        try {
          // Calculate statistics from the chat messages
          const statistics = calculateChatStatistics(chat);
          
          const chatData = {
            title: chat.title,
            messages: (chat.messages || []).map(msg => {
              // Normalize accuracy to a number (handle object or direct value)
              let accuracy = msg.accuracy;
              if (accuracy && typeof accuracy === 'object' && accuracy.overall_accuracy !== undefined) {
                accuracy = parseFloat(accuracy.overall_accuracy) || 0;
              } else if (accuracy !== undefined) {
                accuracy = parseFloat(accuracy) || 0;
              }
              
              return {
                id: msg.id || generateUUID(),
                type: msg.type || "message",
                role: msg.role || "assistant",
                content: msg.content || msg.response || msg.response_text || "",
                prompt: msg.prompt || "",
                response: msg.response || "",
                model: msg.model || "",
                timestamp: msg.timestamp || new Date().toISOString(),
                ...(msg.carbon !== undefined && { carbon: parseFloat(msg.carbon) || 0 }),
                ...(msg.energy !== undefined && { energy: parseFloat(msg.energy) || 0 }),
                ...(msg.tokens !== undefined && { tokens: parseInt(msg.tokens) || 0 }),
                ...(accuracy !== undefined && accuracy !== null && { accuracy }),
                ...(msg.results && { results: msg.results })
              };
            }),
            // Include calculated statistics (pre-normalized)
            total_requests: statistics.total_requests,
            user_prompts: statistics.user_prompts,
            models_used: statistics.models_used,
            total_carbon_emitted_kgco2: statistics.total_carbon_emitted_kgco2,
            total_energy_consumed_kwh: statistics.total_energy_consumed_kwh,
            average_accuracy: statistics.average_accuracy,
            total_tokens: statistics.total_tokens,
            is_comparison: statistics.is_comparison,
            comparison_models: statistics.comparison_models,
            comparison_results: statistics.comparison_results,
            code_generated: statistics.code_generated || null,
            execution_time_ms: statistics.execution_time_ms || null
          };
          
          // Try to update first (works if chat exists)
          console.log(`Attempting to save chat: ${chat.id}`);
          const updateResponse = await fetch(`${API_BASE_URL}/api/chats/${user.id}/${chat.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(chatData)
          });
          
          if (updateResponse.status === 404) {
            // Chat doesn't exist, create it
            console.log(`Chat ${chat.id} not found, creating new...`);
            const createResponse = await fetch(`${API_BASE_URL}/api/chats?user_id=${user.id}`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(chatData)
            });
            
            if (!createResponse.ok) {
              const errorText = await createResponse.text();
              console.error(`Failed to create chat ${chat.id}:`, createResponse.status, errorText);
            } else {
              console.log(`Successfully created chat ${chat.id}`);
            }
          } else if (updateResponse.ok) {
            console.log(`Successfully updated chat ${chat.id}`);
          } else {
            const errorText = await updateResponse.text();
            console.error(`Failed to update chat ${chat.id}:`, updateResponse.status, errorText);
          }
        } catch (chatErr) {
          console.error(`Error processing chat ${chat.id}:`, chatErr);
        }
      }
      
      console.log("Chat save completed");
    } catch (err) {
      console.error("Failed to save chats to database:", err);
      // Fall back to localStorage
      const userData = {
        chats,
        estimates: allEstimates,
        lastUpdated: new Date().toISOString()
      };
      localStorage.setItem(`userData_${user.email}`, JSON.stringify(userData));
    }
  };
  
  // Parse API error messages for user-friendly display
  const parseApiError = (errorText) => {
    try {
      const errorObj = JSON.parse(errorText);
      
      // Handle rate limit (429) errors
      if (errorObj.detail && errorObj.detail.includes("429")) {
        return {
          type: "rate-limit",
          message: "⏱️ Rate limit reached - Models are temporarily unavailable. Please try again in a few minutes.",
          detail: "Some providers are currently rate-limited. This is temporary."
        };
      }
      
      // Handle provider-specific rate limiting
      if (errorObj.detail && errorObj.detail.includes("rate-limited")) {
        return {
          type: "rate-limit",
          message: "⏱️ Provider rate limit exceeded. Please try a different model or wait a few minutes.",
          detail: "The API provider is temporarily rate-limiting requests."
        };
      }
      
      // Handle API key errors
      if (errorObj.detail && (errorObj.detail.includes("401") || errorObj.detail.includes("Unauthorized"))) {
        return {
          type: "auth-error",
          message: "🔑 Authentication failed - Check your API keys configuration.",
          detail: "Unable to authenticate with the API provider."
        };
      }
      
      // Handle estimation failures
      if (errorObj.detail && errorObj.detail.includes("Estimation failed")) {
        return {
          type: "estimation-error",
          message: `⚠️ Estimation failed: ${errorObj.detail}`,
          detail: "The backend estimation service encountered an error."
        };
      }
      
      // Generic detail message
      if (errorObj.detail) {
        return {
          type: "api-error",
          message: `API Error: ${errorObj.detail}`,
          detail: errorObj.detail
        };
      }
      
      return null;
    } catch (e) {
      return null;
    }
  };
  
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
            
            // Parse and handle specific error types
            const parsedError = parseApiError(errorText);
            if (parsedError && parsedError.type === "rate-limit") {
              console.warn(`Rate limit on ${modelName}: ${parsedError.detail}`);
              // Store error for later display but continue trying other models
              continue;
            }
            
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
        const errorMessage = "❌ All models failed to generate estimates.\n\n" +
          "Common reasons:\n" +
          "• Rate limits: Wait a few minutes and try again\n" +
          "• API key issues: Check your backend configuration\n" +
          "• Provider downtime: Try again in a few minutes\n\n" +
          "You can try a specific model or wait before retrying.";
        setError(errorMessage);
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
        const chatName = generateChatNameFromPrompt(input);
        const newChat = {
          id: generateUUID(),
          title: chatName,
          messages: []
        };
        setChats([...chats, newChat]);
        chatId = newChat.id;
        setActiveChatId(chatId);
      }

      // Add message to chat with all estimate data
      // Normalize accuracy to a single number value
      let accuracy = bestResult.overall_accuracy || bestResult.accuracy_scores;
      if (accuracy && typeof accuracy === 'object' && accuracy.overall_accuracy !== undefined) {
        accuracy = parseFloat(accuracy.overall_accuracy) || 0;
      } else if (accuracy) {
        accuracy = parseFloat(accuracy) || 0;
      } else {
        accuracy = 0;
      }
      
      const message = {
        id: generateUUID(),
        type: "estimate",
        role: "assistant",
        content: bestResult.response_text || "",
        prompt: input,
        response: bestResult.response_text || "",
        model: bestModel,
        carbon: parseFloat(bestResult.carbon_emitted_kgco2 || bestResult.carbon_emitted_grams || 0),
        energy: parseFloat(bestResult.energy_consumed_kwh || 0),
        tokens: parseInt(bestResult.total_tokens || 0),
        accuracy: accuracy || 0,
        response_text: bestResult.response_text || "",
        inference_time_ms: bestResult.inference_time_ms || 0,
        tokens_input: bestResult.tokens_input || 0,
        tokens_output: bestResult.tokens_output || 0,
        total_tokens: bestResult.total_tokens || 0,
        provider: bestResult.provider || "unknown",
        timestamp: new Date().toISOString(),
        // Store full estimate for dashboard
        fullEstimate: bestResult
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
        const errorText = await response.text();
        console.error("Backend error:", errorText);
        
        // Parse error for user-friendly message
        const parsedError = parseApiError(errorText);
        if (parsedError) {
          throw new Error(parsedError.message);
        }
        
        throw new Error(`Comparison failed: ${response.status}`);
      }
      
      const result = await response.json();
      console.log("Comparison result:", result);
      setComparisonResults(result);
      setShowComparison(true);
      
      // Add to chat with smart naming
      let chatId = activeChatId;
      let isNewChat = false;
      if (!chatId) {
        isNewChat = true;
        const newChat = {
          id: generateUUID(),
          title: generateChatNameFromPrompt(input),
          messages: []
        };
        setChats([...chats, newChat]);
        chatId = newChat.id;
        setActiveChatId(chatId);
      }
      
      const message = {
        id: generateUUID(),
        type: "comparison",
        role: "assistant",
        content: JSON.stringify(result),
        prompt: input,
        response: JSON.stringify(result),
        model: selectedModels.join(", "),
        results: result,
        models_compared: selectedModels,
        timestamp: new Date().toISOString()
      };
      
      setChats(prev => prev.map(c => 
        c.id === chatId 
          ? { ...c, messages: [...c.messages, message] }
          : c
      ));
      
      // Save to database
      if (user && user.id) {
        const updatedChat = chats.find(c => c.id === chatId);
        if (updatedChat) {
          const chatToSave = {
            ...updatedChat,
            messages: [...(updatedChat.messages || []), message]
          };
          
          const method = isNewChat ? "POST" : "PUT";
          const url = isNewChat 
            ? `${API_BASE_URL}/api/chats?user_id=${user.id}`
            : `${API_BASE_URL}/api/chats/${user.id}/${chatId}`;
          
          try {
            const response = await fetch(url, {
              method: method,
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(chatToSave)
            });
            
            if (!response.ok && response.status === 404 && method === "PUT") {
              await fetch(`${API_BASE_URL}/api/chats?user_id=${user.id}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(chatToSave)
              });
            }
            console.log(`Chat ${isNewChat ? "created" : "updated"} successfully`);
          } catch (saveErr) {
            console.error("Error saving chat to database:", saveErr);
          }
        }
      }
      
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
      id: generateUUID(),
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
        
        {/* User Profile */}
        {user && <UserProfile user={user} onLogout={onLogout} />}
        
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
          {error && (
            <div className="error-message">
              {error.split('\n').map((line, idx) => (
                <div key={idx}>{line}</div>
              ))}
            </div>
          )}
          
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
