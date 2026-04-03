const API_BASE = 'http://localhost:8000';

// ============ AUTHENTICATION ============
// Check if user is logged in
function checkAuth() {
    const user = sessionStorage.getItem('user');
    if (!user && !window.location.pathname.includes('login.html')) {
        window.location.href = '/static/login.html';
        return false;
    }
    return true;
}

// Get current user info
function getCurrentUser() {
    const user = sessionStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

// Add logout button to sidebar with improved styling
function addLogoutButton() {
    const sidebar = document.querySelector('.sidebar .p-4');
    if (sidebar && !document.getElementById('logoutSection')) {
        const logoutSection = document.createElement('div');
        logoutSection.id = 'logoutSection';
        logoutSection.className = 'logout-section';
        logoutSection.innerHTML = `
            <button class="btn-logout" onclick="logout()">
                <i class="fas fa-sign-out-alt"></i> Logout
            </button>
        `;
        sidebar.appendChild(logoutSection);
    }
}

// Logout function
function logout() {
    sessionStorage.removeItem('user');
    window.location.href = '/static/login.html';
}

// Add user info to sidebar with improved styling
function addUserInfo() {
    const user = getCurrentUser();
    if (user) {
        const sidebar = document.querySelector('.sidebar .p-4');
        if (sidebar && !document.getElementById('userInfoSection')) {
            const userInfoDiv = document.createElement('div');
            userInfoDiv.id = 'userInfoSection';
            userInfoDiv.className = 'user-info-section';
            userInfoDiv.innerHTML = `
                <div class="user-avatar">
                    <i class="fas fa-user"></i>
                </div>
                <div class="user-name">${user.name}</div>
                <div class="user-email">${user.email}</div>
                <div class="user-role">
                    <i class="fas fa-shield-alt"></i> ${user.role}
                </div>
            `;
            sidebar.insertBefore(userInfoDiv, sidebar.firstChild);
        }
    }
}

// Helper function to show alerts
function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alertContainer');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show alert-fixed`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    alertContainer.appendChild(alertDiv);
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

// Page navigation
function showPage(page) {
    document.getElementById('tasksPage').style.display = 'none';
    document.getElementById('stagesPage').style.display = 'none';
    document.getElementById('reportsPage').style.display = 'none';
    document.getElementById('remindersPage').style.display = 'none';
    
    document.getElementById(`${page}Page`).style.display = 'block';
    
    // Update active nav link
    document.querySelectorAll('.sidebar .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    if (event && event.target) {
        event.target.closest('.nav-link').classList.add('active');
    }
    
    // Load data based on page
    if (page === 'tasks') loadTasks();
    if (page === 'reports') loadReport();
    if (page === 'reminders') loadReminderLogs();
}

// ============ TASKS CRUD ============
async function loadTasks() {
    try {
        const response = await fetch(`${API_BASE}/tasks`);
        const tasks = await response.json();
        
        const tasksList = document.getElementById('tasksList');
        if (tasks.length === 0) {
            tasksList.innerHTML = '<p class="text-center text-muted">No tasks found</p>';
            return;
        }
        
        tasksList.innerHTML = `
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>ID</th><th>Lesson ID</th><th>User ID</th><th>Start Date</th><th>Due Date</th><th>Status</th><th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${tasks.map(task => `
                        <tr>
                            <td>${task.id}</td>
                            <td><strong>${task.lesson_id}</strong></td>
                            <td>${task.assigned_to}</td>
                            <td>${task.start_date}</td>
                            <td>${task.due_date}</td>
                            <td><span class="status-badge status-${task.status.toLowerCase()}">${task.status}</span></td>
                            <td>
                                <button class="btn btn-sm btn-warning" onclick="editTask(${task.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="deleteTask(${task.id})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        showAlert('Error loading tasks: ' + error.message, 'danger');
    }
}

// Search tasks
const searchInput = document.getElementById('searchTask');
if (searchInput) {
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const rows = document.querySelectorAll('#tasksList table tbody tr');
        rows.forEach(row => {
            const lessonId = row.cells[1].textContent.toLowerCase();
            row.style.display = lessonId.includes(searchTerm) ? '' : 'none';
        });
    });
}

// Add/Update task
const taskForm = document.getElementById('taskForm');
if (taskForm) {
    taskForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const taskId = document.getElementById('taskId').value;
        const taskData = {
            lesson_id: document.getElementById('lessonId').value,
            assigned_to: parseInt(document.getElementById('assignedTo').value),
            start_date: document.getElementById('startDate').value,
            due_date: document.getElementById('dueDate').value,
            status: document.getElementById('status').value
        };
        
        try {
            let response;
            if (taskId) {
                response = await fetch(`${API_BASE}/tasks/${taskId}`, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(taskData)
                });
                if (response.ok) showAlert('Task updated successfully!');
            } else {
                response = await fetch(`${API_BASE}/tasks`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(taskData)
                });
                if (response.ok) showAlert('Task created successfully!');
            }
            
            if (response.ok) {
                clearTaskForm();
                loadTasks();
            } else {
                const error = await response.json();
                showAlert(error.detail || 'Error saving task', 'danger');
            }
        } catch (error) {
            showAlert('Error: ' + error.message, 'danger');
        }
    });
}

