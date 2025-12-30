import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import { 
  FaCloud, FaServer, FaDatabase, FaChartBar, FaComments, 
  FaHistory, FaUser, FaSignOutAlt, FaCog, FaDollarSign,
  FaMapMarkerAlt, FaMicrochip, FaMemory, FaHdd, FaShieldAlt,
  FaTrophy, FaRobot, FaStar, FaAws, FaMicrosoft 
} from 'react-icons/fa';
import { SiGooglecloud, SiOracle, SiIbm, SiDigitalocean, SiLinode, SiAlibaba } from 'react-icons/si';

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('analysis');
  const [recommendations, setRecommendations] = useState([]);
  const [aiExplanation, setAiExplanation] = useState('');
  const [loading, setLoading] = useState(false);
  const [datasetInfo, setDatasetInfo] = useState(null);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (!token || !userData) {
      router.push('/login');
      return;
    }
    
    setUser(JSON.parse(userData));
    fetchDatasetInfo();
  }, [router]);

  const fetchDatasetInfo = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/dataset-info');
      const data = await response.json();
      if (response.ok) {
        setDatasetInfo(data);
      }
    } catch (error) {
      console.error('Error fetching dataset info:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    router.push('/');
  };

  const submitAnalysis = async (formData) => {
    setLoading(true);
    setRecommendations([]);
    setAiExplanation('');
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();
      
      if (response.ok) {
        setRecommendations(data.recommendations || []);
        setAiExplanation(data.ai_explanation || 'No explanation available.');
        
        // Store in analysis history
        const historyItem = {
          id: Date.now(),
          timestamp: new Date().toISOString(),
          budget: formData.budget,
          region: formData.region,
          weights: formData.weights,
          recommendations: data.recommendations?.slice(0, 5) || [],
          total_analyzed: data.total_analyzed || 0
        };
        
        const existingHistory = JSON.parse(localStorage.getItem('analysisHistory') || '[]');
        existingHistory.unshift(historyItem);
        localStorage.setItem('analysisHistory', JSON.stringify(existingHistory.slice(0, 20)));
      } else {
        alert(data.message || 'Failed to get recommendations');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to connect to server. Please check if backend is running.');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-3 text-muted">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Dashboard - CloudOptima</title>
      </Head>

      <div className="container-fluid">
        {/* Top Navigation Bar */}
        <nav className="navbar navbar-expand-lg navbar-light bg-white shadow-sm border-bottom">
          <div className="container-fluid">
            {/* Brand */}
            <div className="d-flex align-items-center">
              <FaCloud className="text-primary me-2" size={24} />
              <span className="fw-bold fs-5">CloudOptima</span>
            </div>
            
            {/* Navigation Links */}
            <div className="d-flex align-items-center">
              <div className="navbar-nav d-flex flex-row me-3">
                <button
                  onClick={() => setActiveTab('analysis')}
                  className={`nav-link btn me-2 ${activeTab === 'analysis' ? 'btn-primary' : 'btn-outline-primary'}`}
                >
                  <FaChartBar className="me-1" />
                  <span className="d-none d-md-inline">Instance Analysis</span>
                  <span className="d-md-none">Analysis</span>
                </button>
                
                <button
                  onClick={() => setActiveTab('reviews')}
                  className={`nav-link btn me-2 ${activeTab === 'reviews' ? 'btn-primary' : 'btn-outline-primary'}`}
                >
                  <FaComments className="me-1" />
                  <span className="d-none d-md-inline">Community Reviews</span>
                  <span className="d-md-none">Reviews</span>
                </button>
                
                <button
                  onClick={() => setActiveTab('history')}
                  className={`nav-link btn me-2 ${activeTab === 'history' ? 'btn-primary' : 'btn-outline-primary'}`}
                >
                  <FaHistory className="me-1" />
                  <span className="d-none d-md-inline">Analysis History</span>
                  <span className="d-md-none">History</span>
                </button>
                
                <button
                  onClick={() => setActiveTab('profile')}
                  className={`nav-link btn me-2 ${activeTab === 'profile' ? 'btn-primary' : 'btn-outline-primary'}`}
                >
                  <FaUser className="me-1" />
                  <span className="d-none d-md-inline">Profile</span>
                  <span className="d-md-none">Profile</span>
                </button>
              </div>
              
              {/* User Info & Logout */}
              <div className="d-flex align-items-center">
                <span className="text-muted me-3 d-none d-lg-inline">Welcome, {user.username}</span>
                <div className="user-avatar me-2">
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <button
                  onClick={handleLogout}
                  className="btn btn-outline-danger btn-sm"
                >
                  <FaSignOutAlt className="me-1" />
                  <span className="d-none d-md-inline">Logout</span>
                </button>
              </div>
            </div>
          </div>
        </nav>

        <div className="row">
          <div className="col-12">

            {/* Dataset Info Header */}
            {datasetInfo && (
              <div className="bg-gradient-primary text-white py-3">
                <div className="container-fluid">
                  <div className="row align-items-center">
                    <div className="col-md-8">
                      <div className="d-flex align-items-center">
                        <FaDatabase className="me-3" size={32} />
                        <div>
                          <h2 className="h4 mb-1 fw-bold">Dataset Information</h2>
                          <p className="mb-0 opacity-75">
                            <span className="fw-bold">{datasetInfo.total_instances?.toLocaleString() || '3000'}</span> instances available
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="col-md-4">
                      <div className="d-flex flex-wrap gap-2 justify-content-end">
                        <span className="badge bg-light text-dark d-flex align-items-center">
                          <FaAws className="me-1" /> AWS
                        </span>
                        <span className="badge bg-light text-dark d-flex align-items-center">
                          <FaMicrosoft className="me-1" /> Azure
                        </span>
                        <span className="badge bg-light text-dark d-flex align-items-center">
                          <SiGooglecloud className="me-1" /> GCP
                        </span>
                        <span className="badge bg-light text-dark d-flex align-items-center">
                          <SiOracle className="me-1" /> Oracle
                        </span>
                        <span className="badge bg-light text-dark d-flex align-items-center">
                          <SiIbm className="me-1" /> IBM
                        </span>
                        <span className="badge bg-light text-dark">+6 more</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <main className="container-fluid py-4">
              {activeTab === 'analysis' && (
                <AnalysisTab 
                  onSubmit={submitAnalysis}
                  loading={loading}
                  recommendations={recommendations}
                  aiExplanation={aiExplanation}
                  datasetInfo={datasetInfo}
                  setRecommendations={setRecommendations}
                />
              )}
              
              {activeTab === 'reviews' && (
                <ReviewsTab />
              )}
              
              {activeTab === 'history' && (
                <HistoryTab />
              )}
              
              {activeTab === 'profile' && (
                <ProfileTab user={user} />
              )}
            </main>
          </div>
        </div>
      </div>
    </>
  );
}

function AnalysisTab({ onSubmit, loading, recommendations, aiExplanation, datasetInfo, setRecommendations }) {
  const [formData, setFormData] = useState({
    budget: 0.2,
    region: 'us-east-1',
    weights: [8, 7, 6, 5, 6]
  });
  const [regions, setRegions] = useState([]);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);

  useEffect(() => {
    fetchRegions();
  }, []);

  const fetchRegions = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/regions');
      const data = await response.json();
      if (response.ok) {
        setRegions(data.regions);
      } else {
        setRegions([
          { value: 'us-east-1', label: 'US East (N. Virginia)' },
          { value: 'us-west-2', label: 'US West (Oregon)' }
        ]);
      }
    } catch (error) {
      setRegions([
        { value: 'us-east-1', label: 'US East (N. Virginia)' },
        { value: 'us-west-2', label: 'US West (Oregon)' }
      ]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleWeightChange = (index, value) => {
    const newWeights = [...formData.weights];
    newWeights[index] = parseInt(value);
    setFormData({...formData, weights: newWeights});
  };

  const getWeightPercentage = (weight) => {
    const total = formData.weights.reduce((a, b) => a + b, 0);
    return ((weight / total) * 100).toFixed(1);
  };

  return (
    <div className="row">
      <div className="col-lg-3 mb-4">
        <div className="card p-3">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h5 className="fw-bold mb-0">Configuration</h5>
            {datasetInfo && (
              <span className="badge bg-info">
                {datasetInfo.total_instances} instances
              </span>
            )}
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label fw-semibold small">
                <FaDollarSign className="me-1 text-success" />
                Budget: ${formData.budget.toFixed(2)}/hour
              </label>
              <input
                type="range"
                className="form-range"
                min="0.01"
                max="2.0"
                step="0.01"
                value={formData.budget}
                onChange={(e) => setFormData({...formData, budget: parseFloat(e.target.value)})}
              />
              <div className="d-flex justify-content-between text-muted small">
                <span>$0.01</span>
                <span>$2.00</span>
              </div>
            </div>

            <div className="mb-3">
              <label className="form-label fw-semibold small">
                <FaMapMarkerAlt className="me-1 text-primary" />
                Region 
              </label>
              <select
                className="form-select"
                value={formData.region}
                onChange={(e) => setFormData({...formData, region: e.target.value})}
              >
                {regions.map(region => (
                  <option key={region.value} value={region.value}>
                    {region.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="mb-3">
              <label className="form-label fw-semibold small">
                <FaCog className="me-1 text-warning" />
                Priority Weights
              </label>
              
              <div className="mb-2">
                <div className="d-flex justify-content-between align-items-center mb-1">
                  <span className="small fw-semibold">
                    <FaDollarSign className="me-1 text-primary" />
                    Cost
                  </span>
                  <span className="small fw-bold text-primary">{formData.weights[0]}/10</span>
                </div>
                <input
                  type="range"
                  className="form-range"
                  min="1"
                  max="10"
                  value={formData.weights[0]}
                  onChange={(e) => handleWeightChange(0, e.target.value)}
                />
              </div>
              
              <div className="mb-2">
                <div className="d-flex justify-content-between align-items-center mb-1">
                  <span className="small fw-semibold">
                    <FaMicrochip className="me-1 text-primary" />
                    CPU
                  </span>
                  <span className="small fw-bold text-primary">{formData.weights[1]}/10</span>
                </div>
                <input
                  type="range"
                  className="form-range"
                  min="1"
                  max="10"
                  value={formData.weights[1]}
                  onChange={(e) => handleWeightChange(1, e.target.value)}
                />
              </div>
              
              <div className="mb-2">
                <div className="d-flex justify-content-between align-items-center mb-1">
                  <span className="small fw-semibold">
                    <FaMemory className="me-1 text-primary" />
                    Memory
                  </span>
                  <span className="small fw-bold text-primary">{formData.weights[2]}/10</span>
                </div>
                <input
                  type="range"
                  className="form-range"
                  min="1"
                  max="10"
                  value={formData.weights[2]}
                  onChange={(e) => handleWeightChange(2, e.target.value)}
                />
              </div>
              
              <div className="mb-2">
                <div className="d-flex justify-content-between align-items-center mb-1">
                  <span className="small fw-semibold">
                    <FaHdd className="me-1 text-primary" />
                    Storage
                  </span>
                  <span className="small fw-bold text-primary">{formData.weights[3]}/10</span>
                </div>
                <input
                  type="range"
                  className="form-range"
                  min="1"
                  max="10"
                  value={formData.weights[3]}
                  onChange={(e) => handleWeightChange(3, e.target.value)}
                />
              </div>
              
              <div className="mb-2">
                <div className="d-flex justify-content-between align-items-center mb-1">
                  <span className="small fw-semibold">
                    <FaShieldAlt className="me-1 text-primary" />
                    Security
                  </span>
                  <span className="small fw-bold text-primary">{formData.weights[4]}/10</span>
                </div>
                <input
                  type="range"
                  className="form-range"
                  min="1"
                  max="10"
                  value={formData.weights[4]}
                  onChange={(e) => handleWeightChange(4, e.target.value)}
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary w-100 py-2 fw-semibold"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="spinner-border spinner-border-sm me-2" role="status"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <FaChartBar className="me-2" />
                  Generate
                </>
              )}
            </button>
          </form>
        </div>
      </div>

      <div className="col-lg-9">
        {loading && (
          <div className="card p-5 text-center">
            <div className="spinner-border text-primary mb-3" role="status"></div>
            <h4 className="fw-bold text-primary mb-2">Analyzing Cloud Instances</h4>
            <p className="text-muted">Processing instances with TOPSIS algorithm...</p>
          </div>
        )}

        {!loading && recommendations.length > 0 && (
          <>
            {/* Top Recommendation Card */}
            <div className="card p-4 mb-4 border-success">
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h3 className="fw-bold mb-0 text-success">
                  <FaTrophy className="me-2" />
                  #1 RECOMMENDED
                </h3>
                <div className="d-flex gap-3 align-items-center">
                  {/* Overall Rating from Community */}
                  {recommendations[0].avg_rating > 0 && (
                    <div className="text-center">
                      <div className="text-warning fw-bold fs-5">
                        {'⭐'.repeat(Math.round(recommendations[0].avg_rating))}
                      </div>
                      <small className="text-muted d-block">
                        {recommendations[0].avg_rating.toFixed(1)}/5 ({recommendations[0].rating_count})
                      </small>
                    </div>
                  )}
                  <span className="badge bg-success fs-6">
                    Hybrid Score: {(recommendations[0].hybrid_score * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
              
              <div className="row">
                <div className="col-md-8">
                  <h4 className="fw-bold text-primary mb-3">
                    {recommendations[0].provider.split(' ')[0]} {recommendations[0].instance_type.split(' ')[0]}
                  </h4>
                  
                  <div className="row g-3 mb-3">
                    <div className="col-sm-6 col-lg-3">
                      <div className="text-center p-3 bg-light rounded">
                        <FaMicrochip className="fs-4 text-primary" />
                        <div className="fw-bold">{Math.round(recommendations[0].vCPU)}</div>
                        <small className="text-muted">vCPUs</small>
                      </div>
                    </div>
                    <div className="col-sm-6 col-lg-3">
                      <div className="text-center p-3 bg-light rounded">
                        <FaMemory className="fs-4 text-info" />
                        <div className="fw-bold">{Math.round(recommendations[0].RAM_GB)} GB</div>
                        <small className="text-muted">RAM</small>
                      </div>
                    </div>
                    <div className="col-sm-6 col-lg-3">
                      <div className="text-center p-3 bg-light rounded">
                        <FaHdd className="fs-4 text-warning" />
                        <div className="fw-bold">{Math.round(recommendations[0].storage_GB)} GB</div>
                        <small className="text-muted">Storage</small>
                      </div>
                    </div>
                    <div className="col-sm-6 col-lg-3">
                      <div className="text-center p-3 bg-light rounded">
                        <FaShieldAlt className="fs-4 text-success" />
                        <div className="fw-bold">{Math.round(recommendations[0].security_score)}</div>
                        <small className="text-muted">Security</small>
                      </div>
                    </div>
                  </div>
                  
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <small className="text-muted">
                        Network: {recommendations[0].network_bandwidth || 'Standard'} • 
                        GPU: {recommendations[0].GPU > 0 ? `${Math.round(recommendations[0].GPU)} units` : 'None'}
                      </small>
                    </div>
                  </div>
                </div>
                
                <div className="col-md-4">
                  <div className="text-center">
                    <div className="display-4 fw-bold text-success mb-2">
                      ${recommendations[0].price_per_hour.toFixed(4)}
                    </div>
                    <div className="text-muted mb-3">per hour</div>
                    
                    <div className="bg-success text-white p-3 rounded">
                      <div className="fw-bold">Monthly Estimate*</div>
                      <div className="fs-5">
                        ${(recommendations[0].price_per_hour * 24 * 30).toFixed(2)}
                      </div>
                      <small>*Based on 24/7 usage</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Alternative Options Table */}
            {recommendations.length > 0 && (
              <div className="card p-4 mb-4">
                <h4 className="fw-bold mb-3">
                  <FaServer className="me-2" />
                  All Recommendations
                </h4>
                
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead className="table-light">
                      <tr>
                        <th>Rank</th>
                        <th>Provider</th>
                        <th>Instance</th>
                        <th>Price/hr</th>
                        <th>vCPU</th>
                        <th>RAM (GB)</th>
                        <th>Storage (GB)</th>
                        <th>Security</th>
                        <th>Hybrid Score</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recommendations.slice(0, 5).map((rec, index) => (
                        <tr key={index} className={index === 0 ? 'table-success' : ''}>
                          <td>
                            <span className={`badge ${index === 0 ? 'bg-success' : 'bg-secondary'}`}>
                              #{index + 1}
                            </span>
                          </td>
                          <td>
                            <span className="fw-semibold">{rec.provider.split(' ')[0]}</span>
                          </td>
                          <td>{rec.instance_type.split(' ')[0]}</td>
                          <td>
                            <span className="fw-bold text-success">
                              ${rec.price_per_hour.toFixed(4)}
                            </span>
                            <br />
                            <small className="text-muted">
                              ${(rec.price_per_hour * 24 * 30).toFixed(0)}/mo
                            </small>
                          </td>
                          <td>{Math.round(rec.vCPU)}</td>
                          <td>{Math.round(rec.RAM_GB)}</td>
                          <td>{Math.round(rec.storage_GB)}</td>
                          <td>{Math.round(rec.security_score)}</td>
                          <td>
                            <span className="fw-bold">
                              {(rec.hybrid_score * 100).toFixed(1)}%
                            </span>
                          </td>
                          <td>
                            <div className="d-flex align-items-center gap-2">
                              {/* Show average rating with count */}
                              {rec.avg_rating > 0 && (
                                <span className="small text-warning fw-bold" title={`Rated by ${rec.rating_count} users`}>
                                  ⭐ {rec.avg_rating.toFixed(1)} ({rec.rating_count})
                                </span>
                              )}
                              {/* Rating button - disabled if already rated */}
                              <button
                                className={`btn btn-sm ${
                                  rec.user_has_rated 
                                    ? 'btn-success' 
                                    : 'btn-outline-primary'
                                }`}
                                onClick={() => {
                                  setSelectedRecommendation(rec);
                                  setShowReviewModal(true);
                                }}
                                disabled={rec.user_has_rated}
                                title={rec.user_has_rated ? `You rated: ${rec.user_rating}★` : 'Rate this'}
                              >
                                {rec.user_has_rated ? `✓ ${rec.user_rating}★` : 'Rate'}
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>

        )}

        {!loading && aiExplanation && (
          <div className="card p-4">
            <div className="d-flex align-items-center justify-content-between mb-3">
              <h5 className="fw-bold mb-0">
                <FaRobot className="text-primary me-2" />
                AI Analysis
              </h5>
              <span className="badge bg-success">Live AI Response</span>
            </div>
            <div className="ai-explanation" style={{maxHeight: '600px', overflowY: 'auto', fontSize: '0.95rem'}}>
              {aiExplanation.split('\n').map((line, index) => {
                const trimmed = line.trim();
                
                // Main headers (##)
                if (line.startsWith('## ')) {
                  return (
                    <h5 key={index} className="fw-bold text-primary mt-4 mb-3 pb-2 border-bottom">
                      {line.replace(/^##\s/, '')}
                    </h5>
                  );
                }
                
                // Sub headers (###)
                if (line.startsWith('### ')) {
                  return (
                    <h6 key={index} className="fw-bold text-secondary mt-3 mb-2">
                      {line.replace(/^###\s/, '')}
                    </h6>
                  );
                }
                
                // Emoji headers (🏆, 📊, etc.)
                if (/^[🏆📊💰🚀🔄⚡🛠️📈🎯💡]/.test(trimmed)) {
                  return (
                    <h5 key={index} className="fw-bold text-success mt-4 mb-3">
                      {trimmed}
                    </h5>
                  );
                }
                
                // Bold text (**text**)
                if (line.startsWith('**') && line.includes(':**')) {
                  const text = line.replace(/\*\*/g, '');
                  const [label, ...rest] = text.split(':');
                  return (
                    <div key={index} className="mb-2">
                      <strong className="text-dark">{label}:</strong>
                      <span className="text-muted ms-1">{rest.join(':')}</span>
                    </div>
                  );
                }
                
                // Numbered lists (1., 2., etc.)
                if (/^\d+\.\s/.test(trimmed)) {
                  return (
                    <div key={index} className="mb-2 ps-3">
                      <strong className="text-primary">{trimmed}</strong>
                    </div>
                  );
                }
                
                // Bullet points (- or •)
                if (line.startsWith('- ') || line.startsWith('• ')) {
                  const text = line.replace(/^[-•]\s/, '');
                  // Check if it's a bold bullet
                  if (text.startsWith('**')) {
                    const cleanText = text.replace(/\*\*/g, '');
                    return (
                      <div key={index} className="ms-4 mb-2">
                        <span className="text-primary me-2">•</span>
                        <strong className="text-dark">{cleanText}</strong>
                      </div>
                    );
                  }
                  return (
                    <div key={index} className="ms-4 mb-1 text-muted">
                      <span className="text-primary me-2">•</span>
                      {text}
                    </div>
                  );
                }
                
                // Horizontal rule (---)
                if (trimmed === '---') {
                  return <hr key={index} className="my-4" />;
                }
                
                // Empty lines
                if (trimmed === '') {
                  return <div key={index} style={{height: '0.5rem'}}></div>;
                }
                
                // Regular paragraphs
                if (trimmed.length > 0) {
                  // Handle inline bold
                  const parts = trimmed.split(/\*\*/);
                  return (
                    <p key={index} className="mb-2 text-dark" style={{lineHeight: '1.6'}}>
                      {parts.map((part, i) => 
                        i % 2 === 1 ? <strong key={i} className="text-primary">{part}</strong> : part
                      )}
                    </p>
                  );
                }
                
                return null;
              })}
            </div>
          </div>
        )}

        {!loading && recommendations.length === 0 && (
          <div className="card p-5 text-center">
            <span className="text-muted mb-3" style={{fontSize: '4rem', opacity: 0.5}}>☁️</span>
            <h4 className="fw-bold text-muted mb-2">Ready for Analysis</h4>
            <p className="text-muted mb-4">
              Configure your requirements and generate recommendations.
            </p>
          </div>
        )}

        {showReviewModal && selectedRecommendation && (
          <ReviewModal
            recommendation={selectedRecommendation}
            onRated={({ provider, instance_type, rating }) => {
              // Update UI immediately without reloading
              setRecommendations((prev) => {
                const updated = prev.map((rec) => {
                  const sameInstance =
                    rec.provider === provider && rec.instance_type === instance_type;
                  if (!sameInstance) return rec;

                  const prevCount = Number(rec.rating_count || 0);
                  const prevAvg = Number(rec.avg_rating || 0);
                  const newCount = prevCount + 1;
                  const newAvg =
                    newCount > 0 ? (prevAvg * prevCount + rating) / newCount : rating;

                  return {
                    ...rec,
                    user_has_rated: true,
                    user_rating: rating,
                    avg_rating: newAvg,
                    rating_count: newCount,
                  };
                });

                // Keep existing order; only reflect rating changes live
                return updated;
              });
            }}
            onClose={() => {
              setShowReviewModal(false);
              setSelectedRecommendation(null);
            }}
          />
        )}
      </div>
    </div>
  );
}

function ReviewModal({ recommendation, onClose, onRated }) {
  const [rating, setRating] = useState(5);
  const [reviewText, setReviewText] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const submitReview = async () => {
    // Prevent re-submission if already rated
    if (recommendation.user_has_rated) {
      alert(`⚠️ You already rated this instance with ${recommendation.user_rating} stars!`);
      onClose();
      return;
    }

    setSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/ratings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          provider: recommendation.provider,
          instance_type: recommendation.instance_type,
          region: recommendation.region,
          price_per_hour: recommendation.price_per_hour,
          vCPU: recommendation.vCPU,
          RAM_GB: recommendation.RAM_GB,
          storage_GB: recommendation.storage_GB,
          security_score: recommendation.security_score,
          topsis_score: recommendation.topsis_score,
          rating: rating,
          comment: reviewText
        })
      });

      const data = await response.json();

      if (response.ok) {
        // Show feedback message from backend
        const feedback = data.feedback || 'Rating submitted successfully!';
        alert(`✅ ${data.message}\n${feedback}`);

        if (typeof onRated === 'function') {
          onRated({
            provider: recommendation.provider,
            instance_type: recommendation.instance_type,
            rating,
          });
        }
      } else if (response.status === 409) {
        // Already rated - show existing rating
        alert(`⚠️ ${data.message}\nYour rating: ${data.existing_rating}★`);
      } else {
        alert(`❌ Error: ${data.error || 'Failed to submit rating'}`);
      }
      onClose();
    } catch (error) {
      console.error('Error submitting rating:', error);
      alert('❌ Error submitting rating');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal show d-block" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">
              {recommendation.user_has_rated ? '✓ You Already Rated' : 'Rate Recommendation'}
            </h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <div className="modal-body">
            <div className="mb-3">
              <strong>{recommendation.provider} {recommendation.instance_type}</strong>
              <br />
              <small className="text-muted">Hybrid Score: {(recommendation.hybrid_score * 100).toFixed(1)}%</small>
            </div>
            
            {/* Show community rating */}
            {recommendation.avg_rating > 0 && (
              <div className="mb-3 p-2 bg-light rounded">
                <small className="d-block mb-1"><strong>Community Rating:</strong></small>
                <div>
                  <span className="text-warning fw-bold">
                    {'⭐'.repeat(Math.round(recommendation.avg_rating))}
                  </span>
                  <span className="ms-2">{recommendation.avg_rating.toFixed(1)}/5 ({recommendation.rating_count} ratings)</span>
                </div>
              </div>
            )}
            
            {/* If already rated, show it */}
            {recommendation.user_has_rated && (
              <div className="mb-3 p-3 bg-success bg-opacity-10 border border-success rounded">
                <small className="d-block mb-2"><strong>Your Rating:</strong></small>
                <div>
                  <span className="text-warning fw-bold fs-5">
                    {'⭐'.repeat(recommendation.user_rating)}
                  </span>
                  <span className="ms-2 fw-bold text-success">{recommendation.user_rating} stars</span>
                </div>
                <small className="d-block mt-2 text-muted">You cannot change your rating once submitted.</small>
              </div>
            )}
            
            {/* Only show rating controls if NOT already rated */}
            {!recommendation.user_has_rated && (
              <div className="mb-3">
                <label className="form-label">Your Rating</label>
                <div>
                  {[1, 2, 3, 4, 5].map(star => (
                    <button
                      key={star}
                      type="button"
                      className={`btn btn-sm ${star <= rating ? 'btn-warning' : 'btn-outline-warning'} me-1`}
                      onClick={() => setRating(star)}
                      disabled={submitting}
                    >
                      ⭐
                    </button>
                  ))}
                  <span className="ms-3 fw-bold">{rating}/5</span>
                </div>
              </div>
            )}

            {!recommendation.user_has_rated && (
              <div className="mb-3">
                <label className="form-label">Feedback (optional)</label>
                <textarea
                  className="form-control"
                  rows={3}
                  value={reviewText}
                  onChange={(e) => setReviewText(e.target.value)}
                  placeholder="Share your thoughts about this recommendation..."
                  disabled={submitting}
                />
              </div>
            )}
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              {recommendation.user_has_rated ? 'Close' : 'Cancel'}
            </button>
            {!recommendation.user_has_rated && (
              <button
                type="button"
                className="btn btn-primary"
                onClick={submitReview}
                disabled={submitting}
              >
                {submitting ? 'Submitting...' : 'Submit Rating'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function ReviewsTab() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReviews();
  }, []);

  const fetchReviews = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/reviews');
      const data = await response.json();
      if (response.ok) {
        setReviews(data.reviews || []);
      }
    } catch (error) {
      console.error('Error fetching reviews:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="card p-4">
      <h3 className="fw-bold mb-4">
        <span className="me-2 text-primary">💬</span>
        Community Reviews
      </h3>
      
      {reviews.length === 0 ? (
        <div className="text-center py-5">
          <span className="text-muted mb-3" style={{fontSize: '3rem', opacity: 0.5}}>💬</span>
          <h5 className="text-muted">No reviews yet</h5>
          <p className="text-muted">Be the first to share your experience!</p>
        </div>
      ) : (
        <div className="row g-3">
          {reviews.map((review, index) => (
            <div key={index} className="col-12">
              <div className="card">
                <div className="card-body py-2 px-3">
                  <div className="d-flex justify-content-between align-items-start mb-3">
                    <div>
                      <h6 className="fw-bold mb-1">{review.username}</h6>
                      <small className="text-muted">
                        {review.provider.split(' ')[0]} {review.instance_type.split(' ')[0]}
                      </small>
                    </div>
                    <div className="text-end">
                      <div className="d-flex align-items-center mb-1">
                        {[...Array(5)].map((_, i) => (
                          <FaStar key={i} className={`${i < review.rating ? 'text-warning' : 'text-muted'} me-1`} size={12} />
                        ))}
                        <span className="ms-1 small fw-bold">{review.rating}</span>
                      </div>
                      <small className="text-muted">
                        Score: {typeof review.topsis_score === 'number' ? review.topsis_score.toFixed(4) : 'N/A'}
                      </small>
                    </div>
                  </div>
                  {review.comment && (
                    <p className="mb-0 text-muted">{review.comment}</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function HistoryTab() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const savedHistory = JSON.parse(localStorage.getItem('analysisHistory') || '[]');
    setHistory(savedHistory);
  }, []);

  // Force refresh when tab becomes active
  useEffect(() => {
    const refreshHistory = () => {
      const savedHistory = JSON.parse(localStorage.getItem('analysisHistory') || '[]');
      setHistory(savedHistory);
    };
    
    // Listen for storage changes
    window.addEventListener('storage', refreshHistory);
    
    // Also refresh on focus
    window.addEventListener('focus', refreshHistory);
    
    return () => {
      window.removeEventListener('storage', refreshHistory);
      window.removeEventListener('focus', refreshHistory);
    };
  }, []);

  return (
    <div className="card p-4">
      <h3 className="fw-bold mb-4">
        <FaHistory className="me-2 text-primary" />
        Analysis History
      </h3>
      
      {history.length === 0 ? (
        <div className="text-center py-5">
          <FaHistory className="text-muted mb-3" style={{fontSize: '3rem', opacity: 0.5}} />
          <h5 className="text-muted">No history available</h5>
          <p className="text-muted">Your analysis history will appear here.</p>
        </div>
      ) : (
        <div className="row g-3">
          {history.map((item, index) => (
            <div key={item.id || index} className="col-12">
              <div className="card border-left-primary">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-start mb-3">
                    <div>
                      <h6 className="fw-bold mb-1">Analysis #{history.length - index}</h6>
                      <small className="text-muted">
                        {new Date(item.timestamp).toLocaleString()}
                      </small>
                    </div>
                    <span className="badge bg-primary">
                      {item.recommendations?.length || 0} recommendations
                    </span>
                  </div>
                  
                  <div className="row mb-3">
                    <div className="col-md-6">
                      <small className="text-muted d-block">Budget: <strong>${item.budget}/hour</strong></small>
                      <small className="text-muted d-block">Region: <strong>{item.region}</strong></small>
                    </div>
                    <div className="col-md-6">
                      <small className="text-muted d-block">Analyzed: <strong>{item.total_analyzed} instances</strong></small>
                    </div>
                  </div>
                  
                  {item.recommendations && item.recommendations.length > 0 && (
                    <div>
                      <small className="text-muted fw-bold">Top Recommendation:</small>
                      <div className="mt-2 p-2 bg-light rounded">
                        <div className="d-flex justify-content-between align-items-center">
                          <div>
                            <span className="fw-bold">{item.recommendations[0].provider.split(' ')[0]} {item.recommendations[0].instance_type.split(' ')[0]}</span>
                            <br />
                            <small className="text-muted">
                              {Math.round(item.recommendations[0].vCPU)} vCPUs • {Math.round(item.recommendations[0].RAM_GB)} GB RAM
                            </small>
                          </div>
                          <div className="text-end">
                            <div className="fw-bold text-success">${item.recommendations[0].price_per_hour.toFixed(4)}/hr</div>
                            <small className="text-muted">Score: {(item.recommendations[0].topsis_score * 100).toFixed(1)}%</small>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ProfileTab({ user }) {
  return (
    <div className="card p-4">
      <h3 className="fw-bold mb-4">
        <span className="me-2 text-primary">👤</span>
        Profile Settings
      </h3>
      
      <div className="row">
        <div className="col-md-6">
          <div className="mb-3">
            <label className="form-label fw-semibold">Username</label>
            <input 
              type="text" 
              className="form-control" 
              value={user.username} 
              readOnly 
            />
          </div>
          
          <div className="mb-3">
            <label className="form-label fw-semibold">Email</label>
            <input 
              type="email" 
              className="form-control" 
              value={user.email} 
              readOnly 
            />
          </div>
        </div>
        
        <div className="col-md-6">
          <div className="text-center">
            <div className="user-avatar-large mb-3">
              {user.username.charAt(0).toUpperCase()}
            </div>
            <h5 className="fw-bold">{user.username}</h5>
            <p className="text-muted">{user.email}</p>
          </div>
        </div>
      </div>
    </div>
  );
}