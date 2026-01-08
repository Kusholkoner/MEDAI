// ============================================
// Medical Diagnosis System - JavaScript (API Version)
// Connected to backend API server
// ============================================

// API Configuration - Auto-detect environment
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000/api'  // Local development
    : `${window.location.origin}/api`;  // Production (same domain as frontend)

// Authentication token storage
let authToken = localStorage.getItem('auth_token');

// ============================================
// API Helper Functions
// ============================================

async function apiCall(endpoint, options = {}) {
    /**
     * Make authenticated API call
     */
    const url = `${API_BASE_URL}${endpoint}`;

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    // Add auth token if available
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers
        });

        // Handle authentication errors
        if (response.status === 401) {
            localStorage.removeItem('auth_token');
            authToken = null;
            if (!window.location.pathname.includes('index.html')) {
                window.location.href = 'index.html';
            }
            throw new Error('Authentication required');
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API request failed');
        }

        return await response.json();

    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ============================================
// Initialize on page load
// ============================================

document.addEventListener('DOMContentLoaded', function () {
    // Initialize theme from localStorage
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);

    // Check if user is logged in
    if (authToken && !window.location.pathname.includes('index.html')) {
        initializeDashboard();
    } else if (!authToken && !window.location.pathname.includes('index.html') && !window.location.pathname.endsWith('/')) {
        window.location.href = 'index.html';
    }
});

async function initializeDashboard() {
    try {
        // Get current user from API
        const userData = await apiCall('/auth/me');

        // Set user info in UI
        document.getElementById('userName').textContent = userData.name;
        document.getElementById('userEmail').textContent = userData.email;
        document.getElementById('userAvatar').textContent = userData.name.charAt(0).toUpperCase();

        // Set profile form values
        if (document.getElementById('profileName')) {
            document.getElementById('profileName').value = userData.name;
            document.getElementById('profileEmail').value = userData.email;
            document.getElementById('profilePhone').value = userData.phone;
        }

        // Load data
        await loadDashboardStats();
        await loadSymptomsList();
        await loadDoctorsList();
        await populateDoctorDropdown();
        await loadAppointments();
        await loadReminders();
        await loadHealthRecords();
        await loadDiagnosisHistory();
        await loadStatistics();

        setupNavigation();
        setupForms();

        // Set default date for health record
        if (document.getElementById('recordDate')) {
            document.getElementById('recordDate').valueAsDate = new Date();
        }

    } catch (error) {
        console.error('Dashboard initialization failed:', error);
        alert('Failed to load dashboard. Please try logging in again.');
        logout();
    }
}

function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const sectionId = this.getAttribute('data-section');
            navigateToSection(sectionId);
        });
    });
}

function navigateToSection(sectionId) {
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');

    // Show section
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionId).classList.add('active');

    // Update title
    const titles = {
        dashboard: 'Dashboard',
        diagnosis: 'Symptom Diagnosis',
        symptoms: 'Available Symptoms',
        doctors: 'Search Doctors',
        appointments: 'Book Appointment',
        reminders: 'Medicine Reminders',
        health: 'Health Monitoring',
        history: 'Diagnosis History',
        emergency: 'Emergency Services',
        account: 'Account Management',
        statistics: 'System Statistics'
    };
    document.getElementById('currentSectionTitle').textContent = titles[sectionId] || 'Dashboard';
}

function setupForms() {
    // Diagnosis form
    document.getElementById('diagnosisForm')?.addEventListener('submit', handleDiagnosis);

    // Appointment form
    document.getElementById('appointmentForm')?.addEventListener('submit', handleAppointment);

    // Reminder form
    document.getElementById('reminderForm')?.addEventListener('submit', handleReminder);

    // Health record form
    document.getElementById('healthRecordForm')?.addEventListener('submit', handleHealthRecord);

    // Profile form
    document.getElementById('profileForm')?.addEventListener('submit', handleProfileUpdate);

    // Symptom search
    document.getElementById('symptomSearch')?.addEventListener('input', filterSymptoms);
}