function editTask(id) {
    fetch(`${API_BASE}/tasks/${id}`)
        .then(res => res.json())
        .then(task => {
            document.getElementById('taskId').value = task.id;
            document.getElementById('lessonId').value = task.lesson_id;
            document.getElementById('assignedTo').value = task.assigned_to;
            document.getElementById('startDate').value = task.start_date;
            document.getElementById('dueDate').value = task.due_date;
            document.getElementById('status').value = task.status;
            showAlert('Now update the task and click Add Task', 'info');
        });
}

async function deleteTask(id) {
    if (confirm('Are you sure you want to delete this task?')) {
        try {
            const response = await fetch(`${API_BASE}/tasks/${id}`, {method: 'DELETE'});
            if (response.ok) {
                showAlert('Task deleted successfully!');
                loadTasks();
            }
        } catch (error) {
            showAlert('Error deleting task', 'danger');
        }
    }
}

function clearTaskForm() {
    document.getElementById('taskId').value = '';
    document.getElementById('taskForm').reset();
}

// ============ TASK STAGES ============
async function loadTaskStages() {
    const taskId = document.getElementById('stageTaskId').value;
    if (!taskId) {
        showAlert('Please enter a Task ID', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/stages/task/${taskId}`);
        const stages = await response.json();
        
        const stagesList = document.getElementById('stagesList');
        stagesList.innerHTML = `
            <div class="row">
                ${stages.map(stage => `
                    <div class="col-md-6">
                        <div class="stage-item">
                            <div class="stage-name">
                                <i class="fas fa-check-circle"></i> ${stage.stage_name}
                            </div>
                            <div class="stage-status-select">
                                <select id="status_${stage.id}" class="form-select">
                                    <option value="Pending" ${stage.stage_status === 'Pending' ? 'selected' : ''}>Pending</option>
                                    <option value="Completed" ${stage.stage_status === 'Completed' ? 'selected' : ''}>Completed</option>
                                </select>
                            </div>
                            <div class="mt-2">
                                <small class="text-muted">Last updated: ${new Date(stage.last_updated).toLocaleString()}</small>
                            </div>
                            <button class="btn btn-sm btn-primary mt-2" onclick="updateStageStatus(${stage.id})">
                                <i class="fas fa-save"></i> Update Status
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        showAlert('Error loading stages: ' + error.message, 'danger');
    }
}

async function updateStageStatus(stageId) {
    const newStatus = document.getElementById(`status_${stageId}`).value;
    try {
        const response = await fetch(`${API_BASE}/stages/${stageId}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({stage_status: newStatus})
        });
        
        if (response.ok) {
            showAlert('Stage status updated successfully!');
            loadTaskStages();
        }
    } catch (error) {
        showAlert('Error updating stage status', 'danger');
    }
}

// ============ REPORTS ============
async function loadReport() {
    try {
        const response = await fetch(`${API_BASE}/reports/task-stage`);
        const reports = await response.json();
        
        const reportList = document.getElementById('reportList');
        if (reports.length === 0) {
            reportList.innerHTML = '<p class="text-center text-muted">No reports found</p>';
            return;
        }
        
        reportList.innerHTML = `
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Task ID</th><th>Lesson ID</th><th>Task Status</th><th>Due Date</th>
                        <th>Stage ID</th><th>Stage Name</th><th>Stage Status</th><th>Last Updated</th>
                    </tr>
                </thead>
                <tbody>
                    ${reports.map(report => `
                        <tr>
                            <td>${report.task_id}</td>
                            <td><strong>${report.lesson_id}</strong></td>
                            <td><span class="status-badge status-${report.task_status.toLowerCase()}">${report.task_status}</span></td>
                            <td>${report.due_date}</td>
                            <td>${report.stage_id}</td>
                            <td>${report.stage_name}</td>
                            <td><span class="status-badge status-${report.stage_status.toLowerCase()}">${report.stage_status}</span></td>
                            <td>${new Date(report.last_updated).toLocaleString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        showAlert('Error loading report: ' + error.message, 'danger');
    }
}

// ============ REMINDER LOGS ============
async function loadReminderLogs() {
    try {
        const response = await fetch(`${API_BASE}/reminder-logs`);
        if (!response.ok) throw new Error('Endpoint not available');
        const logs = await response.json();
        
        const remindersList = document.getElementById('remindersList');
        if (logs.length === 0) {
            remindersList.innerHTML = '<p class="text-center text-muted">No reminder logs found</p>';
            return;
        }
        
        remindersList.innerHTML = `
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>ID</th><th>Task ID</th><th>Reminder Type</th><th>Sent Date</th>
                    </tr>
                </thead>
                <tbody>
                    ${logs.map(log => `
                        <tr>
                            <td>${log.id}</td>
                            <td>${log.task_id}</td>
                            <td><span class="badge bg-info">${log.reminder_type}</span></td>
                            <td>${new Date(log.sent_date).toLocaleString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        document.getElementById('remindersList').innerHTML = '<p class="text-center text-muted">Reminder logs will appear here when reminders are sent</p>';
    }
}

// ============ INITIALIZATION ============
// Check authentication and initialize page
if (window.location.pathname.includes('index.html') || window.location.pathname === '/static/index.html' || window.location.pathname === '/') {
    if (checkAuth()) {
        document.addEventListener('DOMContentLoaded', function() {
            addUserInfo();
            addLogoutButton();
            loadTasks();
        });
    }
}

// Load initial data if on main page
if (!window.location.pathname.includes('login.html')) {
    if (document.getElementById('tasksList')) {
        loadTasks();
    }
}