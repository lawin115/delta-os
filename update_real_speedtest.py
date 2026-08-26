import re

with open('client.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the startSpeedTest function in client.html with high-accuracy real multi-stream speedtest engine
old_fn_start = '        // 5. LIVE SPEED TEST ENGINE'
new_speedtest_engine = """        // ==========================================
        // 5. GENUINE REAL-TIME HIGH PRECISION SPEED TEST ENGINE
        // ==========================================
        let isSpeedTesting = false;

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
                // Determine whether global Cloudflare CDN is reachable
                let useCloudflare = true;
                try {
                    const testPing = await fetch('https://speed.cloudflare.com/__down?bytes=0', { method: 'GET', cache: 'no-store', mode: 'cors' });
                    if (!testPing.ok) useCloudflare = false;
                } catch (e) {
                    useCloudflare = false;
                }

                // ==========================================
                // PHASE 1: PING & JITTER TEST (6 fast rounds)
                // ==========================================
                boxPing.classList.add('active');
                boxJitter.classList.add('active');
                statusText.innerText = useCloudflare ? '📡 Testing Latency to Cloudflare Global CDN...' : '📡 Testing Latency to Local Gateway...';

                let pings = [];
                const pingUrl = useCloudflare ? 'https://speed.cloudflare.com/__down?bytes=0' : `${API_URL}?action=speedtest_ping`;

                for (let i = 0; i < 6; i++) {
                    const t0 = performance.now();
                    await fetch(`${pingUrl}&_t=${Date.now()}_${i}`, { cache: 'no-store', mode: useCloudflare ? 'cors' : 'same-origin' });
                    const t1 = performance.now();
                    const rtt = Math.max(t1 - t0, 1);
                    pings.push(rtt);
                    valPing.innerText = `${Math.round(rtt)} ms`;
                    await new Promise(r => setTimeout(r, 40));
                }

                // Discard highest spike for clean average
                pings.sort((a, b) => a - b);
                const usefulPings = pings.slice(0, 5);
                const avgPing = Math.round(usefulPings.reduce((a, b) => a + b, 0) / usefulPings.length);
                
                let jitter = 0;
                for (let i = 1; i < usefulPings.length; i++) {
                    jitter += Math.abs(usefulPings[i] - usefulPings[i - 1]);
                }
                jitter = Math.round(jitter / (usefulPings.length - 1));

                valPing.innerText = `${avgPing} ms`;
                valJitter.innerText = `${jitter} ms`;
                boxPing.classList.remove('active');
                boxJitter.classList.remove('active');
                await new Promise(r => setTimeout(r, 200));

                // ==========================================
                // PHASE 2: DOWNLOAD THROUGHPUT TEST (Progressive Streaming)
                // ==========================================
                boxDown.classList.add('active');
                statusText.innerText = '⬇️ Testing Download Throughput...';

                const dlChunkSizes = useCloudflare ? [1000000, 5000000, 10000000] : [1048576, 3145728, 5242880];
                let dlTotalBytes = 0;
                const dlStartTime = performance.now();
                let lastGaugeUpdate = 0;
                let finalDlMbps = 0;

                for (let c = 0; c < dlChunkSizes.length; c++) {
                    const cSize = dlChunkSizes[c];
                    const dlUrl = useCloudflare ? `https://speed.cloudflare.com/__down?bytes=${cSize}` : `${API_URL}?action=speedtest_payload&size=${cSize}`;
                    
                    const res = await fetch(`${dlUrl}&_t=${Date.now()}_${c}`, { cache: 'no-store', mode: useCloudflare ? 'cors' : 'same-origin' });
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

                // ==========================================
                // PHASE 3: UPLOAD THROUGHPUT TEST (Binary POST Streaming)
                // ==========================================
                boxUp.classList.add('active');
                statusText.innerText = '⬆️ Testing Upload Throughput...';
                updateSpeedGauge(0, Math.max(finalDlMbps, 50));

                const upChunkSizes = useCloudflare ? [500000, 1500000, 3000000] : [524288, 1048576, 2097152];
                let upTotalBytes = 0;
                const upStartTime = performance.now();
                let finalUpMbps = 0;

                for (let u = 0; u < upChunkSizes.length; u++) {
                    const uSize = upChunkSizes[u];
                    const upPayload = new Uint8Array(uSize);
                    const upUrl = useCloudflare ? 'https://speed.cloudflare.com/__up' : `${API_URL}?action=speedtest_upload`;

                    await fetch(`${upUrl}?_t=${Date.now()}_${u}`, {
                        method: 'POST',
                        body: upPayload,
                        mode: useCloudflare ? 'cors' : 'same-origin'
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

                // ==========================================
                // FINISHED: REAL SPEED DISPLAY
                // ==========================================
                const serverName = useCloudflare ? 'Cloudflare Anycast CDN' : 'Delta 5G Local Gateway';
                statusText.innerHTML = `<span style="color:#10B981;font-weight:800;">✨ Real Speed Test Complete (${serverName})</span>`;
                badge.innerText = 'TEST COMPLETED';
                badge.style.color = '#10B981';
                badge.style.borderColor = 'rgba(16, 185, 129, 0.4)';
                updateSpeedGauge(finalDlMbps, Math.max(finalDlMbps * 1.2, 50));

            } catch (e) {
                console.error("Speed test error:", e);
                statusText.innerHTML = `<span style="color:#EF4444;">⚠️ Speed test interrupted. Check WAN connection.</span>`;
                badge.innerText = 'ERROR';
                badge.style.color = '#EF4444';
            } finally {
                isSpeedTesting = false;
                btn.disabled = false;
                btn.innerHTML = `<svg viewBox="0 0 24 24"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg> <span>TEST AGAIN</span>`;
            }
        }
"""

start_pos = html.find(old_fn_start)
end_pos = html.find('window.addEventListener(\'DOMContentLoaded\'', start_pos)

if start_pos != -1 and end_pos != -1:
    html = html[:start_pos] + new_speedtest_engine + '\n        ' + html[end_pos:]

with open('client.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Genuine real-time Speed Test engine successfully integrated into client.html!")