// ============================================
// Dashboard Stats
// ============================================

async function loadDashboardStats() {
    try {
        const [diagnoses, appointments, reminders, healthRecords] = await Promise.all([
            apiCall('/diagnosis/history'),
            apiCall('/appointments'),
            apiCall('/reminders'),
            apiCall('/health-records')
        ]);

        document.getElementById('totalDiagnoses').textContent = diagnoses.length;
        document.getElementById('totalAppointments').textContent = appointments.count;
        document.getElementById('totalReminders').textContent = reminders.count;
        document.getElementById('totalHealthRecords').textContent = healthRecords.count;

        // Load recent activity
        const activities = [];
        if (diagnoses.length > 0) {
            const latest = diagnoses[diagnoses.length - 1];
            activities.push(`Diagnosis: ${latest.primary_diagnosis.disease} (${new Date(latest.timestamp).toLocaleDateString()})`);
        }
        if (appointments.count > 0) {
            const latest = appointments.appointments[appointments.appointments.length - 1];
            activities.push(`Appointment with doctor on ${latest.appointment_date}`);
        }

        const activityList = document.getElementById('recentActivity');
        if (activities.length > 0) {
            activityList.innerHTML = activities.map(a => `<li class="list-item">${a}</li>`).join('');
        }

    } catch (error) {
        console.error('Failed to load dashboard stats:', error);
    }
}

// ============================================
// Symptoms
// ============================================

let allSymptoms = [];

async function loadSymptomsList() {
    try {
        const data = await apiCall('/symptoms');
        allSymptoms = data.symptoms;

        const container = document.getElementById('symptomsList');
        container.innerHTML = allSymptoms.map(symptom =>
            `<div class="list-item">${symptom}</div>`
        ).join('');

    } catch (error) {
        console.error('Failed to load symptoms:', error);
    }
}

function filterSymptoms(e) {
    const query = e.target.value.toLowerCase();
    const filtered = allSymptoms.filter(s => s.toLowerCase().includes(query));
    const container = document.getElementById('symptomsList');
    container.innerHTML = filtered.map(symptom =>
        `<div class="list-item">${symptom}</div>`
    ).join('');
}

// ============================================
// Diagnosis
// ============================================

async function handleDiagnosis(e) {
    e.preventDefault();

    const symptomsInput = document.getElementById('symptomsInput').value;

    if (!symptomsInput.trim()) {
        alert('Please enter symptoms');
        return;
    }

    try {
        // Show loading state
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Analyzing...';
        submitBtn.disabled = true;

        // Call API
        const result = await apiCall('/diagnosis', {
            method: 'POST',
            body: JSON.stringify({ symptoms: symptomsInput })
        });

        // Display result
        displayDiagnosisResult(result);

        // Reload stats and history
        await loadDashboardStats();
        await loadDiagnosisHistory();

        submitBtn.textContent = originalText;
        submitBtn.disabled = false;

    } catch (error) {
        alert('Diagnosis failed: ' + error.message);
        const submitBtn = e.target.querySelector('button[type="submit"]');
        submitBtn.textContent = 'Analyze Symptoms';
        submitBtn.disabled = false;
    }
}

