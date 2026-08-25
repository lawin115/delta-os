import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update CSS Variables and master styles
css_replacement = """        :root {
            --bg-body: #080C14;
            --bg-sidebar: #0C1220;
            --bg-card: #0F172A;
            --bg-card-hover: #1E293B;
            --bg-input: #080C14;
            --border-color: rgba(255, 255, 255, 0.08);
            --border-focus: #0EA5E9;
            --primary: #0EA5E9;
            --primary-hover: #0284C7;
            --primary-glow: rgba(14, 165, 233, 0.25);
            --accent: #38BDF8;
            --accent-glow: rgba(56, 189, 248, 0.2);
            --success: #10B981;
            --warning: #F59E0B;
            --danger: #EF4444;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --safe-bottom: env(safe-area-inset-bottom, 0px);
            --card-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.06);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            font-family: var(--font-sans);
            background-color: var(--bg-body);
            color: var(--text-main);
            display: flex;
            height: 100vh;
            height: 100dvh;
            overflow: hidden;
            -webkit-font-smoothing: antialiased;
            background-image: radial-gradient(circle at 50% 0%, rgba(14, 165, 233, 0.06) 0%, transparent 60%);
        }

        ::-webkit-scrollbar {
            width: 5px;
            height: 5px;
        }

        ::-webkit-scrollbar-track {
            background: #080C14;
        }

        ::-webkit-scrollbar-thumb {
            background: #1E293B;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary);
        }

        /* LOGIN SCREEN OVERLAY */
        #login-screen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: radial-gradient(circle at 50% 30%, #1E293B 0%, #080C14 80%);
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 16px;
        }

        .login-card {
            background: #0F172A;
            border-radius: 18px;
            width: 100%;
            max-width: 400px;
            padding: 28px 24px;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(255, 255, 255, 0.1);
            animation: loginEntrance 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            text-align: center;
        }

        @keyframes loginEntrance {
            from {
                opacity: 0;
                transform: scale(0.94) translateY(16px);
            }

            to {
                opacity: 1;
                transform: scale(1) translateY(0);
            }
        }

        .login-logo {
            width: 54px;
            height: 54px;
            border-radius: 14px;
            background: rgba(14, 165, 233, 0.15);
            border: 1px solid rgba(14, 165, 233, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 12px;
            box-shadow: 0 4px 14px rgba(14, 165, 233, 0.25);
        }

        .login-logo img {
            width: 36px;
            height: 36px;
            object-fit: contain;
        }

        .login-title {
            font-size: 1.25rem;
            font-weight: 800;
            color: #F8FAFC;
            letter-spacing: -0.3px;
        }

        .login-subtitle {
            font-size: 0.76rem;
            color: var(--text-muted);
            margin-top: 3px;
            margin-bottom: 20px;
        }

        .login-alert {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.35);
            color: #F87171;
            padding: 10px 12px;
            border-radius: 8px;
            font-size: 0.78rem;
            font-weight: 600;
            margin-bottom: 14px;
            display: none;
            text-align: left;
            transition: all 0.2s ease;
        }

        .login-alert.shake {
            animation: alertShake 0.4s ease;
        }

        @keyframes alertShake {
            0%, 100% { transform: translateX(0); }
            20%, 60% { transform: translateX(-6px); }
            40%, 80% { transform: translateX(6px); }
        }

        .input-password-wrapper {
            position: relative;
            display: flex;
            align-items: center;
        }

        .password-toggle-btn {
            position: absolute;
            right: 8px;
            background: none;
            border: none;
            cursor: pointer;
            color: #94A3B8;
            padding: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            transition: color 0.15s;
        }

        .password-toggle-btn:hover {
            color: #F8FAFC;
        }

        .caps-lock-badge {
            display: none;
            font-size: 0.68rem;
            font-weight: 700;
            color: #FBBF24;
            background: rgba(245, 158, 11, 0.15);
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        .security-badge-footer {
            margin-top: 18px;
            padding-top: 14px;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 14px;
            font-size: 0.7rem;
            color: #94A3B8;
        }

        .security-badge-item {
            display: flex;
            align-items: center;
            gap: 4px;
            font-weight: 500;
        }

        .pass-strength-bar {
            height: 4px;
            border-radius: 2px;
            background: #1E293B;
            margin-top: 6px;
            overflow: hidden;
        }

        .pass-strength-fill {
            height: 100%;
            width: 0%;
            transition: all 0.3s ease;
        }

        /* SIDEBAR DRAWER & BACKDROP */
        .sidebar-backdrop {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.65);
            backdrop-filter: blur(8px);
            z-index: 999;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.25s ease;
        }

        .sidebar-backdrop.active {
            opacity: 1;
            pointer-events: auto;
        }

        .sidebar {
            width: 250px;
            background: var(--bg-sidebar);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
            transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1);
            z-index: 1000;
        }

        .sidebar-brand {
            padding: 16px 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border-color);
            background: #0C1220;
        }

        .brand-header-flex {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .brand-logo {
            width: 34px;
            height: 34px;
            border-radius: 9px;
            background: rgba(14, 165, 233, 0.15);
            border: 1px solid rgba(14, 165, 233, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(14, 165, 233, 0.2);
        }

        .brand-logo img {
            width: 22px;
            height: 22px;
            object-fit: contain;
        }

        .brand-text h2 {
            font-size: 0.95rem;
            font-weight: 800;
            color: #F8FAFC;
            letter-spacing: -0.2px;
            line-height: 1.1;
        }

        .brand-text span {
            font-size: 0.65rem;
            font-weight: 700;
            color: #38BDF8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .sidebar-close-btn {
            display: none;
            background: #1E293B;
            border: none;
            width: 28px;
            height: 28px;
            border-radius: 6px;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: #94A3B8;
        }

        .nav-list {
            list-style: none;
            padding: 10px 8px;
            overflow-y: auto;
            flex-grow: 1;
        }

        .nav-section-title {
            font-size: 0.65rem;
            font-weight: 800;
            text-transform: uppercase;
            color: #64748B;
            padding: 10px 10px 4px;
            letter-spacing: 0.8px;
        }

        .nav-item {
            margin-bottom: 2px;
        }

        .nav-link {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 10px;
            border-radius: 8px;
            color: #94A3B8;
            text-decoration: none;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.18s ease;
            user-select: none;
        }

        .nav-link svg {
            width: 16px;
            height: 16px;
            fill: #64748B;
            transition: fill 0.18s ease;
            flex-shrink: 0;
        }

        .nav-link:hover {
            background: rgba(255, 255, 255, 0.05);
            color: #F8FAFC;
        }

        .nav-link:hover svg {
            fill: #38BDF8;
        }

        .nav-link.active {
            background: rgba(14, 165, 233, 0.14);
            color: #38BDF8;
            font-weight: 700;
            border: 1px solid rgba(14, 165, 233, 0.25);
        }

        .nav-link.active svg {
            fill: #38BDF8;
        }

        /* ACCORDION / SUBMENU */
        .nav-group-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
        }

        .nav-chevron {
            width: 14px;
            height: 14px;
            transition: transform 0.2s ease;
        }

        .nav-group.open .nav-chevron {
            transform: rotate(90deg);
        }

        .sub-nav-list {
            list-style: none;
            padding-left: 24px;
            display: none;
            margin-top: 2px;
            margin-bottom: 3px;
        }

        .nav-group.open .sub-nav-list {
            display: block;
        }

        .sub-nav-link {
            display: flex;
            align-items: center;
            gap: 7px;
            padding: 6px 8px;
            border-radius: 6px;
            color: #64748B;
            font-size: 0.76rem;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.18s ease;
        }

        .sub-nav-link:hover {
            color: #F8FAFC;
            background: rgba(255, 255, 255, 0.04);
        }

        .sub-nav-link.active {
            color: #38BDF8;
            font-weight: 700;
            background: rgba(14, 165, 233, 0.1);
        }

        .sub-nav-bullet {
            width: 4px;
            height: 4px;
            border-radius: 50%;
            background: #475569;
        }

        .sub-nav-link.active .sub-nav-bullet {
            background: #38BDF8;
        }

        /* MAIN CONTAINER */
        .main-wrapper {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            height: 100vh;
            height: 100dvh;
            overflow: hidden;
            min-width: 0;
        }

        /* TOPBAR */
        .topbar {
            height: 54px;
            background: #0C1220;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16px;
            flex-shrink: 0;
            z-index: 50;
            gap: 8px;
        }

        .topbar-left {
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 0;
            flex-grow: 1;
        }

        .mobile-menu-btn {
            display: none;
            background: #1E293B;
            border: 1px solid var(--border-color);
            cursor: pointer;
            padding: 7px;
            border-radius: 8px;
            flex-direction: column;
            gap: 3.5px;
            flex-shrink: 0;
        }

        .mobile-menu-btn span {
            width: 18px;
            height: 2px;
            background: #F8FAFC;
            border-radius: 2px;
        }

        .topbar-title {
            min-width: 0;
            overflow: hidden;
        }

        .topbar-title h1 {
            font-size: 0.96rem;
            font-weight: 800;
            color: #F8FAFC;
            letter-spacing: -0.2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .topbar-actions {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-shrink: 0;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 10px;
            background: rgba(14, 165, 233, 0.12);
            border: 1px solid rgba(14, 165, 233, 0.25);
            border-radius: 16px;
            font-size: 0.72rem;
            font-weight: 700;
            color: #38BDF8;
            letter-spacing: 0.3px;
            white-space: nowrap;
        }

        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #10B981;
            box-shadow: 0 0 8px #10B981;
            animation: livePulse 2s infinite;
            flex-shrink: 0;
        }

        @keyframes livePulse {
            0% { transform: scale(0.95); opacity: 0.8; }
            50% { transform: scale(1.15); opacity: 1; }
            100% { transform: scale(0.95); opacity: 0.8; }
        }

        /* CONTENT AREA */
        .content-area {
            padding: 16px 18px;
            overflow-y: auto;
            flex-grow: 1;
            padding-bottom: 40px;
            -webkit-overflow-scrolling: touch;
        }

        .tab-pane {
            display: none;
            animation: fadeIn 0.22s ease;
        }

        .tab-pane.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(4px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* BUTTONS */
        .btn {
            min-height: 34px;
            padding: 6px 12px;
            border-radius: 7px;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            border: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: all 0.18s ease;
            white-space: nowrap;
            user-select: none;
        }

        .btn:active {
            transform: scale(0.96);
        }

        .btn svg {
            width: 14px;
            height: 14px;
            flex-shrink: 0;
        }

        .btn-primary {
            background: linear-gradient(135deg, #0EA5E9, #0284C7);
            color: #FFFFFF;
            box-shadow: 0 3px 10px rgba(14, 165, 233, 0.35);
        }

        .btn-primary:hover {
            box-shadow: 0 4px 14px rgba(14, 165, 233, 0.5);
        }

        .btn-secondary {
            background: #1E293B;
            color: #38BDF8;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .btn-secondary:hover {
            background: #334155;
            color: #F8FAFC;
        }

        .btn-success {
            background: #10B981;
            color: #FFFFFF;
            box-shadow: 0 3px 10px rgba(16, 185, 129, 0.3);
        }

        .btn-success:hover {
            background: #059669;
        }

        .btn-danger {
            background: rgba(239, 68, 68, 0.15);
            color: #F87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .btn-danger:hover {
            background: #EF4444;
            color: #FFFFFF;
        }

        /* CARDS & TABLES */
        .card {
            background: #0F172A;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 14px;
            box-shadow: var(--card-shadow);
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 14px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            flex-wrap: wrap;
            gap: 8px;
        }

        .card-header h2 {
            font-size: 0.92rem;
            font-weight: 700;
            color: #F8FAFC;
        }

        .table-responsive {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(15, 23, 42, 0.5);
        }

        table {
            width: 100%;
            min-width: 540px;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.8rem;
        }

        th {
            background: rgba(255, 255, 255, 0.04);
            color: #94A3B8;
            padding: 10px 12px;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.67rem;
            letter-spacing: 0.5px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            white-space: nowrap;
        }

        td {
            padding: 10px 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            white-space: nowrap;
            color: #F8FAFC;
        }

        tr:hover td {
            background: rgba(255, 255, 255, 0.03);
        }

        .badge {
            display: inline-block;
            padding: 3px 7px;
            border-radius: 5px;
            font-size: 0.68rem;
            font-weight: 700;
            font-family: var(--font-mono);
            letter-spacing: 0.2px;
            white-space: nowrap;
        }

        .badge-success {
            background: rgba(16, 185, 129, 0.15);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .badge-danger {
            background: rgba(239, 68, 68, 0.15);
            color: #F87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .badge-info {
            background: rgba(14, 165, 233, 0.15);
            color: #38BDF8;
            border: 1px solid rgba(14, 165, 233, 0.3);
        }

        .badge-warning {
            background: rgba(245, 158, 11, 0.15);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        /* FORMS */
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 12px;
        }

        .form-group {
            margin-bottom: 10px;
        }

        .form-group label {
            display: block;
            font-size: 0.74rem;
            font-weight: 700;
            color: #94A3B8;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }

        .form-control {
            width: 100%;
            min-height: 38px;
            padding: 6px 10px;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 7px;
            font-size: 0.84rem;
            font-family: var(--font-sans);
            color: #F8FAFC;
            background: #080C14;
            outline: none;
            transition: all 0.18s ease;
        }

        .form-control:focus {
            border-color: var(--border-focus);
            box-shadow: 0 0 0 3px var(--primary-glow);
        }

        /* STAT CARDS */
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin-bottom: 14px;
        }

        .stat-card {
            background: #0F172A;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 14px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            box-shadow: var(--card-shadow);
            transition: transform 0.18s, border-color 0.18s;
        }

        .stat-card:hover {
            border-color: rgba(14, 165, 233, 0.4);
            transform: translateY(-2px);
        }

        .stat-icon {
            width: 38px;
            height: 38px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }

        .stat-icon svg {
            width: 19px;
            height: 19px;
            fill: #FFFFFF;
        }

        .stat-icon.blue { background: linear-gradient(135deg, #0EA5E9, #0284C7); }
        .stat-icon.green { background: linear-gradient(135deg, #10B981, #059669); }
        .stat-icon.purple { background: linear-gradient(135deg, #8B5CF6, #6366F1); }
        .stat-icon.orange { background: linear-gradient(135deg, #F59E0B, #D97706); }

        .stat-info {
            min-width: 0;
            flex-grow: 1;
        }

        .stat-info h3 {
            font-size: 0.68rem;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            margin-bottom: 2px;
        }

        .stat-info .stat-value {
            font-size: 1.15rem;
            font-weight: 700;
            color: #F8FAFC;
            font-family: var(--font-mono);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .stat-desc {
            font-size: 0.7rem;
            color: #64748B;
            margin-top: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .progress-bar-container {
            width: 100%;
            height: 6px;
            background: #1E293B;
            border-radius: 3px;
            overflow: hidden;
            margin-top: 4px;
        }

        .progress-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #0EA5E9, #38BDF8);
            border-radius: 3px;
            transition: width 0.5s ease;
        }

        /* 5G RADAR GRAPHIC */
        .radar-box {
            position: relative;
            width: 76px;
            height: 76px;
            border-radius: 50%;
            background: radial-gradient(circle, #0284C7 0%, #080C14 70%);
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            box-shadow: 0 0 12px rgba(2, 132, 199, 0.3);
            transition: all 0.4s ease;
        }

        .radar-box.locked {
            background: radial-gradient(circle, #10B981 0%, #080C14 70%) !important;
            box-shadow: 0 0 16px rgba(16, 185, 129, 0.45) !important;
        }

        .radar-box.scanning {
            background: radial-gradient(circle, #0284C7 0%, #080C14 70%) !important;
            box-shadow: 0 0 14px rgba(2, 132, 199, 0.4) !important;
        }

        .radar-sweep-arm {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: conic-gradient(from 0deg, rgba(56, 189, 248, 0.7) 0deg, rgba(2, 132, 199, 0.1) 50deg, transparent 60deg);
            animation: radarSweep 1.4s infinite linear;
            transition: opacity 0.3s ease;
        }

        .radar-sweep-arm.locked {
            animation-play-state: paused !important;
            opacity: 0 !important;
        }

        @keyframes radarSweep {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* MODAL */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(8px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            padding: 12px;
        }

        .modal-overlay.active {
            display: flex;
        }

        .modal-card {
            background: #0F172A;
            border-radius: 14px;
            width: 100%;
            max-width: 480px;
            padding: 20px;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.1);
            animation: modalPop 0.22s ease;
            max-height: 90vh;
            overflow-y: auto;
        }

        @keyframes modalPop {
            from { opacity: 0; transform: scale(0.96) translateY(8px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
        }

        .modal-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .modal-header h3 {
            font-size: 0.95rem;
            font-weight: 800;
            color: #F8FAFC;
        }

        .modal-close {
            background: none;
            border: none;
            font-size: 1.2rem;
            cursor: pointer;
            color: #94A3B8;
            padding: 4px;
        }

        .modal-close:hover {
            color: #F8FAFC;
        }"""

