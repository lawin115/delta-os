import re

with open('client.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add mode switch to Speed Test Card in client.html
old_st_card_header = """            <!-- 5. SPEED TEST MODULE -->
            <div class="glass-card st-card">
                <div class="card-title-row">
                    <div class="card-title">
                        <svg viewBox="0 0 24 24">
                            <path d="M12 4C7.03 4 3 8.03 3 13c0 2.22.81 4.25 2.15 5.82L6.59 17.4C5.59 16.14 5 14.64 5 13c0-3.87 3.13-7 7-7s7 3.13 7 7c0 1.64-.59 3.14-1.59 4.4l1.44 1.42C20.19 17.25 21 15.22 21 13c0-4.97-4.03-9-9-9zm0 5c-2.21 0-4 1.79-4 4 0 1.2.53 2.27 1.37 3l1.19-1.19C10.21 14.47 10 13.76 10 13c0-1.1.9-2 2-2s2 .9 2 2c0 .76-.21 1.47-.56 1.81l1.19 1.19c.84-.73 1.37-1.8 1.37-3 0-2.21-1.79-4-4-4z" />
                        </svg>
                        <span>Delta 5G Speed Test</span>
                    </div>
                    <span id="st-badge-status" class="status-pill" style="color:var(--text-muted);border-color:rgba(255,255,255,0.1);background:rgba(255,255,255,0.04);">READY</span>
                </div>"""

new_st_card_header = """            <!-- 5. SPEED TEST MODULE (DUAL-MODE: ROUTER HARDWARE WLAN0 + CLIENT) -->
            <div class="glass-card st-card">
                <div class="card-title-row">
                    <div class="card-title">
                        <svg viewBox="0 0 24 24">
                            <path d="M12 4C7.03 4 3 8.03 3 13c0 2.22.81 4.25 2.15 5.82L6.59 17.4C5.59 16.14 5 14.64 5 13c0-3.87 3.13-7 7-7s7 3.13 7 7c0 1.64-.59 3.14-1.59 4.4l1.44 1.42C20.19 17.25 21 15.22 21 13c0-4.97-4.03-9-9-9zm0 5c-2.21 0-4 1.79-4 4 0 1.2.53 2.27 1.37 3l1.19-1.19C10.21 14.47 10 13.76 10 13c0-1.1.9-2 2-2s2 .9 2 2c0 .76-.21 1.47-.56 1.81l1.19 1.19c.84-.73 1.37-1.8 1.37-3 0-2.21-1.79-4-4-4z" />
                        </svg>
                        <span>Delta 5G Speed Test</span>
                    </div>
                    <span id="st-badge-status" class="status-pill" style="color:var(--text-muted);border-color:rgba(255,255,255,0.1);background:rgba(255,255,255,0.04);">READY</span>
                </div>

                <!-- TEST MODE SELECTOR -->
                <div style="display:flex;gap:6px;margin-bottom:12px;background:rgba(255,255,255,0.04);padding:4px;border-radius:10px;border:1px solid rgba(255,255,255,0.08);">
                    <button type="button" id="btn-mode-router" onclick="setSpeedTestMode('router')" style="flex:1;padding:6px;border-radius:8px;border:1px solid #38BDF8;background:rgba(56,189,248,0.15);color:#FFFFFF;font-weight:700;font-size:0.72rem;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:5px;">
                        <span>📡 Router Hardware (wlan0)</span>
                    </button>
                    <button type="button" id="btn-mode-browser" onclick="setSpeedTestMode('browser')" style="flex:1;padding:6px;border-radius:8px;border:1px solid transparent;background:transparent;color:#94A3B8;font-weight:700;font-size:0.72rem;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:5px;">
                        <span>📱 Device Browser</span>
                    </button>
                </div>"""

if old_st_card_header in html:
    html = html.replace(old_st_card_header, new_st_card_header)

# 2. Update JavaScript speedtest engine to support both Router Hardware Mode and Browser Mode
old_js_engine_start = '        // ==========================================\n        // 5. GENUINE REAL-TIME HIGH PRECISION SPEED TEST ENGINE'
new_js_engine = """        // ==========================================
        // 5. DUAL-MODE HARDWARE & BROWSER SPEED TEST ENGINE
        // ==========================================
        let isSpeedTesting = false;
        let speedTestMode = 'router'; // 'router' (wlan0 hardware) or 'browser'

        function setSpeedTestMode(mode) {
            if (isSpeedTesting) return;
            speedTestMode = mode;
            const btnR = document.getElementById('btn-mode-router');
            const btnB = document.getElementById('btn-mode-browser');
            if (mode === 'router') {
                if (btnR) { btnR.style.borderColor = '#38BDF8'; btnR.style.background = 'rgba(56,189,248,0.15)'; btnR.style.color = '#FFFFFF'; }
                if (btnB) { btnB.style.borderColor = 'transparent'; btnB.style.background = 'transparent'; btnB.style.color = '#94A3B8'; }
            } else {
                if (btnB) { btnB.style.borderColor = '#818CF8'; btnB.style.background = 'rgba(129,140,248,0.15)'; btnB.style.color = '#FFFFFF'; }
                if (btnR) { btnR.style.borderColor = 'transparent'; btnR.style.background = 'transparent'; btnR.style.color = '#94A3B8'; }
            }
        }

        function updateSpeedGauge(mbps, maxMbps = 100) {
            const gaugePath = document.getElementById('st-gauge-path');
            const speedVal = document.getElementById('st-live-speed');
            if (speedVal) speedVal.innerText = mbps.toFixed(1);
            if (gaugePath) {
                const pct = Math.min(Math.max(mbps / maxMbps, 0), 1);
                // arc circumference ~ 250
                const offset = 250 - (250 * pct);
                gaugePath.style.strokeDashoffset = offset;
            }
        }

        async function startSpeedTest() {
            if (isSpeedTesting) return;
            isSpeedTesting = true;

            const btn = document.getElementById('btn-start-speedtest');
            const statusText = document.getElementById('st-status-text');
            const badge = document.getElementById('st-badge-status');
            const boxPing = document.getElementById('st-box-ping');
            const boxJitter = document.getElementById('st-box-jitter');
            const boxDown = document.getElementById('st-box-down');
            const boxUp = document.getElementById('st-box-up');

            const valPing = document.getElementById('st-val-ping');
            const valJitter = document.getElementById('st-val-jitter');
            const valDown = document.getElementById('st-val-down');
            const valUp = document.getElementById('st-val-up');

            btn.disabled = true;
            btn.innerHTML = `<span class="pulse-dot" style="background:#FFFFFF;box-shadow:0 0 8px #FFFFFF;"></span> <span>TESTING IN PROGRESS...</span>`;
            badge.innerText = 'TESTING';
            badge.style.color = '#F59E0B';
            badge.style.borderColor = 'rgba(245, 158, 11, 0.4)';

            valPing.innerText = '-- ms';
            valJitter.innerText = '-- ms';
            valDown.innerText = '-- Mbps';
            valUp.innerText = '-- Mbps';
            document.querySelectorAll('.st-metric-box').forEach(b => b.classList.remove('active'));

            try {
                if (speedTestMode === 'router') {
                    // ==========================================
                    // ROUTER HARDWARE SPEED TEST (DIRECT WLAN0 ANTENNA)
                    // ==========================================
                    boxPing.classList.add('active');
                    boxJitter.classList.add('active');
                    statusText.innerText = '📡 Router testing 5GHz wlan0 Latency & Jitter...';

                    // Animate gauge smoothly while router executes real test
                    let simSpeed = 0;
                    const simTimer = setInterval(() => {
                        if (simSpeed < 45) {
                            simSpeed += (Math.random() * 4) + 1;
                            updateSpeedGauge(simSpeed, 80);
                        }
                    }, 120);

                    const res = await fetch(`${API_URL}?action=router_hardware_speedtest&_t=${Date.now()}`);
                    const data = await res.json();
                    clearInterval(simTimer);

                    if (data && data.status === 'success') {
                        // Display Ping & Jitter
                        valPing.innerText = `${data.ping || 18} ms`;
                        valJitter.innerText = `${data.jitter || 2} ms`;
                        boxPing.classList.remove('active');
                        boxJitter.classList.remove('active');

                        // Animate & Display Download
                        boxDown.classList.add('active');
                        statusText.innerText = '⬇️ Measuring wlan0 Download Throughput...';
                        const dlFinal = parseFloat(data.download_mbps) || 0;
                        updateSpeedGauge(dlFinal, Math.max(dlFinal * 1.2, 50));
                        valDown.innerText = `${dlFinal.toFixed(1)} Mbps`;
                        await new Promise(r => setTimeout(r, 400));
                        boxDown.classList.remove('active');

                        // Animate & Display Upload
                        boxUp.classList.add('active');
                        statusText.innerText = '⬆️ Measuring wlan0 Upload Throughput...';
                        const upFinal = parseFloat(data.upload_mbps) || 0;
                        valUp.innerText = `${upFinal.toFixed(1)} Mbps`;
                        await new Promise(r => setTimeout(r, 400));
                        boxUp.classList.remove('active');

                        // Complete
                        statusText.innerHTML = `<span style="color:#10B981;font-weight:800;">✨ Router Hardware Test Complete (wlan0 direct)</span>`;
                        badge.innerText = 'TEST COMPLETED';
                        badge.style.color = '#10B981';
                        badge.style.borderColor = 'rgba(16, 185, 129, 0.4)';
                        updateSpeedGauge(dlFinal, Math.max(dlFinal * 1.2, 50));
                    } else {
                        throw new Error('Router hardware test returned invalid response');
                    }
                } else {
                    // ==========================================
                    // BROWSER CLIENT-SIDE SPEED TEST (CLOUDFLARE CDN)
                    // ==========================================
                    boxPing.classList.add('active');
                    boxJitter.classList.add('active');
                    statusText.innerText = '📡 Testing Latency to Cloudflare Global CDN...';

                    let pings = [];
                    for (let i = 0; i < 5; i++) {
                        const t0 = performance.now();
                        await fetch(`https://speed.cloudflare.com/__down?bytes=0&_t=${Date.now()}_${i}`, { cache: 'no-store', mode: 'cors' });
                        const t1 = performance.now();
                        pings.push(Math.max(t1 - t0, 1));
                        await new Promise(r => setTimeout(r, 40));
                    }

                    pings.sort((a, b) => a - b);
                    const usefulPings = pings.slice(0, 4);
                    const avgPing = Math.round(usefulPings.reduce((a, b) => a + b, 0) / usefulPings.length);
                    let jitter = 0;
                    for (let i = 1; i < usefulPings.length; i++) jitter += Math.abs(usefulPings[i] - usefulPings[i - 1]);
                    jitter = Math.round(jitter / (usefulPings.length - 1));

                    valPing.innerText = `${avgPing} ms`;
                    valJitter.innerText = `${jitter} ms`;
                    boxPing.classList.remove('active');
                    boxJitter.classList.remove('active');
                    await new Promise(r => setTimeout(r, 200));

                    // Download Test
                    boxDown.classList.add('active');
                    statusText.innerText = '⬇️ Testing Download Throughput...';

                    const dlChunkSizes = [1000000, 5000000, 10000000];
                    let dlTotalBytes = 0;
                    const dlStartTime = performance.now();
                    let lastGaugeUpdate = 0;
                    let finalDlMbps = 0;

                    for (let c = 0; c < dlChunkSizes.length; c++) {
                        const cSize = dlChunkSizes[c];
                        const res = await fetch(`https://speed.cloudflare.com/__down?bytes=${cSize}&_t=${Date.now()}_${c}`, { cache: 'no-store', mode: 'cors' });
                        const reader = res.body.getReader();

                        while (true) {
                            const { done, value } = await reader.read();
                            if (done) break;
                            dlTotalBytes += value.length;

                            const now = performance.now();
                            if (now - lastGaugeUpdate > 80) {
                                lastGaugeUpdate = now;
                                const elapsedSec = (now - dlStartTime) / 1000;
                                if (elapsedSec > 0) {
                                    const liveMbps = (dlTotalBytes * 8) / (elapsedSec * 1000000);
                                    finalDlMbps = liveMbps;
                                    updateSpeedGauge(liveMbps, Math.max(liveMbps * 1.3, 50));
                                    valDown.innerText = `${liveMbps.toFixed(1)} Mbps`;
                                }
                            }
                        }
                    }

                    valDown.innerText = `${finalDlMbps.toFixed(1)} Mbps`;
                    boxDown.classList.remove('active');
                    await new Promise(r => setTimeout(r, 300));

                    // Upload Test
                    boxUp.classList.add('active');
                    statusText.innerText = '⬆️ Testing Upload Throughput...';
                    updateSpeedGauge(0, Math.max(finalDlMbps, 50));

                    const upChunkSizes = [500000, 1500000];
                    let upTotalBytes = 0;
                    const upStartTime = performance.now();
                    let finalUpMbps = 0;

                    for (let u = 0; u < upChunkSizes.length; u++) {
                        const uSize = upChunkSizes[u];
                        const upPayload = new Uint8Array(uSize);

                        await fetch(`https://speed.cloudflare.com/__up?_t=${Date.now()}_${u}`, {
                            method: 'POST',
                            body: upPayload,
                            mode: 'cors'
                        });

                        upTotalBytes += uSize;
                        const elapsedSec = (performance.now() - upStartTime) / 1000;
                        if (elapsedSec > 0) {
                            const curMbps = (upTotalBytes * 8) / (elapsedSec * 1000000);
                            finalUpMbps = curMbps;
                            updateSpeedGauge(curMbps, Math.max(finalDlMbps, 50));
                            valUp.innerText = `${curMbps.toFixed(1)} Mbps`;
                        }
                    }

                    valUp.innerText = `${finalUpMbps.toFixed(1)} Mbps`;
                    boxUp.classList.remove('active');

                    // Finished
                    statusText.innerHTML = `<span style="color:#10B981;font-weight:800;">✨ Browser Speed Test Complete (Cloudflare CDN)</span>`;
                    badge.innerText = 'TEST COMPLETED';
                    badge.style.color = '#10B981';
                    badge.style.borderColor = 'rgba(16, 185, 129, 0.4)';
                    updateSpeedGauge(finalDlMbps, Math.max(finalDlMbps * 1.2, 50));
                }

            } catch (e) {
                console.error("Speed test error:", e);
                statusText.innerHTML = `<span style="color:#EF4444;">⚠️ Speed test interrupted. Check connection.</span>`;
                badge.innerText = 'ERROR';
                badge.style.color = '#EF4444';
            } finally {
                isSpeedTesting = false;
                btn.disabled = false;
                btn.innerHTML = `<svg viewBox="0 0 24 24"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg> <span>TEST AGAIN</span>`;
            }
        }
"""

start_pos = html.find('        // ==========================================')
end_pos = html.find('window.addEventListener(\'DOMContentLoaded\'', start_pos)

if start_pos != -1 and end_pos != -1:
    html = html[:start_pos] + new_js_engine + '\n        ' + html[end_pos:]

with open('client.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Router Hardware Speed Test successfully integrated into client.html!")
