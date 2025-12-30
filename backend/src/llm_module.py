import os
from typing import Dict, List, Any
import pandas as pd

# Try to import Groq, but don't fail if not available
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None

class LLMRecommender:
    """
    LLM-based recommendation explainer using Groq API (LLaMA models)
    Provides detailed analysis of top recommendations with advantages and comparisons
    """
    
    def __init__(self):
        """Initialize Groq client with API key"""
        self.client = None
        self.provider = 'fallback'  # Always use fallback (Groq SDK not installed)
        
        # Get Groq API key from environment
        groq_api_key = os.getenv('GROQ_API_KEY')
        
        if GROQ_AVAILABLE and groq_api_key and groq_api_key.strip():
            try:
                self.client = Groq(api_key=groq_api_key)
                self.provider = 'groq'
                print("✅ LLM: Groq API (LLaMA) initialized successfully")
            except Exception as e:
                print(f"❌ Groq API initialization failed: {e}")
                print("⚠️ Using enhanced fallback explanation mode")
                self.provider = 'fallback'
        else:
            if not GROQ_AVAILABLE:
                print("⚠️ Groq SDK not installed - using enhanced fallback mode")
            else:
                print("⚠️ GROQ_API_KEY not found - using enhanced fallback mode")
            self.provider = 'fallback'

    def build_prompt(self, user_prefs: Dict, recommendations: pd.DataFrame, dataset_stats: Dict) -> str:
        """
        Build an enhanced prompt for detailed recommendation explanation
        
        Args:
            user_prefs: User preferences (budget, region, weights)
            recommendations: Top 5 recommendations DataFrame (MUST be sorted by score, best first)
            dataset_stats: Overall dataset statistics
            
        Returns:
            Detailed prompt string optimized for LLaMA
        """
        
        # Extract user preferences
        budget = user_prefs.get('budget', 0)
        region = user_prefs.get('region', 'N/A')
        weights = user_prefs.get('raw_weights', [])
        
        # Build recommendation details - CRITICAL: Use iloc to ensure correct ranking
        rec_details = []
        for i in range(len(recommendations)):
            row = recommendations.iloc[i]  # Use iloc to get by position, not index
            rec_details.append({
                'rank': i + 1,  # Rank 1 = first row, Rank 2 = second row, etc.
                'provider': row['provider'],
                'instance': row['instance_type'],
                'price': row['price_per_hour'],
                'vcpu': row['vCPU'],
                'ram': row['RAM_GB'],
                'storage': row['storage_GB'],
                'security': row['security_score'],
                'performance': row.get('performance', 0),
                'availability': row.get('availability', 0),
                'latency': row.get('latency', 0),
                'hybrid_score': row.get('hybrid_score', row.get('topsis_score', 0)),
                'network': row.get('network_bandwidth', 'Standard'),
                'bandwidth_score': row.get('bandwidth_score', 7)
            })
        
        # Debug: Log what we're about to explain
        print(f"🔍 LLM Prompt Building - Top 3 instances:")
        for i in range(min(3, len(rec_details))):
            rec = rec_details[i]
            print(f"   Option {i+1}: {rec['provider']} {rec['instance']} (Hybrid: {rec['hybrid_score']:.6f})")
        
        # Build the enhanced prompt optimized for LLaMA
        prompt = f"""You are an expert cloud infrastructure consultant. Analyze these cloud instance recommendations and provide a detailed explanation.

=== USER REQUIREMENTS ===
Budget: ${budget:.4f} per hour
Region: {region}
Instances Analyzed: {len(recommendations)} from {dataset_stats.get('total_instances', 0)} total available
User Priority Weights: {weights}

=== TOP 5 CLOUD RECOMMENDATIONS ===
(Ranked by Hybrid Score from Multi-Criteria Analysis)

"""
        
        # Add each recommendation with complete details
        for i, rec in enumerate(rec_details, 1):
            prompt += f"""
OPTION {i}: {rec['provider']} {rec['instance']}
✓ Hybrid Score: {rec['hybrid_score']:.4f} (0=worst, 1=best)
✓ Price: ${rec['price']:.4f}/hour ({(rec['price']/budget)*100:.1f}% of budget)
✓ Compute: {rec['vcpu']} vCPU | {rec['ram']:.1f} GB RAM | {rec['storage']} GB Storage
✓ Security: {rec['security']}/100
✓ Performance Score: {rec['performance']:.2f}
✓ Availability: {rec['availability']:.2f}%
✓ Network Latency: {rec['latency']:.2f}ms
✓ Network Bandwidth: {rec['network']} (Score: {rec['bandwidth_score']})
"""
        
        prompt += """

=== YOUR TASK ===
Provide a comprehensive analysis following this EXACT structure:

## 🏆 BEST RECOMMENDATION (Option 1: {rec_details[0]['provider']} {rec_details[0]['instance']})

IMPORTANT: Option 1 is {rec_details[0]['provider']} {rec_details[0]['instance']} - ONLY explain THIS instance as the best choice.

Explain why {rec_details[0]['provider']} {rec_details[0]['instance']} is the top choice:

1. Hybrid Score Analysis Results:
   - Why it achieved the highest score
   - Which criteria it excels in
   - How it balances price vs performance

2. Key Advantages:
   - Specific technical strengths
   - Cost-effectiveness benefits
   - Security and reliability features
   - Performance characteristics

3. Best Use Cases:
   - What workloads it handles well
   - Ideal application scenarios
   - Who should choose this option

4. Value Proposition:
   - ROI and cost savings
   - Long-term benefits
   - Competitive advantages

---

## 📊 ALTERNATIVE OPTIONS ANALYSIS

For Options 2-5, explain each:

**Option X: [Provider] [Instance]**
- Unique Strengths: What makes it special
- When to Choose: Specific scenarios where it beats Option 1
- Trade-offs: What you gain/lose vs Option 1
- Best For: Target use cases

---

## 💡 FINAL RECOMMENDATION GUIDE

Provide clear decision guidance:
- Default Choice: Why most users should pick Option 1
- Alternative Scenarios: When to pick Options 2-5
- Budget Optimization: Best value options
- Performance Priority: Best performance options
- Balanced Approach: Best all-around options

=== GUIDELINES ===
• Write in detailed paragraphs, NOT bullet points
• Explain concepts thoroughly with context and examples
• Be specific with numbers and metrics
• Compare options directly with detailed reasoning
• Focus on practical business value and real-world scenarios
• Use professional but conversational language
• Target 1000-1500 words total
• Provide deep technical and business insights
• Explain WHY and HOW, not just WHAT
• Make recommendations actionable with clear decision criteria
"""
        
        return prompt

    def get_explanation(self, prompt: str) -> str:
        """
        Get AI-generated explanation from Groq API (LLaMA)
        ONLY uses real AI - no fallback
        
        Args:
            prompt: The detailed prompt
            
        Returns:
            AI-generated explanation string or error message
        """
        print(f"🤖 LLM get_explanation called (provider: {self.provider})")
        
        if self.provider == 'groq':
            try:
                return self._get_groq_response(prompt)
            except Exception as e:
                print(f"❌ Groq API error: {e}")
                return "❌ AI Analysis Not Available: Groq API error. Please check your API key and internet connection."
        else:
            print("❌ AI not configured - Groq SDK not installed or API key missing")
            return "❌ AI Analysis Not Available: Please install Groq SDK (pip install groq) and configure GROQ_API_KEY in .env file to enable AI-powered analysis."

    def _get_groq_response(self, prompt: str) -> str:
        """
        Get response from Groq API using LLaMA model
        
        Args:
            prompt: The prompt string
            
        Returns:
            LLaMA-generated response
        """
        try:
            print("🔗 Calling Groq API...")
            # Use Groq's LLaMA 3.1 70B model (best quality)
            # Alternative models: llama-3.1-8b-instant (faster), mixtral-8x7b-32768
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert cloud infrastructure consultant with deep knowledge of AWS, Azure, GCP, and multi-criteria decision analysis. Provide detailed, actionable recommendations based on Hybrid Score ranking and the provided metrics."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.3-70b-versatile",  # Latest model (Dec 2024)
                temperature=0.7,
                max_tokens=2048,
                top_p=0.9,
                stream=False
            )
            
            response_text = chat_completion.choices[0].message.content.strip()
            print(f"✅ LLaMA response generated ({len(response_text)} characters)")
            print(f"Response preview: {response_text[:200]}...")
            
            # If response is too short, it might be an error message
            if len(response_text) < 200:
                print(f"⚠️ Warning: Response is very short. Full response: {response_text}")
            
            return response_text
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Groq API request failed: {type(e).__name__}: {error_msg}")
            
            # Check for specific errors
            if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                print("❌ API Key Error: Invalid or expired API key")
            elif "rate limit" in error_msg.lower():
                print("❌ Rate Limit: Too many requests")
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                print("❌ Network Error: Check internet connection")
            
            import traceback
            traceback.print_exc()
            raise

    def _get_fallback_response(self, prompt: str) -> str:
        """
        Generate enhanced fallback response when API is unavailable
        Extracts information from prompt to create detailed explanation
        """
        
        print("🔄 Generating enhanced fallback explanation...")
        
        # Parse the prompt to extract recommendation details
        lines = prompt.split('\n')
        recommendations = []
        current_rec = None
        budget = 0
        region = "selected region"
        
        for line in lines:
            line = line.strip()
            
            # Extract budget and region
            if line.startswith('Budget:'):
                try:
                    budget = float(line.split('$')[1].split()[0])
                except:
                    pass
            if line.startswith('Region:'):
                region = line.split('Region:')[1].strip()
            
            # Extract recommendations
            if line.startswith('OPTION'):
                if current_rec:
                    recommendations.append(current_rec)
                
                # Parse option header
                parts = line.split(':', 1)
                if len(parts) == 2:
                    option_num = parts[0].replace('OPTION', '').strip()
                    name = parts[1].strip()
                    current_rec = {
                        'rank': option_num,
                        'name': name,
                        'details': {}
                    }
            
            elif line.startswith('✓') and current_rec:
                # Parse detail line
                detail = line[1:].strip()  # Remove ✓
                if ':' in detail:
                    key, value = detail.split(':', 1)
                    current_rec['details'][key.strip()] = value.strip()
        
        if current_rec:
            recommendations.append(current_rec)
        
        # Generate comprehensive response
        if not recommendations or len(recommendations) == 0:
            return f"Based on Hybrid Score analysis for {region} region with ${budget:.4f}/hour budget, we've identified optimal cloud instances for your needs."
        
        best = recommendations[0]
        best_name = best.get('name', 'Top recommendation')
        best_score = best['details'].get('Hybrid Score', best['details'].get('TOPSIS Score', 'N/A'))
        best_price = best['details'].get('Price', 'competitive pricing')
        best_compute = best['details'].get('Compute', 'robust resources')
        best_security = best['details'].get('Security', 'high security')
        best_performance = best['details'].get('Performance Score', 'excellent performance')
        best_availability = best['details'].get('Availability', 'high availability')
        best_latency = best['details'].get('Network Latency', 'low latency')
        
        response = f"""## 🏆 BEST RECOMMENDATION: {best_name}

After comprehensive multi-criteria analysis, **{best_name}** emerges as the optimal choice for your {region} deployment.

### Why This is Your Top Choice

**1. Hybrid Score Analysis Results:**
- Achieved the highest overall score of {best_score}, indicating superior balance across all evaluation criteria
- Outperformed all alternatives in the weighted multi-criteria assessment
- Represents the closest solution to the ideal performance benchmark

**2. Key Advantages:**
- **Cost Efficiency**: {best_price} fits comfortably within your ${budget:.4f}/hour budget
- **Compute Power**: {best_compute} provides robust processing capabilities
- **Enterprise Security**: {best_security} ensures compliance and data protection
- **High Performance**: {best_performance} delivers consistent workload execution
- **Reliability**: {best_availability} minimizes downtime risks
- **Network Speed**: {best_latency} ensures responsive applications

**3. Ideal Use Cases:**
- General-purpose web applications and APIs
- Development and testing environments
- Small to medium database workloads
- Microservices architectures
- CI/CD pipelines and automation tasks

**4. Value Proposition:**
- Optimal price-to-performance ratio in {region}
- Proven reliability with enterprise-grade SLA
- Scalable architecture for future growth
- Compatible with modern DevOps tooling

---

## 📊 ALTERNATIVE OPTIONS ANALYSIS

"""
        
        # Add detailed analysis for other options
        for i, rec in enumerate(recommendations[1:], 2):
            rec_name = rec.get('name', f'Option {i}')
            rec_score = rec['details'].get('Hybrid Score', rec['details'].get('TOPSIS Score', 'N/A'))
            rec_price = rec['details'].get('Price', 'N/A')
            rec_compute = rec['details'].get('Compute', 'N/A')
            rec_security = rec['details'].get('Security', 'N/A')
            
            response += f"""**Option {i}: {rec_name}** (Score: {rec_score})

- **Unique Strengths**: """
            
            if i == 2:
                response += f"""Close runner-up with nearly identical capabilities. Excellent alternative with strong provider reputation.
- **When to Choose**: If you have existing infrastructure with this provider or prefer their specific tools and ecosystem.
- **Trade-offs**: Very similar to Option 1, may have marginal differences in regional pricing or feature availability.
- **Best For**: Teams already invested in this provider's ecosystem, multi-cloud strategies."""
            elif i == 3:
                response += f"""Strong compute-focused option with different resource allocation.
- **When to Choose**: For CPU-intensive workloads that need more processing power than storage or memory.
- **Trade-offs**: May cost slightly more but provides better compute performance for parallel processing tasks.
- **Best For**: Data processing pipelines, compilation servers, computational workloads."""
            elif i == 4:
                response += f"""Memory-optimized configuration ideal for specific use cases.
- **When to Choose**: Applications requiring higher RAM allocation, in-memory databases, caching layers.
- **Trade-offs**: Higher memory-to-CPU ratio, may be oversized for standard web applications.
- **Best For**: Redis, Memcached, in-memory analytics, large dataset processing."""
            elif i == 5:
                response += f"""Budget-conscious option maintaining solid performance standards.
- **When to Choose**: Cost optimization is the primary concern while maintaining acceptable performance.
- **Trade-offs**: Lower resource allocation but proportionally lower cost, good value for less demanding workloads.
- **Best For**: Development environments, low-traffic applications, cost-sensitive projects."""
            
            response += f"""
- **Pricing**: {rec_price}
- **Resources**: {rec_compute}
- **Security**: {rec_security}

"""
        
        # Add final recommendation guide
        response += f"""---

## 💡 FINAL RECOMMENDATION GUIDE

### Default Choice: Option 1 ({best_name})
Choose this for the best overall balance of performance, reliability, and cost-effectiveness. With a Hybrid Score of {best_score}, it represents the mathematically optimal solution for your requirements.

### Alternative Scenarios:

**Choose Option 2 if:**
- You have existing workloads on that provider
- You need specific provider features or certifications
- Regional pricing favors this alternative

**Choose Option 3 if:**
- CPU performance is your top priority
- You run compute-intensive batch processing
- Parallel processing workloads are primary use case

**Choose Option 4 if:**
- Memory-intensive applications (databases, caching)
- Large dataset in-memory processing required
- Application architecture demands high RAM

**Choose Option 5 if:**
- Budget constraints are critical
- Lower resource requirements are acceptable
- Development/testing non-production use

### Quick Selection Guide:
- **🏆 Best Overall**: Option 1 - Optimal balance for most workloads
- **💰 Best Value**: Option 5 - Maximum cost efficiency
- **⚡ Best Performance**: Option 3 - Highest compute power
- **🧠 Best for Memory**: Option 4 - Maximum RAM allocation
- **🔄 Best for Migration**: Option 2 - Ecosystem compatibility

All recommendations comply with your ${budget:.4f}/hour budget constraint and are deployed in your specified {region} region."""
        
        return response

    def generate_quick_summary(self, best_option: Dict) -> str:
        """
        Generate a quick one-line summary of the best recommendation
        
        Args:
            best_option: Dictionary containing best recommendation details
            
        Returns:
            Quick summary string
        """
        
        provider = best_option.get('provider', 'N/A')
        instance = best_option.get('instance_type', 'N/A')
        price = best_option.get('price_per_hour', 0)
        vcpu = best_option.get('vCPU', 0)
        ram = best_option.get('RAM_GB', 0)
        score = best_option.get('hybrid_score', best_option.get('topsis_score', 0))
        
        return (
            f"🏆 Best Choice: {provider} {instance} - "
            f"{vcpu} vCPU, {ram} GB RAM at ${price:.4f}/hour "
            f"(Hybrid Score: {score:.4f})"
        )

    def explain_topsis_score(self, score: float) -> str:
        """
        Explain what a Hybrid Score means in simple terms
        
        Args:
            score: Hybrid Score (0-1)
            
        Returns:
            Explanation string
        """
        
        if score >= 0.9:
            return "🌟 Exceptional (0.90-1.00) - Significantly outperforms all alternatives"
        elif score >= 0.8:
            return "⭐ Excellent (0.80-0.89) - Strong performance across all criteria"
        elif score >= 0.7:
            return "✅ Very Good (0.70-0.79) - Well-balanced with good overall performance"
        elif score >= 0.6:
            return "👍 Good (0.60-0.69) - Solid choice meeting most requirements"
        elif score >= 0.5:
            return "➖ Moderate (0.50-0.59) - Acceptable with some trade-offs"
        else:
            return "⚠️ Basic (0.00-0.49) - Meets minimum requirements only"


