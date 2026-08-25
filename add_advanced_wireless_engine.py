import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Advanced Wireless UI Card HTML
adv_wireless_card = """
                <!-- ADVANCED WIRELESS PROTOCOL & RF TUNING ENGINE -->
                <div class="card" id="adv-wireless-card" style="border: 1px solid #BAE6FD; box-shadow: 0 4px 20px -2px rgba(2, 132, 199, 0.08);">
                    <div class="card-header" style="border-bottom: 1px solid #F1F5F9; padding-bottom: 12px;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <div style="width:34px;height:34px;border-radius:10px;background:linear-gradient(135deg, #EFF6FF, #DBEAFE);border:1px solid #BFDBFE;display:flex;align-items:center;justify-content:center;">
                                <svg viewBox="0 0 24 24" style="width:18px;height:18px;fill:#0284C7;">
                                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
                                </svg>
                            </div>
                            <div>
                                <h2 style="font-size:0.98rem;font-weight:800;color:#0F172A;margin:0;">🚀 Advanced Wireless Protocol & RF Engine (بەهێزکردنی وایەرلێس)</h2>
                                <div style="font-size:0.72rem;color:#64748B;margin-top:1px;">ACK Distance Tuning, Frame Bursting, Adaptive Noise Immunity & 1-Click Profiles</div>
                            </div>
                        </div>
                        <label style="display:flex;align-items:center;gap:8px;font-size:0.78rem;font-weight:700;color:#0284C7;cursor:pointer;background:#F0F9FF;padding:5px 12px;border-radius:20px;border:1px solid #BAE6FD;">
                            <input type="checkbox" id="adv-wireless-master-toggle" onchange="toggleAdvWirelessEngine(this.checked)" style="width:16px;height:16px;cursor:pointer;" checked>
                            Engine Active
                        </label>
                    </div>

                    <!-- 1-CLICK WIRELESS OPTIMIZATION PROFILES -->
                    <div style="margin-top:12px;margin-bottom:14px;">
                        <div style="font-size:0.72rem;font-weight:800;color:#64748B;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">1-Click Instant Optimization Profiles</div>
                        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));gap:10px;">
                            <!-- Profile 1: Gaming -->
                            <div onclick="selectWirelessProfile('gaming')" id="prof-card-gaming" style="background:#F8FAFC;border:2px solid #E2E8F0;border-radius:12px;padding:12px;cursor:pointer;transition:all 0.2s ease;">
                                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
                                    <strong style="font-size:0.85rem;color:#0F172A;">🎮 Low Latency & Gaming</strong>
                                    <span class="badge badge-info" id="badge-prof-gaming" style="display:none;">ACTIVE</span>
                                </div>
                                <div style="font-size:0.72rem;color:#64748B;line-height:1.3;">HT20 clean band + Short GI + Bursting for rock-solid CCQ and lowest jitter.</div>
                            </div>

                            <!-- Profile 2: Max Speed -->
                            <div onclick="selectWirelessProfile('max_speed')" id="prof-card-max_speed" style="background:#F8FAFC;border:2px solid #E2E8F0;border-radius:12px;padding:12px;cursor:pointer;transition:all 0.2s ease;">
                                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
                                    <strong style="font-size:0.85rem;color:#0F172A;">⚡ Max Bandwidth Turbo</strong>
                                    <span class="badge badge-success" id="badge-prof-max_speed" style="display:none;">ACTIVE</span>
                                </div>
                                <div style="font-size:0.72rem;color:#64748B;line-height:1.3;">HT40 300Mbps MIMO + 28dBm Max TX Power + Packet Aggregation for top download speed.</div>
                            </div>

                            <!-- Profile 3: Long Range -->
                            <div onclick="selectWirelessProfile('long_range')" id="prof-card-long_range" style="background:#F8FAFC;border:2px solid #E2E8F0;border-radius:12px;padding:12px;cursor:pointer;transition:all 0.2s ease;">
                                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
                                    <strong style="font-size:0.85rem;color:#0F172A;">🛡️ Anti-Interference / Long Range</strong>
                                    <span class="badge badge-warning" id="badge-prof-long_range" style="display:none;">ACTIVE</span>
                                </div>
                                <div style="font-size:0.72rem;color:#64748B;line-height:1.3;">15km ACK timeout + Hardware Noise Immunity (ANI) against noisy towers.</div>
                            </div>
                        </div>
                    </div>

                    <!-- DETAILED HARDWARE TUNERS -->
                    <div id="adv-wireless-tuners-panel" style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;padding:14px;">
                        <div class="form-grid">
                            <!-- 1. Distance Slider (ACK Timeout) -->
                            <div class="form-group" style="grid-column: 1 / -1;">
                                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                                    <label style="margin:0;">🎯 Distance Tuning (ACK Timeout Calibration)</label>
                                    <span id="adv-distance-display" style="font-weight:800;font-size:0.82rem;color:#0284C7;font-family:var(--font-mono);">3,000 m (3.0 km)</span>
                                </div>
                                <input type="range" id="adv-distance-slider" min="500" max="30000" step="500" value="3000" oninput="onDistanceSliderChange(this.value)" style="width:100%;cursor:pointer;accent-color:#0284C7;">
                                <div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#64748B;margin-top:2px;">
                                    <span>500m (Close Tower)</span>
                                    <span>5,000m (5 km)</span>
                                    <span>15,000m (15 km)</span>
                                    <span>30,000m (30 km Long-Range)</span>
                                </div>
                            </div>

                            <!-- 2. TX Output Power Slider -->
                            <div class="form-group" style="grid-column: 1 / -1;">
                                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                                    <label style="margin:0;">📶 Hardware TX Output Power</label>
                                    <span id="adv-txpower-display" style="font-weight:800;font-size:0.82rem;color:#059669;font-family:var(--font-mono);">27 dBm (~500 mW)</span>
                                </div>
                                <input type="range" id="adv-txpower-slider" min="10" max="28" step="1" value="27" oninput="onTxPowerSliderChange(this.value)" style="width:100%;cursor:pointer;accent-color:#059669;">
                                <div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#64748B;margin-top:2px;">
                                    <span>10 dBm (10 mW)</span>
                                    <span>20 dBm (100 mW)</span>
                                    <span>25 dBm (316 mW)</span>
                                    <span>28 dBm (630 mW Max Power)</span>
                                </div>
                            </div>

                            <!-- 3. Channel Bandwidth Mode -->
                            <div class="form-group">
                                <label>Channel Bandwidth (HT Mode)</label>
                                <select class="form-control" id="adv-htmode-select">
                                    <option value="HT40">HT40 - 40 MHz (300 Mbps Turbo)</option>
                                    <option value="HT20">HT20 - 20 MHz (150 Mbps Standard Clean)</option>
                                </select>
                            </div>

                            <!-- 4. Toggle: Frame Bursting & Packet Aggregation -->
                            <div class="form-group">
                                <label>Packet Aggregation (Frame Bursting)</label>
                                <select class="form-control" id="adv-bursting-select">
                                    <option value="1">Enabled (A-MPDU / A-MSDU Bursting Active)</option>
                                    <option value="0">Disabled (Standard Sequential Transmission)</option>
                                </select>
                            </div>

                            <!-- 5. Toggle: Hardware Adaptive Noise Immunity (ANI) -->
                            <div class="form-group">
                                <label>Adaptive Noise Immunity (ANI)</label>
                                <select class="form-control" id="adv-ani-select">
                                    <option value="1">Enabled (Atheros AR9344 Hardware Anti-Noise Filter)</option>
                                    <option value="0">Disabled (Raw RF Receiver)</option>
                                </select>
                            </div>

                            <!-- 6. Toggle: Short Guard Interval (Short GI 400ns) -->
                            <div class="form-group">
                                <label>Short Guard Interval (Short GI)</label>
                                <select class="form-control" id="adv-shortgi-select">
                                    <option value="1">Enabled (400ns - Maximum Bitrate Throughput)</option>
                                    <option value="0">Disabled (800ns - Robust Multipath Fallback)</option>
                                </select>
                            </div>
                        </div>

                        <div style="display:flex;align-items:center;gap:12px;margin-top:14px;flex-wrap:wrap;">
                            <button type="button" onclick="saveWirelessAdvSettings()" class="btn btn-primary" style="font-weight:700;">
                                <svg viewBox="0 0 24 24" style="width:15px;height:15px;fill:currentColor;">
                                    <path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z" />
                                </svg>
                                Save & Apply Wireless Optimization
                            </button>
                            <span id="adv-wireless-save-msg" style="font-size:0.8rem;font-weight:700;display:none;"></span>
                        </div>
                    </div>
                </div>
"""

