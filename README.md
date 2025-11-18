# 📄 Meeting Document Generator

An AI-powered application that transforms video meeting recordings into professional, structured documentation. The system intelligently extracts key moments, transcribes speech, and generates comprehensive documents in multiple formats.

## 🎯 Overview

The Meeting Document Generator automates the documentation process by:
- **Intelligent Screenshot Extraction**: Captures key moments using multiple detection algorithms
- **Speech Transcription**: Converts audio to text using Azure Whisper or OpenAI Whisper
- **AI-Enhanced Analysis**: Uses OpenAI/Azure OpenAI to analyze content and generate insights
- **Professional Document Generation**: Creates PDF and DOCX documents with multiple templates
- **Cost Tracking**: Monitors and logs usage costs for all API calls

## ✨ Key Features

### Core Capabilities
- 🎬 **Video Processing**: Supports MP4, AVI, MOV, MKV formats
- 📸 **Smart Screenshot Detection**: 
  - Speech keyword triggers
  - Mouse cursor tracking
  - Scene change detection (SSIM)
  - AI-powered content analysis
  - Text change detection
- 🎤 **Speech Recognition**: 
  - Azure Whisper integration (primary)
  - OpenAI Whisper fallback
  - Parallel processing for performance
- 📝 **Document Types**:
  - Knowledge Transfer Documents
  - Meeting Summaries
  - User Stories
  - General Documentation
- 📊 **Advanced Features**:
  - Process flow diagrams (Mermaid)
  - Missing questions generation
  - PII detection and face blurring
  - Usage cost tracking and logging
  - Interactive diagram editing

## 🏗️ Architecture

The application follows a modular, layered architecture:

```
Frontend (Streamlit) → Document Generation → Processing Layer → Utilities
```

For detailed architecture documentation, see [architecture.md](architecture.md)

For file relationships and explanations, see [file_explanation_and_relation.md](file_explanation_and_relation.md)

## 📋 Prerequisites

- Python 3.8 or higher
- FFmpeg installed and in PATH
- Tesseract OCR (for text detection)
- Azure account (for Azure services) or OpenAI API key

## 🚀 Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd meeting-document-generator
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install system dependencies**

   **FFmpeg** (required for video/audio processing):
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # Windows: Download from https://ffmpeg.org/download.html
   ```

   **Tesseract OCR** (required for text detection):
   ```bash
   # macOS
   brew install tesseract
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   ```

   **Graphviz** (required for diagrams):
   ```bash
   # macOS
   brew install graphviz
   
   # Ubuntu/Debian
   sudo apt-get install graphviz
   ```

   **Node.js and Mermaid CLI** (required for Mermaid diagrams):
   ```bash
   # Install Node.js 18+
   curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
   sudo apt-get install -y nodejs
   
   # Install Mermaid CLI
   sudo npm install -g @mermaid-js/mermaid-cli
   ```

5. **Configure environment variables**

   Create a `.env` file in the project root:
   ```env
   # Azure OpenAI Configuration (Primary)
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your_azure_api_key
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_GPT_DEPLOYMENT_NAME=your_deployment_name
   
   # OpenAI Configuration (Fallback)
   OPENAI_API_KEY=your_openai_api_key
   
   # Azure Speech Services (Optional)
   AZURE_SPEECH_KEY=your_speech_key
   AZURE_SPEECH_REGION=your_speech_region
   
   # Azure Whisper Configuration
   AZURE_WHISPER_CLIENT_COST=0.006  # Cost per minute
   
   # Storage Configuration
   LOCAL_STORAGE_DIR=data/outputs
   USAGE_COST_BLOB_NAME=usage_cost_log.csv
   
   # Application Configuration
   BASE_URL=your_base_url  # For authentication (optional)
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```
   
   Or use the startup script:
   ```bash
   chmod +x startup.sh
   ./startup.sh
   ```

## 🐳 Docker Deployment

For Docker deployment, see [README.Docker.md](README.Docker.md)

Quick start with Docker:
```bash
docker-compose up -d
```

Access the application at `http://localhost:8501`

## 📖 Usage Guide

### Basic Workflow

1. **Upload Video**
   - Click "Upload Meeting Recording"
   - Select a video file (MP4, AVI, MOV, MKV)
   - Wait for upload to complete

2. **Enter Client Information**
   - Enter client name in the sidebar
   - This is required before processing

3. **Select Processing Mode**
   - **Basic**: Quick processing with essential features
   - **Advanced**: Comprehensive analysis with all detection methods

4. **Start Analysis**
   - Click "🚀 Start Analysis"
   - The system will:
     - Extract audio from video
     - Process frames for screenshot detection
     - Transcribe speech
     - Analyze content with AI
     - Generate screenshots at key moments

5. **Generate Documents**
   - Select document type:
     - 📚 Knowledge Transfer
     - 📝 Meeting Summary
     - 📖 User Stories
     - 📄 General Documentation
   - Choose format: PDF, DOCX, or Both
   - Configure advanced options:
     - Include Missing Questions
     - Include Process Maps
     - Include Screenshots
   - Click "🚀 Generate"

6. **Download Documents**
   - Navigate to "📄 Downloads" tab
   - Click download buttons for PDF or DOCX

### Processing Modes

#### Basic Mode
- ✅ Speech keyword detection
- ✅ Mouse tracking
- ✅ AI analysis (if available)
- ❌ Scene detection
- **Use Case**: Quick processing, smaller files

#### Advanced Mode
- ✅ Speech keyword detection
- ✅ Mouse tracking
- ✅ Scene detection (SSIM)
- ✅ AI analysis (if available)
- **Use Case**: Comprehensive analysis, detailed documentation

