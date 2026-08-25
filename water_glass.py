import re

# Read index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Master CSS for Frosted Liquid Crystal Glassmorphism (Apple macOS / Clear Water Aero style)
water_glass_css = """        :root {
            --bg-body: #F0F7FF;
            --bg-sidebar: rgba(255, 255, 255, 0.75);
            --bg-card: rgba(255, 255, 255, 0.75);
            --bg-card-solid: #FFFFFF;
            --bg-card-hover: rgba(255, 255, 255, 0.9);
            --bg-input: rgba(255, 255, 255, 0.85);
            --border-color: rgba(255, 255, 255, 0.8);
            --border-focus: #0284C7;
            --primary: #0284C7;
            --primary-hover: #0369A1;
            --primary-glow: rgba(2, 132, 199, 0.25);
            --accent: #0EA5E9;
            --accent-glow: rgba(14, 165, 233, 0.2);
            --success: #059669;
            --warning: #D97706;
            --danger: #DC2626;
            --text-main: #0F172A;
            --text-muted: #475569;
            --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --safe-bottom: env(safe-area-inset-bottom, 0px);
            --card-shadow: 0 8px 32px -4px rgba(2, 132, 199, 0.08), 0 2px 6px rgba(0, 0, 0, 0.03), inset 0 1px 0 rgba(255, 255, 255, 0.95);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            font-family: var(--font-sans);
            background: linear-gradient(135deg, #F0F7FF 0%, #E0F2FE 40%, #F8FAFC 100%);
            background-attachment: fixed;
            color: var(--text-main);
            display: flex;
            height: 100vh;
            height: 100dvh;
            overflow: hidden;
            -webkit-font-smoothing: antialiased;
        }

        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(240, 247, 255, 0.5);
        }

        ::-webkit-scrollbar-thumb {
            background: #BAE6FD;
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
            background: linear-gradient(135deg, rgba(224, 242, 254, 0.8) 0%, rgba(240, 247, 255, 0.9) 100%);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 16px;
        }

        .login-card {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(25px) saturate(190%);
            -webkit-backdrop-filter: blur(25px) saturate(190%);
            border-radius: 22px;
            width: 100%;
            max-width: 400px;
            padding: 32px 26px;
            box-shadow: 0 20px 60px rgba(2, 132, 199, 0.15), 0 0 0 1px rgba(255, 255, 255, 0.9), inset 0 1px 0 rgba(255, 255, 255, 1);
            animation: loginEntrance 0.35s cubic-bezier(0.16, 1, 0.3, 1);
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
            width: 56px;
            height: 56px;
            border-radius: 16px;
            background: linear-gradient(135deg, #E0F2FE, #BAE6FD);
            border: 1px solid rgba(255, 255, 255, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 14px;
            box-shadow: 0 8px 20px rgba(2, 132, 199, 0.18);
        }

        .login-logo img {
            width: 38px;
            height: 38px;
            object-fit: contain;
        }

        .login-title {
            font-size: 1.3rem;
            font-weight: 800;
            color: #0F172A;
            letter-spacing: -0.3px;
        }

        .login-subtitle {
            font-size: 0.78rem;
            color: var(--text-muted);
            margin-top: 3px;
            margin-bottom: 22px;
        }

        .login-alert {
            background: rgba(254, 242, 242, 0.9);
            border: 1px solid #FCA5A5;
            color: #DC2626;
            padding: 10px 14px;
            border-radius: 10px;
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
            right: 10px;
            background: none;
            border: none;
            cursor: pointer;
            color: #64748B;
            padding: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            transition: color 0.15s;
        }

        .password-toggle-btn:hover {
            color: #0284C7;
        }

        .caps-lock-badge {
            display: none;
            font-size: 0.68rem;
            font-weight: 700;
            color: #D97706;
            background: #FEF3C7;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid #FDE68A;
        }

        .security-badge-footer {
            margin-top: 20px;
            padding-top: 14px;
            border-top: 1px solid rgba(2, 132, 199, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
            font-size: 0.72rem;
            color: #64748B;
        }

        .security-badge-item {
            display: flex;
            align-items: center;
            gap: 5px;
            font-weight: 600;
        }

        .pass-strength-bar {
            height: 4px;
            border-radius: 2px;
            background: rgba(2, 132, 199, 0.1);
            margin-top: 6px;
            overflow: hidden;
        }

        .pass-strength-fill {
            height: 100%;
            width: 0%;
            transition: all 0.3s ease;
        }

        /* SIDEBAR FROSTED GLASS & BACKDROP */
        .sidebar-backdrop {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(15, 23, 42, 0.3);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
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
            width: 255px;
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(24px) saturate(190%);
            -webkit-backdrop-filter: blur(24px) saturate(190%);
            border-right: 1px solid rgba(255, 255, 255, 0.85);
            box-shadow: 4px 0 24px rgba(2, 132, 199, 0.05);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
            transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1);
            z-index: 1000;
        }

        .sidebar-brand {
            padding: 16px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid rgba(255, 255, 255, 0.8);
            background: rgba(255, 255, 255, 0.4);
        }

        .brand-header-flex {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .brand-logo {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            background: linear-gradient(135deg, #E0F2FE, #BAE6FD);
            border: 1px solid rgba(255, 255, 255, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.12);
        }

        .brand-logo img {
            width: 24px;
            height: 24px;
            object-fit: contain;
        }

        .brand-text h2 {
            font-size: 0.98rem;
            font-weight: 800;
            color: #0F172A;
            letter-spacing: -0.2px;
            line-height: 1.1;
        }

        .brand-text span {
            font-size: 0.65rem;
            font-weight: 700;
            color: #0284C7;
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }

        .sidebar-close-btn {
            display: none;
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.9);
            width: 28px;
            height: 28px;
            border-radius: 6px;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: #64748B;
        }

        .nav-list {
            list-style: none;
            padding: 12px 10px;
            overflow-y: auto;
            flex-grow: 1;
        }

        .nav-section-title {
            font-size: 0.66rem;
            font-weight: 800;
            text-transform: uppercase;
            color: #64748B;
            padding: 12px 10px 4px;
            letter-spacing: 0.8px;
        }

        .nav-item {
            margin-bottom: 3px;
        }

        .nav-link {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 9px 12px;
            border-radius: 10px;
            color: #334155;
            text-decoration: none;
            font-size: 0.84rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            user-select: none;
        }

        .nav-link svg {
            width: 17px;
            height: 17px;
            fill: #64748B;
            transition: fill 0.2s ease;
            flex-shrink: 0;
        }

        .nav-link:hover {
            background: rgba(255, 255, 255, 0.7);
            color: #0284C7;
            box-shadow: 0 2px 8px rgba(2, 132, 199, 0.08);
        }

        .nav-link:hover svg {
            fill: #0284C7;
        }

        .nav-link.active {
            background: linear-gradient(135deg, rgba(2, 132, 199, 0.12), rgba(14, 165, 233, 0.08));
            color: #0284C7;
            font-weight: 700;
            border: 1px solid rgba(2, 132, 199, 0.2);
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.12);
        }

        .nav-link.active svg {
            fill: #0284C7;
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
            padding-left: 26px;
            display: none;
            margin-top: 2px;
            margin-bottom: 4px;
        }

        .nav-group.open .sub-nav-list {
            display: block;
        }

        .sub-nav-link {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 7px 10px;
            border-radius: 8px;
            color: #64748B;
            font-size: 0.78rem;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.18s ease;
        }

        .sub-nav-link:hover {
            color: #0284C7;
            background: rgba(255, 255, 255, 0.6);
        }

        .sub-nav-link.active {
            color: #0284C7;
            font-weight: 700;
            background: rgba(2, 132, 199, 0.08);
        }

        .sub-nav-bullet {
            width: 5px;
            height: 5px;
            border-radius: 50%;
            background: #94A3B8;
        }

        .sub-nav-link.active .sub-nav-bullet {
            background: #0284C7;
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

        /* TOPBAR FROSTED WATER GLASS */
        .topbar {
            height: 56px;
            background: rgba(255, 255, 255, 0.65);
            backdrop-filter: blur(24px) saturate(190%);
            -webkit-backdrop-filter: blur(24px) saturate(190%);
            border-bottom: 1px solid rgba(255, 255, 255, 0.8);
            box-shadow: 0 4px 20px rgba(2, 132, 199, 0.04);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 18px;
            flex-shrink: 0;
            z-index: 50;
            gap: 8px;
        }

        .topbar-left {
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 0;
            flex-grow: 1;
        }

        .mobile-menu-btn {
            display: none;
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.9);
            cursor: pointer;
            padding: 7px;
            border-radius: 8px;
            flex-direction: column;
            gap: 3.5px;
            flex-shrink: 0;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        }

        .mobile-menu-btn span {
            width: 18px;
            height: 2px;
            background: #0F172A;
            border-radius: 2px;
        }

        .topbar-title {
            min-width: 0;
            overflow: hidden;
        }

        .topbar-title h1 {
            font-size: 1rem;
            font-weight: 800;
            color: #0F172A;
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
            padding: 6px 12px;
            background: rgba(224, 242, 254, 0.7);
            border: 1px solid rgba(186, 230, 253, 0.9);
            border-radius: 18px;
            font-size: 0.74rem;
            font-weight: 700;
            color: #0284C7;
            letter-spacing: 0.3px;
            white-space: nowrap;
            box-shadow: 0 2px 8px rgba(2, 132, 199, 0.08);
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10B981;
            box-shadow: 0 0 10px #10B981;
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
            padding: 18px 20px;
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

        /* LIQUID CRYSTAL BUTTONS */
        .btn {
            min-height: 36px;
            padding: 7px 14px;
            border-radius: 10px;
            font-size: 0.82rem;
            font-weight: 700;
            cursor: pointer;
            border: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 7px;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            white-space: nowrap;
            user-select: none;
        }

        .btn:active {
            transform: scale(0.96);
        }

        .btn svg {
            width: 15px;
            height: 15px;
            flex-shrink: 0;
        }

        .btn-primary {
            background: linear-gradient(135deg, #0284C7 0%, #0EA5E9 100%);
            color: #FFFFFF;
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }

        .btn-primary:hover {
            box-shadow: 0 6px 18px rgba(2, 132, 199, 0.45);
            transform: translateY(-1px);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
            color: #0284C7;
            border: 1px solid rgba(255, 255, 255, 0.9);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        .btn-secondary:hover {
            background: #FFFFFF;
            color: #0369A1;
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.12);
        }

        .btn-success {
            background: linear-gradient(135deg, #059669 0%, #10B981 100%);
            color: #FFFFFF;
            box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }

        .btn-success:hover {
            box-shadow: 0 6px 18px rgba(16, 185, 129, 0.4);
            transform: translateY(-1px);
        }

        .btn-danger {
            background: rgba(254, 242, 242, 0.8);
            color: #DC2626;
            border: 1px solid #FECACA;
            box-shadow: 0 2px 8px rgba(220, 38, 38, 0.06);
        }

        .btn-danger:hover {
            background: #EF4444;
            color: #FFFFFF;
        }

        /* FROSTED WATER GLASS CARDS & TABLES */
        .card {
            background: rgba(255, 255, 255, 0.72);
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            border: 1px solid rgba(255, 255, 255, 0.85);
            border-radius: 16px;
            padding: 18px;
            margin-bottom: 16px;
            box-shadow: var(--card-shadow);
            transition: all 0.25s ease;
        }

        .card:hover {
            box-shadow: 0 12px 36px -4px rgba(2, 132, 199, 0.12), 0 2px 6px rgba(0, 0, 0, 0.03), inset 0 1px 0 rgba(255, 255, 255, 1);
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 14px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(2, 132, 199, 0.08);
            flex-wrap: wrap;
            gap: 8px;
        }

        .card-header h2 {
            font-size: 0.96rem;
            font-weight: 800;
            color: #0F172A;
            letter-spacing: -0.2px;
        }

        .table-responsive {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.8);
            background: rgba(255, 255, 255, 0.5);
            backdrop-filter: blur(10px);
        }

        table {
            width: 100%;
            min-width: 540px;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.82rem;
        }

        th {
            background: rgba(240, 247, 255, 0.7);
            color: #475569;
            padding: 11px 14px;
            font-weight: 800;
            text-transform: uppercase;
            font-size: 0.68rem;
            letter-spacing: 0.6px;
            border-bottom: 1px solid rgba(2, 132, 199, 0.1);
            white-space: nowrap;
        }

        td {
            padding: 11px 14px;
            border-bottom: 1px solid rgba(2, 132, 199, 0.06);
            white-space: nowrap;
            color: #0F172A;
        }

        tr:hover td {
            background: rgba(224, 242, 254, 0.4);
        }

        .badge {
            display: inline-block;
            padding: 4px 9px;
            border-radius: 8px;
            font-size: 0.7rem;
            font-weight: 800;
            font-family: var(--font-mono);
            letter-spacing: 0.2px;
            white-space: nowrap;
        }

        .badge-success {
            background: rgba(236, 253, 245, 0.9);
            color: #059669;
            border: 1px solid #A7F3D0;
        }

        .badge-danger {
            background: rgba(254, 242, 242, 0.9);
            color: #DC2626;
            border: 1px solid #FECACA;
        }

        .badge-info {
            background: rgba(240, 249, 255, 0.9);
            color: #0284C7;
            border: 1px solid #BAE6FD;
        }

        .badge-warning {
            background: rgba(255, 251, 235, 0.9);
            color: #D97706;
            border: 1px solid #FDE68A;
        }

        /* FORMS */
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
        }

        .form-group {
            margin-bottom: 12px;
        }

        .form-group label {
            display: block;
            font-size: 0.75rem;
            font-weight: 700;
            color: #475569;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .form-control {
            width: 100%;
            min-height: 40px;
            padding: 7px 12px;
            border: 1px solid rgba(2, 132, 199, 0.2);
            border-radius: 9px;
            font-size: 0.86rem;
            font-family: var(--font-sans);
            color: #0F172A;
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(10px);
            outline: none;
            transition: all 0.2s ease;
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.03);
        }

        .form-control:focus {
            border-color: var(--border-focus);
            background: #FFFFFF;
            box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.2);
        }

        /* STAT CARDS */
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 14px;
            margin-bottom: 16px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.75);
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            border: 1px solid rgba(255, 255, 255, 0.9);
            border-radius: 16px;
            padding: 16px 18px;
            display: flex;
            align-items: center;
            gap: 14px;
            box-shadow: var(--card-shadow);
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .stat-card:hover {
            border-color: rgba(2, 132, 199, 0.4);
            transform: translateY(-2px);
            box-shadow: 0 12px 30px rgba(2, 132, 199, 0.12);
        }

        .stat-icon {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        .stat-icon svg {
            width: 20px;
            height: 20px;
            fill: #FFFFFF;
        }

        .stat-icon.blue { background: linear-gradient(135deg, #0284C7, #38BDF8); }
        .stat-icon.green { background: linear-gradient(135deg, #059669, #34D399); }
        .stat-icon.purple { background: linear-gradient(135deg, #7C3AED, #A78BFA); }
        .stat-icon.orange { background: linear-gradient(135deg, #D97706, #FBBF24); }

        .stat-info {
            min-width: 0;
            flex-grow: 1;
        }

        .stat-info h3 {
            font-size: 0.7rem;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 2px;
        }

        .stat-info .stat-value {
            font-size: 1.2rem;
            font-weight: 800;
            color: #0F172A;
            font-family: var(--font-mono);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .stat-desc {
            font-size: 0.72rem;
            color: var(--text-muted);
            margin-top: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .progress-bar-container {
            width: 100%;
            height: 6px;
            background: rgba(2, 132, 199, 0.1);
            border-radius: 3px;
            overflow: hidden;
            margin-top: 4px;
        }

        .progress-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #0284C7, #38BDF8);
            border-radius: 3px;
            transition: width 0.5s ease;
        }

        /* 5G RADAR GRAPHIC */
        .radar-box {
            position: relative;
            width: 76px;
            height: 76px;
            border-radius: 50%;
            background: radial-gradient(circle, #0284C7 0%, #0369A1 70%);
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(2, 132, 199, 0.3);
            transition: all 0.4s ease;
        }

        .radar-box.locked {
            background: radial-gradient(circle, #10B981 0%, #059669 70%) !important;
            box-shadow: 0 4px 18px rgba(16, 185, 129, 0.4) !important;
        }

        .radar-box.scanning {
            background: radial-gradient(circle, #0284C7 0%, #0369A1 70%) !important;
            box-shadow: 0 4px 16px rgba(2, 132, 199, 0.35) !important;
        }

        .radar-sweep-arm {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: conic-gradient(from 0deg, rgba(255, 255, 255, 0.8) 0deg, rgba(255, 255, 255, 0.1) 50deg, transparent 60deg);
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

        /* FROSTED GLASS MODAL */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(15, 23, 42, 0.25);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            padding: 16px;
        }

        .modal-overlay.active {
            display: flex;
        }

        .modal-card {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(25px) saturate(190%);
            -webkit-backdrop-filter: blur(25px) saturate(190%);
            border-radius: 18px;
            width: 100%;
            max-width: 480px;
            padding: 24px;
            box-shadow: 0 25px 60px rgba(2, 132, 199, 0.18), 0 0 0 1px rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.9);
            animation: modalPop 0.25s cubic-bezier(0.16, 1, 0.3, 1);
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
            margin-bottom: 14px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(2, 132, 199, 0.1);
        }

        .modal-header h3 {
            font-size: 1rem;
            font-weight: 800;
            color: #0F172A;
        }

        .modal-close {
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.9);
            border-radius: 6px;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            cursor: pointer;
            color: #64748B;
        }

        .modal-close:hover {
            color: #0F172A;
            background: #FFFFFF;
        }"""