# Insert the card into index.html right after the radio settings form
radio_card_end = '<!-- TAB: DASHBOARD OVERVIEW -->'
if radio_card_end in html:
    html = html.replace(radio_card_end, adv_wireless_card + '\n\n            ' + radio_card_end)

# 2. JavaScript logic for Advanced Wireless Engine
adv_js_code = """
        // ==========================================
        // ADVANCED WIRELESS RF ENGINE & TUNING LOGIC
        // ==========================================
        let currentAdvProfile = 'gaming';

        function onDistanceSliderChange(val) {
            const num = parseInt(val);
            const km = (num / 1000).toFixed(1);
            document.getElementById('adv-distance-display').innerText = `${num.toLocaleString()} m (${km} km)`;
        }

        function onTxPowerSliderChange(val) {
            const num = parseInt(val);
            let mw = 500;
            if (num <= 10) mw = 10;
            else if (num <= 15) mw = 32;
            else if (num <= 20) mw = 100;
            else if (num <= 23) mw = 200;
            else if (num <= 25) mw = 316;
            else if (num <= 27) mw = 500;
            else if (num >= 28) mw = 630;
            document.getElementById('adv-txpower-display').innerText = `${num} dBm (~${mw} mW)`;
        }

        function toggleAdvWirelessEngine(enabled) {
            const panel = document.getElementById('adv-wireless-tuners-panel');
            if (panel) {
                panel.style.opacity = enabled ? '1' : '0.4';
                panel.style.pointerEvents = enabled ? 'auto' : 'none';
            }
        }

        function selectWirelessProfile(profileName) {
            currentAdvProfile = profileName;
            ['gaming', 'max_speed', 'long_range'].forEach(p => {
                const card = document.getElementById(`prof-card-${p}`);
                const badge = document.getElementById(`badge-prof-${p}`);
                if (card) {
                    if (p === profileName) {
                        card.style.borderColor = '#0284C7';
                        card.style.background = '#F0F9FF';
                    } else {
                        card.style.borderColor = '#E2E8F0';
                        card.style.background = '#F8FAFC';
                    }
                }
                if (badge) badge.style.display = (p === profileName) ? 'inline-block' : 'none';
            });

            if (profileName === 'gaming') {
                document.getElementById('adv-distance-slider').value = 3000;
                onDistanceSliderChange(3000);
                document.getElementById('adv-txpower-slider').value = 25;
                onTxPowerSliderChange(25);
                document.getElementById('adv-htmode-select').value = 'HT20';
                document.getElementById('adv-bursting-select').value = '1';
                document.getElementById('adv-ani-select').value = '1';
                document.getElementById('adv-shortgi-select').value = '1';
            } else if (profileName === 'max_speed') {
                document.getElementById('adv-distance-slider').value = 1000;
                onDistanceSliderChange(1000);
                document.getElementById('adv-txpower-slider').value = 28;
                onTxPowerSliderChange(28);
                document.getElementById('adv-htmode-select').value = 'HT40';
                document.getElementById('adv-bursting-select').value = '1';
                document.getElementById('adv-ani-select').value = '1';
                document.getElementById('adv-shortgi-select').value = '1';
            } else if (profileName === 'long_range') {
                document.getElementById('adv-distance-slider').value = 15000;
                onDistanceSliderChange(15000);
                document.getElementById('adv-txpower-slider').value = 28;
                onTxPowerSliderChange(28);
                document.getElementById('adv-htmode-select').value = 'HT20';
                document.getElementById('adv-bursting-select').value = '1';
                document.getElementById('adv-ani-select').value = '1';
                document.getElementById('adv-shortgi-select').value = '0';
            }
        }

        async function loadWirelessAdvSettings() {
            try {
                const res = await fetch(`${API_URL}?action=get_wireless_adv&token=${authToken}`);
                const data = await res.json();
                if (data.status === 'success') {
                    const masterToggle = document.getElementById('adv-wireless-master-toggle');
                    if (masterToggle) masterToggle.checked = data.enabled !== false;
                    toggleAdvWirelessEngine(data.enabled !== false);

                    if (data.distance) {
                        document.getElementById('adv-distance-slider').value = data.distance;
                        onDistanceSliderChange(data.distance);
                    }
                    if (data.txpower) {
                        document.getElementById('adv-txpower-slider').value = data.txpower;
                        onTxPowerSliderChange(data.txpower);
                    }
                    if (data.htmode) document.getElementById('adv-htmode-select').value = data.htmode;
                    if (data.bursting !== undefined) document.getElementById('adv-bursting-select').value = data.bursting ? '1' : '0';
                    if (data.ani !== undefined) document.getElementById('adv-ani-select').value = data.ani ? '1' : '0';
                    if (data.short_gi !== undefined) document.getElementById('adv-shortgi-select').value = data.short_gi ? '1' : '0';
                    if (data.active_profile) selectWirelessProfile(data.active_profile);
                }
            } catch (e) { console.error('Error loading wireless adv settings:', e); }
        }

        async function saveWirelessAdvSettings() {
            const enabled = document.getElementById('adv-wireless-master-toggle').checked ? '1' : '0';
            const distance = document.getElementById('adv-distance-slider').value;
            const txpower = document.getElementById('adv-txpower-slider').value;
            const htmode = document.getElementById('adv-htmode-select').value;
            const bursting = document.getElementById('adv-bursting-select').value;
            const ani = document.getElementById('adv-ani-select').value;
            const short_gi = document.getElementById('adv-shortgi-select').value;
            const noscan = (htmode === 'HT40') ? '1' : '0';
            const msgEl = document.getElementById('adv-wireless-save-msg');

            if (msgEl) {
                msgEl.style.display = 'inline-block';
                msgEl.style.color = '#0284C7';
                msgEl.innerText = 'Applying RF Protocol & Calibration settings...';
            }

            try {
                const query = `action=set_wireless_adv&enabled=${enabled}&distance=${distance}&txpower=${txpower}&htmode=${htmode}&bursting=${bursting}&ani=${ani}&short_gi=${short_gi}&noscan=${noscan}&profile=${currentAdvProfile}&token=${authToken}`;
                const res = await fetch(`${API_URL}?${query}`);
                const data = await res.json();
                if (data.status === 'success') {
                    if (msgEl) {
                        msgEl.style.color = '#059669';
                        msgEl.innerText = '✅ Wireless Protocol Settings Applied Successfully!';
                        setTimeout(() => { msgEl.style.display = 'none'; }, 4000);
                    }
                } else {
                    if (msgEl) {
                        msgEl.style.color = '#DC2626';
                        msgEl.innerText = '❌ Failed to apply settings: ' + (data.message || 'Unknown error');
                    }
                }
            } catch (e) {
                if (msgEl) {
                    msgEl.style.color = '#DC2626';
                    msgEl.innerText = '❌ Error communicating with router.';
                }
            }
        }
"""

# Insert JS code into index.html
js_anchor = '// DIAGNOSTICS & PING'
if js_anchor in html:
    html = html.replace(js_anchor, adv_js_code + '\n\n        ' + js_anchor)

# Also call loadWirelessAdvSettings() on startup
dom_anchor = "refreshData();"
if dom_anchor in html:
    html = html.replace(dom_anchor, dom_anchor + "\n                        loadWirelessAdvSettings();")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Advanced Wireless Protocol Engine successfully integrated into index.html!")
