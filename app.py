import streamlit as st
import joblib
import pandas as pd
import re
import string
import requests
import urllib.request
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from urllib.error import URLError, HTTPError

# Page configuration
st.set_page_config(
    page_title="News Detection",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Navigation
pages = {
    "Home": "🏠",
    "Verify": "🔍",
    "Learn": "📚",
    "About": "ℹ️"
}

# Initialize selected_page from session state
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Home"
selected_page = st.session_state.selected_page

# Sidebar navigation
st.sidebar.title("📰 News Detection")
st.sidebar.markdown("---")

# Update selected_page from sidebar selection
sidebar_selection = st.sidebar.radio(
    "Navigation",
    list(pages.keys()),
    format_func=lambda x: f"{pages[x]} {x}",
    index=list(pages.keys()).index(selected_page) if selected_page in pages else 0
)

# Update session state when sidebar changes
if sidebar_selection != selected_page:
    st.session_state.selected_page = sidebar_selection
    selected_page = sidebar_selection

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Links")
st.sidebar.markdown("[Home](/)")
st.sidebar.markdown("[Verify News](/verify)")
st.sidebar.markdown("[Learn](/learn)")
st.sidebar.markdown("[About](/about)")

st.sidebar.markdown("---")
st.sidebar.markdown("**© 2026 News Detection AI**")
st.sidebar.markdown("Empowering people to identify and combat misinformation.")

# Load ML model and vectorizer
try:
    vectorizer = joblib.load("vectorizer.jb")
    model = joblib.load("lr_model.jb")
    model_loaded = True
except FileNotFoundError:
    st.error("❌ Model files not found. Please ensure `vectorizer.jb` and `lr_model.jb` are available in the workspace.")
    model_loaded = False
    st.stop()

# Utility functions
def clean_text(text):
    text = text.lower()
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\\W", " ", text)
    text = re.sub(r"https?:://\S+|www\.\S+", "", text)
    text = re.sub(r"<.*?>+", "", text)
    text = re.sub(r"[%s]" % re.escape(string.punctuation), "", text)
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"\w*\d\w*", "", text)
    return text.strip()

def extract_article_text(url: str) -> str | None:
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        article_tag = soup.find("article")
        paragraphs = article_tag.find_all("p") if article_tag else soup.find_all("p")
        text = " ".join(p.get_text(separator=" ", strip=True) for p in paragraphs if p.get_text(strip=True))
        if not text:
            for meta in soup.find_all("meta"):
                name = meta.get("name", "") or meta.get("property", "")
                if name.lower() in ("description", "og:description", "twitter:description"):
                    text = meta.get("content", "").strip()
                    if text:
                        break
        return text.strip() if text else None
    except requests.RequestException:
        return None

# Session state initialization
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "history" not in st.session_state:
    st.session_state.history = []

# Beautiful Navigation Header
st.markdown("""
<style>
.nav-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    z-index: 1000;
    padding: 1rem 0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}
.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2rem;
}
.nav-brand {
    font-size: 1.8rem;
    font-weight: 900;
    color: white;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
}
.nav-brand:hover {
    color: #e8f2ff;
    text-decoration: none;
}
.nav-menu {
    display: flex;
    gap: 2rem;
    align-items: center;
}
.nav-link {
    color: white;
    text-decoration: none;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    border-radius: 50px;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    position: relative;
    cursor: pointer;
    border: none;
    background: transparent;
}
.nav-link:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}
.nav-link.active {
    background: rgba(255, 255, 255, 0.2);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}
.nav-link.active::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 50%;
    transform: translateX(-50%);
    width: 30px;
    height: 3px;
    background: white;
    border-radius: 2px;
}
.nav-cta {
    background: white;
    color: #667eea;
    padding: 0.75rem 1.5rem;
    border-radius: 50px;
    text-decoration: none;
    font-weight: 700;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    border: none;
}
.nav-cta:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
    background: #f8f9ff;
}
.page-content {
    margin-top: 100px;
}
@media (max-width: 768px) {
    .nav-container {
        padding: 0 1rem;
    }
    .nav-menu {
        gap: 1rem;
    }
    .nav-link {
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
    }
    .nav-brand {
        font-size: 1.5rem;
    }
}
</style>
""", unsafe_allow_html=True)

