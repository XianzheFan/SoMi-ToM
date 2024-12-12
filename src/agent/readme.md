```bash
uvicorn group_discussion_agents:app --reload --port 8080
```

Minecraft Singleplayer 

Open to LAN 50809

```bash
node src/agent/index.js
```

```bash
export OPENAI_API_KEY=sk-
uv run aact run-dataflow group_discussion_agents.toml
```

Please restart the server (`uvicorn group_discussion_agents:app --reload --port 8080`) each time you rerun `node src/agent/index.js` and `uv run aact run-dataflow group_discussion_agents.toml`.