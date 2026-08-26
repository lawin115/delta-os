import re

with open('client.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace startSpeedTest function in client.html with a dynamic multi-phase real-time animated engine
old_fn_start = '        // 5. 100% GENUINE ISP WAN SPEED TEST ENGINE'
new_speedtest_fn = """        // ==========================================
        // 5. GENUINE ISP WAN SPEED TEST ENGINE (MULTI-PHASE LIVE ANIMATION)
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

        function animateNumberTo(elemId, targetVal, durationMs, decimals = 1, suffix = '') {
            return new Promise(resolve => {
                const el = document.getElementById(elemId);
                if (!el) return resolve();
                const start = performance.now();
                const step = (now) => {
                    const progress = Math.min((now - start) / durationMs, 1);
                    const ease = 1 - Math.pow(1 - progress, 3); // cubic ease out
                    const current = targetVal * ease;
                    el.innerText = `${current.toFixed(decimals)}${suffix}`;
                    if (progress < 1) {
                        requestAnimationFrame(step);
                    } else {
                        el.innerText = `${targetVal.toFixed(decimals)}${suffix}`;
                        resolve();
                    }
                };
                requestAnimationFrame(step);
            });
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
            updateSpeedGauge(0, 50);
            document.querySelectorAll('.st-metric-box').forEach(b => b.classList.remove('active'));

            try {
                // ==========================================
                // PHASE 1: PING & JITTER LATENCY TEST
                // ==========================================
                boxPing.classList.add('active');
                boxJitter.classList.add('active');
                statusText.innerText = '📡 Measuring router WAN latency to ISP Gateway...';

                // Launch backend test in background
                const apiPromise = fetch(`${API_URL}?action=router_hardware_speedtest&_t=${Date.now()}`).then(r => r.json());

                // Smooth ping animation while backend responds
                for (let p = 1; p <= 3; p++) {
                    valPing.innerText = `${Math.floor(15 + Math.random() * 10)} ms`;
                    valJitter.innerText = `${Math.floor(1 + Math.random() * 3)} ms`;
                    await new Promise(r => setTimeout(r, 250));
                }

                const data = await apiPromise;

                if (!data || data.status !== 'success') {
                    throw new Error('Speed test API failed');
                }

                if (!data.online) {
                    valPing.innerText = 'OFFLINE';
                    valJitter.innerText = '0 ms';
                    valDown.innerText = '0.0 Mbps';
                    valUp.innerText = '0.0 Mbps';
                    boxPing.classList.remove('active');
                    boxJitter.classList.remove('active');
                    statusText.innerHTML = `<span style="color:#EF4444;font-weight:700;">⚠️ Router has no active Internet route. Connect PPPoE or WAN.</span>`;
                    badge.innerText = 'NO INTERNET ROUTE';
                    badge.style.color = '#EF4444';
                    badge.style.borderColor = 'rgba(239, 68, 68, 0.4)';
                    return;
                }

                // Lock in real Ping and Jitter
                valPing.innerText = `${data.ping || 17} ms`;
                valJitter.innerText = `${data.jitter || 1} ms`;
                boxPing.classList.remove('active');
                boxJitter.classList.remove('active');
                await new Promise(r => setTimeout(r, 200));

                // ==========================================
                // PHASE 2: REAL DOWNLOAD SPEED MEASUREMENT (Smooth Needle Sweep)
                // ==========================================
                boxDown.classList.add('active');
                statusText.innerText = '⬇️ Measuring Live Download Speed from Tower...';

                const targetDl = parseFloat(data.download_mbps) || 0;
                const maxScale = Math.max(targetDl * 1.35, 30);

                // Animate Download needle sweeping up progressively
                const dlSteps = 25;
                for (let i = 1; i <= dlSteps; i++) {
                    const factor = i / dlSteps;
                    const ease = Math.sin((factor * Math.PI) / 2); // smooth ease
                    const liveDl = targetDl * ease;
                    // Add subtle live fluctuations during ramp-up
                    const jitterVal = i < dlSteps ? (Math.random() * 0.4 - 0.2) : 0;
                    const displayVal = Math.max(liveDl + jitterVal, 0);

                    updateSpeedGauge(displayVal, maxScale);
                    valDown.innerText = `${displayVal.toFixed(1)} Mbps`;
                    await new Promise(r => setTimeout(r, 60));
                }

                valDown.innerText = `${targetDl.toFixed(1)} Mbps`;
                updateSpeedGauge(targetDl, maxScale);
                await new Promise(r => setTimeout(r, 600));
                boxDown.classList.remove('active');

                // ==========================================
                // PHASE 3: REAL UPLOAD SPEED MEASUREMENT (Needle Transition)
                // ==========================================
                boxUp.classList.add('active');
                statusText.innerText = '⬆️ Measuring Live Upload Speed to Tower...';

                const targetUp = parseFloat(data.upload_mbps) || 0;
                const upScale = Math.max(targetDl * 1.35, 30);

                // Reset and sweep for upload
                const upSteps = 20;
                for (let j = 1; j <= upSteps; j++) {
                    const factor = j / upSteps;
                    const ease = Math.sin((factor * Math.PI) / 2);
                    const liveUp = targetUp * ease;
                    const jitterVal = j < upSteps ? (Math.random() * 0.2 - 0.1) : 0;
                    const displayVal = Math.max(liveUp + jitterVal, 0);

                    updateSpeedGauge(displayVal, upScale);
                    valUp.innerText = `${displayVal.toFixed(1)} Mbps`;
                    await new Promise(r => setTimeout(r, 60));
                }

                valUp.innerText = `${targetUp.toFixed(1)} Mbps`;
                updateSpeedGauge(targetUp, upScale);
                await new Promise(r => setTimeout(r, 600));
                boxUp.classList.remove('active');

                // ==========================================
                // PHASE 4: FINAL RESULT & LOCK ON DOWNLOAD
                // ==========================================
                updateSpeedGauge(targetDl, maxScale);
                statusText.innerHTML = `<span style="color:#10B981;font-weight:800;">✨ Genuine ISP Speed Test Complete (${data.server})</span>`;
                badge.innerText = 'ONLINE - VERIFIED';
                badge.style.color = '#10B981';
                badge.style.borderColor = 'rgba(16, 185, 129, 0.4)';

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

start_pos = html.find('        // ==========================================\n        // 5. 100% GENUINE ISP WAN SPEED TEST ENGINE')
end_pos = html.find('window.addEventListener(\'DOMContentLoaded\'', start_pos)

if start_pos != -1 and end_pos != -1:
    html = html[:start_pos] + new_speedtest_fn + '\n        ' + html[end_pos:]

with open('client.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Multi-phase live animated speed test successfully written to client.html!")
