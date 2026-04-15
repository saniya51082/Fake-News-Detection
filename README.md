# News Detection AI

An AI-powered web application for detecting fake news and verifying the authenticity of news articles using machine learning.

## Features

- 🏠 **Home Page** - Welcome and overview
- 🔍 **Verify Page** - AI-powered news detection (TRUE/FALSE results)
- 📚 **Learn Page** - Comprehensive fake news detection guide
- ℹ️ **About Page** - Mission and approach
- 🎨 **Beautiful Navigation** - Attractive header with page switching
- 📊 **Real-time Analysis** - ML model predictions with confidence scores

## Live Demo

Visit the live application at: [news-detection.streamlit.app](https://news-detection.streamlit.app)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/saniya51082/Fake-News-Detection.git
cd Fake-News-Detection
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. **Navigate** between pages using the top navigation bar
2. **Verify News** by entering URLs or pasting article text
3. **Learn** about fake news detection techniques
4. **Get Results** with confidence scores and analysis

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **ML Model**: Logistic Regression with TF-IDF
- **Data Processing**: BeautifulSoup, Requests
- **Deployment**: Streamlit Cloud

## Model Information

The application uses a trained Logistic Regression model to classify news articles as:
- **TRUE**: Legitimate news
- **FALSE**: Fake/misleading news

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Contact

For questions or feedback, please open an issue on GitHub.