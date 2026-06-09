import { API_BASE_URL } from './api';
import React, { useState, useEffect } from 'react';
import './Dashboard.css';

const Dashboard = ({ estimates = [] }) => {
  const [stats, setStats] = useState({
    totalRequests: 0,
    totalCarbon: 0,
    averageAccuracy: 0,
    totalEnergy: 0,
    modelBreakdown: {},
    topModels: []
  });

  useEffect(() => {
    if (estimates && estimates.length > 0) {
      calculateStats();
    }
  }, [estimates]);

  const calculateStats = () => {
    console.log('Estimates received in Dashboard:', estimates);
    
    // Normalize all input data to ensure proper types
    const normalizedEstimates = estimates.map(e => {
      // Handle accuracy from multiple possible locations
      let accuracy = 0;
      if (e.accuracy !== undefined && e.accuracy !== null && e.accuracy !== 0) {
        accuracy = parseFloat(e.accuracy);
      } else if (e.overall_accuracy !== undefined && e.overall_accuracy !== null && e.overall_accuracy !== 0) {
        accuracy = parseFloat(e.overall_accuracy);
      } else if (e.accuracy_scores?.overall_accuracy !== undefined && e.accuracy_scores.overall_accuracy !== null) {
        accuracy = parseFloat(e.accuracy_scores.overall_accuracy);
      }
      
      return {
        id: e.id,
        model_name: e.model_name || e.model || "unknown",
        carbon_emitted_kgco2: parseFloat(e.carbon || e.carbon_emitted_kgco2 || 0),
        energy_consumed_kwh: parseFloat(e.energy || e.energy_consumed_kwh || 0),
        overall_accuracy: accuracy >= 0 && accuracy <= 100 ? accuracy : 0,
        accuracy_scores: e.accuracy_scores || null,
        tokens: parseInt(e.tokens || 0)
      };
    }).filter(e => e.carbon_emitted_kgco2 > 0 || e.overall_accuracy > 0 || e.tokens > 0);  // Filter out empty estimates
    
    console.log('Normalized estimates:', normalizedEstimates);
    
    const totalRequests = normalizedEstimates.length;
    const totalCarbon = normalizedEstimates.reduce((sum, e) => sum + (e.carbon_emitted_kgco2 || 0), 0);
    const totalEnergy = normalizedEstimates.reduce((sum, e) => sum + (e.energy_consumed_kwh || 0), 0);
    
    // Extract accuracy values
    const validAccuracies = normalizedEstimates
      .map(e => e.overall_accuracy)
      .filter(acc => acc > 0 && acc <= 100);
    
    const averageAccuracy = validAccuracies.length > 0 
      ? validAccuracies.reduce((sum, acc) => sum + acc, 0) / validAccuracies.length 
      : 0;

    // Calculate model breakdown with normalized data
    const modelBreakdown = {};
    
    normalizedEstimates.forEach(e => {
      const modelName = e.model_name;
      
      if (!modelBreakdown[modelName]) {
        modelBreakdown[modelName] = {
          count: 0,
          totalCarbon: 0,
          totalEnergy: 0,
          totalAccuracy: 0,
          accuracyCount: 0
        };
      }
      modelBreakdown[modelName].count += 1;
      modelBreakdown[modelName].totalCarbon += e.carbon_emitted_kgco2 || 0;
      modelBreakdown[modelName].totalEnergy += e.energy_consumed_kwh || 0;
      
      // Handle accuracy
      if (e.overall_accuracy > 0 && e.overall_accuracy <= 100) {
        modelBreakdown[modelName].totalAccuracy += e.overall_accuracy;
        modelBreakdown[modelName].accuracyCount += 1;
      }
    });
      let accuracy = e.overall_accuracy;
      if (accuracy === undefined || accuracy === null || accuracy === 0) {
        accuracy = e.accuracy_scores?.overall_accuracy;
      }
      
      if (accuracy && accuracy >= 0 && accuracy <= 100) {
        modelBreakdown[modelName].totalAccuracy += accuracy;
        modelBreakdown[modelName].accuracyCount += 1;
      }
    });

    // Get top models by usage - normalized and sorted
    const topModels = Object.entries(modelBreakdown)
      .map(([name, data]) => ({
        name,
        count: data.count,
        carbonPerRequest: data.totalCarbon / data.count,
        totalCarbon: data.totalCarbon,
        totalEnergy: data.totalEnergy,
        accuracyAvg: data.accuracyCount > 0 ? data.totalAccuracy / data.accuracyCount : 0
      }))
      .sort((a, b) => b.count - a.count);
    
    console.log('Model Breakdown keys:', Object.keys(modelBreakdown));
    console.log('Top Models:', topModels);

    setStats({
      totalRequests,
      totalCarbon,
      averageAccuracy: parseFloat(averageAccuracy.toFixed(2)),
      totalEnergy,
      modelBreakdown,
      topModels
    });
  };

  const formatCarbonKg = (kg) => {
    if (!kg || isNaN(kg)) return "0.00";
    return (kg * 1000000).toFixed(2);
  };
  
  const formatEnergy = (kwh) => {
    if (!kwh || isNaN(kwh)) return "0.00";
    return (kwh * 1000 * 3600).toFixed(2);
  };
  
  const formatPercentage = (val) => {
    if (!val || isNaN(val)) return "0.00";
    // If value is already 0-100 (accuracy from evaluator), don't multiply
    // If it's 0-1 (rare case), multiply by 100
    if (val > 1) {
      return val.toFixed(1);
    } else {
      return (val * 100).toFixed(1);
    }
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>📊 Carbon Footprint Dashboard</h2>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <h3>Total Requests</h3>
            <p className="stat-value">{stats.totalRequests}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🌱</div>
          <div className="stat-content">
            <h3>Total CO₂ Emitted</h3>
            <p className="stat-value">{formatCarbonKg(stats.totalCarbon)} μg</p>
            <p className="stat-subtext">{stats.totalCarbon.toFixed(6)} kg</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <h3>Total Energy</h3>
            <p className="stat-value">{formatEnergy(stats.totalEnergy)} J</p>
            <p className="stat-subtext">{(stats.totalEnergy * 1000).toFixed(2)} Wh</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <h3>Average Accuracy</h3>
            <p className="stat-value">{formatPercentage(stats.averageAccuracy)}%</p>
          </div>
        </div>
      </div>

      {stats.topModels.length > 0 && (
        <div className="models-section">
          <h3>📋 Model Performance Breakdown</h3>
          <div className="models-grid">
            {stats.topModels.map((model, idx) => (
              <div key={idx} className="model-card">
                <div className="model-header">
                  <h4>{model.name}</h4>
                  <span className="model-badge">{model.count} requests</span>
                </div>
                <div className="model-stats">
                  <div className="model-stat">
                    <span className="stat-label">🌱 CO₂/Request:</span>
                    <strong>{formatCarbonKg(model.carbonPerRequest)} μg</strong>
                    <span className="stat-detail">({model.carbonPerRequest.toFixed(8)} kg)</span>
                  </div>
                  <div className="model-stat">
                    <span className="stat-label">🌍 Total CO₂:</span>
                    <strong>{formatCarbonKg(model.totalCarbon)} μg</strong>
                  </div>
                  <div className="model-stat">
                    <span className="stat-label">⚡ Total Energy:</span>
                    <strong>{formatEnergy(model.totalEnergy)} J</strong>
                  </div>
                  <div className="model-stat">
                    <span className="stat-label">🎯 Accuracy:</span>
                    <strong>{formatPercentage(model.accuracyAvg)}%</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {stats.totalRequests === 0 && (
        <div className="empty-state">
          <p>No data yet. Make some requests to see dashboard statistics!</p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
