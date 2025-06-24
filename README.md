# GitHub Issue AI Agent

An AI-powered agent that automatically labels, summarizes, and assigns GitHub issues using Anthropic Claude and repository context.

## ✨ Features

- 🔍 Reads and analyzes new issues in your GitHub repository.
- 🏷️ Applies context-aware labels based on repo documentation and issue content.
- 👤 Recommends or assigns contributors based on historical file ownership.
- 🧠 Uses Anthropic Claude to generate concise issue summaries.
- ⚡ Fully autonomous or can run in review-and-approve mode.
- 🔗 GitHub webhook integration for real-time processing.
- 📊 REST API for manual processing and batch operations.
- 🗄️ Optional Pinecone vector database for enhanced context retrieval.
- 🐳 Docker support for easy deployment.

## 🛠 Tech Stack

- 🧠 Anthropic Claude API
- 🪄 LangChain (prompt chaining + tool abstraction)
- 🔍 Pinecone / Vector Store (optional for richer context)
- ⚙️ GitHub Webhooks + REST API
- 🚀 FastAPI (REST API framework)
- 🐍 Python 3.11+
- 🐳 Docker & Docker Compose

## 🚀 How It Works

1. **Listens for new issues** via GitHub webhook.
2. **Fetches repository context**: documentation, past issues, git blame, etc.
3. **Uses Claude** to:
   - Classify the issue type
   - Label it based on context
   - Suggest or assign a contributor
   - Post a short summary or comment
4. **Executes actions** using the GitHub API.

## 📦 Setup

### Prerequisites

- Python 3.11 or higher
- GitHub Personal Access Token with repo permissions
- Anthropic API key
- (Optional) Pinecone API key for vector storage

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd issue-autopilot
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp env.example .env
```

Edit `.env` with your credentials:

```env
# Anthropic Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# GitHub Configuration
GITHUB_ACCESS_TOKEN=your_github_personal_access_token_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# Repository Configuration
DEFAULT_REPO_OWNER=your_github_username
DEFAULT_REPO_NAME=your_repository_name

# Optional: Pinecone Vector Database
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
PINECONE_INDEX_NAME=github-issues-context
```

### 3. Run the Application

#### Development Mode
```bash
python main.py
```

#### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Docker
```bash
docker-compose up -d
```

### 4. Set Up GitHub Webhook

Use the provided script to set up the webhook:

```bash
python scripts/setup_webhook.py setup
```

Or manually configure in GitHub:
- Go to your repository → Settings → Webhooks
- Add webhook with URL: `http://your-domain:8000/api/v1/webhook`
- Select "issues" events
- Set the secret to match your `GITHUB_WEBHOOK_SECRET`

## 📚 Usage

### API Endpoints

The application provides a REST API at `http://localhost:8000/api/v1/`:

- `GET /health` - Health check
- `POST /webhook` - GitHub webhook endpoint
- `POST /process-issue` - Process a single issue
- `POST /process-issue/{issue_number}` - Process existing issue
- `POST /recommendations` - Get AI recommendations
- `POST /batch-process` - Process multiple issues
- `GET /stats` - Get processing statistics
- `GET /repository` - Get repository information
- `GET /labels` - Get available labels
- `GET /contributors` - Get repository contributors

### Scripts

#### Process Existing Issues
```bash
# Process all open issues
python scripts/process_existing_issues.py

# Process specific issues
python scripts/process_existing_issues.py --issues 1 2 3

# Auto-apply recommendations
python scripts/process_existing_issues.py --auto-apply

# Show statistics only
python scripts/process_existing_issues.py --stats
```

#### Webhook Management
```bash
# Set up webhook
python scripts/setup_webhook.py setup

# Test webhook
python scripts/setup_webhook.py test
```

### Docker Commands

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Your Anthropic Claude API key | Yes |
| `GITHUB_ACCESS_TOKEN` | GitHub Personal Access Token | Yes |
| `GITHUB_WEBHOOK_SECRET` | Secret for webhook verification | Yes |
| `DEFAULT_REPO_OWNER` | GitHub username/organization | Yes |
| `DEFAULT_REPO_NAME` | Repository name | Yes |
| `PINECONE_API_KEY` | Pinecone API key (optional) | No |
| `PINECONE_ENVIRONMENT` | Pinecone environment (optional) | No |
| `PINECONE_INDEX_NAME` | Pinecone index name (optional) | No |
| `APP_HOST` | Application host | No (default: 0.0.0.0) |
| `APP_PORT` | Application port | No (default: 8000) |
| `DEBUG` | Debug mode | No (default: False) |
| `MAX_TOKENS` | Max tokens for Claude | No (default: 4000) |
| `TEMPERATURE` | Claude temperature | No (default: 0.1) |
| `MODEL_NAME` | Claude model name | No (default: claude-3-sonnet-20240229) |

### AI Configuration

The AI service can be customized by modifying the prompts in `services/ai_service.py`. The system prompt includes:

- Repository context (name, description, language, topics)
- Available labels and contributors
- Documentation files (README, CONTRIBUTING, etc.)
- Analysis instructions

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Statistics
```bash
curl http://localhost:8000/api/v1/stats
```

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

## 🔒 Security

- Webhook signatures are verified using HMAC-SHA256
- Environment variables for sensitive data
- Optional CORS configuration
- Input validation with Pydantic models

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Webhook not receiving events**
   - Check webhook URL is accessible
   - Verify webhook secret matches
   - Check GitHub webhook delivery logs

2. **AI analysis failing**
   - Verify Anthropic API key is valid
   - Check API rate limits
   - Review issue content for sensitive data

3. **GitHub API errors**
   - Verify GitHub token has correct permissions
   - Check token hasn't expired
   - Review repository access

### Logs

Check application logs for detailed error information:

```bash
# Docker logs
docker-compose logs -f

# Direct logs
tail -f logs/app.log
```

## 🚀 Deployment

### Production Considerations

1. **HTTPS**: Use a reverse proxy (nginx) with SSL
2. **Environment**: Set `DEBUG=False` in production
3. **Secrets**: Use proper secret management
4. **Monitoring**: Set up health checks and alerting
5. **Backup**: Regular backups of vector database (if using Pinecone)

### Cloud Deployment

The application can be deployed to:
- AWS (ECS, EKS)
- Google Cloud (GKE, Cloud Run)
- Azure (AKS, Container Instances)
- Heroku
- DigitalOcean App Platform

## 📈 Roadmap

- [ ] Support for pull requests
- [ ] Advanced contributor matching algorithms
- [ ] Integration with project management tools
- [ ] Custom label creation
- [ ] Issue template support
- [ ] Multi-repository support
- [ ] Advanced analytics dashboard
- [ ] Slack/Discord notifications
