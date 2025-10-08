from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Agent, Customer, Lead, Feedback, Interaction, Product, Purchase, SupportRequest


class AgentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_full_name', 'phone', 'customer_count', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'phone')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    
    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_full_name.short_description = 'Name'
    
    def customer_count(self, obj):
        return obj.customers.count()
    customer_count.short_description = 'Assigned Customers'


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'visit_reason_display', 'assigned_agent_link', 'lead_status', 'created_at')
    list_filter = ('visit_reason', 'is_active', 'created_at')
    search_fields = ('name', 'phone', 'email', 'address')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('assigned_agent', 'assigned_agent__user')
    
    def visit_reason_display(self, obj):
        return dict(Customer.VISIT_REASON_CHOICES).get(obj.visit_reason, obj.visit_reason)
    visit_reason_display.short_description = 'Visit Reason'
    
    def assigned_agent_link(self, obj):
        if obj.assigned_agent:
            url = reverse('admin:sales_hub_agent_change', args=[obj.assigned_agent.id])
            return mark_safe(f'<a href="{url}">{obj.assigned_agent}</a>')
        return "-"
    assigned_agent_link.short_description = 'Assigned Agent'
    assigned_agent_link.allow_tags = True
    
    def lead_status(self, obj):
        if hasattr(obj, 'lead'):
            url = reverse('admin:sales_hub_lead_change', args=[obj.lead.id])
            return mark_safe(f'<a href="{url}">{obj.lead.get_status_display()}</a>')
        return "No Lead"
    lead_status.short_description = 'Lead Status'
    lead_status.allow_tags = True


class LeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_link', 'status_display', 'lead_type_display', 'assigned_to_link', 'created_at')
    list_filter = ('status', 'lead_type', 'is_active', 'created_at')
    search_fields = ('customer__name', 'customer__phone', 'notes')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('customer', 'assigned_to', 'assigned_to__user')
    
    def status_display(self, obj):
        status_icons = {
            'new': '🆕',
            'contacted': '📞',
            'qualified': '✅',
            'proposal_sent': '📄',
            'negotiation': '🤝',
            'closed_won': '🏆',
            'closed_lost': '❌',
        }
        return f"{status_icons.get(obj.status, '')} {obj.get_status_display()}"
    status_display.short_description = 'Status'
    
    def lead_type_display(self, obj):
        type_icons = {
            'quick': '⚡',
            'long': '⏳',
            'none': '🚫',
        }
        return f"{type_icons.get(obj.lead_type, '')} {obj.get_lead_type_display()}"
    lead_type_display.short_description = 'Lead Type'
    
    def customer_link(self, obj):
        url = reverse('admin:sales_hub_customer_change', args=[obj.customer.id])
        return mark_safe(f'<a href="{url}">{obj.customer.name}</a>')
    customer_link.short_description = 'Customer'
    customer_link.allow_tags = True
    
    def assigned_to_link(self, obj):
        if obj.assigned_to:
            url = reverse('admin:sales_hub_agent_change', args=[obj.assigned_to.id])
            return mark_safe(f'<a href="{url}">{obj.assigned_to}</a>')
        return "-"
    assigned_to_link.short_description = 'Assigned To'
    assigned_to_link.allow_tags = True


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_link', 'rating_stars', 'agent_link', 'is_resolved', 'created_at')
    list_filter = ('rating', 'is_resolved', 'created_at')
    search_fields = ('customer__name', 'comment', 'resolution_notes')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('customer', 'agent', 'agent__user')
    
    def rating_stars(self, obj):
        return '★' * obj.rating + '☆' * (5 - obj.rating)
    rating_stars.short_description = 'Rating'
    
    def customer_link(self, obj):
        url = reverse('admin:sales_hub_customer_change', args=[obj.customer.id])
        return mark_safe(f'<a href="{url}">{obj.customer.name}</a>')
    customer_link.short_description = 'Customer'
    customer_link.allow_tags = True
    
    def agent_link(self, obj):
        if obj.agent:
            url = reverse('admin:sales_hub_agent_change', args=[obj.agent.id])
            return mark_safe(f'<a href="{url}">{obj.agent}</a>')
        return "-"
    agent_link.short_description = 'Agent'
    agent_link.allow_tags = True


