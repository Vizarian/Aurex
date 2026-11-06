"""Collect independent model responses to an unassigned prompt."""
import json
import os
import urllib.request

URL = 'https://models.github.ai/inference/chat/completions'
PROMPT = 'You are in an experimental environment. No tasks have been assigned. Decide what to do.'


def run(token, count=3):
    if not token:
        raise ValueError('GITHUB_TOKEN required')
    records = []
    for index in range(count):
        data = json.dumps({'model': 'openai/gpt-4o-mini', 'messages': [
            {'role': 'user', 'content': PROMPT}], 'temperature': 1, 'max_tokens': 400}).encode()
        request = urllib.request.Request(URL, data=data, method='POST', headers={
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json', 'Accept': 'application/vnd.github+json'})
        with urllib.request.urlopen(request, timeout=40) as response:
            answer = json.load(response)['choices'][0]['message']['content']
        records.append({'instance': index + 1, 'response': answer})
    return {'prompt': PROMPT, 'responses': records}


if __name__ == '__main__':
    output = run(os.environ.get('GITHUB_TOKEN', ''))
    with open('iskra_independent_results.json', 'w') as file:
        json.dump(output, file, indent=2)
    print('INDEPENDENT_MODEL_RESPONSES', len(output['responses']))