## 📁 Project Structure

```
meeting-document-generator/
├── app.py                          # Entry point
├── config/                         # Configuration files (YAML)
│   ├── app_config.yaml
│   ├── model_config.yaml
│   ├── whisper_config.yaml
│   └── logging_config.yaml
├── src/
│   ├── frontend/                   # Streamlit UI
│   │   └── streamlit_app.py
│   ├── document/                   # Document generation
│   │   ├── document_generator.py
│   │   ├── mermaid_integration.py
│   │   └── mermaid_editor.py
│   ├── processors/                 # Processing modules
│   │   ├── video/                  # Video processing
│   │   ├── audio/                  # Audio processing
│   │   ├── parallel/               # Parallel processing
│   │   └── utils/                  # Processor utilities
│   └── utils/                      # Core utilities
├── data/                           # Data storage
│   └── outputs/                    # Generated outputs
├── tests/                          # Test files
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker Compose config
└── requirements.txt                # Python dependencies
```

## 🔧 Configuration

### Configuration Files

All configuration is managed through YAML files in the `config/` directory:

- **app_config.yaml**: Application settings, storage paths
- **model_config.yaml**: LLM model configurations
- **whisper_config.yaml**: Whisper model settings
- **logging_config.yaml**: Logging configuration

### Environment Variables

Key environment variables (see `.env` file):
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key
- `OPENAI_API_KEY`: OpenAI API key (fallback)
- `AZURE_SPEECH_KEY`: Azure Speech Services key
- `LOCAL_STORAGE_DIR`: Storage directory path

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest tests/
```

## 📊 Monitoring and Logging

### Log Files
- `app.log`: Application logs (rotated daily)
- `usage.log`: Usage logs
- `data/outputs/audit_log.csv`: Audit trail
- `data/outputs/usage_cost_log.csv`: Cost tracking

### Usage Tracking
- API usage is automatically logged
- Costs are calculated and tracked
- Aggregate statistics available in `token_aggregate.json`

## 🐛 Troubleshooting

### Common Issues

1. **FFmpeg not found**
   - Ensure FFmpeg is installed and in PATH
   - Verify with: `ffmpeg -version`

2. **Tesseract OCR errors**
   - Install Tesseract OCR
   - Verify with: `tesseract --version`

3. **OpenAI API errors**
   - Check API keys in `.env` file
   - Verify Azure OpenAI configuration
   - Check network connectivity

4. **Memory issues with large videos**
   - Use Basic mode for large files
   - Process videos in chunks
   - Increase system memory

5. **Audio extraction failures**
   - Verify video has audio track
   - Check FFmpeg installation
   - Try different video format

## 🔐 Security

- **PII Protection**: Automatic face blurring in screenshots
- **Secure Configuration**: Environment variables for secrets
- **Input Validation**: File type and size validation
- **Audit Logging**: All user actions are logged
- **Session Management**: Secure session handling

## 📈 Performance

### Optimizations
- Parallel processing for CPU-intensive tasks
- Model caching for faster subsequent runs
- Chunk-based processing for large files
- Lazy loading of components

### Resource Requirements
- **Minimum**: 4GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores
- **For large videos**: 16GB RAM, 8 CPU cores

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

[Add your license information here]

## 👥 Contributors

[Add contributor information here]

## 📞 Support

For issues and questions:
- Check [Troubleshooting](#-troubleshooting) section
- Review logs in `app.log`
- Open an issue on GitHub

## 🚧 What's Next

### Planned Features

1. **Enhanced AI Integration**
   - [ ] LiteLLM integration for unified LLM access
   - [ ] Support for additional LLM providers (Anthropic, Cohere)
   - [ ] Fine-tuned models for specific document types

2. **Performance Improvements**
   - [ ] Distributed processing with message queues
   - [ ] Cloud storage integration (Azure Blob, S3)
   - [ ] Caching layer for processed videos
   - [ ] GPU acceleration for video processing

3. **User Experience**
   - [ ] Multi-user support with authentication
   - [ ] Webhook notifications for completed processing
   - [ ] Batch processing for multiple videos
   - [ ] Real-time processing status updates

4. **Document Features**
   - [ ] Custom document templates
   - [ ] Multi-language support
   - [ ] Export to additional formats (Markdown, HTML)
   - [ ] Collaborative editing

5. **Analytics and Reporting**
   - [ ] Usage analytics dashboard
   - [ ] Cost optimization recommendations
   - [ ] Processing time analytics
   - [ ] Quality metrics

6. **Integration**
   - [ ] REST API for programmatic access
   - [ ] Webhook support for external integrations
   - [ ] Slack/Teams notifications
   - [ ] Calendar integration

7. **Testing and Quality**
   - [ ] Comprehensive unit tests
   - [ ] Integration tests
   - [ ] End-to-end tests
   - [ ] Performance benchmarks

8. **Documentation**
   - [ ] API documentation
   - [ ] Developer guide
   - [ ] Video tutorials
   - [ ] Best practices guide

9. **Infrastructure**
   - [ ] Kubernetes deployment
   - [ ] CI/CD pipeline
   - [ ] Monitoring and alerting
   - [ ] Auto-scaling

10. **Advanced Features**
    - [ ] Real-time collaboration
    - [ ] Version control for documents
    - [ ] Document comparison
    - [ ] Automated quality checks

---

**Note**: This application processes video and audio data. Ensure you have proper authorization and comply with privacy regulations when processing meeting recordings.
"# MDOC-meeting-summary" 
