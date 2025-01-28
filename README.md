# AI-Powered Script Generator

An advanced script generation tool that transforms complex source material into engaging YouTube documentary scripts using AI and natural language processing.

## Features

- Intelligent text chunking and processing
- AI-powered script generation with OpenAI GPT models
- Real-time script validation and improvement
- Modern React-based editor interface
- Parallel processing of large documents
- Quality control and readability metrics

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/script-generator.git
cd script-generator
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
OPENAI_API_KEY=your_api_key_here
```

4. Install frontend dependencies:
```bash
cd app/static
npm install
```

## Usage

1. Start the backend server:
```bash
cd app
uvicorn api.main:app --reload
```

2. Start the frontend development server:
```bash
cd app/static
npm start
```

3. Open your browser and navigate to `http://localhost:3000`

## Configuration

### AI Model Settings
Edit `app/config/llm.yaml` to configure:
- Model selection
- Temperature and token limits
- System prompts
- Validation thresholds

### Quality Control
Edit `app/config/quality_control.yaml` to adjust:
- Readability requirements
- Structure validation
- Style guidelines
- Coherence checks

## API Endpoints

- `POST /api/generate-script`: Generate a new script
- `GET /api/script-status/{task_id}`: Check generation status
- `POST /api/upload-file`: Upload source material
- `POST /api/validate-script`: Validate script quality

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
