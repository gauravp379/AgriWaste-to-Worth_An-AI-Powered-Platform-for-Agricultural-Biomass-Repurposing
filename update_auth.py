import os

files = ['ai-analyzer.html', 'marketplace.html', 'dashboard.html', 'chatbot.html', 'about.html']
auth_html = '''
    <!-- Auth Modal -->
    <div id="authModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <div class="auth-container">
                <div class="auth-form" id="loginForm">
                    <h2>Welcome Back</h2>
                    <form>
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" id="loginEmail" required>
                        </div>
                        <div class="form-group">
                            <label>Password</label>
                            <input type="password" id="loginPassword" required>
                        </div>
                        <button type="submit" class="btn-primary btn-block">Login</button>
                        <p class="auth-switch">Don't have an account? <a href="#" id="showSignup">Sign Up</a></p>
                    </form>
                </div>
                <div class="auth-form hidden" id="signupForm">
                    <h2>Create Account</h2>
                    <form>
                        <div class="form-group">
                            <label>Full Name</label>
                            <input type="text" id="signupName" required>
                        </div>
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" id="signupEmail" required>
                        </div>
                        <div class="form-group">
                            <label>Password</label>
                            <input type="password" id="signupPassword" required>
                        </div>
                        <div class="form-group">
                            <label>User Type</label>
                            <select id="userType" required>
                                <option value="farmer">Farmer</option>
                                <option value="aggregator">Aggregator</option>
                                <option value="processor">Processor</option>
                                <option value="transporter">Transporter</option>
                                <option value="buyer">Buyer</option>
                                <option value="ngo">NGO/Regulator</option>
                                <option value="admin">Admin</option>
                            </select>
                        </div>
                        <button type="submit" class="btn-primary btn-block">Sign Up</button>
                        <p class="auth-switch">Already have an account? <a href="#" id="showLogin">Login</a></p>
                    </form>
                </div>
            </div>
        </div>
    </div>
'''

auth_btns = '''                <button class="btn-primary" id="loginBtn">Login</button>
                <button class="btn-secondary" id="signupBtn">Sign Up</button>'''

for f in files:
    path = os.path.join(r'd:\SEM 5\AI\Agriculture_waste_marketplace', f)
    if not os.path.exists(path): continue
    with open(path, 'r', encoding='utf-8') as file: content = file.read()
    
    content = content.replace('<div class="user-menu" id="userMenu">', '<div class="user-menu" id="userMenu" style="display:none">')
    
    tgt_menu = '<button class="btn-text" id="logoutBtn" style="margin-left:12px">Logout</button>\n                </div>'
    if 'id="loginBtn"' not in content: content = content.replace(tgt_menu, tgt_menu + '\n' + auth_btns)
    if 'id="authModal"' not in content:
        if '<script src="js/main.js"></script>' in content:
            content = content.replace('<script src="js/main.js"></script>', auth_html + '\n    <script src="js/main.js"></script>')
        else:
            content = content.replace('</body>', auth_html + '\n</body>')
    if 'js/auth.js' not in content: content = content.replace('</body>', '    <script src="js/auth.js"></script>\n</body>')
    
    with open(path, 'w', encoding='utf-8') as file: file.write(content)