# Testing function
def test_llm_module():
    """Test the LLM module with Groq API"""
    
    print("="*60)
    print("TESTING GROQ API (LLaMA) LLM MODULE")
    print("="*60)
    
    # Create sample recommendations
    sample_data = pd.DataFrame([
        {
            'provider': 'AWS',
            'instance_type': 't3.micro',
            'region': 'us-east-1',
            'price_per_hour': 0.0530,
            'vCPU': 2,
            'RAM_GB': 1.0,
            'storage_GB': 20,
            'security_score': 90,
            'performance': 85.2,
            'availability': 100,
            'latency': 1.17,
            'topsis_score': 0.8745,
            'network_bandwidth': 'Standard',
            'bandwidth_score': 7
        },
        {
            'provider': 'AWS',
            'instance_type': 't3.nano',
            'region': 'us-east-1',
            'price_per_hour': 0.0475,
            'vCPU': 2,
            'RAM_GB': 0.5,
            'storage_GB': 10,
            'security_score': 90,
            'performance': 75.1,
            'availability': 100,
            'latency': 1.33,
            'topsis_score': 0.8234,
            'network_bandwidth': 'Standard',
            'bandwidth_score': 7
        }
    ])
    
    # Create LLM recommender
    llm = LLMRecommender()
    
    # Build prompt
    user_prefs = {
        'budget': 0.2,
        'region': 'us-east-1',
        'raw_weights': [0.3, 0.2, 0.2, 0.15, 0.15]
    }
    
    dataset_stats = {
        'total_instances': 3000,
        'providers': ['AWS', 'Azure', 'GCP'],
        'regions': 45
    }
    
    print("\n📝 Building prompt...")
    prompt = llm.build_prompt(user_prefs, sample_data, dataset_stats)
    
    print("🤖 Getting LLaMA explanation via Groq API...")
    explanation = llm.get_explanation(prompt)
    
    print("\n" + "="*60)
    print("GENERATED EXPLANATION:")
    print("="*60)
    print(explanation)
    print("="*60)
    
    # Test utilities
    best_option = sample_data.iloc[0].to_dict()
    summary = llm.generate_quick_summary(best_option)
    score_explanation = llm.explain_topsis_score(0.8745)
    
    print(f"\n📊 Quick Summary: {summary}")
    print(f"📈 Score Meaning: {score_explanation}")
    print("\n✅ Test completed successfully!")


if __name__ == "__main__":
    test_llm_module()
