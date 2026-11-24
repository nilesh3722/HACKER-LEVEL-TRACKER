import os
import sqlite3
import time
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string
import requests

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dashboard.db")
API_URL = "https://fruxaio-theta.vercel.app/get_player_personal_show"
POLL_SECONDS = 300

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SILENT GMR · Player Workspace</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>
:root{
  color-scheme:dark;
  --bg:#080914;
  --bg-accent:radial-gradient(ellipse 72% 44% at 12% -8%, rgba(135,92,255,.25), transparent 65%), radial-gradient(ellipse 60% 38% at 100% 0%, rgba(34,211,238,.13), transparent 70%), radial-gradient(ellipse 45% 30% at 55% 100%, rgba(244,114,182,.07), transparent 70%);
  --panel:rgba(17,19,37,.80);
  --panel-solid:#121429;
  --panel2:#1a1d38;
  --panel3:#25284a;
  --text:#f8f7ff;
  --muted:#9698b3;
  --line:rgba(220,218,255,.11);
  --line-strong:rgba(220,218,255,.24);
  --green:#8b7bff;
  --green-soft:rgba(139,123,255,.15);
  --blue:#37d8ee;
  --blue-soft:rgba(55,216,238,.14);
  --amber:#ffc76b;
  --amber-soft:rgba(255,199,107,.15);
  --red:#ff779d;
  --red-soft:rgba(255,119,157,.14);
  --radius:24px;
}

html[data-theme=light]{
  color-scheme:light;
  --bg:#f4f6fb;
  --bg-accent:radial-gradient(ellipse 80% 45% at 15% -10%,rgba(139,123,255,.14),transparent 68%),radial-gradient(ellipse 55% 35% at 100% 0%,rgba(55,216,238,.11),transparent 70%);
  --panel:rgba(255,255,255,.84);
  --panel-solid:#ffffff;
  --panel2:#eef0f8;
  --panel3:#e3e6f3;
  --text:#17172b;
  --muted:#69708c;
  --line:rgba(31,35,75,.12);
  --line-strong:rgba(31,35,75,.24);
  --green:#6557df;
  --green-soft:rgba(101,87,223,.12);
  --blue:#079eb6;
  --blue-soft:rgba(7,158,182,.12);
  --amber:#b97800;
  --amber-soft:rgba(185,120,0,.12);
  --red:#d94d78;
  --red-soft:rgba(217,77,120,.11);
}

