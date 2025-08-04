<!DOCTYPE html>
<html lang="en">

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

</body>
</html>
