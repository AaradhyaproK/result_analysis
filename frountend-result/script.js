import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getFirestore, collection, getDocs } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";
import { firebaseConfig } from "./config.js";

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

let allStudents = [];
let chartInstance = null;

async function syncSystem() {
    const snap = await getDocs(collection(db, "result_files"));
    const map = new Map();
    let stats = { sum: 0, count: 0, passed: 0, total: 0 };

    snap.forEach(doc => {
        const file = doc.data();
        (file.students_data || []).forEach(s => {
            if (!map.has(s.PRN)) map.set(s.PRN, { name: s.Name, prn: s.PRN });
            const sgpa = parseFloat(s.SGPA) || 0;
            if (sgpa > 0) { stats.sum += sgpa; stats.count++; }
            if (s['Result Status'] === 'Pass') stats.passed++;
            stats.total++;
        });
    });

    allStudents = Array.from(map.values());
    document.getElementById('globalStats').classList.remove('hidden');
    document.getElementById('totalStudents').innerText = allStudents.length;
    document.getElementById('avgSgpa').innerText = (stats.sum / stats.count || 0).toFixed(2);
    document.getElementById('passRate').innerText = `${Math.round((stats.passed/stats.total)*100 || 0)}%`;
    document.getElementById('loader').classList.add('hidden');
}

const searchInput = document.getElementById('studentSearch');
const resultsBox = document.getElementById('resultsDropdown');

searchInput.addEventListener('input', (e) => {
    const val = e.target.value.toLowerCase().trim();
    resultsBox.innerHTML = '';
    if (val.length < 2) return resultsBox.classList.add('hidden');
    const matches = allStudents.filter(s => s.name.toLowerCase().includes(val) || s.prn.includes(val)).slice(0, 5);
    if (matches.length > 0) {
        resultsBox.classList.remove('hidden');
        matches.forEach(s => {
            const div = document.createElement('div');
            div.className = 'result-item';
            div.innerHTML = `<strong>${s.name}</strong><br><small class="dim">${s.prn}</small>`;
            div.onclick = () => loadStudent(s.prn, s.name);
            resultsBox.appendChild(div);
        });
    }
});

async function loadStudent(prn, name) {
    resultsBox.classList.add('hidden');
    searchInput.value = name;
    document.getElementById('loader').classList.remove('hidden');
    const snap = await getDocs(collection(db, "result_files"));
    let history = [];
    snap.forEach(doc => {
        const file = doc.data();
        const std = (file.students_data || []).find(s => s.PRN === prn);
        if (std) history.push({ exam: file.exam_tag, sgpa: parseFloat(std.SGPA) || 0, subjects: std.Subjects || [], date: file.uploaded_at?.toDate() || new Date() });
    });
    history.sort((a, b) => a.date - b.date);
    renderDashboard(name, prn, history);
    document.getElementById('loader').classList.add('hidden');
}

function renderDashboard(name, prn, history) {
    document.getElementById('dashboard').classList.remove('hidden');
    document.getElementById('displayName').innerText = name;
    document.getElementById('displayPRN').innerText = `PRN: ${prn}`;
    document.getElementById('avatarIcon').innerText = name.split(' ').map(n => n[0]).join('').slice(0, 2);
    document.getElementById('predictionVal').innerText = predict(history.map(h => h.sgpa));

    const list = document.getElementById('transcriptList');
    list.innerHTML = history.slice().reverse().map((sem, i) => `
        <div class="sem-block">
            <div class="sem-head" onclick="toggleAccordion(${i})">
                <div><i class="fas fa-chevron-right toggle-icon" id="icon-${i}"></i> <strong>${sem.exam}</strong></div>
                <span class="dim">SGPA: ${sem.sgpa.toFixed(2)}</span>
            </div>
            <div class="sem-body-wrapper" id="body-${i}">
                <table class="subject-table">
                    <tbody>${sem.subjects.map(sub => `<tr><td data-label="Subject">${sub['Course Name']}</td><td data-label="Code">${sub['Course Code']}</td><td data-label="Grade"><span class="grade-badge">${sub.Grade}</span></td></tr>`).join('')}</tbody>
                </table>
            </div>
        </div>
    `).join('');
    updateChart(history);
}

window.toggleAccordion = (i) => {
    const b = document.getElementById(`body-${i}`);
    const ic = document.getElementById(`icon-${i}`);
    const isOpen = b.style.maxHeight && b.style.maxHeight !== "0px";
    b.style.maxHeight = isOpen ? "0px" : "1000px";
    ic.style.transform = isOpen ? "rotate(0deg)" : "rotate(90deg)";
};

function predict(data) {
    if (data.length < 2) return (data[0] || 0).toFixed(2);
    const n = data.length;
    let sx=0, sy=0, sxy=0, sxx=0;
    for(let i=0; i<n; i++) { sx+=i; sy+=data[i]; sxy+=i*data[i]; sxx+=i*i; }
    const m = (n*sxy - sx*sy) / (n*sxx - sx*sx);
    const b = (sy - m*sx) / n;
    return Math.min(10, Math.max(0, m*n + b)).toFixed(2);
}

function updateChart(history) {
    const ctx = document.getElementById('performanceChart').getContext('2d');
    if (chartInstance) chartInstance.destroy();
    
    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: history.map(h => h.exam),
            datasets: [{ 
                label: 'SGPA', 
                data: history.map(h => h.sgpa), 
                borderColor: '#38bdf8', 
                tension: 0.4, 
                fill: true, 
                backgroundColor: 'rgba(56,189,248,0.05)' 
            }]
        },
        options: { 
            responsive: true,
            maintainAspectRatio: false, // Critical: Allows the chart to follow CSS height
            plugins: { legend: { display: false } }, 
            scales: { 
                y: { min: 0, max: 10, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { grid: { display: false } }
            } 
        }
    });
}

syncSystem();