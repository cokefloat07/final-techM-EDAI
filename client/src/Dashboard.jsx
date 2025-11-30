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
    const totalRequests = estimates.length;
    const totalCarbon = estimates.reduce((sum, e) => sum + (e.carbon_emitted_kgco2 || 0), 0);
    const totalEnergy = estimates.reduce((sum, e) => sum + (e.energy_consumed_kwh || 0), 0);
    
    // Extract accuracy values - handle both cases where it could be nested or top-level
    const validAccuracies = estimates
      .map(e => {
        let accuracy = e.overall_accuracy;
        if (accuracy === undefined || accuracy === null) {
          accuracy = e.accuracy_scores?.overall_accuracy;
        }
        // Return only valid accuracy values (0-100 range is expected)
        return accuracy && accuracy >= 0 && accuracy <= 100 ? accuracy : null;
      })
      .filter(acc => acc !== null);
    
    const totalAccuracy = validAccuracies.reduce((sum, acc) => sum + acc, 0);
    const averageAccuracy = validAccuracies.length > 0 ? totalAccuracy / validAccuracies.length : 0;

    // Calculate model breakdown
    const modelBreakdown = {};
    
    estimates.forEach(e => {
      // Ensure we have a model name - handle both API response and chat message formats
      const modelName = e.model_name || e.model || "unknown";
      
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
      
      // Handle accuracy - check multiple possible locations
      let accuracy = e.overall_accuracy;
      if (accuracy === undefined || accuracy === null) {
        accuracy = e.accuracy_scores?.overall_accuracy;
      }
      
      if (accuracy && accuracy >= 0 && accuracy <= 100) {
        modelBreakdown[modelName].totalAccuracy += accuracy;
        modelBreakdown[modelName].accuracyCount += 1;
      }
    });

    // Get top models by usage
    const topModels = Object.entries(modelBreakdown)
      .map(([name, data]) => ({
        name,
        count: data.count,
        carbonPerRequest: data.totalCarbon / data.count,
        accuracyAvg: data.accuracyCount > 0 ? data.totalAccuracy / data.accuracyCount : 0
      }))
      .sort((a, b) => b.count - a.count);
    
    console.log('Model Breakdown keys:', Object.keys(modelBreakdown));
    console.log('Top Models:', topModels);

    setStats({
      totalRequests,
      totalCarbon,
      averageAccuracy,
      totalEnergy,
      modelBreakdown,
      topModels
    });
  };

  const formatCarbonKg = (kg) => (kg * 1000000).toFixed(2); // Convert to micrograms
  const formatEnergy = (kwh) => (kwh * 1000 * 3600).toFixed(2); // Convert to Joules
  const formatPercentage = (val) => {
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
          <h3>📋 Model Performance</h3>
          <div className="models-grid">
            {stats.topModels.map((model, idx) => (
              <div key={idx} className="model-card">
                <h4>{model.name}</h4>
                <div className="model-stat">
                  <span>Requests:</span>
                  <strong>{model.count}</strong>
                </div>
                <div className="model-stat">
                  <span>Avg CO₂/Request:</span>
                  <strong>{formatCarbonKg(model.carbonPerRequest)} μg</strong>
                </div>
                <div className="model-stat">
                  <span>Avg Accuracy:</span>
                  <strong>{formatPercentage(model.accuracyAvg)}%</strong>
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