function displayDiagnosisResult(result) {
    const resultDiv = document.getElementById('diagnosisResult');
    const contentDiv = document.getElementById('diagnosisResultContent');

    const isEmergency = result.is_emergency;

    contentDiv.innerHTML = `
        ${isEmergency ? '<div class="alert alert-danger"><strong>🚨 EMERGENCY - IMMEDIATE MEDICAL ATTENTION REQUIRED!</strong></div>' : ''}
        
        <h3>Primary Diagnosis</h3>
        <div class="list-item">
            <h4>${result.disease}</h4>
            <p><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(1)}%</p>
            <p><strong>Description:</strong> ${result.info.description}</p>
            <p><strong>Severity:</strong> ${result.info.severity}</p>
            <p><strong>Duration:</strong> ${result.info.duration}</p>
            <p><strong>Treatment:</strong> ${result.info.treatment}</p>
        </div>

        <h3 class="mt-3">Symptoms Entered</h3>
        <div class="flex gap-2" style="flex-wrap: wrap;">
            ${result.symptoms.map(s => `<span class="badge badge-info">${s}</span>`).join('')}
        </div>

        ${result.ai_analysis ? `
            <h3 class="mt-3">AI Analysis</h3>
            <div class="list-item">
                <p style="white-space: pre-wrap;">${result.ai_analysis}</p>
            </div>
        ` : ''}

        <div class="alert alert-info mt-3">
            <strong>⚠️ DISCLAIMER:</strong> This is an AI-assisted diagnostic tool. Always consult with a qualified healthcare professional for medical advice.
        </div>

        ${isEmergency ? `
            <div class="mt-3">
                <button class="btn btn-danger" onclick="navigateToSection('emergency')">
                    🚨 Access Emergency Services
                </button>
            </div>
        ` : ''}
    `;

    resultDiv.style.display = 'block';
}