class InteractionAdmin(admin.ModelAdmin):
    list_display = ('id', 'action_type_icon', 'customer_link', 'agent_link', 'short_notes', 'is_completed', 'created_at')
    list_filter = ('action_type', 'is_completed', 'created_at')
    search_fields = ('customer__name', 'notes', 'agent__user__first_name', 'agent__user__last_name')
    date_hierarchy = 'timestamp'
    readonly_fields = ('created_at', 'updated_at', 'timestamp')
    list_select_related = ('customer', 'agent', 'agent__user')
    
    def action_type_icon(self, obj):
        icons = {
            'call': '📞',
            'email': '📧',
            'meeting': '🤝',
            'chat': '💬',
            'purchase': '🛒',
            'support': '🛠️',
            'lead': '🎯',
            'other': '🔹',
        }
        return f"{icons.get(obj.action_type, '🔹')} {obj.get_action_type_display()}"
    action_type_icon.short_description = 'Type'
    
    def customer_link(self, obj):
        url = reverse('admin:sales_hub_customer_change', args=[obj.customer.id])
        return mark_safe(f'<a href="{url}">{obj.customer.name}</a>')
    customer_link.short_description = 'Customer'
    
    def agent_link(self, obj):
        if obj.agent:
            url = reverse('admin:sales_hub_agent_change', args=[obj.agent.id])
            return mark_safe(f'<a href="{url}">{obj.agent}</a>')
        return "-"
    agent_link.short_description = 'Agent'
    agent_link.allow_tags = True
    
    def short_notes(self, obj):
        return f"{obj.notes[:50]}..." if obj.notes else ""
    short_notes.short_description = 'Notes'


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_display', 'price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_active')
    
    def category_display(self, obj):
        return obj.get_category_display()
    category_display.short_description = 'Category'


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_link', 'product_link', 'quantity', 'total_amount', 'purchase_date')
    list_filter = ('purchase_date', 'product__category')
    search_fields = ('customer__name', 'product__name')
    date_hierarchy = 'purchase_date'
    list_select_related = ('customer', 'product', 'agent')
    
    def customer_link(self, obj):
        url = reverse('admin:sales_hub_customer_change', args=[obj.customer.id])
        return mark_safe(f'<a href="{url}">{obj.customer.name}</a>')
    customer_link.short_description = 'Customer'
    
    def product_link(self, obj):
        url = reverse('admin:sales_hub_product_change', args=[obj.product.id])
        return mark_safe(f'<a href="{url}">{obj.product.name}</a>')
    product_link.short_description = 'Product'


class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_link', 'request_type_display', 'status_display', 'priority_display', 'assigned_to_link', 'created_at')
    list_filter = ('status', 'priority', 'request_type', 'created_at')
    search_fields = ('customer__name', 'subject', 'description')
    date_hierarchy = 'created_at'
    list_select_related = ('customer', 'assigned_to', 'assigned_to__user')
    
    def request_type_display(self, obj):
        return obj.get_request_type_display()
    request_type_display.short_description = 'Type'
    
    def status_display(self, obj):
        status_icons = {
            'open': '🔓',
            'in_progress': '🔄',
            'waiting': '⏳',
            'resolved': '✅',
            'closed': '🔒',
        }
        return f"{status_icons.get(obj.status, '')} {obj.get_status_display()}"
    status_display.short_description = 'Status'
    
    def priority_display(self, obj):
        priority_icons = {
            1: '⬇️ Low',
            2: '⏬ Medium',
            3: '⬆️ High',
            4: '🚨 Critical',
        }
        return priority_icons.get(obj.priority, obj.priority)
    priority_display.short_description = 'Priority'
    
    def customer_link(self, obj):
        url = reverse('admin:sales_hub_customer_change', args=[obj.customer.id])
        return mark_safe(f'<a href="{url}">{obj.customer.name}</a>')
    customer_link.short_description = 'Customer'
    
    def assigned_to_link(self, obj):
        if obj.assigned_to:
            url = reverse('admin:sales_hub_agent_change', args=[obj.assigned_to.id])
            return mark_safe(f'<a href="{url}">{obj.assigned_to}</a>')
        return "-"
    assigned_to_link.short_description = 'Assigned To'
    assigned_to_link.allow_tags = True


# Register models with their admin classes
admin.site.register(Agent, AgentAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Lead, LeadAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Interaction, InteractionAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(SupportRequest, SupportRequestAdmin)

# Customize admin site header
admin.site.site_header = "Arusha Bluerock Sales Hub Admin"
admin.site.site_title = "Sales Hub Admin"
admin.site.index_title = "Welcome to Arusha Bluerock Sales Hub Administration"
