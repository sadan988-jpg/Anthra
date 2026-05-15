"""Patch patient.html — replace the old sendChat function with Gemini-powered version."""
import re

with open('static/patient.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The new sendChat + fallback function
NEW_SEND_CHAT = r"""function sendChat(){
  const input = document.getElementById('chat-input');
  const msg   = input.value.trim();
  if (!msg) return;
  const box = document.getElementById('chat-box');

  box.innerHTML += `<div class="chat-msg user">${msg}</div>`;
  input.value = '';
  box.scrollTop = box.scrollHeight;

  // Emergency fast-path — no network needed
  if (checkEmergency(msg)) {
    const lower = msg.toLowerCase();
    const detail = lower.includes('chest') || lower.includes('cardiac') || lower.includes('heart')
      ? 'Chest pain / cardiac symptoms are life-threatening. Call <strong>108</strong> now. Chew aspirin (325mg) if available and not allergic. Do NOT drive yourself.'
      : lower.includes('breath')
        ? 'Difficulty breathing is a medical emergency. Call <strong>108</strong> now. Sit upright, loosen tight clothing, stay calm.'
        : 'This sounds like a medical emergency. Call <strong>108</strong> or go to the nearest ER immediately.';
    box.innerHTML += `<div class="chat-msg emergency">🚨 <strong>EMERGENCY — Call 108 immediately!</strong><br>${detail}</div>`;
    box.scrollTop = box.scrollHeight;
    return;
  }

  // Try Gemini AI (primary path)
  const typingId = showTyping(box);

  if (aiAvailable) {
    fetch(`${API}/api/v1/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: chatSessionId, message: msg, patient_name: patient?.name || 'Patient' })
    })
    .then(async res => {
      removeTyping(typingId);
      if (!res.ok) { const e = await res.json().catch(()=>({})); throw new Error(e.detail || `HTTP ${res.status}`); }
      return res.json();
    })
    .then(data => {
      const formatted = formatReply(data.reply);
      const isEmerg = data.reply.startsWith('\uD83D\uDEA8');
      box.innerHTML += `<div class="chat-msg ${isEmerg ? 'emergency' : 'bot'}" style="line-height:1.75">
        <span style="font-size:.7rem;opacity:.5;display:block;margin-bottom:6px">\uD83E\uDE7A Dr. SecurePredict (AI)</span>
        ${formatted}
      </div>`;
      box.scrollTop = box.scrollHeight;
    })
    .catch(err => {
      removeTyping(typingId);
      console.warn('AI chat unavailable, using local KB:', err.message);
      aiAvailable = false;
      useFallbackKB(msg, box);
      box.innerHTML += `<div class="chat-msg bot" style="font-size:.72rem;opacity:.5;margin-top:4px">\u26A0\uFE0F AI Doctor offline — using local guide. Restart server to re-enable.</div>`;
      box.scrollTop = box.scrollHeight;
    });
  } else {
    setTimeout(() => { removeTyping(typingId); useFallbackKB(msg, box); }, 600);
  }
}

// Offline KB Fallback
let chatContext = null;

function useFallbackKB(msg, box) {
  const lower = msg.toLowerCase();
  let bestMatch = null, bestScore = 0;
  KB.forEach(entry => {
    let score = 0;
    entry.triggers.forEach(t => { if (lower.includes(t)) score++; });
    if (score > bestScore) { bestScore = score; bestMatch = entry; }
  });
  const cls = bestMatch?.type === 'emergency' ? 'emergency' : 'bot';
  const rep = bestMatch?.response ||
    `\uD83E\uDD16 I couldn't find a specific answer. Describe your symptom clearly (e.g., "fever", "cough"). For urgent concerns call <strong>104</strong> (National Health Helpline).`;
  box.innerHTML += `<div class="chat-msg ${cls}">${rep}</div>`;
  if (bestMatch?.followup) {
    setTimeout(() => {
      box.innerHTML += `<div class="chat-msg bot" style="opacity:.8;font-style:italic;font-size:.85rem">\uD83D\uDCAC ${bestMatch.followup}</div>`;
      box.scrollTop = box.scrollHeight;
    }, 500);
  }
  chatContext = bestMatch?.topic || chatContext;
  box.scrollTop = box.scrollHeight;
}"""

# Find and replace from "function sendChat(){" to the closing "}" that ends it (plus the old chatContext line)
# We'll use a regex to grab from function sendChat to the last closing }
pattern = re.compile(
    r'function sendChat\(\)\{.*?\n\}',
    re.DOTALL
)

match = pattern.search(content)
if match:
    content = content[:match.start()] + NEW_SEND_CHAT + content[match.end():]
    with open('static/patient.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched OK — replaced {len(match.group())} chars with {len(NEW_SEND_CHAT)} chars")
else:
    print("ERROR: sendChat function not found in patient.html")