# Navigation buttons
st.markdown("""
<style>
.nav-row {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}
.nav-brand-btn {
    background: transparent !important;
    border: none !important;
    color: white !important;
    font-size: 1.5rem !important;
    font-weight: 900 !important;
    cursor: pointer !important;
    padding: 0.5rem 1rem !important;
    border-radius: 10px !important;
    transition: all 0.3s ease !important;
}
.nav-brand-btn:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    transform: translateY(-2px) !important;
}
.nav-btn {
    background: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    color: white !important;
    padding: 0.75rem 1.5rem !important;
    border-radius: 50px !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    margin: 0 0.25rem !important;
}
.nav-btn:hover {
    background: rgba(255, 255, 255, 0.2) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
}
.nav-btn-active {
    background: rgba(255, 255, 255, 0.3) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
}
.nav-cta-btn {
    background: white !important;
    color: #667eea !important;
    border: none !important;
    padding: 0.75rem 1.5rem !important;
    border-radius: 50px !important;
    font-weight: 700 !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
}
.nav-cta-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2) !important;
    background: #f8f9ff !important;
}
</style>
""", unsafe_allow_html=True)

nav_cols = st.columns([2, 1, 1, 1, 1, 2])
with nav_cols[0]:
    if st.button("📰 News Detection", key="brand", help="Go to Home", 
                 use_container_width=True):
        st.session_state.selected_page = "Home"
        st.rerun()
with nav_cols[1]:
    button_class = "nav-btn-active" if selected_page == "Home" else "nav-btn"
    if st.button("🏠 Home", key="nav_home", help="Go to Home", 
                 use_container_width=True):
        st.session_state.selected_page = "Home"
        st.rerun()
with nav_cols[2]:
    button_class = "nav-btn-active" if selected_page == "Verify" else "nav-btn"
    if st.button("🔍 Verify", key="nav_verify", help="Verify News", 
                 use_container_width=True):
        st.session_state.selected_page = "Verify"
        st.rerun()
with nav_cols[3]:
    button_class = "nav-btn-active" if selected_page == "Learn" else "nav-btn"
    if st.button("📚 Learn", key="nav_learn", help="Learn About Fake News", 
                 use_container_width=True):
        st.session_state.selected_page = "Learn"
        st.rerun()
with nav_cols[4]:
    button_class = "nav-btn-active" if selected_page == "About" else "nav-btn"
    if st.button("ℹ️ About", key="nav_about", help="About Us", 
                 use_container_width=True):
        st.session_state.selected_page = "About"
        st.rerun()
with nav_cols[5]:
    if st.button("🚀 Get Started", key="nav_cta", help="Start Verifying News", 
                 use_container_width=True):
        st.session_state.selected_page = "Verify"
        st.rerun()

# Update selected_page from session state
if "selected_page" in st.session_state:
    selected_page = st.session_state.selected_page

st.markdown("""
<div class="nav-spacer"></div>
<style>
.nav-spacer { margin-top: 80px; }
</style>
""", unsafe_allow_html=True)

