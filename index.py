"""
👑 ROYAL GROCERIES - Single File Edition
This script contains the entire application (HTML, CSS, JS, and Backend).
Run: python royal_single_app.py
"""

import http.server
import json
import urllib.request
import urllib.parse
import smtplib
import random
import string
import threading
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import os
import traceback

PORT = int(os.environ.get('ROYAL_PORT', 8000))

# ── Configuration ──────────────────────────────────────────
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get('ROYAL_SMTP_EMAIL', 'siddharths1003@gmail.com')
SENDER_PASSWORD = os.environ.get('ROYAL_SMTP_PASSWORD', 'vsekxaewjkzvhfpl')
ADMIN_EMAIL = 'siddharths1003@gmail.com'

TWILIO_SID = os.environ.get('ROYAL_TWILIO_SID', '')
TWILIO_TOKEN = os.environ.get('ROYAL_TWILIO_TOKEN', '')
TWILIO_PHONE = os.environ.get('ROYAL_TWILIO_PHONE', '')

# OTP store: {identifier: {otp, timestamp}}
otp_store = {}
OTP_EXPIRY_SECONDS = 600

# ── Content Placeholders ───────────────────────────────────
# We will fill these in via follow-up edits to avoid token limits
CSS_CONTENT = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:wght@700;800;900&display=swap');
:root {
  --royal-900: #020617; --royal-800: #0A192F; --royal-700: #0F2240; --royal-600: #172A45; --royal-500: #1E3A5F;
  --accent: #3A7BD5; --accent-light: #5B9BF0; --accent-glow: rgba(58, 123, 213, 0.4);
  --text-primary: #FFFFFF; --text-secondary: #CBD5E1; --text-muted: #64748B;
  --glass-bg: rgba(10, 25, 47, 0.85); --glass-bg-light: rgba(23, 42, 69, 0.6);
  --glass-border: rgba(58, 123, 213, 0.2); --glass-border-hover: rgba(58, 123, 213, 0.5);
  --success: #22C55E; --danger: #EF4444; --warning: #F59E0B;
  --radius-sm: 8px; --radius-md: 12px; --radius-lg: 16px; --radius-xl: 24px;
  --shadow-sm: 0 2px 8px rgba(0,0,0,0.2); --shadow-md: 0 8px 24px rgba(0,0,0,0.3); --shadow-lg: 0 16px 48px rgba(0,0,0,0.4);
  --shadow-glow: 0 0 30px var(--accent-glow); --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
*, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Inter',sans-serif; background:var(--royal-900); color:var(--text-primary); min-height:100vh; overflow-x:hidden; line-height:1.6; }
.hidden { display:none !important; }
.bg-particles { position:fixed; top:0; left:0; width:100%; height:100%; z-index:0; pointer-events:none; background:radial-gradient(ellipse at 20% 50%, rgba(58,123,213,0.08) 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, rgba(58,123,213,0.05) 0%, transparent 40%); }
.overlay { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(2,6,23,0.92); backdrop-filter:blur(20px); display:flex; justify-content:center; align-items:center; z-index:2000; }
.auth-box { background:linear-gradient(145deg, rgba(15,34,64,0.95), rgba(10,25,47,0.98)); border:1px solid var(--glass-border); padding:3rem 2.5rem; border-radius:var(--radius-xl); width:92%; max-width:420px; text-align:center; box-shadow:var(--shadow-lg), var(--shadow-glow); }
.auth-logo { font-family:'Playfair Display',serif; font-size:2.5rem; font-weight:900; background:linear-gradient(135deg, #fff, var(--accent-light)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:0.3rem; }
.auth-input { width:100%; padding:14px 18px; margin-bottom:1rem; border:1px solid var(--glass-border); background:rgba(255,255,255,0.04); color:var(--text-primary); border-radius:var(--radius-md); outline:none; transition:var(--transition); }
.auth-input:focus { border-color:var(--accent); background:rgba(255,255,255,0.08); }
.captcha-box { background:rgba(255,255,255,0.03); padding:20px; border-radius:var(--radius-md); margin-bottom:1.2rem; border:1px solid var(--glass-border); }
.captcha-puzzle { display:flex; align-items:center; justify-content:center; gap:12px; font-size:1.8rem; font-weight:700; background:rgba(0,0,0,0.2); border-radius:var(--radius-sm); margin-bottom:12px; font-family:'Playfair Display',serif; }
.otp-inputs { display:flex; gap:10px; justify-content:center; margin:1.5rem 0; }
.otp-digit { width:44px; height:52px; text-align:center; font-size:1.5rem; background:rgba(255,255,255,0.05); border:2px solid var(--glass-border); color:var(--accent-light); border-radius:var(--radius-sm); outline:none; }
.navbar { display:flex; justify-content:space-between; align-items:center; padding:0.8rem 5%; background:rgba(2,6,23,0.9); border-bottom:1px solid var(--glass-border); backdrop-filter:blur(20px); position:sticky; top:0; z-index:500; }
.nav-logo { font-family:'Playfair Display',serif; font-size:1.8rem; font-weight:900; background:linear-gradient(135deg, #fff, var(--accent-light)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; text-decoration:none; display:flex; align-items:center; gap:8px; }
.search-wrapper { display:flex; align-items:center; background:rgba(255,255,255,0.06); border:1px solid var(--glass-border); border-radius:999px; padding:4px 6px 4px 18px; width:100%; }
.search-wrapper input { background:none; border:none; color:#fff; width:100%; padding:8px; outline:none; }
.search-wrapper button { background:var(--accent); border:none; color:#fff; width:34px; height:34px; border-radius:50%; cursor:pointer; }
.hero { min-height:400px; display:flex; align-items:center; justify-content:center; text-align:center; padding:80px 20px; background:linear-gradient(135deg,rgba(2,6,23,0.8),rgba(10,25,47,0.7)), url('https://images.unsplash.com/photo-1542838132-92c53300491e?w=1200'); background-size:cover; background-position:center; position:relative; }
.hero h1 { font-family:'Playfair Display',serif; font-size:3.5rem; color:#fff; margin-bottom:1rem; }
.products-grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(250px, 1fr)); gap:24px; padding:40px 5%; }
.product-card { background:rgba(255,255,255,0.03); border:1px solid var(--glass-border); border-radius:var(--radius-lg); overflow:hidden; transition:var(--transition); backdrop-filter:blur(10px); }
.product-card:hover { transform:translateY(-5px); border-color:var(--accent); }
.product-card-img { width:100%; height:180px; object-fit:cover; }
.product-card-body { padding:20px; }
.btn { padding:12px 24px; border-radius:var(--radius-md); font-weight:600; cursor:pointer; border:none; transition:var(--transition); }
.btn-primary { background:var(--accent); color:#fff; width:100%; }
.modal-overlay { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); backdrop-filter:blur(10px); display:flex; justify-content:center; align-items:center; z-index:1500; }
.modal { background:var(--royal-700); padding:30px; border-radius:var(--radius-xl); border:1px solid var(--glass-border); width:90%; max-width:600px; max-height:80vh; overflow-y:auto; }
.ai-chat-container { position:fixed; bottom:90px; right:24px; width:350px; z-index:1000; }
.ai-chat { background:var(--royal-800); border:1px solid var(--glass-border); border-radius:var(--radius-xl); height:450px; display:flex; flex-direction:column; overflow:hidden; }
.chat-header { background:var(--accent); padding:15px; display:flex; justify-content:space-between; }
.chat-body { flex:1; padding:15px; overflow-y:auto; display:flex; flex-direction:column; gap:10px; }
.chat-msg { padding:10px 15px; border-radius:15px; max-width:80%; font-size:0.9rem; }
.chat-msg.bot { background:rgba(255,255,255,0.05); align-self:flex-start; }
.chat-msg.user { background:var(--accent); align-self:flex-end; }
.chat-fab { position:fixed; bottom:24px; right:24px; width:60px; height:60px; border-radius:50%; background:var(--accent); color:#fff; border:none; font-size:1.5rem; cursor:pointer; box-shadow:0 8px 24px rgba(0,0,0,0.3); z-index:1000; }
.toast-container { position:fixed; top:20px; right:20px; z-index:3000; display:flex; flex-direction:column; gap:10px; }
.toast { padding:12px 20px; border-radius:8px; color:#fff; background:var(--accent); animation: slideIn 0.3s ease; }
@keyframes slideIn { from{transform:translateX(100%)} to{transform:translateX(0)} }
"""
JS_CONTENT = """
const BACKEND_URL = '';
const ADMIN_EMAIL = 'siddharths1003@gmail.com';
const Store = {
  get(k, f=null) { try { const v=localStorage.getItem(k); return v?JSON.parse(v):f } catch(e){return f} },
  set(k, v) { localStorage.setItem(k, JSON.stringify(v)) },
  remove(k) { localStorage.removeItem(k) }
};
const DB = {
  USERS:'royal_users_v3', PRODUCTS:'royal_products_v3', SESSION:'royal_session_v3', BANNER:'royal_banner_v3', CART:'royal_cart_v3'
};
const DEFAULT_PRODUCTS = [
  {id:'p1',name:'Fresh Apples',price:120,category:'fruits',image:'https://images.unsplash.com/photo-1560806887-1e4cd0b6caa6?w=400'},
  {id:'p2',name:'Organic Bananas',price:60,category:'fruits',image:'https://images.unsplash.com/photo-1571501679680-de32f1e7aad4?w=400'},
  {id:'p3',name:'Almond Milk',price:250,category:'dairy',image:'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400'},
  {id:'p4',name:'Whole Wheat Bread',price:40,category:'bakery',image:'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400'},
  {id:'p5',name:'Farm Fresh Eggs',price:80,category:'dairy',image:'https://images.unsplash.com/photo-1506976785307-8732e854ad03?w=400'},
  {id:'p6',name:'Basmati Rice 5kg',price:350,category:'staples',image:'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400'},
  {id:'p7',name:'Organic Honey',price:320,category:'condiments',image:'https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=400'},
  {id:'p8',name:'Fresh Tomatoes',price:30,category:'vegetables',image:'https://images.unsplash.com/photo-1546470427-0d4db154ceb8?w=400'},
  {id:'p9',name:'Avocados',price:180,category:'fruits',image:'https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=400'},
  {id:'p10',name:'Orange Juice 1L',price:110,category:'beverages',image:'https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=400'}
];
if(!Store.get(DB.PRODUCTS)) Store.set(DB.PRODUCTS, DEFAULT_PRODUCTS);
if(!Store.get(DB.USERS)) Store.set(DB.USERS, {});
if(!Store.get(DB.BANNER)) Store.set(DB.BANNER, {type:'text', data:'Enjoy shopping with ROYAL'});

let currentUser=Store.get(DB.SESSION);
let cart=Store.get(DB.CART,[]);
let pendingAuthId, expectedOtp, otpInterval, captchaAnswer;

async function api(path, data) {
  try {
    const res = await fetch(path, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) });
    return await res.json();
  } catch(e) { return {status:'error', message:'Server error'} }
}

function showToast(m, t='info') {
  let c = document.getElementById('toast-c') || Object.assign(document.body.appendChild(document.createElement('div')), {id:'toast-c', className:'toast-container'});
  let x = Object.assign(c.appendChild(document.createElement('div')), {className:`toast ${t}`, textContent:m});
  setTimeout(() => { x.style.opacity='0'; setTimeout(()=>x.remove(), 400) }, 3000);
}

function showAuth() { document.getElementById('authOverlay').style.display='flex'; document.getElementById('app').classList.add('hidden'); }
function showApp() { document.getElementById('authOverlay').style.display='none'; document.getElementById('app').classList.remove('hidden'); render(); }

function handleAuthContinue() {
  let id = document.getElementById('authInput').value.trim();
  if(!id) return showToast('Enter email/phone','error');
  let users=Store.get(DB.USERS,{});
  if(!users[id] && document.getElementById('captchaSection').classList.contains('hidden')) {
    document.getElementById('captchaSection').classList.remove('hidden');
    let a=Math.floor(Math.random()*20), b=Math.floor(Math.random()*15);
    captchaAnswer=a+b;
    document.getElementById('captchaPuzzle').textContent=`${a} + ${b} = ?`;
    return showToast('Solve captcha','warning');
  }
  if(!users[id] && parseInt(document.getElementById('captchaInput').value)!==captchaAnswer) return showToast('Wrong captcha','error');
  sendOtp(id);
}

async function sendOtp(id) {
  pendingAuthId = id;
  expectedOtp = Math.floor(100000 + Math.random()*900000).toString();
  let res = await api('/send-otp', {identifier:id, otp:expectedOtp});
  if(res.devOtp) showToast(`OTP (Dev): ${res.devOtp}`, 'warning');
  else if(res.status==='success') showToast('OTP sent!','success');
  document.getElementById('loginForm').classList.add('hidden');
  document.getElementById('otpForm').classList.remove('hidden');
  document.getElementById('authSubtitle').textContent='Enter 6-digit OTP';
}

function verifyOtp() {
  let val = Array.from(document.querySelectorAll('.otp-digit')).map(i=>i.value).join('');
  if(val !== expectedOtp) return showToast('Invalid OTP','error');
  let users = Store.get(DB.USERS,{});
  if(!users[pendingAuthId]) users[pendingAuthId] = {identifier:pendingAuthId, searches:[]};
  Store.set(DB.USERS, users);
  currentUser = users[pendingAuthId];
  Store.set(DB.SESSION, currentUser);
  showApp();
}

function render() {
  let p = Store.get(DB.PRODUCTS,[]);
  let g = document.getElementById('productsGrid');
  g.innerHTML = p.map(x => `
    <div class="product-card">
      <img src="${x.image}" class="product-card-img">
      <div class="product-card-body">
        <div class="product-card-name">${x.name}</div>
        <div class="product-card-price">₹${x.price}</div>
        <button class="btn btn-primary" onclick="addToCart('${x.id}')">Add to Cart</button>
      </div>
    </div>`).join('');
  document.getElementById('adminLink').classList.toggle('hidden', currentUser?.identifier !== ADMIN_EMAIL);
}

function addToCart(id) {
  let p = Store.get(DB.PRODUCTS,[]).find(x=>x.id===id);
  let item = cart.find(x=>x.id===id);
  if(item) item.qty++; else cart.push({...p, qty:1});
  Store.set(DB.CART, cart);
  document.getElementById('cartBadge').textContent = cart.reduce((a,b)=>a+b.qty,0);
  document.getElementById('cartBadge').style.display='flex';
  showToast('Added to cart','success');
}

function openCart() {
  let m = document.getElementById('cartOverlay');
  document.getElementById('cartItems').innerHTML = cart.map((x,i)=>`<div>${x.name} x${x.qty} - ₹${x.price*x.qty} <button onclick="cart.splice(${i},1);Store.set(DB.CART,cart);openCart()">x</button></div>`).join('');
  document.getElementById('cartTotal').innerHTML = `<h3>Total: ₹${cart.reduce((a,b)=>a+b.price*b.qty,0)}</h3><button class="btn btn-primary" onclick="placeOrder()">Checkout</button>`;
  m.classList.remove('hidden');
}

async function placeOrder() {
  let res = await api('/send-order', {user:currentUser.identifier, items:cart, total:cart.reduce((a,b)=>a+b.price*b.qty,0), method:'shop'});
  alert(`Order Placed! Code: ${res.code}`);
  cart=[]; Store.set(DB.CART,[]); document.getElementById('cartOverlay').classList.add('hidden'); render();
}

function logout() { Store.remove(DB.SESSION); location.reload(); }
function toggleChat() { document.getElementById('aiChatContainer').classList.toggle('hidden'); }

function sendChat() {
  let i=document.getElementById('chatMsgInput'), b=document.getElementById('chatBody'), m=i.value;
  if(!m)return; i.value='';
  b.innerHTML += `<div class="chat-msg user">${m}</div>`;
  setTimeout(()=> {
    let r = "I'm Royal AI. Contact us at " + ADMIN_EMAIL + " for support!";
    if(m.toLowerCase().includes('price')) r="Our products start from ₹30!";
    b.innerHTML += `<div class="chat-msg bot">${r}</div>`;
    b.scrollTop = b.scrollHeight;
  }, 600);
}

document.addEventListener('DOMContentLoaded', ()=> {
  if(currentUser) showApp(); else showAuth();
  document.querySelectorAll('.otp-digit').forEach((el,i,arr)=>el.oninput=()=>i<5?arr[i+1].focus():verifyOtp());
});
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Royal — Premium Groceries</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        {{CSS_HERE}}
    </style>
</head>
<body>
    {{HTML_BODY_HERE}}
    <script>
        {{JS_HERE}}
    </script>
</body>
</html>"""

# ── Helper Functions ───────────────────────────────────────
def send_email(to_email, subject, html_body):
    if not SENDER_PASSWORD:
        print(f"[SIMULATE] Email to {to_email} | Subject: {subject}")
        return True
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f'Royal Groceries <{SENDER_EMAIL}>'
        msg['To'] = to_email
        msg.attach(MIMEText(html_body, 'html'))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[FAIL] Email error: {e}")
        return False

def generate_order_code(): return ''.join(random.choices(string.digits, k=4)) + ''.join(random.choices(string.ascii_uppercase, k=2))
def store_otp(identifier, otp): otp_store[identifier] = {'otp': otp, 'time': time.time()}
def verify_stored_otp(identifier, otp):
    entry = otp_store.get(identifier)
    if not entry or time.time() - entry['time'] > OTP_EXPIRY_SECONDS: return False
    if entry['otp'] == otp:
        del otp_store[identifier]
        return True
    return False

def cleanup_expired_otps():
    while True:
        time.sleep(60)
        now = time.time()
        expired = [k for k, v in otp_store.items() if now - v['time'] > OTP_EXPIRY_SECONDS]
        for k in expired: del otp_store[k]

def otp_email_html(otp):
    return f"""<div style="font-family:sans-serif;max-width:500px;margin:auto;padding:40px;background:#0A192F;border-radius:20px;color:#fff;border:1px solid #3A7BD5">
    <h1 style="text-align:center;color:#3A7BD5">👑 Royal Groceries</h1>
    <p style="text-align:center;">Your verification code</p>
    <div style="text-align:center;font-size:42px;font-weight:bold;letter-spacing:12px;color:#3A7BD5;padding:25px;background:rgba(255,255,255,0.05);border-radius:16px;margin:25px 0;">{otp}</div>
    <p style="text-align:center;color:#8892B0;font-size:13px">Expires in 10 minutes.</p></div>"""

def order_email_html(user, items, total, method, address, delivery_charge, code):
    rows = ''.join(f"<tr><td>{it['name']}</td><td>₹{it['price']}</td><td>{it.get('qty',1)}</td></tr>" for it in items)
    return f"<h1>New Order [{code}]</h1><p>Customer: {user}</p><p>Total: ₹{total + delivery_charge}</p><table>{rows}</table>"

class RoyalHandler(http.server.BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            # Construct final HTML
            full_html = HTML_TEMPLATE.replace('{{CSS_HERE}}', CSS_CONTENT)\
                                     .replace('{{JS_HERE}}', JS_CONTENT)\
                                     .replace('{{HTML_BODY_HERE}}', HTML_BODY_CONTENT)
            self.wfile.write(full_html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def respond_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length).decode('utf-8')) if length else {}

        if self.path == '/send-otp':
            id, otp = body.get('identifier', ''), body.get('otp', '')
            store_otp(id, otp)
            ok = send_email(id, "Royal OTP", otp_email_html(otp)) if '@' in id else True
            self.respond_json({"status": "success" if ok else "error", "devOtp": otp if not SENDER_PASSWORD else None})

        elif self.path == '/verify-otp':
            id, otp = body.get('identifier', ''), body.get('otp', '')
            valid = verify_stored_otp(id, otp)
            self.respond_json({"status": "success" if valid else "error"})

        elif self.path == '/send-order':
            user, items, total = body.get('user'), body.get('items'), body.get('total')
            method, addr, dc = body.get('method'), body.get('address'), body.get('deliveryCharge', 0)
            code = generate_order_code()
            ok = send_email(ADMIN_EMAIL, f"New Order {code}", order_email_html(user, items, total, method, addr, dc, code))
            self.respond_json({"status": "success" if ok else "error", "code": code})

        elif self.path == '/notify-admin':
            msg = body.get('message', '')
            ok = send_email(ADMIN_EMAIL, "Royal Admin Alert", f"<p>{msg}</p>")
            self.respond_json({"status": "success" if ok else "error"})

        elif self.path == '/health':
            self.respond_json({"status": "ok", "smtp": bool(SENDER_PASSWORD)})

def run():
    threading.Thread(target=cleanup_expired_otps, daemon=True).start()
    server = http.server.ThreadingHTTPServer(('', PORT), RoyalHandler)
    print(f"🚀 ROYAL GROCERIES starting at http://localhost:{PORT}")
    try: server.serve_forever()
    except KeyboardInterrupt: server.shutdown()

HTML_BODY_CONTENT = """
    <!-- Background Ambient -->
    <div class="bg-particles" aria-hidden="true"></div>

    <!-- AUTH OVERLAY -->
    <div id="authOverlay" class="overlay">
        <div class="auth-box">
            <span class="auth-crown">👑</span>
            <div class="auth-logo">Royal</div>
            <p class="auth-subtitle" id="authSubtitle">Enter your email or phone to continue</p>

            <div id="loginForm">
                <input type="text" id="authInput" class="auth-input" placeholder="Email address or phone number"
                    autocomplete="email" spellcheck="false">
                <div id="captchaSection" class="captcha-box hidden">
                    <div class="captcha-label"><i class="fas fa-shield-halved"></i> Human Verification</div>
                    <div class="captcha-puzzle" id="captchaPuzzle">? + ? = ?</div>
                    <input type="number" id="captchaInput" class="auth-input" placeholder="Your answer" style="margin-bottom:0">
                </div>
                <button id="authBtn" class="btn btn-primary" onclick="handleAuthContinue()">
                    <i class="fas fa-arrow-right"></i> Continue
                </button>
            </div>

            <div id="otpForm" class="hidden">
                <p style="color:var(--text-secondary);margin-bottom:8px">Enter the 6-digit OTP sent to you</p>
                <div class="otp-timer">Expires in <span id="otpTimer">10:00</span></div>
                <div class="otp-inputs">
                    <input type="text" class="otp-digit" maxlength="1" inputmode="numeric" pattern="[0-9]">
                    <input type="text" class="otp-digit" maxlength="1" inputmode="numeric" pattern="[0-9]">
                    <input type="text" class="otp-digit" maxlength="1" inputmode="numeric" pattern="[0-9]">
                    <input type="text" class="otp-digit" maxlength="1" inputmode="numeric" pattern="[0-9]">
                    <input type="text" class="otp-digit" maxlength="1" inputmode="numeric" pattern="[0-9]">
                    <input type="text" class="otp-digit" maxlength="1" inputmode="numeric" pattern="[0-9]">
                </div>
                <button class="btn btn-primary" onclick="verifyOtp()"><i class="fas fa-check-circle"></i> Verify OTP</button>
                <button class="btn-ghost" onclick="backToLogin()"><i class="fas fa-arrow-left"></i> Change email/phone</button>
            </div>
            <p id="authError" class="error-msg"></p>
        </div>
    </div>

    <!-- MAIN APPLICATION -->
    <div id="app" class="hidden">
        <nav class="navbar" id="navbar">
            <a href="#" class="nav-logo" onclick="location.reload()"><span>👑</span> Royal</a>
            <div class="search-container">
                <div class="search-wrapper">
                    <input type="text" id="searchInput" placeholder="Search for groceries..." autocomplete="off" spellcheck="false">
                    <button onclick="handleSearch()"><i class="fas fa-search"></i></button>
                </div>
            </div>
            <div class="nav-actions">
                <a href="#" id="adminLink" class="hidden" onclick="openAdmin(); return false;"><i class="fas fa-gauge-high"></i> <span class="nav-text">Admin</span></a>
                <button onclick="openCart()"><i class="fas fa-shopping-cart"></i> <span class="nav-text">Cart</span><span class="cart-badge" id="cartBadge" style="display:none">0</span></button>
                <button onclick="logout()"><i class="fas fa-sign-out-alt"></i> <span class="nav-text">Logout</span></button>
            </div>
        </nav>

        <section class="hero" id="heroSection">
            <div class="hero-content" id="heroContent">
                <h1>Enjoy shopping with ROYAL</h1>
                <p>Premium groceries delivered to your doorstep. Quality you can trust.</p>
            </div>
        </section>

        <section class="section hidden" id="recommendSection">
            <h2 class="section-title">Recommended For You</h2>
            <div class="products-grid" id="recommendGrid"></div>
        </section>

        <section class="section">
            <h2 class="section-title" id="productsSectionTitle">Our Selection</h2>
            <div class="products-grid" id="productsGrid"></div>
            <div id="noResults" class="no-results hidden">
                <i class="fas fa-search"></i>
                <h3>Not available</h3>
                <p>Sorry for the inconvenience.</p>
            </div>
        </section>

        <footer class="footer">
            <p>👑 Royal Groceries &copy; 2026. Premium quality, always.</p>
            <p style="margin-top:6px"><a href="mailto:siddharths1003@gmail.com">Contact Admin</a> &bull; All prices in Indian Rupees (₹)</p>
        </footer>
    </div>

    <!-- MODALS -->
    <div id="cartOverlay" class="modal-overlay hidden">
        <div class="modal">
            <div class="modal-header"><h2><i class="fas fa-shopping-cart"></i> Your Cart</h2><button class="modal-close" onclick="closeCart()">&times;</button></div>
            <div id="cartItems"></div>
            <div id="cartTotal"></div>
        </div>
    </div>

    <div id="checkoutOverlay" class="modal-overlay hidden">
        <div class="modal">
            <div class="modal-header"><h2><i class="fas fa-credit-card"></i> Checkout</h2><button class="modal-close" onclick="closeCheckout()">&times;</button></div>
            <div class="form-group">
                <label class="form-label">Delivery Method</label>
                <select id="deliveryMethod" class="form-select" onchange="toggleDeliveryField()">
                    <option value="home">🚚 Home Delivery</option>
                    <option value="shop">🏪 Collect from Shop</option>
                </select>
            </div>
            <div class="form-group" id="addressGroup">
                <label class="form-label">Delivery Address</label>
                <textarea id="deliveryAddress" class="form-textarea" placeholder="Enter your full address..."></textarea>
                <p class="form-hint">Free delivery within 15km. ₹100/km beyond that.</p>
            </div>
            <button class="btn btn-primary" onclick="placeOrder()"><i class="fas fa-check"></i> Place Order</button>
        </div>
    </div>

    <div id="adminOverlay" class="modal-overlay hidden">
        <div class="modal" style="max-width:750px">
            <div class="modal-header"><h2><i class="fas fa-gauge-high"></i> Admin Dashboard</h2><button class="modal-close" onclick="closeAdmin()">&times;</button></div>
            <div class="admin-section">
                <h3><i class="fas fa-image"></i> Offer Banner</h3>
                <input type="file" id="adminBannerFile" accept="image/*" class="admin-input" style="padding:8px">
                <div style="display:flex;gap:10px;margin-top:4px">
                    <button class="btn btn-primary btn-sm" onclick="adminUploadBanner()">Upload</button>
                    <button class="btn btn-secondary btn-sm" onclick="adminClearBanner()">Clear</button>
                </div>
            </div>
            <div class="admin-section">
                <h3><i class="fas fa-box"></i> Add/Edit Product</h3>
                <input type="text" id="adminProdName" class="admin-input" placeholder="Product Name">
                <input type="number" id="adminProdPrice" class="admin-input" placeholder="Price (₹)">
                <input type="text" id="adminProdImg" class="admin-input" placeholder="Image URL">
                <button class="btn btn-primary btn-sm" onclick="adminSaveProduct()">Save Product</button>
            </div>
            <div class="admin-section">
                <h3><i class="fas fa-list"></i> Products List</h3>
                <table class="admin-table">
                    <thead><tr><th>Product</th><th>Price</th><th>Actions</th></tr></thead>
                    <tbody id="adminProductsList"></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- AI CHAT -->
    <div id="aiChatContainer" class="ai-chat-container hidden">
        <div class="ai-chat">
            <div class="chat-header"><h3><span class="status-dot"></span> Royal AI Assistant</h3><button onclick="toggleChat()"><i class="fas fa-minus"></i></button></div>
            <div class="chat-body" id="chatBody"><div class="chat-msg bot">Hello! 👋 I'm your Royal AI Assistant.</div></div>
            <div class="chat-input-area">
                <input type="text" id="chatMsgInput" placeholder="Ask me..." onkeypress="handleChatKey(event)">
                <button onclick="sendChat()"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>
    </div>
    <button id="chatFab" class="chat-fab" onclick="toggleChat()"><i class="fas fa-robot"></i><span class="badge"></span></button>
"""

if __name__ == "__main__":
    run()