async function loadDiagnosisHistory() {
    try {
        const diagnoses = await apiCall('/diagnosis/history');

        const container = document.getElementById('diagnosisHistoryList');
        if (diagnoses.length === 0) {
            container.innerHTML = '<p class="text-muted">No diagnosis history yet</p>';
            return;
        }

        container.innerHTML = diagnoses.slice(-10).reverse().map(diag => `
            <div class="list-item">
                <div class="flex-between">
                    <div>
                        <h4>${diag.primary_diagnosis.disease}</h4>
                        <p><strong>Date:</strong> ${new Date(diag.timestamp).toLocaleString()}</p>
                        <p><strong>Confidence:</strong> ${(diag.primary_diagnosis.confidence * 100).toFixed(1)}%</p>
                        <p><strong>Symptoms:</strong> ${diag.input_symptoms.join(', ')}</p>
                    </div>
                    <div>
                        ${diag.primary_diagnosis.is_emergency ? '<span class="badge badge-danger">Emergency</span>' : '<span class="badge badge-success">Non-Emergency</span>'}
                    </div>
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error('Failed to load diagnosis history:', error);
    }
}

// ============================================
// Doctors
// ============================================

async function loadDoctorsList() {
    await searchDoctors();
}

async function searchDoctors() {
    try {
        const specialization = document.getElementById('specializationFilter')?.value || '';
        const emergencyOnly = document.getElementById('emergencyFilter')?.checked || false;

        let endpoint = '/doctors?';
        if (specialization) endpoint += `specialization=${encodeURIComponent(specialization)}&`;
        if (emergencyOnly) endpoint += `emergency=true`;

        const data = await apiCall(endpoint);
        const doctors = data.doctors;

        const container = document.getElementById('doctorResults');
        if (doctors.length === 0) {
            container.innerHTML = '<div class="card"><div class="card-body"><p class="text-muted">No doctors found matching your criteria</p></div></div>';
            return;
        }

        container.innerHTML = doctors.map(doctor => `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">👨‍⚕️ ${doctor.name}</h3>
                    <span class="badge badge-info">${doctor.specialization}</span>
                </div>
                <div class="card-body">
                    <p><strong>Qualifications:</strong> ${doctor.qualifications}</p>
                    <p><strong>Experience:</strong> ${doctor.experience}</p>
                    <p><strong>Hospital:</strong> ${doctor.hospital}</p>
                    <p><strong>Phone:</strong> ${doctor.phone}</p>
                    <p><strong>Available:</strong> ${doctor.available_days.join(', ')}</p>
                    <p><strong>Timings:</strong> ${doctor.available_times.join(', ')}</p>
                    <p><strong>Fee:</strong> ₹${doctor.consultation_fee}</p>
                    <p><strong>Rating:</strong> ${'⭐'.repeat(Math.floor(doctor.rating))} (${doctor.rating}/5)</p>
                    ${doctor.emergency_available ? '<span class="badge badge-danger">Emergency Available</span>' : ''}
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error('Failed to load doctors:', error);
    }
}

async function populateDoctorDropdown() {
    try {
        const data = await apiCall('/doctors');
        const doctors = data.doctors;

        const select = document.getElementById('aptDoctor');
        if (select) {
            select.innerHTML = '<option value="">Choose a doctor...</option>' +
                doctors.map(d => `<option value="${d.id}">${d.name} - ${d.specialization}</option>`).join('');
        }

    } catch (error) {
        console.error('Failed to populate doctor dropdown:', error);
    }
}

// ============================================
// Appointments
// ============================================

async function handleAppointment(e) {
    e.preventDefault();

    try {
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Booking...';
        submitBtn.disabled = true;

        const appointmentData = {
            age: document.getElementById('aptAge').value,
            symptoms: document.getElementById('aptSymptoms').value,
            doctor_id: document.getElementById('aptDoctor').value,
            appointment_date: document.getElementById('aptDate').value,
            appointment_time: document.getElementById('aptTime').value,
            is_emergency: false
        };

        await apiCall('/appointments', {
            method: 'POST',
            body: JSON.stringify(appointmentData)
        });

        alert('✅ Appointment booked successfully!');
        e.target.reset();
        await loadAppointments();
        await loadDashboardStats();

        submitBtn.textContent = originalText;
        submitBtn.disabled = false;

    } catch (error) {
        alert('Failed to book appointment: ' + error.message);
        const submitBtn = e.target.querySelector('button[type="submit"]');
        submitBtn.textContent = 'Book Appointment';
        submitBtn.disabled = false;
    }
}

async function loadAppointments() {
    try {
        const data = await apiCall('/appointments');
        const appointments = data.appointments;

        const container = document.getElementById('appointmentsList');
        if (appointments.length === 0) {
            container.innerHTML = '<p class="text-muted">No appointments booked yet</p>';
            return;
        }

        container.innerHTML = appointments.map(apt => `
            <div class="list-item">
                <div class="flex-between">
                    <div>
                        <h4>Doctor ID: ${apt.doctor_id}</h4>
                        <p><strong>Date:</strong> ${apt.appointment_date} at ${apt.appointment_time}</p>
                        <p><strong>Symptoms:</strong> ${apt.symptoms}</p>
                        <p><strong>Status:</strong> <span class="badge badge-success">${apt.status}</span></p>
                    </div>
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error('Failed to load appointments:', error);
    }
}

// ============================================
// Medicine Reminders
// ============================================

async function handleReminder(e) {
    e.preventDefault();

    try {
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Adding...';
        submitBtn.disabled = true;

        const reminderData = {
            medicine_name: document.getElementById('medicineName').value,
            dosage: document.getElementById('dosage').value,
            time: document.getElementById('reminderTime').value,
            start_date: document.getElementById('startDate').value,
            end_date: document.getElementById('endDate').value || null,
            notes: document.getElementById('reminderNotes').value
        };

        await apiCall('/reminders', {
            method: 'POST',
            body: JSON.stringify(reminderData)
        });

        alert('✅ Reminder added successfully!');
        e.target.reset();
        await loadReminders();
        await loadDashboardStats();

        submitBtn.textContent = originalText;
        submitBtn.disabled = false;

    } catch (error) {
        alert('Failed to add reminder: ' + error.message);
        const submitBtn = e.target.querySelector('button[type="submit"]');
        submitBtn.textContent = 'Add Reminder';
        submitBtn.disabled = false;
    }
}

async function loadReminders() {
    try {
        const data = await apiCall('/reminders');
        const reminders = data.reminders;

        const container = document.getElementById('remindersList');
        if (reminders.length === 0) {
            container.innerHTML = '<p class="text-muted">No reminders set yet</p>';
            return;
        }

        container.innerHTML = reminders.map(rem => `
            <div class="list-item">
                <h4>💊 ${rem.medicine_name}</h4>
                <p><strong>Dosage:</strong> ${rem.dosage}</p>
                <p><strong>Time:</strong> ${rem.time}</p>
                <p><strong>Duration:</strong> ${rem.start_date} ${rem.end_date ? 'to ' + rem.end_date : '(ongoing)'}</p>
                ${rem.notes ? `<p><strong>Notes:</strong> ${rem.notes}</p>` : ''}
            </div>
        `).join('');

    } catch (error) {
        console.error('Failed to load reminders:', error);
    }
}

// ============================================
// Health Monitoring
// ============================================

async function handleHealthRecord(e) {
    e.preventDefault();

    try {
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Adding...';
        submitBtn.disabled = true;

        const recordData = {
            date: document.getElementById('recordDate').value,
            blood_pressure: document.getElementById('bloodPressure').value || null,
            heart_rate: parseInt(document.getElementById('heartRate').value) || null,
            sugar_level: parseFloat(document.getElementById('sugarLevel').value) || null,
            weight: parseFloat(document.getElementById('weight').value) || null,
            temperature: parseFloat(document.getElementById('temperature').value) || null
        };

        await apiCall('/health-records', {
            method: 'POST',
            body: JSON.stringify(recordData)
        });

        alert('✅ Health record added successfully!');
        e.target.reset();
        document.getElementById('recordDate').valueAsDate = new Date();
        await loadHealthRecords();
        await loadDashboardStats();

        submitBtn.textContent = originalText;
        submitBtn.disabled = false;

    } catch (error) {
        alert('Failed to add health record: ' + error.message);
        const submitBtn = e.target.querySelector('button[type="submit"]');
        submitBtn.textContent = 'Add Record';
        submitBtn.disabled = false;
    }
}

async function loadHealthRecords() {
    try {
        const data = await apiCall('/health-records');
        const records = data.records;

        const container = document.getElementById('healthRecordsList');
        if (records.length === 0) {
            container.innerHTML = '<p class="text-muted">No health records yet</p>';
            return;
        }

        container.innerHTML = records.slice(-10).reverse().map(rec => `
            <div class="list-item">
                <p><strong>Date:</strong> ${rec.date}</p>
                <div class="grid grid-3">
                    ${rec.blood_pressure ? `<p>BP: ${rec.blood_pressure}</p>` : ''}
                    ${rec.heart_rate ? `<p>HR: ${rec.heart_rate} bpm</p>` : ''}
                    ${rec.sugar_level ? `<p>Sugar: ${rec.sugar_level} mg/dL</p>` : ''}
                    ${rec.weight ? `<p>Weight: ${rec.weight} kg</p>` : ''}
                    ${rec.temperature ? `<p>Temp: ${rec.temperature}°C</p>` : ''}
                </div>
            </div>
        `).join('');

        updateHeartRateChart(records);

    } catch (error) {
        console.error('Failed to load health records:', error);
    }
}

function updateHeartRateChart(records) {
    const heartRateData = records.filter(r => r.heart_rate).slice(-10);

    if (heartRateData.length === 0) return;

    const ctx = document.getElementById('heartRateChart');
    if (!ctx) return;

    // Destroy existing chart if any
    if (window.heartRateChartInstance) {
        window.heartRateChartInstance.destroy();
    }

    window.heartRateChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: heartRateData.map(r => r.date),
            datasets: [{
                label: 'Heart Rate (bpm)',
                data: heartRateData.map(r => r.heart_rate),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: '#b8b8d1' }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: { color: '#b8b8d1' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                x: {
                    ticks: { color: '#b8b8d1' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                }
            }
        }
    });
}

// ============================================
// Profile Management
// ============================================

async function handleProfileUpdate(e) {
    e.preventDefault();

    try {
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Updating...';
        submitBtn.disabled = true;

        const name = document.getElementById('profileName').value;
        const phone = document.getElementById('profilePhone').value;

        const userData = await apiCall(`/auth/profile?name=${encodeURIComponent(name)}&phone=${encodeURIComponent(phone)}`, {
            method: 'PUT'
        });

        document.getElementById('userName').textContent = userData.name;
        document.getElementById('userAvatar').textContent = userData.name.charAt(0).toUpperCase();

        alert('✅ Profile updated successfully!');

        submitBtn.textContent = originalText;
        submitBtn.disabled = false;

    } catch (error) {
        alert('Failed to update profile: ' + error.message);
        const submitBtn = e.target.querySelector('button[type="submit"]');
        submitBtn.textContent = 'Update Profile';
        submitBtn.disabled = false;
    }
}

// ============================================
// Statistics
// ============================================

async function loadStatistics() {
    try {
        const stats = await apiCall('/statistics');

        document.getElementById('statDiseases').textContent = stats.database.total_diseases;
        document.getElementById('statSymptoms').textContent = stats.database.total_symptoms;
        document.getElementById('statDoctors').textContent = stats.doctors.total_doctors;
        document.getElementById('statEmergency').textContent = stats.database.emergency_conditions;

        document.getElementById('statTotalUsers').textContent = stats.user.total_users;
        document.getElementById('statLoginCount').textContent = stats.user.login_count;
        document.getElementById('statLastLogin').textContent = stats.user.registered_on ? new Date(stats.user.registered_on).toLocaleString() : '-';
        document.getElementById('statRegistered').textContent = stats.user.registered_on ? new Date(stats.user.registered_on).toLocaleDateString() : '-';

    } catch (error) {
        console.error('Failed to load statistics:', error);
    }
}

// ============================================
// Emergency Services
// ============================================

function findNearbyHospitals() {
    const location = document.getElementById('locationInput')?.value || 'Nanded, Maharashtra, India';
    const emergencyType = document.getElementById('emergencyType')?.value || '';

    let searchQuery = `hospitals near ${location}`;

    if (emergencyType === 'cardiac') {
        searchQuery = `cardiac hospitals near ${location}`;
    } else if (emergencyType === 'trauma') {
        searchQuery = `trauma centers near ${location}`;
    } else if (emergencyType === 'emergency') {
        searchQuery = `emergency hospitals near ${location}`;
    }

    const mapsUrl = `https://www.google.com/maps/search/${encodeURIComponent(searchQuery)}`;
    window.open(mapsUrl, '_blank');
}

function bookEmergencyAppointment() {
    navigateToSection('appointments');
    alert('🚨 For emergency appointments, please select an emergency-available doctor and mention "EMERGENCY" in symptoms.');
}

function emergencySymptomCheck() {
    navigateToSection('diagnosis');
    alert('🚨 Please enter your emergency symptoms. If critical, call 112 or 108 immediately!');
}

// ============================================
// Account Management
// ============================================

function switchAccount() {
    const choice = confirm('Do you want to switch to a different account? This will log you out.');
    if (choice) {
        logout();
    }
}

function logout() {
    const confirmLogout = window.confirm('Are you sure you want to logout?');
    if (confirmLogout) {
        // Clear authentication token
        localStorage.removeItem('auth_token');
        authToken = null;

        // Clear any other user-specific data
        // (You can add more items to clear if needed)

        // Show logout message
        console.log('User logged out successfully');

        // Redirect to login page
        window.location.href = 'index.html';
    }
}

// ============================================
// Responsive Sidebar Toggle Menu
// ============================================

(function () {
    const sidebar = document.getElementById('sidebar');
    const menuToggle = document.getElementById('menuToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    if (!sidebar || !menuToggle) return;

    // Toggle sidebar menu
    function toggleSidebar() {
        sidebar.classList.toggle('active');
        menuToggle.classList.toggle('active');
        sidebarOverlay.classList.toggle('active');

        // Prevent body scroll when sidebar is open
        if (sidebar.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    }

    // Close sidebar
    function closeSidebar() {
        sidebar.classList.remove('active');
        menuToggle.classList.remove('active');
        sidebarOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Event listeners
    menuToggle.addEventListener('click', toggleSidebar);

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }

    // Close sidebar when clicking nav links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', closeSidebar);
    });
})();