# Main content based on selected page
if selected_page == "Home":
    st.markdown('<div class="page-content">', unsafe_allow_html=True)
    # HOME PAGE CONTENT
    st.markdown("""
    <style>
    .hero-section {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 3rem;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        margin-bottom: 1rem;
    }
    .hero-subtitle {
        font-size: 1.3rem;
        margin-bottom: 2rem;
        opacity: 0.9;
    }
    .cta-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
    }
    .cta-button {
        background: white;
        color: #667eea;
        padding: 1rem 2rem;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 700;
        display: inline-block;
        transition: transform 0.2s;
    }
    .cta-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    .section {
        padding: 3rem 0;
        border-bottom: 1px solid #eee;
    }
    .section-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 2rem;
        text-align: center;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
    }
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        text-align: center;
    }
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .feature-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .recent-checks {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
    }
    .check-card {
        background: white;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .check-status {
        padding: 0.5rem 1rem;
        font-weight: 700;
        text-align: center;
    }
    .check-status.false {
        background: #fee;
        color: #c92a2a;
    }
    .check-status.misleading {
        background: #fff3cd;
        color: #856404;
    }
    .check-status.true {
        background: #d4edda;
        color: #155724;
    }
    .check-content {
        padding: 1.5rem;
    }
    .check-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .check-source {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    .check-description {
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    .read-more {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Detect Fake News with Confidence</h1>
        <p class="hero-subtitle">Our AI-powered platform helps you identify misinformation and verify the authenticity of news articles and information online.</p>
        <div class="cta-buttons">
            <a href="/verify" class="cta-button">Verify News Now</a>
            <a href="/learn" class="cta-button">Learn More</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # How It Works Section
    st.markdown("""
    <div class="section">
        <h2 class="section-title">How News Detection AI Works</h2>
        <p style="text-align: center; font-size: 1.1rem; color: #666; margin-bottom: 3rem;">
            Our platform uses advanced algorithms and fact-checking techniques to help you identify misinformation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature Grid
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h3 class="feature-title">Content Analysis</h3>
            <p>Our system analyzes the content of news articles for signs of misinformation. We check for sensationalist language, clickbait headlines, and other red flags that might indicate fake news.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🏢</div>
            <h3 class="feature-title">Source Credibility</h3>
            <p>We evaluate the credibility of news sources based on their track record. Our database contains information about thousands of news sources, helping you identify trustworthy outlets.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📚</div>
            <h3 class="feature-title">Educational Resources</h3>
            <p>Learn how to spot fake news and improve your media literacy skills. Access guides, tutorials, and tips to help you become better at identifying misinformation on your own.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Recent Fact Checks Section
    st.markdown("""
    <div class="section">
        <h2 class="section-title">Recent Fact Checks</h2>
        <p style="text-align: center; font-size: 1.1rem; color: #666; margin-bottom: 3rem;">
            See examples of recent news stories we've analyzed and fact-checked.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Recent Checks Grid
    st.markdown("""
    <div class="recent-checks">
        <div class="check-card">
            <div class="check-status false">False</div>
            <div class="check-content">
                <h4 class="check-title">Climate Change Hoax Exposed</h4>
                <div class="check-source">Originally published on ClimateSkeptic.com</div>
                <p class="check-description">This article makes false claims about climate data and misrepresents scientific consensus on climate change.</p>
                <a href="#" class="read-more">Read Full Analysis →</a>
            </div>
        </div>
        <div class="check-card">
            <div class="check-status misleading">Misleading</div>
            <div class="check-content">
                <h4 class="check-title">Senator's Statement Taken Out of Context</h4>
                <div class="check-source">Originally published on PoliticsDaily.net</div>
                <p class="check-description">While the quote is real, it was taken out of context and misrepresents the senator's full statement on the issue.</p>
                <a href="#" class="read-more">Read Full Analysis →</a>
            </div>
        </div>
        <div class="check-card">
            <div class="check-status true">True</div>
            <div class="check-content">
                <h4 class="check-title">New Study Shows Promise for Cancer Treatment</h4>
                <div class="check-source">Originally published on MedicalJournal.org</div>
                <p class="check-description">This article accurately reports on a peer-reviewed study published in a reputable medical journal.</p>
                <a href="#" class="read-more">Read Full Analysis →</a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA Section
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%); border-radius: 20px; margin: 3rem 0;">
        <h2 style="font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem;">Ready to Fight Misinformation?</h2>
        <p style="font-size: 1.2rem; color: #666; margin-bottom: 2rem;">Start verifying news articles and information today with our easy-to-use platform.</p>
        <a href="/verify" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 2rem; border-radius: 50px; text-decoration: none; font-weight: 700; display: inline-block; transition: transform 0.2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">Get Started Now</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

elif selected_page == "Verify":
    st.markdown('<div class="page-content">', unsafe_allow_html=True)
    # VERIFY PAGE CONTENT
    st.markdown("""
    <style>
    .verify-hero {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 3rem;
    }
    .verify-title {
        font-size: 3rem;
        font-weight: 900;
        margin-bottom: 1rem;
    }
    .verify-subtitle {
        font-size: 1.2rem;
        margin-bottom: 2rem;
        opacity: 0.9;
    }
    .tool-section {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 2rem 0;
    }
    .tool-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-align: center;
    }
    .tool-description {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .tab-content {
        margin-top: 2rem;
    }
    .input-section {
        background: #f8f9ff;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
    }
    .example-url {
        background: #e8f2ff;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-family: monospace;
        color: #667eea;
    }
    .result-true {
        background: linear-gradient(135deg, rgba(47, 158, 68, 0.1), rgba(47, 158, 68, 0.2));
        border: 2px solid #2f9e44;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
    }
    .result-false {
        background: linear-gradient(135deg, rgba(201, 42, 42, 0.1), rgba(201, 42, 42, 0.2));
        border: 2px solid #c92a2a;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="verify-hero">
        <h1 class="verify-title">AI-Powered Verification</h1>
        <p class="verify-subtitle">Enter a URL or paste text to analyze its credibility with our secure AI backend.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="tool-section">
        <h2 class="tool-title">News Verification Tool</h2>
        <p class="tool-description">Our AI-powered system will analyze the content and provide a credibility assessment.</p>
    </div>
    """, unsafe_allow_html=True)

    # Tabs for URL and Text analysis
    tab1, tab2 = st.tabs(["📎 Analyze URL", "📝 Analyze Text"])

    with tab1:
        st.markdown("""
        <div class="input-section">
            <h3 style="margin-bottom: 1rem;">Enter Article URL</h3>
            <div class="example-url">Example: https://example.com/news/article</div>
        </div>
        """, unsafe_allow_html=True)
        
        url_input = st.text_input("Article URL", placeholder="https://example.com/news/article", key="url_input")
        
        if st.button("🔍 Analyze URL", use_container_width=True):
            if url_input:
                with st.spinner("Extracting article text..."):
                    extracted_text = extract_article_text(url_input.strip())
                
                if extracted_text and len(extracted_text.strip()) > 50:
                    with st.spinner("Analyzing content..."):
                        cleaned_input = clean_text(extracted_text)
                        transform_input = vectorizer.transform([cleaned_input])
                        prediction = model.predict(transform_input)[0]
                        prob = model.predict_proba(transform_input)[0]
                        confidence = max(prob) * 100
                        label = "TRUE" if prediction == 1 else "FALSE"
                        
                        st.session_state.last_result = {
                            "label": label,
                            "confidence": confidence,
                            "probabilities": prob,
                            "transform_input": transform_input,
                            "source": "URL",
                            "url": url_input
                        }
                        
                        st.session_state.history.append({
                            "Preview": extracted_text[:120].strip() + ("..." if len(extracted_text) > 120 else ""),
                            "Source": "URL",
                            "Result": label,
                            "Confidence": f"{confidence:.2f}%",
                            "URL": url_input
                        })
                        
                        st.success("✅ Analysis complete!")
                        st.rerun()
                else:
                    st.error("❌ Could not extract sufficient text from URL. Please try pasting the article text directly.")
            else:
                st.error("❌ Please enter a URL")

    with tab2:
        st.markdown("""
        <div class="input-section">
            <h3 style="margin-bottom: 1rem;">Paste Article Text</h3>
            <p style="color: #666;">Copy and paste the news article content you want to verify.</p>
        </div>
        """, unsafe_allow_html=True)
        
        text_input = st.text_area("Article Text", height=200, placeholder="Paste your news article here...", key="text_input")
        
        if st.button("🔍 Analyze Text", use_container_width=True):
            if text_input and len(text_input.strip()) > 10:
                with st.spinner("Analyzing content..."):
                    cleaned_input = clean_text(text_input)
                    transform_input = vectorizer.transform([cleaned_input])
                    prediction = model.predict(transform_input)[0]
                    prob = model.predict_proba(transform_input)[0]
                    confidence = max(prob) * 100
                    label = "TRUE" if prediction == 1 else "FALSE"
                    
                    st.session_state.last_result = {
                        "label": label,
                        "confidence": confidence,
                        "probabilities": prob,
                        "transform_input": transform_input,
                        "source": "Text",
                        "text_preview": text_input[:200] + ("..." if len(text_input) > 200 else "")
                    }
                    
                    st.session_state.history.append({
                        "Preview": text_input[:120].strip() + ("..." if len(text_input) > 120 else ""),
                        "Source": "Text",
                        "Result": label,
                        "Confidence": f"{confidence:.2f}%"
                    })
                    
                    st.success("✅ Analysis complete!")
                    st.rerun()
            else:
                st.error("❌ Please enter at least 10 characters of text")

    # Display results if available
    if st.session_state.last_result:
        result = st.session_state.last_result
        label_class = "true" if result['label'] == "TRUE" else "false"
        
        st.markdown("---")
        st.markdown("## 🎯 Analysis Result")
        
        # Result badge
        if result['label'] == "TRUE":
            st.success(f"✅ **TRUE NEWS** - This article appears to be legitimate with {result['confidence']:.1f}% confidence")
        else:
            st.error(f"❌ **FALSE NEWS** - This article appears to be fake/misleading with {result['confidence']:.1f}% confidence")
        
        # Confidence breakdown
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📊 Confidence Breakdown")
            probs_df = pd.DataFrame({
                "Category": ["FALSE", "TRUE"],
                "Probability": result["probabilities"]
            })
            st.bar_chart(probs_df.set_index("Category"))
        
        with col2:
            st.markdown("### 📋 Analysis Details")
            st.markdown(f"**Source:** {result.get('source', 'Unknown')}")
            if 'url' in result:
                st.markdown(f"**URL:** {result['url']}")
            st.markdown(f"**Confidence:** {result['confidence']:.2f}%")
            st.markdown(f"**Result:** {result['label']}")

    # Recent History
    if st.session_state.history:
        st.markdown("---")
        st.markdown("## 📈 Recent Analysis History")
        history_df = pd.DataFrame(st.session_state.history[-5:])  # Show last 5
        st.dataframe(history_df, use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)

elif selected_page == "Learn":
    st.markdown('<div class="page-content">', unsafe_allow_html=True)
    # LEARN PAGE CONTENT
    st.markdown("""
    <style>
    .learn-hero {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 3rem;
    }
    .learn-title {
        font-size: 3rem;
        font-weight: 900;
        margin-bottom: 1rem;
    }
    .learn-subtitle {
        font-size: 1.2rem;
        margin-bottom: 2rem;
        opacity: 0.9;
    }
    .content-section {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 2rem 0;
    }
    .section-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 2rem;
        color: #333;
    }
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    .info-card {
        background: #f8f9ff;
        padding: 2rem;
        border-radius: 15px;
        border-left: 4px solid #667eea;
    }
    .info-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #333;
    }
    .impact-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    .impact-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .impact-title {
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="learn-hero">
        <h1 class="learn-title">Learn to Spot Fake News</h1>
        <p class="learn-subtitle">Improve your media literacy skills and learn how to identify misinformation online.</p>
    </div>
    """, unsafe_allow_html=True)

    # Tabs for different learning sections
    tab1, tab2, tab3 = st.tabs(["📖 Basics", "🛠️ Techniques", "📚 Resources"])

    with tab1:
        st.markdown("""
        <div class="content-section">
            <h2 class="section-title">What is Fake News?</h2>
            <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 2rem;">
                Understanding misinformation and disinformation in the digital age. Fake news refers to false or misleading information presented as legitimate news. It's designed to influence public opinion, generate clicks, or advance specific agendas. Unlike errors in reporting, fake news is often deliberately created to deceive.
            </p>
            
            <div class="info-grid">
                <div class="info-card">
                    <h3 class="info-title">📢 Misinformation</h3>
                    <p>False information that is spread regardless of intent to mislead. The person sharing it may believe it to be true.</p>
                </div>
                <div class="info-card">
                    <h3 class="info-title">🎭 Disinformation</h3>
                    <p>Deliberately false information created and spread with the intention to deceive or cause harm.</p>
                </div>
            </div>
        </div>
        
        <div class="content-section">
            <h2 class="section-title">Why Fake News Spreads</h2>
            <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 2rem;">
                Understanding the psychology and technology behind viral misinformation. Fake news spreads rapidly due to several factors, including social media algorithms, confirmation bias, and emotional triggers.
            </p>
            
            <div class="info-grid">
                <div class="info-card">
                    <h3 class="info-title">🤖 Social Media Algorithms</h3>
                    <p>Algorithms prioritize engaging content, often amplifying sensational or emotional posts regardless of accuracy.</p>
                </div>
                <div class="info-card">
                    <h3 class="info-title">🧠 Confirmation Bias</h3>
                    <p>People tend to believe and share information that aligns with their existing beliefs and worldviews.</p>
                </div>
                <div class="info-card">
                    <h3 class="info-title">😱 Emotional Triggers</h3>
                    <p>Content that evokes strong emotions like anger, fear, or outrage spreads more quickly than neutral facts.</p>
                </div>
                <div class="info-card">
                    <h3 class="info-title">🏠 Echo Chambers</h3>
                    <p>People surrounded by like-minded individuals are less exposed to diverse viewpoints and critical thinking.</p>
                </div>
            </div>
        </div>
        
        <div class="content-section">
            <h2 class="section-title">The Impact of Fake News</h2>
            <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 2rem;">
                How misinformation affects society and individuals. Fake news has real-world consequences that extend beyond the digital realm.
            </p>
            
            <h3 style="color: #667eea; margin: 2rem 0 1rem;">Social Impacts</h3>
            <div class="impact-grid">
                <div class="impact-card">
                    <div class="impact-title">🏛️ Erodes Trust</div>
                    <p>Erodes trust in legitimate media and institutions</p>
                </div>
                <div class="impact-card">
                    <div class="impact-title">⚖️ Polarization</div>
                    <p>Increases political polarization and division</p>
                </div>
                <div class="impact-card">
                    <div class="impact-title">🗳️ Democracy</div>
                    <p>Undermines democratic processes and elections</p>
                </div>
                <div class="impact-card">
                    <div class="impact-title">🤔 Confusion</div>
                    <p>Creates confusion about important issues</p>
                </div>
            </div>
            
            <h3 style="color: #667eea; margin: 2rem 0 1rem;">Individual Impacts</h3>
            <div class="impact-grid">
                <div class="impact-card">
                    <div class="impact-title">🤔 Poor Decisions</div>
                    <p>Leads to poor decision-making based on false information</p>
                </div>
                <div class="impact-card">
                    <div class="impact-title">😰 Anxiety</div>
                    <p>Creates unnecessary fear or anxiety</p>
                </div>
                <div class="impact-card">
                    <div class="impact-title">💔 Relationships</div>
                    <p>Damages personal relationships and social bonds</p>
                </div>
                <div class="impact-card">
                    <div class="impact-title">🧠 Critical Thinking</div>
                    <p>Reduces critical thinking skills over time</p>
                </div>
            </div>
            
            <div style="background: #fff3cd; padding: 2rem; border-radius: 15px; margin: 2rem 0; border-left: 4px solid #856404;">
                <h3 style="color: #856404; margin-bottom: 1rem;">📊 Case Study: Health Misinformation</h3>
                <p>During the COVID-19 pandemic, health misinformation led to people taking unproven treatments, avoiding vaccines, and ignoring public health guidelines. This directly contributed to preventable illnesses and deaths.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("""
        <div class="content-section">
            <h2 class="section-title">Complete Guide to Detecting Fake News</h2>
            <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 2rem;">
                Detecting false news involves checking the source, verifying facts, analyzing content critically, and using digital tools to confirm authenticity. Follow these comprehensive steps to identify and avoid misinformation.
            </p>
            
            <div style="background: #fff3cd; padding: 2rem; border-radius: 15px; margin: 2rem 0; border-left: 4px solid #856404;">
                <h3 style="color: #856404; margin-bottom: 1rem;">🎯 Key Steps to Identify Fake News</h3>
            </div>
            
            <div class="info-grid">
                <div class="info-card">
                    <h3 class="info-title">🔍 1. Check the Source</h3>
                    <p>Examine the website or publisher. Look for unusual domain names, spelling errors, or unfamiliar extensions. Trusted news outlets usually have clear editorial standards and an About Us section explaining their mission and credibility.</p>
                    <div style="font-size: 0.9rem; color: #667eea; margin-top: 0.5rem;"><strong>Source:</strong> Kaspersky</div>
                </div>
                <div class="info-card">
                    <h3 class="info-title">👤 2. Verify the Author</h3>
                    <p>Research the author's credentials and reputation. Ensure they have expertise in the topic and consider their potential biases or motivations.</p>
                    <div style="font-size: 0.9rem; color: #667eea; margin-top: 0.5rem;"><strong>Source:</strong> Kaspersky</div>
                </div>
                <div class="info-card">
                    <h3 class="info-title">🔗 3. Cross-Check with Other Sources</h3>
                    <p>Confirm whether reputable news organizations are reporting the same story. If multiple credible sources cover it, the information is more likely to be accurate.</p>
                    <div style="font-size: 0.9rem; color: #667eea; margin-top: 0.5rem;"><strong>Source:</strong> Kaspersky</div>
                </div>
                <div class="info-card">
                    <h3 class="info-title">📝 4. Analyze the Content Critically</h3>
                    <p>Be cautious of sensationalist headlines, emotionally charged language, or content designed to provoke fear or anger. Ask why the story was written and whether it promotes a particular agenda.</p>
                    <div style="font-size: 0.9rem; color: #667eea; margin-top: 0.5rem;"><strong>Source:</strong> Australian Conservation Foundation</div>
                </div>
                <div class="info-card">
                    <h3 class="info-title">🖼️ 5. Fact-Check Images and Videos</h3>
                    <p>Use reverse image searches (Google Images, TinEye) to verify photos. Look for signs of manipulation such as inconsistent lighting, unnatural movements, or mismatched audio in videos.</p>
                    <div style="font-size: 0.9rem; color: #667eea; margin-top: 0.5rem;"><strong>Source:</strong> eSafety Commissioner</div>
                </div>
                <div class="info-card">
                    <h3 class="info-title">🎣 6. Identify Clickbait and Bias</h3>
                    <p>Headlines that exaggerate or misrepresent the story are often clickbait. Consider the poster’s or platform's biases and whether the content omits important context.</p>
                    <div style="font-size: 0.9rem; color: #667eea; margin-top: 0.5rem;"><strong>Source:</strong> NSW Government</div>
                </div>
                <div class="info-card">
                    <h3 class="info-title">🏷️ 7. Understand Types of False Content</h3>
                    <p>Distinguish between misinformation (false information shared unintentionally) and disinformation (deliberately misleading content). Malinformation involves true information presented out of context to cause harm.</p>
                    <div style="font-size: 0.9rem; color: #667eea; margin-top: 0.5rem;"><strong>Source:</strong> Freedom Forum</div>
                </div>
                <div class="info-card">
                    <h3 class="info-title">🧠 8. Maintain a Critical Mindset</h3>
                    <p>Pause before sharing content, especially if it triggers strong emotions. Question the evidence, reasoning, and whether alternative perspectives are included.</p>
                    <div style="font-size: 0.9rem; color: #667eea; margin-top: 0.5rem;"><strong>Source:</strong> eSafety Commissioner</div>
                </div>
                <div class="info-card">
                    <h3 class="info-title">🛠️ 9. Use Fact-Checking Tools</h3>
                    <p>Websites like Snopes, FactCheck.org, and local fact-checking services can help verify claims and provide context for suspicious stories.</p>
                    <div style="font-size: 0.9rem; color: #667eea; margin-top: 0.5rem;"><strong>Source:</strong> Kaspersky</div>
                </div>
                <div class="info-card">
                    <h3 class="info-title">📚 10. Educate Yourself on Digital Literacy</h3>
                    <p>Understanding how algorithms, social media feeds, and online advertising influence the spread of information can help you recognize patterns of manipulation and avoid being misled.</p>
                    <div style="font-size: 0.9rem; color: #667eea; margin-top: 0.5rem;"><strong>Source:</strong> NSW Government</div>
                </div>
            </div>
            
            <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); padding: 2rem; border-radius: 15px; margin: 2rem 0; border-left: 4px solid #667eea;">
                <h3 style="color: #667eea; margin-bottom: 1rem;">💡 Pro Tip</h3>
                <p style="margin: 0;">By combining these strategies—source verification, cross-checking, critical analysis, and digital tools—you can significantly reduce the risk of believing or sharing false news.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown("""
        <div class="content-section">
            <h2 class="section-title">Educational Resources</h2>
            <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 2rem;">
                Access guides, tools, and additional resources to improve your media literacy.
            </p>
            
            <div class="info-grid">
                <div class="info-card">
                    <h3 class="info-title">📖 Media Literacy Guide</h3>
                    <p>Comprehensive guide covering all aspects of media literacy and critical thinking.</p>
                </div>
                <div class="info-card">
                    <h3 class="info-title">🔬 Research Papers</h3>
                    <p>Academic research on misinformation, fact-checking, and media psychology.</p>
                </div>
                <div class="info-card">
                    <h3 class="info-title">🎥 Educational Videos</h3>
                    <p>Video tutorials and documentaries about identifying and combating fake news.</p>
                </div>
                <div class="info-card">
                    <h3 class="info-title">🛠️ Fact-Checking Tools</h3>
                    <p>Additional tools and resources for verifying information online.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

elif selected_page == "About":
    st.markdown('<div class="page-content">', unsafe_allow_html=True)
    # ABOUT PAGE CONTENT
    st.markdown("""
    <style>
    .about-hero {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 3rem;
    }
    .about-title {
        font-size: 3rem;
        font-weight: 900;
        margin-bottom: 1rem;
    }
    .about-subtitle {
        font-size: 1.2rem;
        margin-bottom: 2rem;
        opacity: 0.9;
    }
    .content-section {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 2rem 0;
    }
    .section-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 2rem;
        color: #333;
    }
    .story-content {
        font-size: 1.1rem;
        line-height: 1.6;
        margin-bottom: 2rem;
    }
    .mission-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    .mission-card {
        background: #f8f9ff;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        border-left: 4px solid #667eea;
    }
    .mission-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .mission-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .team-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    .team-card {
        background: white;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        text-align: center;
    }
    .team-image {
        width: 100%;
        height: 200px;
        object-fit: cover;
    }
    .team-info {
        padding: 1.5rem;
    }
    .team-name {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .team-role {
        color: #667eea;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .contact-section {
        background: linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%);
        padding: 3rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
    }
    .contact-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 1rem;
    }
    .contact-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 700;
        display: inline-block;
        margin: 1rem;
        transition: transform 0.2s;
    }
    .contact-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="about-hero">
        <h1 class="about-title">About News Detection AI</h1>
        <p class="about-subtitle">Our mission is to combat misinformation and empower people with the tools to identify fake news.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="content-section">
        <h2 class="section-title">Our Story</h2>
        <p class="story-content">
            News Detection AI was founded in 2023 by a team of journalists, data scientists, and educators concerned about the rapid spread of misinformation in the digital age. We recognized that while technology has made it easier to spread fake news, it can also be harnessed to identify and combat it. Our platform combines human expertise with advanced algorithms to help users navigate the complex information landscape. Today, News Detection AI is used by individuals, educators, and organizations worldwide to verify information and improve media literacy.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="content-section">
        <h2 class="section-title">Our Mission</h2>
        <div class="mission-grid">
            <div class="mission-card">
                <div class="mission-icon">🛡️</div>
                <h3 class="mission-title">Combat Misinformation</h3>
                <p>We're committed to reducing the spread and impact of fake news by providing tools that help identify misleading content.</p>
            </div>
            <div class="mission-card">
                <div class="mission-icon">📚</div>
                <h3 class="mission-title">Promote Media Literacy</h3>
                <p>We believe in empowering people with the knowledge and skills to critically evaluate the information they encounter online.</p>
            </div>
            <div class="mission-card">
                <div class="mission-icon">📰</div>
                <h3 class="mission-title">Support Quality Journalism</h3>
                <p>We aim to highlight and promote credible, fact-based reporting that adheres to journalistic standards and ethics.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="content-section">
        <h2 class="section-title">Our Approach</h2>
        <h3 style="color: #667eea; margin: 2rem 0 1rem;">How We Verify Content</h3>
        <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 1rem;">
            Our verification process combines automated analysis with human expertise:
        </p>
        <ul style="font-size: 1.1rem; line-height: 1.6;">
            <li><strong>AI Analysis:</strong> Our algorithms examine content for patterns associated with misinformation.</li>
            <li><strong>Source Evaluation:</strong> We maintain a database of source credibility based on track record and transparency.</li>
            <li><strong>Cross-Referencing:</strong> We check claims against multiple reliable sources.</li>
            <li><strong>Expert Review:</strong> Our team of fact-checkers reviews complex or high-impact claims.</li>
        </ul>
        
        <h3 style="color: #667eea; margin: 2rem 0 1rem;">Our Commitment to Neutrality</h3>
        <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 1rem;">
            We are committed to political neutrality and objectivity in our assessments:
        </p>
        <ul style="font-size: 1.1rem; line-height: 1.6;">
            <li><strong>Transparent Methodology:</strong> Our verification process is fully documented and available for review.</li>
            <li><strong>Diverse Team:</strong> Our staff represents a range of political viewpoints and backgrounds.</li>
            <li><strong>Focus on Facts:</strong> We evaluate claims based on factual accuracy, not ideological alignment.</li>
            <li><strong>Correction Policy:</strong> We promptly correct any errors in our assessments.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="contact-section">
        <h2 class="contact-title">Contact Us</h2>
        <p style="font-size: 1.1rem; color: #666; margin-bottom: 2rem;">
            Have questions or feedback? We'd love to hear from you.
        </p>
        <a href="mailto:info@newsdetectionai.com" class="contact-button">Email Us</a>
        <a href="#" class="contact-button">Join Our Community</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**© 2026 News Detection AI**")
    st.markdown("All rights reserved.")
with col2:
    st.markdown("**Privacy Policy**")
    st.markdown("**Terms of Service**")
with col3:
    st.markdown("**Follow us:**")
    st.markdown("Twitter | Facebook | GitHub")
