# Ollama Hunter

**Ollama Hunter** is a Python tool that searches Shodan for publicly exposed Ollama LLM instances running on port `11434`, and retrieves the list of available models from each host.

This tool is designed for researchers, security analysts, and red teamers who want to map the exposure of open LLM endpoints on the internet.

---

## 🔍 Features

- Scrapes Shodan using your session cookie to find hosts running Ollama.
- Connects to each host and queries `/api/tags` to list all available LLM models.
- Automatically handles pagination and deduplicates IPs.
- Saves results in a clean text file: `ollama_hosts_with_models.txt`.

---

## 🚀 Usage

```bash
python ollama_hunter.py
