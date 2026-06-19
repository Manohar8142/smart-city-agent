# 🌆 Smart City Assistant

> An intelligent multi-tool agent system that provides real-time city information including weather, time, places, news, and more.

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🎯 Project Status

**Current Phase:** Phase 1 - Foundation  
**Days Active:** 1  
**Progress:** 10%

### ✅ Completed
- [x] Basic agent structure
- [x] Weather tool (New York)
- [x] Time tool (New York)
- [x] Learning roadmap

### 🚧 In Progress
- [ ] Git repository setup
- [ ] Project restructuring
- [ ] Input validation
- [ ] Error handling improvements

### 📅 Next Up
- [ ] MCP integration
- [ ] Langfuse tracing
- [ ] Multi-city support

---

## 🚀 Quick Start

### Prerequisites
```bash
python --version  # 3.13+
pip --version
```

### Installation
```bash
# Clone repository
git clone <repo-url>
cd adk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

### Run the Agent
```bash
cd multi_tool_agent
adk run
```

---

## 🏗️ Architecture

### Current (Phase 1)
```
┌─────────────────────────────────┐
│      Root Agent (LLaMA 3.3)     │
├─────────────────────────────────┤
│  Tools:                         │
│  • get_weather(city)            │
│  • get_time(city)               │
└─────────────────────────────────┘
```

### Target (Phase 8)
```
┌────────────────────────────────────────┐
│         Orchestrator Agent             │
└───────────────┬────────────────────────┘
                │
    ┌───────────┼───────────┬───────────┐
    │           │           │           │
┌───▼────┐ ┌───▼────┐ ┌───▼────┐ ┌───▼────┐
│Weather │ │Travel  │ │ News   │ │Events  │
│ Agent  │ │ Agent  │ │ Agent  │ │ Agent  │
└───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
    │          │          │          │
    │          │          │          │
┌───▼──────────▼──────────▼──────────▼────┐
│          MCP Tool Registry               │
│  • Weather API  • Places API             │
│  • News API     • Transit API            │
│  • Events API   • Time API               │
└──────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **Framework** | Google ADK |
| **LLM** | Groq (LLaMA 3.3 70B) |
| **Language** | Python 3.13 |
| **Observability** | Langfuse (Phase 3) |
| **MCP** | OpenWeatherMap, NewsAPI (Phase 2) |
| **Deployment** | Azure Container Apps (Phase 7) |
| **Testing** | pytest (Phase 6) |

---

## 📚 Documentation

- [Learning Roadmap](LEARNING_ROADMAP.md) - Complete 30-day plan
- [Architecture](docs/ARCHITECTURE.md) - System design (Coming soon)
- [API Documentation](docs/API.md) - Tool interfaces (Coming soon)
- [Deployment Guide](docs/DEPLOYMENT.md) - Cloud setup (Coming soon)

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=multi_tool_agent --cov-report=html

# Specific test
pytest tests/unit/test_weather.py
```

---

## 🤝 Contributing

This is a learning project following a structured roadmap. Daily commits track progress.

### Git Workflow
```bash
git checkout -b feature/your-feature
# Make changes
git commit -m "feat: add new feature"
git push origin feature/your-feature
```

---

## 📈 Progress Tracking

| Phase | Days | Status |
|-------|------|--------|
| **Phase 1:** Foundation | 1-3 | 🟡 In Progress |
| **Phase 2:** MCP Integration | 4-6 | ⚪ Planned |
| **Phase 3:** Observability | 7-9 | ⚪ Planned |
| **Phase 4:** Advanced Tools | 10-14 | ⚪ Planned |
| **Phase 5:** Multi-Agent | 15-18 | ⚪ Planned |
| **Phase 6:** Production | 19-23 | ⚪ Planned |
| **Phase 7:** Deployment | 24-27 | ⚪ Planned |
| **Phase 8:** Advanced Features | 28-30 | ⚪ Planned |

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

- Google ADK Team
- Groq for fast LLM inference
- Langfuse for observability
- MCP community

---

**Built with ❤️ as a portfolio project | [View Roadmap](LEARNING_ROADMAP.md)**