# Replace the style block
start_idx = html.find('<style>')
end_idx = html.find('/* MOBILE RESPONSIVE TUNING */')
if start_idx != -1 and end_idx != -1:
    html = html[:start_idx + len('<style>\n')] + water_glass_css + '\n\n        ' + html[end_idx:]

# 2. Update Antenna Alignment Widget to Crystal Water Glass style:
align_widget_old = """                <!-- ANTENNA ALIGNMENT & AUDIO TONE BEEPER WIDGET -->
                <div class="card" style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); border: 1px solid #334155; color: #F8FAFC; margin-bottom: 12px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);">
                    <div class="card-header" style="border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <div style="width:10px;height:10px;border-radius:50%;background:#10B981;box-shadow:0 0 12px #10B981;animation:pulseDot 2s infinite;"></div>
                            <div>
                                <h2 style="color:#F8FAFC;font-size:1rem;margin:0;font-weight:800;letter-spacing:-0.2px;">🎯 Antenna Alignment & Audio Beeper (وەستای تاوەر)</h2>
                                <div style="font-size:0.72rem;color:#94A3B8;margin-top:1px;">Live acoustic tone & signal precision meter for dish mounting</div>
                            </div>
                        </div>
                        <button type="button" id="btn-audio-align" onclick="toggleAudioAlignment()" class="btn" style="background:#2563EB;color:#FFF;font-weight:800;font-size:0.75rem;padding:7px 14px;border-radius:8px;display:flex;align-items:center;gap:6px;cursor:pointer;border:none;box-shadow:0 0 15px rgba(37,99,235,0.4);transition:all 0.2s;">
                            <span>🔊</span> <span id="btn-audio-text">Audio Beeper: OFF</span>
                        </button>
                    </div>
                    
                    <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:12px;padding-top:12px;">
                        <!-- Big Dial -->
                        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:16px;text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center;">
                            <div style="font-size:0.7rem;color:#94A3B8;text-transform:uppercase;font-weight:800;letter-spacing:0.5px;">Live Signal Strength</div>
                            <div id="align-signal-val" style="font-size:2.5rem;font-weight:900;color:#10B981;font-family:var(--font-mono);margin:4px 0;text-shadow:0 0 25px rgba(16,185,129,0.5);">-- dBm</div>
                            <div id="align-quality-text" style="font-size:0.72rem;font-weight:800;color:#10B981;background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);padding:3px 12px;border-radius:20px;">SEARCHING SIGNAL...</div>
                        </div>

                        <!-- 4 High Precision Metrics -->
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:10px;text-align:center;">
                                <div style="font-size:0.65rem;color:#94A3B8;text-transform:uppercase;font-weight:800;">CCQ Quality</div>
                                <div id="align-ccq-val" style="font-size:1.25rem;font-weight:900;color:#38BDF8;margin-top:2px;">--%</div>
                                <div style="font-size:0.62rem;color:#94A3B8;">Packet Success</div>
                            </div>
                            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:10px;text-align:center;">
                                <div style="font-size:0.65rem;color:#94A3B8;text-transform:uppercase;font-weight:800;">Noise Floor</div>
                                <div id="align-noise-val" style="font-size:1.25rem;font-weight:900;color:#F59E0B;margin-top:2px;">-- dBm</div>
                                <div style="font-size:0.62rem;color:#94A3B8;">RF Spectrum</div>
                            </div>
                            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:10px;text-align:center;">
                                <div style="font-size:0.65rem;color:#94A3B8;text-transform:uppercase;font-weight:800;">SNR Ratio</div>
                                <div id="align-snr-val" style="font-size:1.25rem;font-weight:900;color:#A78BFA;margin-top:2px;">-- dB</div>
                                <div style="font-size:0.62rem;color:#94A3B8;">Signal / Noise</div>
                            </div>
                            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:10px;text-align:center;">
                                <div style="font-size:0.65rem;color:#94A3B8;text-transform:uppercase;font-weight:800;">Frequency</div>
                                <div id="align-freq-val" style="font-size:1.25rem;font-weight:900;color:#34D399;margin-top:2px;">-- MHz</div>
                                <div style="font-size:0.62rem;color:#94A3B8;">Operating Band</div>
                            </div>
                        </div>
                    </div>
                </div>"""

