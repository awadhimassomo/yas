/**
 * Dashboard API Integration
 * Handles all API calls and data updates for the YAS Sales Hub dashboard
 */

class DashboardAPI {
    constructor() {
        this.baseUrl = '/api';
        this.csrfToken = this.getCSRFToken();
        this.initializeEventListeners();
        this.loadDashboardData();
        
        // Refresh data every 5 minutes
        setInterval(() => this.loadDashboardData(), 5 * 60 * 1000);
    }

    getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }

    async fetchData(url, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            ...options.headers
        };

        // Add CSRF token for non-GET requests
        if (options.method && options.method !== 'GET') {
            headers['X-CSRFToken'] = this.csrfToken;
        }

        try {
            const response = await fetch(`${this.baseUrl}${url}`, {
                credentials: 'same-origin',
                ...options,
                headers
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching data:', error);
            this.showError('Failed to load data. Please try again later.');
            throw error;
        }
    }

    async loadDashboardData() {
        try {
            // Show loading state
            document.body.classList.add('loading');
            
            // Fetch dashboard stats and recent activity in parallel
            const [stats, activities] = await Promise.all([
                this.fetchData('/dashboard/stats/'),
                this.fetchData('/recent-activity/')
            ]);

            this.updateDashboardStats(stats);
            this.updateRecentActivity(activities);
            this.updateTimeAgo();
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        } finally {
            // Remove loading state
            document.body.classList.remove('loading');
        }
    }

    updateDashboardStats(stats) {
        if (!stats) return;

        // Update leads card
        this.updateElementText('.leads-total', stats.leads?.total || 0);
        this.updateElementText('.leads-new', stats.leads?.new_7d || 0);
        this.updateProgressBar('.leads-new-progress', stats.leads?.new_7d || 0);
        this.updateElementText('.leads-contacted', stats.leads?.contacted || 0);
        this.updateProgressBar('.leads-contacted-progress', stats.leads?.contacted || 0);
        this.updateElementText('.leads-qualified', stats.leads?.qualified || 0);
        this.updateProgressBar('.leads-qualified-progress', stats.leads?.qualified || 0);

        // Update conversion rate card
        this.updateElementText('.conversion-rate', stats.leads?.conversion_rate || 0);
        this.updateElementText('.leads-won', stats.leads?.closed_won || 0);
        this.updateProgressBar('.leads-won-progress', stats.leads?.closed_won || 0);
        this.updateElementText('.leads-lost', stats.leads?.closed_lost || 0);
        this.updateProgressBar('.leads-lost-progress', stats.leads?.closed_lost || 0);

        // Update customers card
        this.updateElementText('.customers-total', stats.customers?.total || 0);
        this.updateElementText('.customers-new', stats.customers?.new_7d || 0);
        this.updateElementText('.customers-growth', 
            this.calculateGrowth(stats.customers?.new_7d, stats.customers?.new_30d) || '0%');

        // Update revenue card
        this.updateElementText('.revenue-total', this.formatCurrency(stats.purchases?.revenue_30d || 0));
        this.updateElementText('.revenue-week', this.formatCurrency(stats.purchases?.revenue_7d || 0));
        this.updateElementText('.revenue-growth', 
            this.calculateGrowth(stats.purchases?.revenue_7d, stats.purchases?.revenue_30d) || '0%');
    }

    updateRecentActivity(activities) {
        if (!activities || !activities.length) return;

        const activityContainer = document.querySelector('.recent-activities');
        if (!activityContainer) return;

        // Clear existing activities
        activityContainer.innerHTML = '';

        // Add each activity to the container
        activities.forEach(activity => {
            const activityEl = this.createActivityElement(activity);
            if (activityEl) {
                activityContainer.appendChild(activityEl);
            }
        });
    }

    createActivityElement(activity) {
        const activityEl = document.createElement('div');
        activityEl.className = 'activity-item border-b border-gray-100 py-3';
        
        let icon = '';
        let color = 'blue';
        
        switch(activity.type) {
            case 'interaction':
                icon = this.getInteractionIcon(activity.action_type);
                break;
            case 'purchase':
                icon = '💳';
                color = 'green';
                break;
            case 'support':
                icon = '🛟';
                color = 'red';
                break;
            case 'lead':
                icon = '📝';
                color = 'yellow';
                break;
            default:
                icon = '🔔';
        }

        const timeAgo = this.timeAgo(new Date(activity.timestamp || activity.date || activity.created_at));
        
        activityEl.innerHTML = `
            <div class="flex items-start">
                <div class="flex-shrink-0 h-10 w-10 rounded-full bg-${color}-100 flex items-center justify-center text-${color}-600 text-lg">
                    ${icon}
                </div>
                <div class="ml-3 flex-1">
                    <div class="flex items-center justify-between">
                        <p class="text-sm font-medium text-gray-900">
                            ${this.escapeHtml(activity.customer || 'Unknown')}
                        </p>
                        <div class="text-sm text-gray-500" data-timestamp="${activity.timestamp || activity.date || activity.created_at}">
                            ${timeAgo}
                        </div>
                    </div>
                    <p class="text-sm text-gray-500">
                        ${this.getActivityDescription(activity)}
                    </p>
                </div>
            </div>
        `;

        return activityEl;
    }

    getInteractionIcon(actionType) {
        const icons = {
            'call': '📞',
            'email': '✉️',
            'meeting': '🤝',
            'chat': '💬',
            'purchase': '💳',
            'support': '🛟',
            'lead': '📝',
            'other': '🔔'
        };
        return icons[actionType] || '🔔';
    }

    getActivityDescription(activity) {
        switch(activity.type) {
            case 'interaction':
                return `New ${activity.action_type} interaction` + (activity.notes ? `: ${activity.notes}` : '');
            case 'purchase':
                return `Purchased ${activity.product} for ${this.formatCurrency(activity.amount)}`;
            case 'support':
                return `${activity.request_type} support request: ${activity.subject || 'No subject'}`;
            case 'lead':
                return `New lead added: ${activity.status} (${activity.lead_type})`;
            default:
                return 'New activity';
        }
    }

    updateElementText(selector, text) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            if (el) el.textContent = text;
        });
    }

    updateProgressBar(selector, percentage) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            if (el) el.style.width = `${Math.min(100, percentage)}%`;
        });
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }

    calculateGrowth(weekly, monthly) {
        if (!weekly || !monthly || monthly === 0) return '0%';
        const growth = (weekly / (monthly / 4) - 1) * 100;
        return `${growth > 0 ? '+' : ''}${Math.round(growth)}%`;
    }

    timeAgo(date) {
        if (!(date instanceof Date)) {
            date = new Date(date);
        }
        
        const seconds = Math.floor((new Date() - date) / 1000);
        
        let interval = Math.floor(seconds / 31536000);
        if (interval >= 1) return interval + 'y ago';
        
        interval = Math.floor(seconds / 2592000);
        if (interval >= 1) return interval + 'mo ago';
        
        interval = Math.floor(seconds / 86400);
        if (interval >= 1) return interval + 'd ago';
        
        interval = Math.floor(seconds / 3600);
        if (interval >= 1) return interval + 'h ago';
        
        interval = Math.floor(seconds / 60);
        if (interval >= 1) return interval + 'm ago';
        
        return 'just now';
    }

    updateTimeAgo() {
        document.querySelectorAll('[data-timestamp]').forEach(el => {
            if (el.dataset.timestamp) {
                el.textContent = this.timeAgo(new Date(el.dataset.timestamp));
            }
        });
    }

    escapeHtml(unsafe) {
        return unsafe
            .toString()
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    showError(message) {
        // Check if error container exists, if not create it
        let errorContainer = document.getElementById('error-container');
        if (!errorContainer) {
            errorContainer = document.createElement('div');
            errorContainer.id = 'error-container';
            errorContainer.className = 'fixed bottom-4 right-4 z-50';
            document.body.appendChild(errorContainer);
        }

        // Create error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-2 rounded shadow-lg';
        errorDiv.role = 'alert';
        
        const errorContent = document.createElement('div');
        errorContent.className = 'flex items-center';
        
        errorContent.innerHTML = `
            <svg class="h-5 w-5 text-red-500 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <p>${this.escapeHtml(message)}</p>
        `;
        
        errorDiv.appendChild(errorContent);
        errorContainer.prepend(errorDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            errorDiv.classList.add('opacity-0', 'transition-opacity', 'duration-500');
            setTimeout(() => errorDiv.remove(), 500);
        }, 5000);
    }

    initializeEventListeners() {
        // Add any event listeners needed for interactive elements
        document.addEventListener('DOMContentLoaded', () => {
            // Update time ago every minute
            setInterval(() => this.updateTimeAgo(), 60000);
            
            // Manual refresh button if it exists
            const refreshBtn = document.getElementById('refresh-dashboard');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.loadDashboardData();
                });
            }
        });
    }
}

// Initialize the dashboard when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize on the dashboard page
    if (document.querySelector('.dashboard-page')) {
        window.dashboard = new DashboardAPI();
    }
});
