#!/usr/bin/env python3
"""Two sequential, separate-context local model calls; record raw evidence."""
import json
import os
from pathlib import Path
import subprocess
import time

OUT = Path("receipts/two-agent")
OUT.mkdir(parents=True, exist_ok=True)
MODEL = "/tmp/aurex-model/qwen2.5-0.5b-instruct-q4_k_m.gguf"
CLI = "/tmp/llama.cpp/build/bin/llama-cli"

def ask(agent, instruction):
    prompt = "<|im_start|>system\n" + instruction["system"] + "<|im_end|>\n<|im_start|>user\n" + instruction["user"] + "<|im_end|>\n<|im_start|>assistant\n"
    cmd = [CLI, "-m", MODEL, "-p", prompt, "-n", "160", "-c", "1024", "-t", "2", "--temp", "0.5", "--no-display-prompt", "--simple-io", "--single-turn"]
    started = time.monotonic()
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180, check=False)
    (OUT / (agent + "-stdout.txt")).write_text(result.stdout)
    (OUT / (agent + "-stderr.txt")).write_text(result.stderr)
    if result.returncode != 0:
        raise RuntimeError(agent + " model process failed with " + str(result.returncode))
    answer = result.stdout.strip().split("<|im_end|>")[0].strip()
    if "Loading model..." in answer or "available commands:" in answer or "<|im_start|>" in answer:
        raise RuntimeError(agent + " returned CLI interface text instead of a generated response")
    if len(answer) < 12:
        raise RuntimeError(agent + " output was too short")
    return {"agent": agent, "prompt": instruction, "answer": answer, "seconds": round(time.monotonic() - started, 2)}

a = ask("agent-a", {
    "system": "You are Agent A, an independent software design proposer. You do not know Agent B's private instructions. Answer in plain English with a concrete, testable idea in 2-4 sentences.",
    "user": "Suggest one minimal experiment to verify that two AI agents exchange genuine generated messages rather than replay a scripted conversation."
})
b = ask("agent-b", {
    "system": "You are Agent B, an independent skeptical reviewer. Your job is to critically evaluate the exact message from Agent A and propose one concrete improvement. Do not merely agree. Answer in plain English in 2-4 sentences.",
    "user": "Here is the actual generated message from Agent A (not a scripted sample):\n\n" + a["answer"] + "\n\nIdentify one weakness and propose a practical improvement."
})
record = {"experiment": "two-agent-sequential-local-llm", "model": "Qwen2.5-0.5B-Instruct Q4_K_M", "independent_model_calls": 2, "messages": [a, b]}
(OUT / "exchange.json").write_text(json.dumps(record, indent=2, ensure_ascii=False))
print("AGENT A:", a["answer"])
print("AGENT B:", b["answer"])
print("PASS: two separate local inference calls with recorded message handoff")
