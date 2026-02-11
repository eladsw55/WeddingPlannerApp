/**
 * Wedding Elite - API Client
 * Frontend JavaScript for connecting to FastAPI backend
 */

// ==================== CONFIGURATION ====================
const API_URL = "http://localhost:8000";  // שנה לכתובת הייצור שלך
const WEDDING_ID = 1;  // TODO: לשמור ב-localStorage אחרי יצירת חתונה

// ==================== API HELPERS ====================

async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data && (method === 'POST' || method === 'PATCH')) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showToast('שגיאה בתקשורת עם השרת', '⚠️');
        throw error;
    }
}

// ==================== WEDDING API ====================

async function createWedding(groomName, brideName, weddingDate, totalBudget = 165000) {
    const data = {
        groom_name: groomName,
        bride_name: brideName,
        wedding_date: weddingDate,
        total_budget: totalBudget,
        guest_count: 400
    };
    
    const wedding = await apiCall('/weddings', 'POST', data);
    
    // שמור wedding_id ב-localStorage
    localStorage.setItem('wedding_id', wedding.id);
    localStorage.setItem('wedding_data', JSON.stringify(wedding));
    
    return wedding;
}

async function getWeddingDetails() {
    const weddingId = localStorage.getItem('wedding_id') || WEDDING_ID;
    const wedding = await apiCall(`/weddings/${weddingId}`);
    
    // עדכן UI
    document.getElementById('user-name').textContent = wedding.bride_name;
    document.getElementById('days-left').textContent = wedding.days_remaining;
    
    return wedding;
}

async function getDashboard() {
    const weddingId = localStorage.getItem('wedding_id') || WEDDING_ID;
    const dashboard = await apiCall(`/weddings/${weddingId}/dashboard`);
    
    // עדכן Dashboard UI
    updateDashboardUI(dashboard);
    
    return dashboard;
}

function updateDashboardUI(dashboard) {
    // Days remaining
    document.getElementById('days-left').textContent = dashboard.days_remaining;
    
    // Control meter
    document.getElementById('control-percent').textContent = `${dashboard.control_percentage}%`;
    document.getElementById('control-bar').style.width = `${dashboard.control_percentage}%`;
    
    const emoji = dashboard.control_percentage >= 80 ? '😌' : 
                  dashboard.control_percentage >= 60 ? '😊' : 
                  dashboard.control_percentage >= 40 ? '😐' : '😰';
    document.getElementById('control-emoji').textContent = emoji;
    
    // Tasks
    document.getElementById('tasks-done').textContent = dashboard.tasks_completed;
    document.getElementById('tasks-urgent').textContent = dashboard.tasks_urgent;
    
    // Budget
    document.getElementById('budget-planned').textContent = `₪${dashboard.budget_planned.toLocaleString()}`;
    document.getElementById('budget-actual').textContent = `₪${dashboard.budget_actual.toLocaleString()}`;
    document.getElementById('budget-remaining').textContent = `₪${dashboard.budget_remaining.toLocaleString()} 🎉`;
    
    const budgetPercentage = dashboard.budget_percentage;
    document.getElementById('budget-bar').style.width = `${budgetPercentage}%`;
    
    const savings = dashboard.budget_planned - dashboard.budget_actual;
    if (savings > 0) {
        document.getElementById('budget-status').textContent = `+₪${savings.toLocaleString('he-IL')}`;
        document.getElementById('budget-status').className = 'text-2xl font-bold text-green-600';
    } else {
        document.getElementById('budget-status').textContent = `-₪${Math.abs(savings).toLocaleString('he-IL')}`;
        document.getElementById('budget-status').className = 'text-2xl font-bold text-red-600';
    }
    
    // Update countdown ring
    const totalDays = 365; // Assuming 1 year planning
    const progress = ((totalDays - dashboard.days_remaining) / totalDays) * 440;
    document.getElementById('countdown-progress').style.strokeDashoffset = 440 - progress;
}

// ==================== BUDGET API ====================

async function getBudgetCategories() {
    const weddingId = localStorage.getItem('wedding_id') || WEDDING_ID;
    const categories = await apiCall(`/weddings/${weddingId}/budget`);
    
    // עדכן UI של Budget tab
    updateBudgetUI(categories);
    
    return categories;
}

function updateBudgetUI(categories) {
    // TODO: בנה את רשימת הקטגוריות דינמית
    console.log('Budget categories:', categories);
}

