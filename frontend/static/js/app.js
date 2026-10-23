const API = 'http://192.168.1.2:8080/api';
let ME = null;
let TOKEN = null;
let countdownTimer = null;
let resetPwTarget = null;

let html5QrCode = null;

const COLORS = ['#2563eb', '#7c3aed', '#059669', '#dc2626', '#d97706', '#0891b2', '#be185d'];

async function apiFetch(path, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    if (TOKEN) headers['Authorization'] = `Bearer ${TOKEN}`;
    return fetch(`${API}${path}`, { ...options, headers });
}

async function login() {
    const user_id = document.getElementById('loginId').value.trim();
    const password = document.getElementById('loginPass').value.trim();
    if (!user_id || !password) { setLoginError('Please enter your User ID and Password'); return; }
    try {
        const res = await fetch(`${API}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id, password })
        });
        const data = await res.json();
        if (data.success) {
            ME = data;
            TOKEN = data.token;
            initApp();
        } else {
            setLoginError(data.message || 'Invalid credentials');
        }
    } catch { setLoginError('Cannot connect to server. Make sure Docker is running.'); }
}

async function logout() {
    try { await apiFetch('/logout', { method: 'POST' }); } catch { }
    stopScanner();
    ME = null; TOKEN = null;
    if (countdownTimer) clearInterval(countdownTimer);
    document.getElementById('loginPage').classList.add('active');
    document.getElementById('appContainer').classList.add('hidden');
    document.getElementById('navbar').classList.add('hidden');
    document.getElementById('loginId').value = '';
    document.getElementById('loginPass').value = '';
    setLoginError('');
}

function setLoginError(msg) { document.getElementById('loginError').textContent = msg; }

function initApp() {
    document.getElementById('loginPage').classList.remove('active');
    document.getElementById('navbar').classList.remove('hidden');
    document.getElementById('appContainer').classList.remove('hidden');
    document.getElementById('navName').textContent = ME.name;
    const badge = document.getElementById('navRole');
    badge.textContent = ME.role;
    badge.className = `nav-role-badge role-${ME.role}`;
    document.querySelectorAll('.panel').forEach(p => p.classList.add('hidden'));

    if (ME.role === 'admin') initAdmin();
    else if (ME.role === 'instructor') initInstructor();
    else initStudent();
}

function initAdmin() {
    document.getElementById('adminPanel').classList.remove('hidden');
    loadAdminStats();
    loadUsers('all');
}

async function loadAdminStats() {
    try {
        const res = await apiFetch('/admin/stats');
        const d = await res.json();
        document.getElementById('adminStats').innerHTML = `
            <div class="stat-card"><div class="stat-num">${d.students}</div><div class="stat-label">Students</div></div>
            <div class="stat-card"><div class="stat-num">${d.instructors}</div><div class="stat-label">Instructors</div></div>
            <div class="stat-card"><div class="stat-num">${d.sessions}</div><div class="stat-label">Sessions</div></div>
            <div class="stat-card"><div class="stat-num">${d.records}</div><div class="stat-label">Attendances</div></div>
        `;
    } catch { }
}

async function loadUsers(role) {
    const el = document.getElementById('usersTable');
    el.innerHTML = '<p class="empty">Loading users...</p>';
    try {
        const url = role === 'all' ? '/admin/users' : `/admin/users?role=${role}`;
        const res = await apiFetch(url);
        const data = await res.json();
        if (!data.users.length) { el.innerHTML = '<p class="empty">No users found</p>'; return; }

        el.innerHTML = `<div class="tbl-wrap"><table>
            <thead><tr><th>User ID</th><th>Name</th><th>Role</th><th>Actions</th></tr></thead>
            <tbody>${data.users.map(u => `
                <tr>
                    <td><code>${u.user_id}</code></td>
                    <td><strong>${u.name}</strong></td>
                    <td><span class="badge ${u.role}">${u.role}</span></td>
                    <td><div class="actions">
                        <button class="btn-warning" onclick="showResetPw('${u.user_id}')">Reset</button>
                        ${u.user_id !== 'admin' ? `<button class="btn-danger" onclick="deleteUser('${u.user_id}','${u.name}')">Delete</button>` : ''}
                    </div></td>
                </tr>`).join('')}
            </tbody></table></div>`;
    } catch { el.innerHTML = '<p class="empty">Error loading users</p>'; }
}

async function addUser() {
    const user_id = document.getElementById('newUserId').value.trim();
    const name = document.getElementById('newUserName').value.trim();
    const email = document.getElementById('newUserEmail').value.trim();
    const role = document.getElementById('newUserRole').value;
    const password = document.getElementById('newUserPw').value.trim();

    if (!user_id || !name || !password) {
        showMsg('addUserMsg', 'User ID, Name, and Password are required', false);
        return;
    }

    try {
        const res = await apiFetch('/admin/users', {
            method: 'POST',
            body: JSON.stringify({ user_id, name, email, role, password })
        });
        const data = await res.json();
        showMsg('addUserMsg', data.message, data.success);

        if (data.success) {
            document.getElementById('newUserId').value = '';
            document.getElementById('newUserName').value = '';
            document.getElementById('newUserEmail').value = '';
            document.getElementById('newUserPw').value = '';
            loadUsers('all');
            loadAdminStats();
        }
    } catch (err) {
        showMsg('addUserMsg', 'Server error while adding user', false);
    }
}

async function deleteUser(user_id, name) {
    if (!confirm(`Are you sure you want to delete user: ${name}?`)) return;
    try {
        const res = await apiFetch(`/admin/users/${user_id}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            loadUsers('all');
            loadAdminStats();
        } else {
            alert(data.message);
        }
    } catch {
        alert('Server error');
    }
}