html[data-theme=light] body{color:#17172b}
html[data-theme=light] header{background:rgba(255,255,255,.78);box-shadow:0 12px 36px rgba(39,43,82,.10)}
html[data-theme=light] input,html[data-theme=light] select{background:#fff;color:var(--text)}
html[data-theme=light] .seg-toggle{background:#e8eaf4}
html[data-theme=light] .progress-track{background:#dfe2ef}
html[data-theme=light] .toast{background:#fff;color:var(--text);box-shadow:0 14px 30px rgba(39,43,82,.18)}
html[data-theme=light] .modal{background:#fff}

*{box-sizing:border-box}
html,body{margin:0;padding:0;min-height:100%}
body{
  background-color:var(--bg);
  background-image:var(--bg-accent);
  background-attachment:fixed;
  color:var(--text);
  font:14px/1.5 'Inter',system-ui,-apple-system,sans-serif;
  -webkit-font-smoothing:antialiased;
  letter-spacing:-.01em;
  overflow-x:hidden;
}
.mono{font-family:'JetBrains Mono',ui-monospace,monospace;font-variant-numeric:tabular-nums}
.num{font-variant-numeric:tabular-nums}

/* Header */
header{
  position:sticky;top:0;z-index:20;
  background:rgba(8,9,20,.78);
  backdrop-filter:blur(16px);
  -webkit-backdrop-filter:blur(16px);
  border-bottom:1px solid var(--line);
  box-shadow:0 16px 48px rgba(0,0,0,.25);
  padding:14px max(18px,calc((100% - 1240px)/2));
  display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;
}
.brand-wrap{display:flex;align-items:center;gap:11px}
.logo-badge{
  width:40px;height:40px;border-radius:13px;
  background:linear-gradient(145deg,#e7dcff 0%,#9b87ff 36%,#5043c7 100%);
  display:grid;place-items:center;
  font-weight:800;font-size:14px;color:#17112f;
  box-shadow:0 0 0 5px rgba(139,123,255,.10),0 0 32px rgba(139,123,255,.34);
  flex-shrink:0;
}
.brand{font-weight:850;font-size:16px;letter-spacing:1.8px;line-height:1.1}
.brand span{color:var(--green)}
.sub{color:#7d80a3;font-size:10px;letter-spacing:1.4px;margin-top:4px;font-weight:750}

.header-right{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.live-pill{
  display:inline-flex;align-items:center;gap:7px;
  background:var(--panel2);border:1px solid var(--line);
  padding:5px 11px;border-radius:999px;font-size:12px;color:var(--muted);
}
.pulse{
  width:7px;height:7px;border-radius:50%;background:#37d8ee;
  animation:pulse 2s infinite;
}
.pulse.err{background:var(--red);animation:none;box-shadow:0 0 8px var(--red)}
@keyframes pulse{
  0%{box-shadow:0 0 0 0 rgba(34,217,130,0.65)}
  70%{box-shadow:0 0 0 7px rgba(34,217,130,0)}
  100%{box-shadow:0 0 0 0 rgba(34,217,130,0)}
}
.auto-select{
  background:var(--panel2);border:1px solid var(--line);color:var(--text);
  border-radius:999px;padding:5px 10px;font-size:12px;cursor:pointer;outline:none;
}
.theme-toggle{padding:6px 10px;border-radius:999px;background:var(--panel2);font-size:12px;min-width:76px}
.theme-toggle span:first-child{font-size:14px;line-height:1}
.theme-toggle:hover{border-color:var(--green);color:var(--green)}

/* Main */
main{max-width:1240px;margin:22px auto;padding:0 18px 90px}

/* Stats */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.stat{
  position:relative;overflow:hidden;
  background:var(--panel);border:1px solid var(--line);
  border-radius:var(--radius);padding:18px 20px;
  box-shadow:0 16px 40px rgba(0,0,0,.24), inset 0 1px 0 rgba(255,255,255,.035);
}
.stat::before{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,var(--accent,rgba(255,255,255,0.18)),transparent);
}
.stat.s-green{--accent:var(--green)}
.stat.s-blue{--accent:var(--blue)}
.stat.s-amber{--accent:var(--amber)}
.stat label{display:block;color:var(--muted);font-size:13px;font-weight:500;margin-bottom:8px}
.stat strong{display:block;font-size:29px;font-weight:850;letter-spacing:-.8px}
.green{color:var(--green)}
.blue{color:var(--blue)}
.amber{color:var(--amber)}

/* Section Head */
.section-head{
  display:flex;align-items:center;justify-content:space-between;
  gap:10px;margin:26px 0 14px;flex-wrap:wrap;
}
.section-head h2{font-size:19px;font-weight:750;margin:0;display:flex;align-items:center;gap:8px}
.count-badge{
  font-size:12px;font-weight:700;padding:3px 9px;border-radius:999px;
  background:var(--panel2);border:1px solid var(--line);color:var(--muted);
}
.head-controls{display:flex;align-items:center;gap:8px;flex-wrap:wrap}

/* Segmented Toggle (Detailed / Compact) */
.seg-toggle{
  display:inline-flex;background:#0b0c10;border:1px solid var(--line);
  border-radius:12px;padding:3px;gap:3px;
}
.seg-toggle button{
  border:0;background:transparent;color:var(--muted);
  padding:7px 12px;border-radius:9px;font-size:12px;font-weight:650;
}
.seg-toggle button.active{background:var(--panel3);color:var(--text)}

/* Buttons & Inputs */
button,input,select{font:inherit}
button{
  display:inline-flex;align-items:center;justify-content:center;gap:6px;
  border:1px solid var(--line);border-radius:11px;
  background:var(--panel2);color:var(--text);
  padding:9px 13px;font-weight:600;font-size:13px;
  cursor:pointer;transition:all .15s ease;white-space:nowrap;
}
button:hover:not(:disabled){background:var(--panel3);border-color:var(--line-strong)}
button:active:not(:disabled){transform:scale(0.98)}
button:disabled{opacity:.55;cursor:not-allowed}
button.primary{
  background:linear-gradient(135deg,#e8e0ff 0%,#9b87ff 38%,#6255e8 100%);
  border-color:transparent;color:#17112f;font-weight:750;
}
button.primary:hover:not(:disabled){filter:brightness(1.08)}
button.ghost{background:transparent;border-color:var(--line)}
button.danger{background:var(--red-soft);border-color:rgba(255,94,120,0.25);color:#ff8fa2}
button.danger:hover:not(:disabled){background:rgba(255,94,120,0.25)}
button.warn{background:var(--amber-soft);border-color:rgba(240,184,73,0.28);color:#ffd578}

input,select{
  background:#0a0c10;border:1px solid var(--line);color:var(--text);
  border-radius:11px;padding:9px 12px;min-width:0;outline:none;
  transition:border-color .15s ease;
}
input:focus,select:focus{border-color:var(--green);box-shadow:0 0 0 4px rgba(139,123,255,.11)}

/* Add Box */
.addbox{
  background:var(--panel);border:1px solid var(--line);
  border-radius:var(--radius);padding:0 16px;
  max-height:0;overflow:hidden;opacity:0;
  transition:max-height .25s ease,opacity .2s ease,padding .2s ease,margin .2s ease;
  margin-bottom:0;
}
.addbox.open{
  max-height:260px;opacity:1;padding:16px;margin-bottom:14px;
  border-color:rgba(34,217,130,0.32);
}
.addrow{display:grid;grid-template-columns:1fr 130px auto;gap:10px}
.hint{font-size:12px;color:var(--muted);margin-top:9px;line-height:1.5}
.error-msg{color:#ff8796;font-size:12px;margin-top:7px;min-height:16px}

/* Toolbar */
.toolbar{
  background:var(--panel);border:1px solid var(--line);
  border-radius:var(--radius);padding:11px;
  display:flex;gap:9px;align-items:center;flex-wrap:wrap;
}
.search-wrap{position:relative;flex:1;min-width:180px;display:flex;align-items:center}
.search-wrap svg{position:absolute;left:11px;color:var(--muted);pointer-events:none}
.search-wrap input{width:100%;padding-left:34px;padding-right:30px}
.clear-btn{
  position:absolute;right:6px;background:transparent;border:0;color:var(--muted);
  padding:4px 6px;display:none;font-size:13px;
}
.clear-btn.show{display:inline-flex}
.target-pill{
  display:inline-flex;align-items:center;gap:6px;
  background:#0a0c10;border:1px solid var(--line);
  border-radius:11px;padding:4px 10px;font-size:12px;color:var(--amber);font-weight:600;
}
.target-pill input{
  width:52px;padding:4px 6px;border:1px solid var(--line);border-radius:7px;
  background:var(--panel2);color:var(--text);text-align:center;font-weight:700;
}

/* Accounts Container */
.accounts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:14px}
.accounts.compact-mode{grid-template-columns:1fr}

/* Account Card */
.card{
  position:relative;overflow:hidden;
  background:var(--panel);border:1px solid var(--line);
  border-radius:var(--radius);padding:17px 18px 15px;
  box-shadow:0 10px 28px rgba(0,0,0,0.34);
  display:flex;flex-direction:column;gap:13px;
  transition:border-color .18s ease,transform .18s ease,box-shadow .18s ease;
}
.card:hover{border-color:rgba(139,123,255,.38);transform:translateY(-2px);box-shadow:0 22px 48px rgba(0,0,0,.30),inset 0 1px 0 rgba(255,255,255,.05)}

.topline{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}
.identity{min-width:0;flex:1}
.name-row{display:flex;align-items:center;gap:7px;flex-wrap:wrap}
.rank-badge{
  font-size:11px;font-weight:800;padding:2px 7px;border-radius:7px;
  background:var(--panel2);color:var(--muted);border:1px solid var(--line);
}
.rank-badge.r1{background:var(--amber-soft);color:#ffd56b;border-color:rgba(240,184,73,0.35)}
.rank-badge.r2{background:rgba(203,213,225,0.14);color:#e2e8f0}
.rank-badge.r3{background:rgba(217,119,6,0.18);color:#fbbf24}

.nickname{font-size:18px;font-weight:750;overflow-wrap:anywhere;line-height:1.2}
.server{
  background:var(--panel3);color:#cfd5e3;border:1px solid var(--line);
  padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700;
}

.uid-row{display:flex;align-items:center;gap:7px;margin-top:7px;flex-wrap:wrap}
.uid-chip{
  display:inline-flex;align-items:center;gap:5px;
  background:#0a0c10;border:1px solid var(--line);
  color:var(--muted);font-size:12px;padding:3px 8px;border-radius:8px;
  cursor:pointer;
}
.uid-chip:hover{color:var(--text);border-color:var(--line-strong)}
.status-tag{
  display:inline-flex;align-items:center;gap:6px;
  background:var(--blue-soft);color:#8ec0ff;
  border:1px solid rgba(77,148,255,0.22);
  padding:3px 9px;border-radius:999px;font-size:11px;font-weight:600;
}
.status-dot{width:6px;height:6px;border-radius:50%;background:var(--blue)}

/* Right Level Block */
.level-side{text-align:right;white-space:nowrap;flex-shrink:0}
.level-main{font-size:13px;color:var(--muted);font-weight:600}
.level-main b{font-size:23px;color:var(--text);font-weight:800;margin-left:3px}
.level-pct{font-size:13px;font-weight:700;color:#d6dce8;margin-top:1px}
.level-target{font-size:12px;font-weight:700;color:var(--amber);margin-top:2px}
.level-target.reached{color:var(--green)}

/* Next Level Info Banner */
.next-banner{
  background:linear-gradient(90deg, rgba(255,255,255,.035), rgba(139,123,255,.10) 55%, rgba(55,216,238,.05));
  border:1px solid var(--line);
  border-radius:13px;padding:10px 12px;
  display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;
}
.next-left{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.lv-pill{
  display:inline-flex;align-items:center;gap:5px;
  background:var(--panel3);border:1px solid var(--line-strong);
  padding:3px 9px;border-radius:999px;font-size:12px;font-weight:700;
}
.lv-pill .arrow{color:var(--green)}
.exp-need-text{font-size:12px;color:#dbe1ee}
.exp-need-text b{color:var(--green)}
.exp-sub{font-size:11px;color:var(--muted)}

/* Metrics Grid (Detailed) */
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.metric{
  background:linear-gradient(145deg,rgba(31,34,69,.88),rgba(20,22,46,.82));border:1px solid rgba(255,255,255,0.04);
  border-radius:12px;padding:9px 10px;
}
.metric label{display:block;color:var(--muted);font-size:11px;margin-bottom:3px}
.metric strong{font-size:15px;font-weight:750;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

/* Compact Inline Row */
.compact-row{
  display:none;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;
}
.compact-stats{display:flex;gap:16px;align-items:center;flex-wrap:wrap}
.c-stat label{display:block;font-size:11px;color:var(--muted)}
.c-stat strong{font-size:14px;font-weight:750}
.compact-actions{display:flex;gap:6px;align-items:center}
.compact-actions button{padding:7px 9px;font-size:12px;border-radius:9px}

/* Detailed Actions */
.actions{
  display:flex;gap:7px;flex-wrap:wrap;
  padding-top:11px;border-top:1px solid var(--line);
}
.actions button{font-size:12px;padding:7px 10px;border-radius:9px}
.actions .spacer{flex:1}

/* Bottom Next-Level Progress Section */
.lvl-progress-wrap{margin-top:2px}
.lvl-progress-meta{
  display:flex;align-items:center;justify-content:space-between;gap:8px;
  font-size:11.5px;margin-bottom:6px;flex-wrap:wrap;
}
.lvl-progress-meta .done-txt{color:#e6ebf5;font-weight:650}
.lvl-progress-meta .left-txt{color:var(--amber);font-weight:700}
.progress-track{
  height:7px;width:100%;border-radius:999px;
  background:#242731;overflow:hidden;
  box-shadow:inset 0 1px 2px rgba(0,0,0,0.6);
}
.progress-fill{
  height:100%;border-radius:999px;
  background:linear-gradient(90deg,#ffffff 0%, #c2b8ff 45%, #8b7bff 100%);
  box-shadow:0 0 10px rgba(139,123,255,.50);
  transition:width .45s cubic-bezier(.22,1,.36,1);
}

/* Compact Mode Rules */
.accounts.compact-mode .metrics,
.accounts.compact-mode .actions{display:none}
.accounts.compact-mode .compact-row{display:flex}
.accounts.compact-mode .card{padding:15px 16px 13px;gap:10px}
.accounts.compact-mode .next-banner{padding:8px 10px}

/* Empty */
.empty{
  grid-column:1/-1;padding:48px 20px;text-align:center;
  color:var(--muted);background:var(--panel);
  border:1px dashed var(--line-strong);border-radius:var(--radius);
}
.empty h3{margin:6px 0;color:var(--text);font-size:16px}
.empty p{margin:0;font-size:13px}

/* Spinner */
.spin{display:inline-block;animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

/* Toasts */
.toasts{
  position:fixed;bottom:18px;right:18px;z-index:100;
  display:flex;flex-direction:column;gap:8px;max-width:330px;
}
.toast{
  background:#141720;border:1px solid var(--line-strong);color:var(--text);
  padding:10px 14px;border-radius:12px;font-size:13px;font-weight:500;
  box-shadow:0 12px 30px rgba(0,0,0,0.55);
  display:flex;align-items:center;gap:8px;
}
.toast.ok{border-color:rgba(139,123,255,.50)}
.toast.err{border-color:rgba(255,94,120,0.5);color:#ffb3c0}

/* Modal */
.modal-backdrop{
  position:fixed;inset:0;z-index:90;
  background:rgba(4,5,8,0.74);backdrop-filter:blur(6px);
  display:none;place-items:center;padding:16px;
}
.modal-backdrop.open{display:grid}
.modal{
  width:100%;max-width:390px;background:var(--panel-solid);
  border:1px solid var(--line-strong);border-radius:18px;padding:20px;
}
.modal h3{margin:0 0 8px;font-size:17px}
.modal p{margin:0 0 18px;color:var(--muted);font-size:13px;line-height:1.5}
.modal-actions{display:flex;justify-content:flex-end;gap:8px}

.foot{color:#6c7282;font-size:12px;text-align:center;margin-top:26px;line-height:1.6}

@media(max-width:960px){
  .accounts{grid-template-columns:1fr}
}
@media(max-width:720px){
  main{margin-top:16px}

  .stats{grid-template-columns:repeat(2,1fr);gap:10px}
  .stat{padding:14px 15px}
  .stat strong{font-size:23px}
  .metrics{grid-template-columns:repeat(2,1fr)}
  .addrow{grid-template-columns:1fr 110px}
  .addrow button{grid-column:1/-1}
}
@media(max-width:460px){
  header{padding:11px 14px}
  .card{padding:14px 14px 13px}
  .nickname{font-size:16px}
  .level-main b{font-size:20px}
  .actions .spacer{display:none}
  .actions button{flex:1}
  .toasts{left:14px;right:14px;bottom:14px;max-width:none}
}

/* Rebuilt workspace UI */
:root{
  --radius:16px;
  --workspace-bg:#090b16;
  --workspace-accent:rgba(139,123,255,.13);
  --card-shadow:0 12px 28px rgba(0,0,0,.20);
}
html[data-theme=light]{
  --workspace-bg:#f3f5fb;
  --workspace-accent:rgba(101,87,223,.08);
  --card-shadow:0 10px 24px rgba(44,51,92,.09);
}
body{background-color:var(--workspace-bg);background-image:radial-gradient(circle at 8% 0%,var(--workspace-accent),transparent 26%),radial-gradient(circle at 100% 12%,rgba(55,216,238,.07),transparent 22%);}
header{padding:12px max(20px,calc((100% - 1280px)/2));background:color-mix(in srgb,var(--panel-solid) 88%,transparent);border-bottom:1px solid var(--line);box-shadow:0 6px 22px rgba(0,0,0,.10)}
.logo-badge{width:36px;height:36px;border-radius:10px;box-shadow:none;background:linear-gradient(145deg,#d9d2ff,#7769ed);}
.brand{font-size:15px;letter-spacing:1.5px}.sub{font-size:9px;letter-spacing:1.1px}
main{max-width:1280px;margin:20px auto;padding:0 20px 70px}
.stats{gap:14px;margin-bottom:24px}.stat{border-radius:16px;padding:16px 18px;background:var(--panel-solid);box-shadow:var(--card-shadow);border-color:var(--line)}
.stat::before{height:3px;background:var(--accent,var(--green))}.stat label{font-size:10px;letter-spacing:1px;text-transform:uppercase;font-weight:800}.stat strong{font-size:27px;margin-top:4px}
.section-head{margin:22px 0 12px}.section-head h2{font-size:18px;letter-spacing:-.3px}.count-badge{background:var(--panel2);color:var(--text)}
.toolbar{padding:9px;background:var(--panel-solid);border-radius:16px;box-shadow:var(--card-shadow);border-color:var(--line)}
.toolbar input,.toolbar select,.target-pill{min-height:38px}.target-pill{background:var(--panel2)}
.accounts{gap:16px;margin-top:16px}.card{border-radius:18px;padding:18px;background:var(--panel-solid);box-shadow:var(--card-shadow);border-color:var(--line);gap:14px}.card:hover{transform:translateY(-1px);box-shadow:0 16px 32px rgba(0,0,0,.22)}
.nickname{font-size:17px}.rank-badge{border-radius:6px}.server{border-radius:7px}
.next-banner{border-radius:12px;padding:12px 13px;background:var(--panel2);border-color:var(--line)}
.next-banner .exp-need-text{color:var(--text)}.next-banner .exp-need-text b{color:var(--green)}
.next-banner .exp-sub{color:var(--muted)}
.metrics{gap:9px}.metric{border-radius:10px;background:var(--panel2);border-color:var(--line);padding:10px}.metric label{font-size:10px;text-transform:uppercase;letter-spacing:.35px}.metric strong{font-size:15px;color:var(--text)}
.level-main{color:var(--muted)}.level-main b{color:var(--text)}.level-pct{color:var(--text)}
.lvl-progress-meta .done-txt{color:var(--text)}.lvl-progress-meta .left-txt{color:var(--amber)}
.actions{padding-top:12px}.actions button{border-radius:8px}.progress-track{height:8px;background:var(--panel3)}
.empty{background:var(--panel-solid);box-shadow:var(--card-shadow)}
.foot{color:var(--muted)}
html[data-theme=light] .card,html[data-theme=light] .stat,html[data-theme=light] .toolbar,html[data-theme=light] .empty{background:#fff}
html[data-theme=light] .next-banner,html[data-theme=light] .metric,html[data-theme=light] .target-pill{background:#f0f2fa}
html[data-theme=light] .nickname,html[data-theme=light] .level-main b,html[data-theme=light] .level-pct,html[data-theme=light] .next-banner .exp-need-text,html[data-theme=light] .metric strong,html[data-theme=light] .lvl-progress-meta .done-txt{color:#1b1d35}
html[data-theme=light] .exp-need-text b,html[data-theme=light] .green{color:#5748d5}
html[data-theme=light] .blue{color:#007f95}
html[data-theme=light] .amber,html[data-theme=light] .level-target{color:#9a6500}
html[data-theme=light] .status-tag{background:rgba(7,158,182,.10);color:#007f95;border-color:rgba(7,158,182,.20)}
html[data-theme=light] .uid-chip{background:#f0f2fa;color:#69708c}
@media(max-width:720px){main{margin-top:14px;padding:0 14px 55px}.stat{padding:14px}.card{padding:15px}.toolbar{border-radius:14px}.stats{margin-bottom:18px}}

</style>
</head>
<body>

<header>
  <div class="brand-wrap">
    <div class="logo-badge">SG</div>
    <div>
      <div class="brand">SILENT <span>GMR</span></div>
      <div class="sub">PLAYER WORKSPACE</div>
    </div>
  </div>
  <div class="header-right">
    <div class="live-pill">
      <span class="pulse" id="statusDot"></span>
      <span id="lastRefresh">Syncing…</span>
    </div>
    <button class="theme-toggle" id="themeToggle" type="button" onclick="toggleTheme()" aria-label="Switch theme" title="Switch theme"><span id="themeIcon">☾</span><span id="themeLabel">Dark</span></button>
    <select class="auto-select" id="autoInterval" onchange="setAutoRefresh()">
      <option value="300" selected>Auto: 5m</option>
      <option value="60">Auto: 1m</option>
      <option value="0">Auto: Off</option>
    </select>
  </div>
</header>

<main>
  <section class="stats">
    <div class="stat">
      <label>ACCOUNTS</label>
      <strong class="num" id="totalAccounts">0</strong>
    </div>
    <div class="stat s-green">
      <label>EXP GAINED</label>
      <strong class="green num" id="totalGained">+0</strong>
    </div>
    <div class="stat s-blue">
      <label>EXP / HOUR</label>
      <strong class="blue num" id="totalRate">0</strong>
    </div>
    <div class="stat s-amber">
      <label>MATCHES</label>
      <strong class="num" id="totalMatches">0</strong>
    </div>
  </section>

  <div class="section-head">
    <h2>Accounts <span class="count-badge num" id="countLabel">0</span></h2>
    <div class="head-controls">
      <div class="seg-toggle" role="group" aria-label="Card density">
        <button type="button" id="detailedBtn" class="active" onclick="setMode('detailed')">Detailed</button>
        <button type="button" id="compactBtn" onclick="setMode('compact')">Compact</button>
      </div>
      <button class="primary" id="toggleAddBtn" onclick="toggleAdd()">＋ Add</button>
    </div>
  </div>

  <div class="addbox" id="addBox">
    <form id="addForm">
      <div class="addrow">
        <input id="uid" placeholder="Enter Free Fire UID" inputmode="numeric" autocomplete="off" required>
        <select id="server">
          <option value="IND">IND</option>
          <option value="SG">SG</option>
          <option value="BR">BR</option>
          <option value="US">US</option>
          <option value="EU">EU</option>
          <option value="ME">ME</option>
          <option value="BD">BD</option>
          <option value="PK">PK</option>
          <option value="TH">TH</option>
          <option value="ID">ID</option>
          <option value="VN">VN</option>
          <option value="TW">TW</option>
          <option value="RU">RU</option>
        </select>
        <button class="primary" type="submit" id="addSubmitBtn">Fetch & Add</button>
      </div>
    </form>
    <div class="hint">Account ka current level, EXP, next level requirement aur progress % automatically calculate ho jayega.</div>
    <div id="addError" class="error-msg"></div>
  </div>

  <div class="toolbar">
    <div class="search-wrap">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
      <input id="search" placeholder="Search player or UID…" oninput="onSearchInput()">
      <button type="button" class="clear-btn" id="clearSearch" onclick="clearSearch()">✕</button>
    </div>

    <select id="regionFilter" onchange="render()">
      <option value="ALL">All Servers</option>
    </select>

    <select id="sort" onchange="render()">
      <option value="level">Sort: Level</option>
      <option value="pct">Sort: Next Lv %</option>
      <option value="gained">Sort: EXP Gained</option>
      <option value="rate">Sort: EXP / Hour</option>
      <option value="name">Sort: Nickname</option>
    </select>

    <label class="target-pill" title="Target Level goal">
      Target Lv
      <input id="targetLvInput" type="number" min="2" max="100" value="22" oninput="onTargetChange()">
    </label>

    <button id="refreshAllBtn" onclick="refreshAll()">
      <span id="refreshAllIcon">↻</span> Refresh All
    </button>
  </div>

  <section class="accounts" id="accounts">
    <div class="empty">
      <h3>Loading accounts…</h3>
      <p>Pulling the latest player snapshots from the sync engine.</p>
    </div>
  </section>

  <div class="foot" id="footerNote">
    Auto-refresh active · Match count is manual.
  </div>
</main>

<div class="toasts" id="toasts"></div>

<div class="modal-backdrop" id="confirmModal" onclick="if(event.target===this)closeModal(false)">
  <div class="modal" role="dialog" aria-modal="true">
    <h3 id="modalTitle">Confirm</h3>
    <p id="modalBody"></p>
    <div class="modal-actions">
      <button type="button" class="ghost" onclick="closeModal(false)">Cancel</button>
      <button type="button" id="modalConfirmBtn" class="danger" onclick="closeModal(true)">Confirm</button>
    </div>
  </div>
</div>

<script>
const FF_LEVEL_EXP = {
  1: 0, 2: 48, 3: 202, 4: 544, 5: 1012,
  6: 1844, 7: 2792, 8: 3800, 9: 4870, 10: 6004,
  11: 7192, 12: 8448, 13: 9760, 14: 11140, 15: 12566,
  16: 14060, 17: 15610, 18: 17224, 19: 18902, 20: 20632,
  21: 22424
};

let accounts = [];
let autoTimer = null;
let countdownTimer = null;
let nextRefreshAt = 0;
let modalResolver = null;
let cardMode = localStorage.getItem('sg_card_mode') || 'detailed';
let targetLv = Number(localStorage.getItem('sg_target_lv') || 22);

const fmt = n => Number(n || 0).toLocaleString('en-IN');

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({
    '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
  }[c]));
}

function getLevelThreshold(lv) {
  if (lv <= 1) return 0;
  if (FF_LEVEL_EXP[lv] !== undefined) return FF_LEVEL_EXP[lv];
  const keys = Object.keys(FF_LEVEL_EXP).map(Number).sort((a, b) => a - b);
  const lastLv = keys[keys.length - 1];
  const prevLv = keys[keys.length - 2];
  let exp = FF_LEVEL_EXP[lastLv];
  let step = FF_LEVEL_EXP[lastLv] - FF_LEVEL_EXP[prevLv];
  for (let l = lastLv + 1; l <= lv; l++) {
    step += (l <= 40 ? 60 : l <= 60 ? 200 : 500);
    exp += step;
  }
  return exp;
}

function formatEta(expNeeded, rate) {
  if (!(rate > 0 && expNeeded > 0)) return '';
  const hrs = expNeeded / rate;
  if (hrs < 1) return '~' + Math.max(1, Math.round(hrs * 60)) + 'm';
  if (hrs < 48) return '~' + hrs.toFixed(1) + 'h';
  return '~' + (hrs / 24).toFixed(1) + 'd';
}

function calcLevelProgress(acc) {
  const lv = Math.max(1, Number(acc.level || 1));
  const nextLv = lv + 1;
  const exp = Math.max(0, Number(acc.exp || 0));

  const currStart = acc.level_start_exp !== undefined ? Number(acc.level_start_exp) : getLevelThreshold(lv);
  const nextReq = acc.next_level_exp !== undefined ? Number(acc.next_level_exp) : getLevelThreshold(nextLv);
  const levelSpan = Math.max(1, nextReq - currStart);

  const inLevelExp = Math.max(0, Math.min(levelSpan, exp - currStart));
  const expNeeded = Math.max(0, nextReq - exp);

  let donePct = (inLevelExp / levelSpan) * 100;
  if (exp >= nextReq && nextReq > 0) donePct = 100;
  if (exp <= currStart) donePct = 0;

  const doneFixed = Number(donePct.toFixed(1));
  const leftFixed = Number(Math.max(0, 100 - doneFixed).toFixed(1));
  const etaText = formatEta(expNeeded, acc.rate);

  // Target Level Calculation
  const goalLv = targetLv > lv ? targetLv : nextLv;
  const goalReq = getLevelThreshold(goalLv);
  const goalExpNeeded = Math.max(0, goalReq - exp);
  const goalEta = formatEta(goalExpNeeded, acc.rate);

  return {
    lv,
    nextLv,
    exp,
    currStart,
    nextReq,
    levelSpan,
    inLevelExp,
    expNeeded,
    donePct: doneFixed,
    leftPct: leftFixed,
    etaText,
    goalLv,
    goalExpNeeded,
    goalEta
  };
}

function relTime(ts) {
  if (!ts) return '—';
  const diff = Math.max(0, Math.floor(Date.now() / 1000 - ts));
  if (diff < 15) return 'Just now';
  if (diff < 60) return diff + 's ago';
  if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
  if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
  return Math.floor(diff / 86400) + 'd ago';
}

function toast(msg, type = 'ok') {
  const wrap = document.getElementById('toasts');
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  el.innerHTML = '<span>' + (type === 'ok' ? '✓' : '⚠') + '</span><span>' + esc(msg) + '</span>';
  wrap.appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transition = 'opacity .2s ease';
    setTimeout(() => el.remove(), 220);
  }, 2800);
}

function askConfirm(title, body, confirmText = 'Confirm', btnClass = 'danger') {
  document.getElementById('modalTitle').textContent = title;
  document.getElementById('modalBody').textContent = body;
  const btn = document.getElementById('modalConfirmBtn');
  btn.textContent = confirmText;
  btn.className = btnClass;
  document.getElementById('confirmModal').classList.add('open');
  return new Promise(res => { modalResolver = res; });
}

function closeModal(result) {
  document.getElementById('confirmModal').classList.remove('open');
  if (modalResolver) {
    modalResolver(result);
    modalResolver = null;
  }
}

function toggleAdd(force) {
  const box = document.getElementById('addBox');
  const isOpen = typeof force === 'boolean' ? force : !box.classList.contains('open');
  box.classList.toggle('open', isOpen);
  document.getElementById('toggleAddBtn').textContent = isOpen ? '✕ Close' : '＋ Add';
  if (isOpen) setTimeout(() => document.getElementById('uid').focus(), 100);
}

function setMode(mode) {
  cardMode = mode;
  localStorage.setItem('sg_card_mode', mode);
  document.getElementById('accounts').classList.toggle('compact-mode', mode === 'compact');
  document.getElementById('detailedBtn').classList.toggle('active', mode === 'detailed');
  document.getElementById('compactBtn').classList.toggle('active', mode === 'compact');
}

function onTargetChange() {
  const val = Number(document.getElementById('targetLvInput').value);
  targetLv = val >= 2 ? Math.min(100, val) : 0;
  localStorage.setItem('sg_target_lv', targetLv);
  render();
}

function onSearchInput() {
  const val = document.getElementById('search').value;
  document.getElementById('clearSearch').classList.toggle('show', val.length > 0);
  render();
}

function clearSearch() {
  document.getElementById('search').value = '';
  onSearchInput();
}

async function copyUid(uid) {
  try {
    await navigator.clipboard.writeText(uid);
    toast('UID ' + uid + ' copied');
  } catch {
    toast('Copy failed', 'err');
  }
}

async function api(path, opts = {}) {
  const r = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...opts
  });
  let j = {};
  try { j = await r.json(); } catch {}
  if (!r.ok) throw Error(j.error || ('Request failed (' + r.status + ')'));
  return j;
}

function updateRegionOptions() {
  const sel = document.getElementById('regionFilter');
  const prev = sel.value;
  const regions = [...new Set(accounts.map(a => a.region).filter(Boolean))].sort();
  sel.innerHTML = '<option value="ALL">All Servers</option>' +
    regions.map(r => '<option value="' + esc(r) + '">' + esc(r) + '</option>').join('');
  if (regions.includes(prev)) sel.value = prev;
}

function updateStats(d) {
  const s = d.summary || {};
  document.getElementById('totalAccounts').textContent = fmt(s.accounts);
  document.getElementById('countLabel').textContent = fmt(s.accounts);
  document.getElementById('totalGained').textContent = '+' + fmt(s.gained);
  document.getElementById('totalRate').textContent = fmt(Math.round(s.rate || 0));
  document.getElementById('totalMatches').textContent = fmt(s.matches);
}

async function load(silent = false) {
  try {
    const d = await api('/api/accounts');
    accounts = Array.isArray(d.accounts) ? d.accounts : [];
    updateStats(d);
    updateRegionOptions();
    render();
    document.getElementById('statusDot').classList.remove('err');
    document.getElementById('lastRefresh').textContent = 'Updated ' + new Date().toLocaleTimeString([], { hour:'2-digit', minute:'2-digit', second:'2-digit' });
  } catch (e) {
    document.getElementById('statusDot').classList.add('err');
    document.getElementById('lastRefresh').textContent = 'Connection error';
    if (!silent) toast(e.message, 'err');
  }
}

function render() {
  const q = document.getElementById('search').value.trim().toLowerCase();
  const region = document.getElementById('regionFilter').value;
  const sort = document.getElementById('sort').value;
  const root = document.getElementById('accounts');

  if (!accounts.length) {
    root.innerHTML = '<div class="empty"><h3>No accounts added yet</h3><p>Add a player UID above to start tracking progress.</p></div>';
    return;
  }

  let list = accounts.filter(x => {
    const matchesText = ((x.nickname || '') + ' ' + (x.uid || '')).toLowerCase().includes(q);
    const matchesRegion = region === 'ALL' || x.region === region;
    return matchesText && matchesRegion;
  }).map(x => ({ ...x, _prog: calcLevelProgress(x) }));

  list.sort((x, y) => {
    if (sort === 'pct') return y._prog.donePct - x._prog.donePct;
    if (sort === 'gained') return (y.gained || 0) - (x.gained || 0);
    if (sort === 'rate') return (y.rate || 0) - (x.rate || 0);
    if (sort === 'name') return String(x.nickname || '').localeCompare(String(y.nickname || ''));
    return (y.level || 0) - (x.level || 0) || (y.exp || 0) - (x.exp || 0);
  });

  if (!list.length) {
    root.innerHTML = '<div class="empty"><h3>No matching accounts</h3><p>Try another search term or server filter.</p></div>';
    return;
  }

  root.innerHTML = list.map((x, i) => {
    const p = x._prog;
    const rankClass = i === 0 ? 'r1' : i === 1 ? 'r2' : i === 2 ? 'r3' : '';
    const uidEsc = esc(x.uid);
    const regEsc = esc(x.region);
    const nameEsc = esc(x.nickname || 'Unknown Player');
    const exactTime = x.updated ? new Date(x.updated * 1000).toLocaleString() : '—';

    let targetLabel = '';
    let targetReached = false;
    if (targetLv > 0 && p.lv >= targetLv) {
      targetLabel = '✓ Lv ' + targetLv + ' Reached';
      targetReached = true;
    } else if (targetLv > p.lv) {
      targetLabel = 'Target Lv ' + targetLv + ' (' + fmt(p.goalExpNeeded) + ' EXP)';
    } else {
      targetLabel = 'Next Lv ' + p.nextLv;
    }

    return `
      <article class="card">
        <div class="topline">
          <div class="identity">
            <div class="name-row">
              <span class="rank-badge ${rankClass}">#${i + 1}</span>
              <div class="nickname">${nameEsc}</div>
              <span class="server">${regEsc || '—'}</span>
            </div>
            <div class="uid-row">
              <button type="button" class="uid-chip mono" onclick="copyUid('${uidEsc}')" title="Copy UID">UID ${uidEsc} 📋</button>
              <span class="status-tag"><span class="status-dot"></span>EXP Tracking Active</span>
            </div>
          </div>

          <div class="level-side">
            <div class="level-main">Level <b class="num">${p.lv}</b></div>
            <div class="level-pct mono">${p.donePct}%</div>
            <div class="level-target ${targetReached ? 'reached' : ''}">${targetLabel}</div>
          </div>
        </div>

        <div class="next-banner">
          <div class="next-left">
            <span class="lv-pill num">Lv ${p.lv} <span class="arrow">→</span> Lv ${p.nextLv}</span>
            <span class="exp-need-text">
              Next level ke liye <b class="num">${fmt(p.expNeeded)} EXP</b> chahiye${p.etaText ? ' <span class="exp-sub">(' + p.etaText + ')</span>' : ''}
            </span>
          </div>
          <div class="exp-sub mono">${fmt(p.exp)} / ${fmt(p.nextReq)} EXP</div>
        </div>

        <div class="metrics">
          <div class="metric">
            <label>EXP Gained</label>
            <strong class="num ${x.gained > 0 ? 'green' : ''}">+${fmt(x.gained)}</strong>
          </div>
          <div class="metric">
            <label>EXP / Hour</label>
            <strong class="num ${x.rate > 0 ? 'blue' : ''}">${fmt(Math.round(x.rate || 0))}</strong>
          </div>
          <div class="metric">
            <label>MATCHES</label>
            <strong class="num">${fmt(x.matches)}</strong>
          </div>
          <div class="metric" title="${esc(exactTime)}">
            <label>Updated</label>
            <strong>${relTime(x.updated)}</strong>
          </div>
        </div>

        <div class="compact-row">
          <div class="compact-stats">
            <div class="c-stat">
              <label>Gained</label>
              <strong class="green num">+${fmt(x.gained)}</strong>
            </div>
            <div class="c-stat">
              <label>EXP / hr</label>
              <strong class="blue num">${fmt(Math.round(x.rate || 0))}</strong>
            </div>
            <div class="c-stat">
              <label>MATCHES</label>
              <strong class="num">${fmt(x.matches)}</strong>
            </div>
          </div>
          <div class="compact-actions">
            <button onclick="refreshOne(this,'${uidEsc}','${regEsc}')" title="Refresh">↻</button>
            <button onclick="addMatch(this,'${uidEsc}')" title="Add Match">＋M</button>
            <button class="warn" onclick="resetBaseline('${uidEsc}')" title="Reset Baseline">↺</button>
            <button class="danger" onclick="removeAccount('${uidEsc}','${nameEsc}')" title="Delete">🗑</button>
          </div>
        </div>

        <div class="actions">
          <button onclick="refreshOne(this,'${uidEsc}','${regEsc}')">↻ Refresh</button>
          <button onclick="addMatch(this,'${uidEsc}')">＋ Match</button>
          <button class="warn" onclick="resetBaseline('${uidEsc}')">↺ Baseline</button>
          <span class="spacer"></span>
          <button class="danger" onclick="removeAccount('${uidEsc}','${nameEsc}')">🗑 Delete</button>
        </div>

        <div class="lvl-progress-wrap">
          <div class="lvl-progress-meta">
            <span class="done-txt mono">Lv ${p.lv} → Lv ${p.nextLv}: ${p.donePct}% complete</span>
            <span class="left-txt mono">${p.leftPct}% bacha hai (${fmt(p.expNeeded)} EXP)</span>
          </div>
          <div class="progress-track" title="${p.donePct}% done · ${p.leftPct}% left">
            <div class="progress-fill" style="width:${p.donePct}%"></div>
          </div>
        </div>
      </article>
    `;
  }).join('');
}

document.getElementById('addForm').onsubmit = async e => {
  e.preventDefault();
  const uidInput = document.getElementById('uid');
  const btn = document.getElementById('addSubmitBtn');
  const err = document.getElementById('addError');
  const uid = uidInput.value.trim();
  const server = document.getElementById('server').value;
  if (!uid) return;

  btn.disabled = true;
  btn.textContent = 'Fetching…';
  err.textContent = '';

  try {
    await api('/api/accounts', { method:'POST', body:JSON.stringify({ uid, server }) });
    uidInput.value = '';
    toggleAdd(false);
    toast('Account ' + uid + ' added');
    await load();
  } catch (x) {
    err.textContent = x.message;
  } finally {
    btn.disabled = false;
    btn.textContent = 'Fetch & Add';
  }
};

async function refreshOne(btn, uid, server) {
  const prev = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<span class="spin">↻</span>';
  try {
    await api('/api/refresh', { method:'POST', body:JSON.stringify({ uid, server }) });
    await load(true);
    toast('Account refreshed');
  } catch (e) {
    toast(e.message, 'err');
  } finally {
    btn.disabled = false;
    btn.innerHTML = prev;
  }
}

async function refreshAll(silent = false) {
  const btn = document.getElementById('refreshAllBtn');
  const icon = document.getElementById('refreshAllIcon');
  btn.disabled = true;
  icon.classList.add('spin');
  try {
    await api('/api/refresh-all', { method:'POST' });
    await load(true);
    if (!silent) toast('All accounts refreshed');
  } catch (e) {
    if (!silent) toast(e.message, 'err');
  } finally {
    btn.disabled = false;
    icon.classList.remove('spin');
  }
}

async function addMatch(btn, uid) {
  btn.disabled = true;
  try {
    await api('/api/match', { method:'POST', body:JSON.stringify({ uid }) });
    await load(true);
    toast('Match +1');
  } catch (e) {
    toast(e.message, 'err');
  } finally {
    btn.disabled = false;
  }
}

async function resetBaseline(uid) {
  const ok = await askConfirm(
    'Reset EXP Baseline?',
    'Current EXP ko naya baseline set kar diya jayega aur purana gained EXP zero ho jayega.',
    'Reset Baseline',
    'warn'
  );
  if (!ok) return;
  try {
    await api('/api/baseline', { method:'POST', body:JSON.stringify({ uid }) });
    await load(true);
    toast('Baseline updated');
  } catch (e) {
    toast(e.message, 'err');
  }
}

async function removeAccount(uid, label) {
  const ok = await askConfirm(
    'Delete Account?',
    '"' + label + '" (UID ' + uid + ') aur iski tracking history delete ho jayegi.',
    'Delete',
    'danger'
  );
  if (!ok) return;
  try {
    await api('/api/delete', { method:'POST', body:JSON.stringify({ uid }) });
    await load(true);
    toast('Account deleted');
  } catch (e) {
    toast(e.message, 'err');
  }
}

function setAutoRefresh() {
  clearInterval(autoTimer);
  clearInterval(countdownTimer);
  const secs = Number(document.getElementById('autoInterval').value);
  const foot = document.getElementById('footerNote');

  if (!secs) {
    foot.textContent = 'Auto-refresh paused · Match count is tracked manually.';
    return;
  }

  nextRefreshAt = Date.now() + secs * 1000;
  const updateFoot = () => {
    const rem = Math.max(0, Math.ceil((nextRefreshAt - Date.now()) / 1000));
    const m = Math.floor(rem / 60);
    const s = String(rem % 60).padStart(2, '0');
    foot.textContent = 'Next auto-refresh in ' + m + ':' + s + ' · Match count is tracked manually.';
  };
  updateFoot();

  countdownTimer = setInterval(updateFoot, 1000);
  autoTimer = setInterval(async () => {
    nextRefreshAt = Date.now() + secs * 1000;
    await refreshAll(true);
  }, secs * 1000);
}

function applyTheme(theme) {
  const isLight = theme === 'light';
  document.documentElement.dataset.theme = isLight ? 'light' : 'dark';
  localStorage.setItem('sg_theme', isLight ? 'light' : 'dark');
  document.getElementById('themeIcon').textContent = isLight ? '☀' : '☾';
  document.getElementById('themeLabel').textContent = isLight ? 'Light' : 'Dark';
}

function toggleTheme() {
  applyTheme(document.documentElement.dataset.theme === 'light' ? 'dark' : 'light');
}

applyTheme(localStorage.getItem('sg_theme') || 'dark');

// Init
document.getElementById('targetLvInput').value = targetLv || 22;
setMode(cardMode);
setAutoRefresh();
load();
</script>
</body>
</html>
"""


def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS accounts(
        uid TEXT PRIMARY KEY, server TEXT NOT NULL, nickname TEXT NOT NULL,
        region TEXT NOT NULL, level INTEGER NOT NULL, exp INTEGER NOT NULL,
        last_exp INTEGER NOT NULL, gained INTEGER NOT NULL DEFAULT 0,
        matches INTEGER NOT NULL DEFAULT 0, first_seen REAL NOT NULL,
        updated REAL NOT NULL)""")
    con.commit()
    return con


def fetch_player(uid, server):
    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36"}
    r = requests.get(API_URL, params={"uid": uid, "server": server}, headers=headers, timeout=20)
    r.raise_for_status()
    data = r.json()
    basic = data.get("basicInfo") or {}
    required = ("accountId", "nickname", "region", "level", "exp")
    if not all(k in basic for k in required):
        raise ValueError("API response does not contain all required basicInfo fields")
    return {
        "uid": str(basic["accountId"]),
        "nickname": str(basic["nickname"]),
        "region": str(basic["region"]),
        "level": int(basic["level"]),
        "exp": int(basic["exp"]),
    }


def refresh_account(uid, server=None):
    con = db()
    row = con.execute("SELECT * FROM accounts WHERE uid=?", (uid,)).fetchone()
    if not row:
        con.close()
        raise ValueError("Account not found")
    server = server or row["server"]
    player = fetch_player(uid, server)
    now = time.time()
    delta = max(0, player["exp"] - int(row["last_exp"]))
    con.execute(
        """UPDATE accounts SET server=?,nickname=?,region=?,level=?,exp=?,
        last_exp=?,gained=gained+?,updated=? WHERE uid=?""",
        (
            server,
            player["nickname"],
            player["region"],
            player["level"],
            player["exp"],
            player["exp"],
            delta,
            now,
            uid,
        ),
    )
    con.commit()
    con.close()


def account_dict(row):
    elapsed = max((time.time() - row["first_seen"]) / 3600, 1 / 60)
    return {**dict(row), "rate": row["gained"] / elapsed}


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.get("/api/accounts")
def get_accounts():
    con = db()
    rows = [account_dict(r) for r in con.execute("SELECT * FROM accounts ORDER BY updated DESC")]
    con.close()
    summary = {
        "accounts": len(rows),
        "gained": sum(x["gained"] for x in rows),
        "rate": sum(x["rate"] for x in rows),
        "matches": sum(x["matches"] for x in rows),
    }
    return jsonify(accounts=rows, summary=summary)


@app.post("/api/accounts")
def add_account():
    body = request.get_json(silent=True) or {}
    uid, server = str(body.get("uid", "")).strip(), str(body.get("server", "IND")).upper()
    if not uid.isdigit():
        return jsonify(error="Enter a valid numeric UID"), 400
    try:
        player = fetch_player(uid, server)
        now = time.time()
        con = db()
        con.execute(
            """INSERT INTO accounts(uid,server,nickname,region,level,exp,last_exp,gained,matches,first_seen,updated)
            VALUES(?,?,?,?,?,?,?,0,0,?,?) ON CONFLICT(uid) DO UPDATE SET
            server=excluded.server,nickname=excluded.nickname,region=excluded.region,
            level=excluded.level,exp=excluded.exp,last_exp=excluded.exp,updated=excluded.updated""",
            (
                player["uid"],
                server,
                player["nickname"],
                player["region"],
                player["level"],
                player["exp"],
                player["exp"],
                now,
                now,
            ),
        )
        con.commit()
        con.close()
        return jsonify(ok=True, player=player)
    except Exception as e:
        return jsonify(error=f"Could not fetch account: {e}"), 502


@app.post("/api/refresh")
def refresh_one():
    body = request.get_json(silent=True) or {}
    try:
        refresh_account(str(body.get("uid", "")), body.get("server"))
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(error=str(e)), 502


@app.post("/api/refresh-all")
def refresh_all():
    con = db()
    rows = con.execute("SELECT uid,server FROM accounts").fetchall()
    con.close()
    errors = []
    for row in rows:
        try:
            refresh_account(row["uid"], row["server"])
        except Exception as e:
            errors.append({"uid": row["uid"], "error": str(e)})
    return jsonify(ok=not errors, errors=errors)


@app.post("/api/match")
def match():
    uid = str((request.get_json(silent=True) or {}).get("uid", ""))
    con = db()
    cur = con.execute("UPDATE accounts SET matches=matches+1 WHERE uid=?", (uid,))
    con.commit()
    con.close()
    if not cur.rowcount:
        return jsonify(error="Account not found"), 404
    return jsonify(ok=True)


@app.post("/api/baseline")
def baseline():
    uid = str((request.get_json(silent=True) or {}).get("uid", ""))
    con = db()
    cur = con.execute(
        "UPDATE accounts SET last_exp=exp,gained=0,first_seen=?,updated=? WHERE uid=?",
        (time.time(), time.time(), uid),
    )
    con.commit()
    con.close()
    if not cur.rowcount:
        return jsonify(error="Account not found"), 404
    return jsonify(ok=True)


@app.post("/api/delete")
def delete():
    uid = str((request.get_json(silent=True) or {}).get("uid", ""))
    con = db()
    cur = con.execute("DELETE FROM accounts WHERE uid=?", (uid,))
    con.commit()
    con.close()
    if not cur.rowcount:
        return jsonify(error="Account not found"), 404
    return jsonify(ok=True)


if __name__ == "__main__":
    db().close()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "9000")), debug=False)