async function addBudgetCategory(name, icon, plannedAmount) {
    const weddingId = localStorage.getItem('wedding_id') || WEDDING_ID;
    const data = {
        name: name,
        icon: icon,
        planned_amount: plannedAmount
    };
    
    const category = await apiCall(`/weddings/${weddingId}/budget`, 'POST', data);
    showToast('קטגוריה נוספה בהצלחה!', '✅');
    
    // רענן את רשימת הקטגוריות
    await getBudgetCategories();
    
    return category;
}

// ==================== VENDOR API ====================

async function getVendors() {
    const weddingId = localStorage.getItem('wedding_id') || WEDDING_ID;
    const vendors = await apiCall(`/weddings/${weddingId}/vendors`);
    
    return vendors;
}

async function addVendor(categoryId, name, amount, depositPaid = 0, paymentDate = null, notes = "") {
    const weddingId = localStorage.getItem('wedding_id') || WEDDING_ID;
    const data = {
        category_id: categoryId,
        name: name,
        amount: amount,
        deposit_paid: depositPaid,
        payment_date: paymentDate,
        notes: notes
    };
    
    const vendor = await apiCall(`/weddings/${weddingId}/vendors`, 'POST', data);
    showToast('הספק נוסף בהצלחה! 🎉', '✅');
    
    // רענן Dashboard
    await getDashboard();
    
    return vendor;
}

// ==================== TASK API ====================

async function getTasks(timelinePeriod = null) {
    const weddingId = localStorage.getItem('wedding_id') || WEDDING_ID;
    let endpoint = `/weddings/${weddingId}/tasks`;
    
    if (timelinePeriod) {
        endpoint += `?timeline_period=${timelinePeriod}`;
    }
    
    const tasks = await apiCall(endpoint);
    
    return tasks;
}

async function addTask(title, description = "", timelinePeriod, dueDate = null, isUrgent = false) {
    const weddingId = localStorage.getItem('wedding_id') || WEDDING_ID;
    const data = {
        title: title,
        description: description,
        timeline_period: timelinePeriod,
        due_date: dueDate,
        is_urgent: isUrgent
    };
    
    const task = await apiCall(`/weddings/${weddingId}/tasks`, 'POST', data);
    showToast('משימה נוספה!', '✅');
    
    return task;
}

async function completeTask(taskId) {
    await apiCall(`/tasks/${taskId}/complete`, 'PATCH');
    showToast('משימה הושלמה! 🎉', '✅');
    
    // רענן Dashboard
    await getDashboard();
}

async function uncompleteTask(taskId) {
    await apiCall(`/tasks/${taskId}/uncomplete`, 'PATCH');
    showToast('משימה סומנה כלא הושלמה', 'ℹ️');
    
    // רענן Dashboard
    await getDashboard();
}

// ==================== INITIALIZATION ====================

async function initializeApp() {
    try {
        // בדוק אם יש wedding_id ב-localStorage
        const weddingId = localStorage.getItem('wedding_id');
        
        if (!weddingId) {
            // אין חתונה - הצג onboarding או טופס יצירת חתונה
            console.log('No wedding found - show onboarding');
            // TODO: הצג מסך onboarding
            return;
        }
        
        // טען נתוני חתונה
        await getWeddingDetails();
        
        // טען Dashboard
        await getDashboard();
        
        // טען קטגוריות תקציב
        await getBudgetCategories();
        
        // טען משימות
        await getTasks();
        
        console.log('App initialized successfully');
        
    } catch (error) {
        console.error('Initialization error:', error);
        showToast('שגיאה בטעינת הנתונים', '⚠️');
    }
}

// ==================== EVENT LISTENERS ====================

// טען את האפליקציה כשהדף נטען
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    
    // הוסף event listeners לכפתורים
    setupEventListeners();
});

function setupEventListeners() {
    // דוגמה: כפתור השלמת משימה
    document.querySelectorAll('.task-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', async function() {
            const taskId = this.dataset.taskId;
            if (this.checked) {
                await completeTask(taskId);
            } else {
                await uncompleteTask(taskId);
            }
        });
    });
    
    // TODO: הוסף עוד event listeners
}

// ==================== EXPORT (אם משתמשים במודולים) ====================
// export { 
//     createWedding, 
//     getWeddingDetails, 
//     getDashboard,
//     addVendor,
//     addTask,
//     completeTask
// };