function filterUsers(role, btn) {
    document.querySelectorAll('.ftab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    loadUsers(role);
}

function initInstructor() {
    document.getElementById('instructorPanel').classList.remove('hidden');
    loadInstructorStats();
    loadSessions();
}

async function loadInstructorStats() {
    try {
        const res = await apiFetch('/sessions');
        const data = await res.json();
        document.getElementById('instructorStats').innerHTML = `
            <div class="stat-card"><div class="stat-num">${data.sessions.length}</div><div class="stat-label">My Sessions</div></div>
        `;
    } catch { }
}

async function generateQR() {
    const course_name = document.getElementById('courseName').value;
    const duration = document.getElementById('qrDuration').value;
    try {
        const res = await apiFetch('/generate-qr', {
            method: 'POST',
            body: JSON.stringify({ course_name, duration: parseInt(duration) })
        });
        const data = await res.json();
        if (data.success) {
            document.getElementById('qrDisplay').classList.remove('hidden');
            document.getElementById('qrImage').src = data.qr_image;
            document.getElementById('qrTokenText').textContent = data.qr_data;
            startCountdown(data.duration * 60);
            loadSessions();
        }
    } catch { alert('Failed to generate QR'); }
}

function startCountdown(seconds) {
    if (countdownTimer) clearInterval(countdownTimer);
    let r = seconds;
    const el = document.getElementById('countdown');
    countdownTimer = setInterval(() => {
        r--;
        const m = String(Math.floor(r / 60)).padStart(2, '0');
        const s = String(r % 60).padStart(2, '0');
        el.textContent = `⏱ ${m}:${s}`;
        if (r <= 0) clearInterval(countdownTimer);
    }, 1000);
}

async function loadSessions() {
    const el = document.getElementById('sessionsList');
    try {
        const res = await apiFetch('/sessions');
        const data = await res.json();
        el.innerHTML = `<div class="tbl-wrap"><table>
            <thead><tr><th>Session ID</th><th>Course</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>${data.sessions.map(s => `
                <tr>
                    <td><code>${s.session_id}</code></td>
                    <td>${s.course_name}</td>
                    <td>${s.attendance_count} Students</td>
                    <td><button class="btn-secondary" onclick="viewAttendance('${s.session_id}')">View</button></td>
                </tr>`).join('')}
            </tbody></table></div>`;
    } catch { }
}

async function viewAttendance(session_id) {
    document.getElementById('attendanceModal').classList.remove('hidden');
    const body = document.getElementById('attendanceModalBody');
    body.innerHTML = 'Loading...';
    try {
        const res = await apiFetch(`/session/${session_id}/attendance`);
        const data = await res.json();
        body.innerHTML = data.records.map((r, i) => `
            <div class="att-item">
                <div class="att-avatar" style="background:${COLORS[i % COLORS.length]}">${r.name[0]}</div>
                <div class="att-info"><strong>${r.name}</strong><br><small>${r.student_id}</small></div>
                <div class="att-time">${r.marked_at}</div>
            </div>`).join('');
    } catch { body.innerHTML = 'Error loading records'; }
}

function initStudent() {
    document.getElementById('studentPanel').classList.remove('hidden');
    document.getElementById('studentWelcomeName').textContent = ME.name;
    loadMyAttendance();
}

function switchScanTab(tab, btn) {
    document.querySelectorAll('.stab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    if (tab === 'camera') {
        document.getElementById('cameraTab').classList.remove('hidden');
        document.getElementById('manualTab').classList.add('hidden');
    } else {
        stopScanner();
        document.getElementById('cameraTab').classList.add('hidden');
        document.getElementById('manualTab').classList.remove('hidden');
    }
}

async function startScanner() {
    const startBtn = document.getElementById('startCamBtn');
    if (startBtn) startBtn.classList.add('hidden');

    const readerDiv = document.getElementById('reader');
    if (!html5QrCode) { html5QrCode = new Html5Qrcode("reader"); }

    const config = { fps: 20, qrbox: { width: 250, height: 250 }, aspectRatio: 1.0 };

    try {
        await html5QrCode.start(
            { facingMode: "environment" },
            config,
            (decodedText) => {
                stopScanner();
                doCheckin(decodedText);
            }
        );
        document.getElementById('stopCamBtn')?.classList.remove('hidden');
    } catch (err) {
        alert("Camera error! Use HTTPS or localhost.");
        if (startBtn) startBtn.classList.remove('hidden');
    }
}

function stopScanner() {
    if (html5QrCode && html5QrCode.isScanning) {
        html5QrCode.stop().then(() => {
            html5QrCode.clear();
            document.getElementById('stopCamBtn')?.classList.add('hidden');
            document.getElementById('startCamBtn')?.classList.remove('hidden');
        }).catch(err => console.error(err));
    }
}

async function doCheckin(qr_data) {
    try {
        const res = await apiFetch('/checkin', {
            method: 'POST',
            body: JSON.stringify({ qr_data })
        });
        const data = await res.json();
        showCheckinResult(data.message, data.success);
        if (data.success) loadMyAttendance();
    } catch { showCheckinResult('Connection error', false); }
}

function showCheckinResult(msg, ok) {
    const el = document.getElementById('checkinResult');
    if (el) {
        el.textContent = (ok ? '✅ ' : '❌ ') + msg;
        el.className = `result-box ${ok ? 'ok' : 'fail'}`;
        el.classList.remove('hidden');
    }
}

async function loadMyAttendance() {
    const el = document.getElementById('myAttendanceList');
    try {
        const res = await apiFetch('/student/attendance');
        const data = await res.json();
        document.getElementById('studentTotalAtt').textContent = data.total;
        el.innerHTML = data.records.map((r, i) => `
            <div class="att-item">
                <div class="att-avatar" style="background:${COLORS[i % COLORS.length]}">📚</div>
                <div class="att-info"><strong>${r.course_name}</strong><br><small>${r.instructor_name}</small></div>
                <div class="att-time">${r.marked_at}</div>
            </div>`).join('');
    } catch { }
}

function submitManualQR() {
    const qr = document.getElementById('manualQR').value.trim();
    if (qr) doCheckin(qr);
}

function showMsg(id, msg, ok) {
    const el = document.getElementById(id);
    if (el) {
        el.textContent = (ok ? '✅ ' : '❌ ') + msg;
        el.className = `msg-box ${ok ? 'ok' : 'fail'}`;
        el.classList.remove('hidden');
    }
}

function showResetPw(user_id) {
    resetPwTarget = user_id;
    document.getElementById('resetPwUserId').textContent = user_id;
    document.getElementById('resetPwModal').classList.remove('hidden');
}

async function doResetPassword() {
    const new_password = document.getElementById('resetPwValue').value;
    const res = await apiFetch(`/admin/users/${resetPwTarget}/reset-password`, {
        method: 'POST',
        body: JSON.stringify({ new_password })
    });
    const data = await res.json();
    showMsg('resetPwMsg', data.message, data.success);
    if (data.success) setTimeout(() => closeModal('resetPwModal'), 1000);
}

function togglePw(id) {
    const inp = document.getElementById(id);
    inp.type = inp.type === 'password' ? 'text' : 'password';
}

function closeModal(id) { document.getElementById(id).classList.add('hidden'); }

function showChangePassword() { document.getElementById('changePwModal').classList.remove('hidden'); }

async function changePassword() {
    const old_password = document.getElementById('oldPw').value;
    const new_password = document.getElementById('newPw').value;
    const res = await apiFetch('/change-password', { method: 'POST', body: JSON.stringify({ old_password, new_password }) });
    const data = await res.json();
    showMsg('changePwMsg', data.message, data.success);
    if (data.success) setTimeout(() => closeModal('changePwModal'), 1000);
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('loginPass')?.addEventListener('keydown', e => { if (e.key === 'Enter') login(); });
});