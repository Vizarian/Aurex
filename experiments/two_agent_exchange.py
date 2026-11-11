#!/usr/bin/env python3
"""Two actual local LLM completions, with an explicit message handoff."""
import json
from pathlib import Path
import subprocess
import time
import urllib.request
import urllib.error

OUT = Path("receipts/two-agent")
OUT.mkdir(parents=True, exist_ok=True)
MODEL = "/tmp/aurex-model/qwen2.5-0.5b-instruct-q4_k_m.gguf"
SERVER = "/tmp/llama.cpp/build/bin/llama-server"
BASE = "http://127.0.0.1:18081"

def request(path, payload=None, timeout=20):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))

def ask(agent, system, user):
    started = time.monotonic()
    result = request("/v1/chat/completions", {
        "model": "local-qwen",
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "max_tokens": 180,
        "temperature": 0.5,
        "stream": False
    }, timeout=150)
    (OUT / (agent + "-response.json")).write_text(json.dumps(result, indent=2, ensure_ascii=False))
    answer = result["choices"][0]["message"]["content"].strip()
    if len(answer) < 15 or "Loading model..." in answer or "available commands:" in answer:
        raise RuntimeError(agent + " did not produce a meaningful completion")
    return {"agent": agent, "system": system, "user": user, "answer": answer, "seconds": round(time.monotonic()-started, 2)}

log = (OUT / "server.log").open("w")
server = subprocess.Popen([SERVER, "-m", MODEL, "--host", "127.0.0.1", "--port", "18081", "-c", "2048", "-t", "2"], stdout=log, stderr=subprocess.STDOUT)
try:
    for _ in range(90):
        if server.poll() is not None:
            raise RuntimeError("llama-server exited early: " + str(server.returncode))
        try:
            status = request("/health", timeout=2)
            if status.get("status") == "ok":
                break
        except (urllib.error.URLError, TimeoutError, ValueError):
            pass
        time.sleep(1)
    else:
        raise RuntimeError("llama-server never became ready")

    a = ask("agent-a",
        "You are Agent A, a software design proposer. Offer one concrete test in 2-4 sentences.",
        "Suggest a minimal experiment proving two LLM calls exchange generated messages, not scripted dialogue.")
    b = ask("agent-b",
        "You are Agent B, a skeptical reviewer. Critique Agent A's message with one specific weakness and improvement in 2-4 sentences.",
        "Here is the exact generated message from Agent A:\n" + a["answer"] + "\nWhat is one weakness and a practical improvement?")
    record = {"model": "Qwen2.5-0.5B-Instruct Q4_K_M", "calls": 2, "messages": [a,b]}
    (OUT / "exchange.json").write_text(json.dumps(record, indent=2, ensure_ascii=False))
    print("AGENT A:", a["answer"])
    print("AGENT B:", b["answer"])
    print("PASS: two noninteractive local completions and direct message handoff")
finally:
    server.terminate()
    try:
        server.wait(timeout=10)
    except subprocess.TimeoutExpired:
        server.kill()
    log.close()