# Replace the style block in html
start_idx = html.find('<style>')
end_idx = html.find('/* MOBILE RESPONSIVE TUNING */')
if start_idx != -1 and end_idx != -1:
    html = html[:start_idx + len('<style>\n')] + css_replacement + '\n\n        ' + html[end_idx:]

# 2. Universal Dark Theme Search and Replace for all inline colors:
# Replace white cards & backgrounds
html = html.replace('background:#FFFFFF;', 'background:rgba(255,255,255,0.03);')
html = html.replace('background: #FFFFFF;', 'background: rgba(255,255,255,0.03);')
html = html.replace('background:#F8FAFC;', 'background:rgba(255,255,255,0.03);')
html = html.replace('background: #F8FAFC;', 'background: rgba(255,255,255,0.03);')
html = html.replace('background:#F1F5F9;', 'background:rgba(255,255,255,0.05);')
html = html.replace('background: #F1F5F9;', 'background: rgba(255,255,255,0.05);')
html = html.replace('background:linear-gradient(135deg, #F8FAFC, #EFF6FF);', 'background:rgba(255,255,255,0.03);')
html = html.replace('background: linear-gradient(135deg, #F8FAFC, #EFF6FF);', 'background: rgba(255,255,255,0.03);')

# Replace white borders
html = html.replace('border:1px solid #E2E8F0;', 'border:1px solid rgba(255,255,255,0.08);')
html = html.replace('border: 1px solid #E2E8F0;', 'border: 1px solid rgba(255,255,255,0.08);')
html = html.replace('border:1px solid #CBD5E1;', 'border:1px solid rgba(255,255,255,0.1);')
html = html.replace('border: 1px solid #CBD5E1;', 'border: 1px solid rgba(255,255,255,0.1);')
html = html.replace('border:1px solid #BFDBFE;', 'border:1px solid rgba(14,165,233,0.3);')
html = html.replace('border: 1px solid #BFDBFE;', 'border: 1px solid rgba(14,165,233,0.3);')
html = html.replace('border:1px solid #A7F3D0;', 'border:1px solid rgba(16,185,129,0.3);')
html = html.replace('border: 1px solid #A7F3D0;', 'border: 1px solid rgba(16,185,129,0.3);')

# Replace dark text on light backgrounds
html = html.replace('color:#0F172A;', 'color:#F8FAFC;')
html = html.replace('color: #0F172A;', 'color: #F8FAFC;')
html = html.replace('color:#1E293B;', 'color:#F8FAFC;')
html = html.replace('color: #1E293B;', 'color: #F8FAFC;')
html = html.replace('color:#475569;', 'color:#94A3B8;')
html = html.replace('color: #475569;', 'color: #94A3B8;')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Theme overhaul complete! index.html size: {len(html)} bytes")
