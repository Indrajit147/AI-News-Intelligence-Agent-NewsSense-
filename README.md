<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>NewsSense – AI News Intelligence Agent</title>
  <style>
    body { font-family: 'Segoe UI', Arial, sans-serif; margin: 2em; background: #fcfcfc; }
    h1, h2, h3 { color: #104c91; }
    h1 { border-bottom: 2px solid #47a3ff; }
    code, pre { background: #f0f8ff; border-radius: 4px; padding: 2px 4px; font-size: 95%; }
    ul { margin-left: 1.5em; }
    .block { background: #f7fbfd; border: 1px solid #e3eaf2; padding: 14px 18px; margin: 1.5em 0; border-radius: 8px; }
    .terminal { background: #23272e; color: #e2e8f0; padding: 16px; border-radius: 7px; font-family: 'Fira Mono', 'Consolas', monospace; margin: 14px 0; }
    table { border-collapse: collapse; background: #fff; }
    th, td { border: 1px solid #d8e2ef; padding: 6px 12px; }
    th { background: #eaf6ff; }
    hr { border: none; border-top: 1px solid #bbc8db; margin: 28px 0 14px 0; }
    .diagram { font-family: "Fira Mono", monospace; background: #f3f7fa; padding: 12px; border-radius: 4px; color: #18304b; }
  </style>
</head>
<body>

<h1>📰 NewsSense: AI News Intelligence Agent</h1>

<h2>🔍 Objective</h2>
<p>
  <b>NewsSense</b> is a multi-agent AI system that helps users <b>track, verify, and summarize breaking news</b> from across the web.
  It automatically detects trending topics, fact-checks claims using simulated web search and retrieval-augmented generation (RAG), and produces concise, readable news briefs.
</p>

<hr>

<h2>✅ System Overview</h2>

<h3>🤖 Agents</h3>
<ul>
  <li>
    <b>Conversation Agent (Controller)</b>
    <ul>
      <li>Main entry point for all user queries.</li>
      <li>Detects user intent: <i>“Get Trending”</i>, <i>“Verify Claim”</i>, <i>“Summarize Topic”</i>.</li>
      <li>Routes queries to specialist agents accordingly.</li>
      <li>Logs all routing and decisions with Logfire; validates I/O via Pydantic.</li>
    </ul>
  </li>
  <li>
    <b>Trending News Agent</b>
    <ul>
      <li>Fetches trending headlines in tech, finance, politics, etc.</li>
      <li>Uses a simulated web search tool.</li>
      <li>Groups and ranks topics by frequency; summarizes key trends.</li>
      <li><b>Tool:</b> <code>get_trending_news(topic: str, category: str)</code></li>
    </ul>
  </li>
  <li>
    <b>Fact Checker Agent</b>
    <ul>
      <li>Verifies factual claims with a simulated RAG approach.</li>
      <li>Returns verdict and supporting sources.</li>
      <li><b>Tool:</b> <code>fact_check_claim(claim: str)</code></li>
    </ul>
  </li>
  <li>
    <b>News Summarizer Agent</b>
    <ul>
      <li>Summarizes articles or topics into 3–5 bullet points.</li>
      <li><b>Tool:</b> <code>summarize_news(article_text: str, topic: str)</code></li>
    </ul>
  </li>
</ul>

<hr>

<div class="block">
<b>Features:</b>
<ul>
  <li>Multi-agent routing: user queries sent to correct specialist</li>
  <li>Logfire logging: trace all agent decisions</li>
  <li>Strict Pydantic validation of all agent I/O</li>
  <li>Dummy datasets for news, fact-checks, summaries (easy to upgrade to real APIs)</li>
  <li>Chat interface: interact in real time, classify, route, and summarize</li>
</ul>
</div>

<h2>🚀 Getting Started</h2>
<ol>
  <li><b>Clone and Install</b>
    <div class="terminal">
      git clone https://github.com/yourusername/newssense.git<br>
      cd newssense<br>
      pip install -r requirements.txt
    </div>
  </li>

  <li><b>Set Environment Variables (.env or shell)</b>
    <div class="terminal">
      OPENAI_API_KEY=your-openai-key<br>
      LOGFIRE_TOKEN=your-logfire-token<br>
      BASE_URL=https://api.openai.com/v1
    </div>
    <i>(Authenticate Logfire with <code>logfire auth</code> for local development)</i>
  </li>

  <li><b>Run the agent</b>
    <div class="terminal">python newssense.py</div>
  </li>
</ol>

<h3>💬 Example Interaction</h3>
<div class="terminal">
You: What's trending in tech today?<br>
NewsSense:<br>
🌏 TRENDING TOPIC: AI ADVANCEMENTS<br>
1. OpenAI releases GPT-5<br>
2. Apple unveils new AI chip<br>
3. Microsoft invests in robotics startup<br>
Summary: AI continues to lead tech trends with new releases and investments.<br><br>

You: Did Apple acquire OpenAI?<br>
NewsSense:<br>
❓ CLAIM: Did Apple acquire OpenAI?<br>
Verdict: False<br>
Sources:<br>
- TechCrunch, 2025-08-01<br>
- Reuters, 2025-07-30<br>
Summary: There is no verified report of Apple acquiring OpenAI; sources suggest only collaborations.<br><br>

You: Summarize: OpenAI released a new version...<br>
NewsSense:<br>
✍️ SUMMARY FOR TOPIC: OpenAI<br>
- Key events outlined and context provided.<br>
- Expert opinions and implications discussed.<br>
...
</div>

<hr>

<h2>🏗️ System Architecture</h2>
<div class="diagram">
User<br>
 &nbsp;|<br>
 v<br>
[Controller Agent] ---------+<br>
 |           |            |<br>
 v           v            v<br>
[Trending] [FactCheck] [Summarizer]
</div>
<ul>
  <li>Controller parses the query and routes to the relevant agent.</li>
  <li>Each agent uses a simulated tool, validates outputs, and logs transactions.</li>
</ul>

<hr>

<h2>🧩 Customization & Extension</h2>
<ul>
  <li>Swap dummy functions for real news/fact/summarizer APIs</li>
  <li>Add more routing or agent types</li>
  <li>Improve the chat UI or deploy as a web/app service</li>
</ul>

<h2>📝 Requirements</h2>
<ul>
  <li>Python 3.9+</li>
  <li>All dependencies in <code>requirements.txt</code>: openai, pydantic, logfire, etc.</li>
</ul>

<h2>📈 Logging & Monitoring</h2>
<ul>
  <li>All agent actions are logged via Logfire (see <a href='https://logfire.pydantic.dev' target='_blank'>logfire.pydantic.dev</a>).</li>
  <li>Monitor your project dashboard to view traces and events in real-time.</li>
</ul>

<h2>👨‍💻 Author &amp; License</h2>
<ul>
  <li><b>Author:</b> Indrajit Gupta</li>
  <li><b>License:</b> MIT (or your chosen license)</li>
</ul>

<h2>🤝 Contribution</h2>
<p>
  Pull requests, issue reports, and feature suggestions are all encouraged!
</p>
<hr>
<p><b>Enjoy using NewsSense — your AI-powered breaking news companion!</b></p>

</body>
</html>
