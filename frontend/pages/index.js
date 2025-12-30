import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { FaCloud, FaStar, FaRocket, FaShieldAlt, FaDollarSign } from 'react-icons/fa';

export default function Home() {
  const [reviews, setReviews] = useState([]);
  const [stats, setStats] = useState({ users: 0, recommendations: 0, providers: 3 });
  const [recentRecommendations, setRecentRecommendations] = useState([]);

  useEffect(() => {
    // Fetch real reviews from API
    const fetchReviews = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/reviews');
        const data = await response.json();
        if (response.ok && data.reviews) {
          setReviews(data.reviews.slice(0, 6)); // Show top 6 reviews
        } else {
          // Fallback to mock data
          setReviews([
            {
              username: 'JohnD',
              provider: 'AWS',
              instance_type: 't3.medium',
              topsis_score: 0.7234,
              rating: 5,
              comment: 'Great recommendation! Saved me 40% on cloud costs.'
            },
            {
              username: 'SarahM',
              provider: 'Azure',
              instance_type: 'D2s_v3',
              topsis_score: 0.6891,
              rating: 4,
              comment: 'Perfect for our development environment.'
            },
            {
              username: 'MikeT',
              provider: 'GCP',
              instance_type: 'n1-standard-2',
              topsis_score: 0.6543,
              rating: 5,
              comment: 'Excellent performance and cost balance.'
            }
          ]);
        }
      } catch (error) {
        console.error('Error fetching reviews:', error);
        // Use fallback data
        setReviews([
          {
            username: 'JohnD',
            provider: 'AWS',
            instance_type: 't3.medium',
            topsis_score: 0.7234,
            rating: 5,
            comment: 'Great recommendation! Saved me 40% on cloud costs.'
          }
        ]);
      }
    };

    fetchReviews();
    
    // Fetch recent recommendations for animation
    const fetchRecentRecommendations = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/reviews');
        const data = await response.json();
        if (response.ok && data.reviews) {
          setRecentRecommendations(data.reviews);
        }
      } catch (error) {
        console.error('Error fetching recommendations:', error);
      }
    };
    
    fetchRecentRecommendations();
    
    // Fetch real stats from API
    const fetchStats = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/stats');
        const data = await response.json();
        if (response.ok && data.stats) {
          setStats(data.stats);
        }
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };
    
    fetchStats();
  }, []);

  return (
    <>
      <Head>
        <title>CloudOptima - AI Cloud Recommendation</title>
        <meta name="description" content="AI-powered cloud instance recommendation engine" />
      </Head>

      {/* Navigation */}
      <nav className="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
        <div className="container">
          <Link href="/" className="navbar-brand d-flex align-items-center">
            <FaCloud className="text-primary me-2" style={{fontSize: '1.8rem'}} />
            <span className="fw-bold">CloudOptima</span>
          </Link>
          
          <div className="navbar-nav ms-auto">
            <Link href="/login" className="nav-link text-dark fw-semibold px-3">
              Login
            </Link>
            <Link href="/register" className="btn btn-primary px-4 ms-2">
              Sign Up
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-8 mx-auto text-center">
              <h1 className="display-4 fw-bold mb-4">
                AI-Powered Cloud Instance Recommendations
              </h1>
              <p className="lead mb-5 fs-4">
                Smart TOPSIS algorithm analyzes cost, performance, and security to find your perfect cloud solution
              </p>
              <Link href="/register" className="btn btn-light btn-lg px-5 py-3 fw-bold">
                Get Started Free
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Animated Recommendations Section */}
      <section className="py-5 bg-white overflow-hidden">
        <div className="container">
          <h2 className="text-center mb-4 fw-bold">Recent Recommendations</h2>
          <div className="animated-recommendations-wrapper">
            <div className="animated-recommendations">
              {recentRecommendations.concat(recentRecommendations).map((rec, index) => (
                <div key={index} className="notification-card">
                  <div className="notification-header">
                    <span className={`provider-dot provider-${(rec.provider || rec.selected_provider).toLowerCase().split(' ')[0]}`}></span>
                    <strong>{rec.username}</strong>
                    <div className="notification-stars">
                      {[...Array(5)].map((_, i) => (
                        <FaStar key={i} className={i < rec.rating ? 'star-filled' : 'star-empty'} />
                      ))}
                      
                    </div>
                  </div>
                  <div className="notification-body">
                    <div className="notification-instance">{(rec.instance_type || rec.selected_instance).split(' ')[0]}</div>
                    <div className="notification-score">Score: {typeof rec.topsis_score === 'number' ? rec.topsis_score.toFixed(2) : 'N/A'}</div>
                  </div>
                  <div className="notification-feedback" title={rec.comment || rec.review_text}>
                    {rec.comment || rec.review_text}
                  </div>
                </div>
              ))}
            </div>
          </div>
      {/* Features Section */}
        </div>
      </section>

      {/* User Reviews Section */}
      {/* <section className="py-5 bg-light">
        <div className="container">
          <h2 className="text-center mb-5 fw-bold">What Our Users Say</h2>
          <div className="row g-4">
            {reviews.map((review, index) => (
              <div key={index} className="col-md-6 col-lg-4">
                <div className="review-card custom-card">
                  <div className="review-header">
                    <div className="user-avatar">
                      {review.username.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h6 className="fw-bold mb-1">{review.username}</h6>
                      <div className="text-warning">
                        {[...Array(5)].map((_, i) => (
                          <FaStar key={i} className={i < review.rating ? 'text-warning' : 'text-muted'} />
                        ))}
                      </div>
                    </div>
                  </div>
                  <p className="text-muted mb-2">
                    {review.comment || review.review_text}
                  </p>
                  <small className="text-muted">
                    Chose: {(review.provider || review.selected_provider).split(' ')[0]} {(review.instance_type || review.selected_instance).split(' ')[0]}
                  </small>
                  <div className="mt-2">
                    <small className="text-primary">
                      Score: {typeof review.topsis_score === 'number' ? review.topsis_score.toFixed(4) : 'N/A'}
                    </small>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section> */}

      <section className="py-5 bg-white">
        <div className="container">
          <h2 className="text-center mb-5 fw-bold">Why Choose CloudOptima?</h2>
          <div className="row g-4">
            <div className="col-md-4">
              <div className="feature-card custom-card">
                <FaDollarSign className="feature-icon text-success" />
                <h4 className="fw-bold mb-3">Cost Optimization</h4>
                <p className="text-muted">
                  AI analyzes pricing across providers to find the most cost-effective solutions for your budget.
                </p>
              </div>
            </div>
            <div className="col-md-4">
              <div className="feature-card custom-card">
                <FaRocket className="feature-icon text-primary" />
                <h4 className="fw-bold mb-3">Performance Analysis</h4>
                <p className="text-muted">
                  Advanced TOPSIS algorithm evaluates CPU, memory, and storage performance metrics.
                </p>
              </div>
            </div>
            <div className="col-md-4">
              <div className="feature-card custom-card">
                <FaShieldAlt className="feature-icon text-warning" />
                <h4 className="fw-bold mb-3">Security First</h4>
                <p className="text-muted">
                  Comprehensive security scoring and compliance analysis for enterprise-grade protection.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-5 bg-light">
        <div className="container">
          <div className="row g-4">
            <div className="col-md-4 text-center">
              <div className="stats-counter">
                <span className="stats-number">{stats.users}+</span>
                <div className="stats-label">Happy Users</div>
              </div>
            </div>
            <div className="col-md-4 text-center">
              <div className="stats-counter">
                <span className="stats-number">{stats.recommendations}+</span>
                <div className="stats-label">Recommendations</div>
              </div>
            </div>
            <div className="col-md-4 text-center">
              <div className="stats-counter">
                <span className="stats-number">{stats.providers}</span>
                <div className="stats-label">Cloud Providers</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-5 bg-primary text-white">
        <div className="container">
          <div className="row">
            <div className="col-lg-8 mx-auto text-center">
              <h2 className="fw-bold mb-4">Ready to Optimize Your Cloud?</h2>
              <p className="lead mb-4">
                Join thousands of developers and businesses making smarter cloud decisions
              </p>
              <Link href="/register" className="btn btn-light btn-lg px-5 fw-bold">
                Start Free Today
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-dark text-white py-4">
        <div className="container text-center">
          <div className="d-flex align-items-center justify-content-center mb-3">
            <FaCloud className="text-primary me-2" style={{fontSize: '1.5rem'}} />
            <span className="fw-bold fs-5">CloudOptima</span>
          </div>
          <p className="text-white mb-0">AI-Powered Cloud Recommendation Engine</p>
          <p className="text-white small mt-2">© 2025 CloudOptima. All rights reserved.</p>
        </div>
      </footer>
    </>
  );
}