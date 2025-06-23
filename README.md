# GitHub Issue AI Agent

An AI-powered agent that automatically labels, summarizes, and assigns GitHub issues using Anthropic Claude and repository context.

## ✨ Features

- 🔍 Reads and analyzes new issues in your GitHub repository.
- 🏷️ Applies context-aware labels based on repo documentation and issue content.
- 👤 Recommends or assigns contributors based on historical file ownership.
- 🧠 Uses Anthropic Claude to generate concise issue summaries.
- ⚡ Fully autonomous or can run in review-and-approve mode.

## 🛠 Tech Stack

- 🧠 Anthropic Claude API
- 🪄 LangChain (prompt chaining + tool abstraction)
- 🔍 Pinecone / Vector Store (optional for richer context)
- ⚙️ GitHub Webhooks + REST API
- 🐍 Python

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

1. Clone this repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