align_widget_new = """                <!-- ANTENNA ALIGNMENT & AUDIO TONE BEEPER WIDGET -->
                <div class="card" style="background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(24px) saturate(190%); -webkit-backdrop-filter: blur(24px) saturate(190%); border: 1px solid rgba(255, 255, 255, 0.95); margin-bottom: 14px; box-shadow: 0 10px 30px -4px rgba(2, 132, 199, 0.12), inset 0 1px 0 rgba(255, 255, 255, 1);">
                    <div class="card-header" style="border-bottom: 1px solid rgba(2, 132, 199, 0.1); padding-bottom: 12px;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <div style="width:10px;height:10px;border-radius:50%;background:#10B981;box-shadow:0 0 12px #10B981;animation:pulseDot 2s infinite;"></div>
                            <div>
                                <h2 style="color:#0F172A;font-size:1.02rem;margin:0;font-weight:800;letter-spacing:-0.2px;">🎯 Antenna Alignment & Audio Beeper (وەستای تاوەر)</h2>
                                <div style="font-size:0.74rem;color:#64748B;margin-top:1px;">Live acoustic tone & signal precision meter for dish mounting</div>
                            </div>
                        </div>
                        <button type="button" id="btn-audio-align" onclick="toggleAudioAlignment()" class="btn btn-primary" style="font-weight:800;font-size:0.78rem;padding:7px 16px;border-radius:10px;display:flex;align-items:center;gap:6px;cursor:pointer;">
                            <span>🔊</span> <span id="btn-audio-text">Audio Beeper: OFF</span>
                        </button>
                    </div>
                    
                    <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:14px;padding-top:14px;">
                        <!-- Big Dial -->
                        <div style="background:linear-gradient(135deg, rgba(240, 249, 255, 0.8), rgba(224, 242, 254, 0.6));border:1px solid rgba(255, 255, 255, 0.95);border-radius:14px;padding:18px;text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:inset 0 1px 0 rgba(255,255,255,1), 0 4px 16px rgba(2, 132, 199, 0.06);">
                            <div style="font-size:0.72rem;color:#0369A1;text-transform:uppercase;font-weight:800;letter-spacing:0.6px;">Live Signal Strength</div>
                            <div id="align-signal-val" style="font-size:2.6rem;font-weight:900;color:#059669;font-family:var(--font-mono);margin:4px 0;text-shadow:0 2px 10px rgba(5,150,105,0.2);">-- dBm</div>
                            <div id="align-quality-text" style="font-size:0.74rem;font-weight:800;color:#059669;background:rgba(236, 253, 245, 0.9);border:1px solid #A7F3D0;padding:4px 14px;border-radius:20px;">SEARCHING SIGNAL...</div>
                        </div>

                        <!-- 4 High Precision Metrics -->
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                            <div style="background:rgba(255,255,255,0.7);backdrop-filter:blur(10px);border:1px solid rgba(255, 255, 255, 0.9);border-radius:12px;padding:12px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.02);">
                                <div style="font-size:0.67rem;color:#64748B;text-transform:uppercase;font-weight:800;">CCQ Quality</div>
                                <div id="align-ccq-val" style="font-size:1.3rem;font-weight:900;color:#0284C7;margin-top:2px;">--%</div>
                                <div style="font-size:0.64rem;color:#64748B;">Packet Success</div>
                            </div>
                            <div style="background:rgba(255,255,255,0.7);backdrop-filter:blur(10px);border:1px solid rgba(255, 255, 255, 0.9);border-radius:12px;padding:12px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.02);">
                                <div style="font-size:0.67rem;color:#64748B;text-transform:uppercase;font-weight:800;">Noise Floor</div>
                                <div id="align-noise-val" style="font-size:1.3rem;font-weight:900;color:#D97706;margin-top:2px;">-- dBm</div>
                                <div style="font-size:0.64rem;color:#64748B;">RF Spectrum</div>
                            </div>
                            <div style="background:rgba(255,255,255,0.7);backdrop-filter:blur(10px);border:1px solid rgba(255, 255, 255, 0.9);border-radius:12px;padding:12px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.02);">
                                <div style="font-size:0.67rem;color:#64748B;text-transform:uppercase;font-weight:800;">SNR Ratio</div>
                                <div id="align-snr-val" style="font-size:1.3rem;font-weight:900;color:#7C3AED;margin-top:2px;">-- dB</div>
                                <div style="font-size:0.64rem;color:#64748B;">Signal / Noise</div>
                            </div>
                            <div style="background:rgba(255,255,255,0.7);backdrop-filter:blur(10px);border:1px solid rgba(255, 255, 255, 0.9);border-radius:12px;padding:12px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.02);">
                                <div style="font-size:0.67rem;color:#64748B;text-transform:uppercase;font-weight:800;">Frequency</div>
                                <div id="align-freq-val" style="font-size:1.3rem;font-weight:900;color:#059669;margin-top:2px;">-- MHz</div>
                                <div style="font-size:0.64rem;color:#64748B;">Operating Band</div>
                            </div>
                        </div>
                    </div>
                </div>"""

