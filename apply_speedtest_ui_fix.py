import re

with open('client.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Speed Test Card HTML in client.html
old_card = """            <!-- CARD 2.5: LIVE SPEED TEST COMPONENT -->
            <section class="glass-card st-card">
                <div class="card-title-row">
                    <div class="card-title">
                        <svg viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14.5v-9l6 4.5-6 4.5z" />
                        </svg>
                        <span>Delta 5G Speed Test</span>
                    </div>
                    <div class="link-quality-badge" id="st-badge-status" style="background:rgba(56,189,248,0.12);color:#38BDF8;border-color:rgba(56,189,248,0.3);">
                        🌍 Global Internet CDN
                    </div>
                </div>

                <!-- SERVER INFO BAR -->
                <div style="display:flex;justify-content:space-between;align-items:center;padding:5px 10px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:8px;font-size:0.68rem;margin-bottom:8px;">
                    <span style="color:#94A3B8;">Test Server:</span>
                    <span id="st-server-info" style="font-weight:700;color:#38BDF8;">Cloudflare Global High-Speed CDN</span>
                </div>"""

new_card = """            <!-- CARD 2.5: LIVE SPEED TEST COMPONENT (DUAL-MODE ROUTER & BROWSER) -->
            <section class="glass-card st-card">
                <div class="card-title-row">
                    <div class="card-title">
                        <svg viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14.5v-9l6 4.5-6 4.5z" />
                        </svg>
                        <span>Delta 5G Speed Test</span>
                    </div>
                    <div class="link-quality-badge" id="st-badge-status" style="background:rgba(56,189,248,0.12);color:#38BDF8;border-color:rgba(56,189,248,0.3);">
                        📡 5GHz Router Ready
                    </div>
                </div>

                <!-- TEST MODE SELECTOR TABS -->
                <div style="display:flex;gap:6px;margin-bottom:10px;background:rgba(255,255,255,0.04);padding:4px;border-radius:10px;border:1px solid rgba(255,255,255,0.08);">
                    <button type="button" id="btn-mode-router" onclick="setSpeedTestMode('router')" style="flex:1;padding:8px 4px;border-radius:8px;border:1px solid #38BDF8;background:rgba(56,189,248,0.18);color:#FFFFFF;font-weight:800;font-size:0.75rem;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;transition:all 0.2s ease;">
                        <span>📡 Router Hardware (wlan0)</span>
                    </button>
                    <button type="button" id="btn-mode-browser" onclick="setSpeedTestMode('browser')" style="flex:1;padding:8px 4px;border-radius:8px;border:1px solid transparent;background:transparent;color:#94A3B8;font-weight:700;font-size:0.75rem;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;transition:all 0.2s ease;">
                        <span>📱 Device Browser</span>
                    </button>
                </div>

                <!-- SERVER INFO BAR -->
                <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 12px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:8px;font-size:0.68rem;margin-bottom:8px;">
                    <span style="color:#94A3B8;">Test Target:</span>
                    <span id="st-server-info" style="font-weight:800;color:#38BDF8;">MikroTik 5GHz Radio (wlan0 direct)</span>
                </div>"""

if old_card in html:
    html = html.replace(old_card, new_card)
else:
    print("WARNING: old_card not found by exact string, checking regex...")

# 2. Update setSpeedTestMode function in JS
js_block = """        function setSpeedTestMode(mode) {
            if (isSpeedTesting) return;
            speedTestMode = mode;
            const btnR = document.getElementById('btn-mode-router');
            const btnB = document.getElementById('btn-mode-browser');
            const info = document.getElementById('st-server-info');
            const badge = document.getElementById('st-badge-status');
            
            if (mode === 'router') {
                if (btnR) { btnR.style.borderColor = '#38BDF8'; btnR.style.background = 'rgba(56,189,248,0.18)'; btnR.style.color = '#FFFFFF'; }
                if (btnB) { btnB.style.borderColor = 'transparent'; btnB.style.background = 'transparent'; btnB.style.color = '#94A3B8'; }
                if (info) info.innerText = 'MikroTik 5GHz Radio (wlan0 direct)';
                if (badge) { badge.innerText = '📡 5GHz Router Ready'; badge.style.color = '#38BDF8'; badge.style.borderColor = 'rgba(56,189,248,0.3)'; }
            } else {
                if (btnB) { btnB.style.borderColor = '#818CF8'; btnB.style.background = 'rgba(129,140,248,0.18)'; btnB.style.color = '#FFFFFF'; }
                if (btnR) { btnR.style.borderColor = 'transparent'; btnR.style.background = 'transparent'; btnR.style.color = '#94A3B8'; }
                if (info) info.innerText = 'Cloudflare Global High-Speed CDN';
                if (badge) { badge.innerText = '🌍 Global Internet CDN'; badge.style.color = '#818CF8'; badge.style.borderColor = 'rgba(129,140,248,0.3)'; }
            }
        }"""

html = re.sub(r'function setSpeedTestMode\(mode\)\s*\{.*?\n        \}', js_block, html, flags=re.DOTALL)

with open('client.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Speed test UI fix successfully written to client.html!")
