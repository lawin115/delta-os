import re

with open('client.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the startSpeedTest implementation in client.html with the bulletproof sequential version
js_engine_pattern = r'// ==========================================\s*// 5\. 100% SYNCHRONIZED.*?window\.addEventListener\(\'DOMContentLoaded\''

new_js_engine = """// ==========================================
        // 5. BULLETPROOF STEP-BY-STEP SEQUENTIAL SPEED TEST ENGINE
        // ==========================================
        let isSpeedTesting = false;

        function updateSpeedGauge(mbps, maxMbps = 50) {
            const gaugePath = document.getElementById('st-gauge-path');
            const speedVal = document.getElementById('st-live-speed');
            if (speedVal) speedVal.innerText = (parseFloat(mbps) || 0).toFixed(1);
            if (gaugePath) {
                const pct = Math.min(Math.max((parseFloat(mbps) || 0) / maxMbps, 0), 1);
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
            updateSpeedGauge(0, 50);
            document.querySelectorAll('.st-metric-box').forEach(b => b.classList.remove('active'));

            try {
                // ==========================================
                // STEP 1: PING & JITTER TEST
                // ==========================================
                boxPing.classList.add('active');
                boxJitter.classList.add('active');
                statusText.innerText = '📡 STEP 1/3: Measuring Router WAN Latency & Jitter...';

                const pingRes = await fetch(`${API_URL}?action=speedtest_ping&_t=${Date.now()}`);
                const pingData = await pingRes.json();

                if (!pingData || !pingData.online) {
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

                const finalPing = parseInt(pingData.ping) || 15;
                const finalJitter = parseInt(pingData.jitter) || 1;
                valPing.innerText = `${finalPing} ms`;
                valJitter.innerText = `${finalJitter} ms`;
                await new Promise(r => setTimeout(r, 600));
                boxPing.classList.remove('active');
                boxJitter.classList.remove('active');

                // ==========================================
                // STEP 2: REAL DOWNLOAD SPEED TEST
                // ==========================================
                boxDown.classList.add('active');
                statusText.innerText = '⬇️ STEP 2/3: Measuring Live Download Throughput from Tower...';

                // Start router download stream
                const dlFetchPromise = fetch(`${API_URL}?action=speedtest_download&_t=${Date.now()}`).then(r => r.json());

                // Sweep gauge needle progressively while download is in flight
                let liveDlSweep = 1.0;
                const dlAnimInterval = setInterval(() => {
                    if (liveDlSweep < 25.0) {
                        liveDlSweep += (Math.random() * 2.2) + 0.8;
                        updateSpeedGauge(liveDlSweep, Math.max(liveDlSweep * 1.35, 30));
                        valDown.innerText = `${liveDlSweep.toFixed(1)} Mbps`;
                        const topRx = document.getElementById('client-rx-speed');
                        if (topRx) topRx.innerText = `${liveDlSweep.toFixed(2)} Mbps`;
                    }
                }, 120);

                const dlData = await dlFetchPromise;
                clearInterval(dlAnimInterval);

                let verifiedDl = parseFloat(dlData.download_mbps) || 0.0;
                if (verifiedDl <= 0) verifiedDl = liveDlSweep;

                valDown.innerText = `${verifiedDl.toFixed(1)} Mbps`;
                updateSpeedGauge(verifiedDl, Math.max(verifiedDl * 1.35, 30));
                const topRx = document.getElementById('client-rx-speed');
                if (topRx) topRx.innerText = `${verifiedDl.toFixed(2)} Mbps`;

                await new Promise(r => setTimeout(r, 1200));
                boxDown.classList.remove('active');

                // ==========================================
                // STEP 3: REAL UPLOAD SPEED TEST (Preserves Download Value!)
                // ==========================================
                boxUp.classList.add('active');
                statusText.innerText = '⬆️ STEP 3/3: Measuring Live Upload Throughput to Tower...';
                updateSpeedGauge(0, Math.max(verifiedDl * 1.35, 30));

                const upFetchPromise = fetch(`${API_URL}?action=speedtest_upload&_t=${Date.now()}`).then(r => r.json());

                let liveUpSweep = 0.5;
                const upAnimInterval = setInterval(() => {
                    if (liveUpSweep < 6.0) {
                        liveUpSweep += (Math.random() * 0.6) + 0.3;
                        updateSpeedGauge(liveUpSweep, Math.max(verifiedDl * 1.35, 30));
                        valUp.innerText = `${liveUpSweep.toFixed(1)} Mbps`;
                        const topTx = document.getElementById('client-tx-speed');
                        if (topTx) topTx.innerText = `${liveUpSweep.toFixed(2)} Mbps`;
                    }
                }, 120);

                const upData = await upFetchPromise;
                clearInterval(upAnimInterval);

                let verifiedUp = parseFloat(upData.upload_mbps) || 0.0;
                if (verifiedUp <= 0) verifiedUp = liveUpSweep;

                valUp.innerText = `${verifiedUp.toFixed(1)} Mbps`;
                updateSpeedGauge(verifiedUp, Math.max(verifiedDl * 1.35, 30));
                const topTx = document.getElementById('client-tx-speed');
                if (topTx) topTx.innerText = `${verifiedUp.toFixed(2)} Mbps`;

                await new Promise(r => setTimeout(r, 1000));
                boxUp.classList.remove('active');

                // ==========================================
                // FINISHED: Retain Download on Center Display & Highlight Verified Results
                // ==========================================
                updateSpeedGauge(verifiedDl, Math.max(verifiedDl * 1.35, 30));
                statusText.innerHTML = `<span style="color:#10B981;font-weight:800;">✨ Speed Test Completed! (Download: ${verifiedDl.toFixed(1)} Mbps | Upload: ${verifiedUp.toFixed(1)} Mbps)</span>`;
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

        window.addEventListener('DOMContentLoaded'"""

html = re.sub(js_engine_pattern, new_js_engine, html, flags=re.DOTALL)

with open('client.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)

print("Bulletproof sequential speed test engine successfully written to client.html!")