if align_widget_old in html:
    html = html.replace(align_widget_old, align_widget_new)

# 3. Update Throughput canvas background
html = html.replace('background:#0F172A;border-radius:8px;overflow:hidden;border:1px solid #1E293B;', 'background:linear-gradient(180deg, rgba(240, 249, 255, 0.7), rgba(224, 242, 254, 0.5));border-radius:12px;overflow:hidden;border:1px solid rgba(255, 255, 255, 0.9);box-shadow:inset 0 1px 3px rgba(2, 132, 199, 0.05);')

# 4. Update inner card boxes styling:
html = html.replace('background:rgba(255,255,255,0.03);', 'background:rgba(255,255,255,0.65);backdrop-filter:blur(12px);')
html = html.replace('background: rgba(255,255,255,0.03);', 'background: rgba(255,255,255,0.65); backdrop-filter: blur(12px);')
html = html.replace('border:1px solid rgba(255,255,255,0.08);', 'border:1px solid rgba(255,255,255,0.85);box-shadow:0 2px 8px rgba(2,132,199,0.04);')
html = html.replace('border: 1px solid rgba(255,255,255,0.08);', 'border: 1px solid rgba(255,255,255,0.85); box-shadow: 0 2px 8px rgba(2,132,199,0.04);')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Liquid Crystal Water Glassmorphism applied successfully!")
