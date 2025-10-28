from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import messages
from django.utils.html import format_html
from django.db.models import CharField
from django.db.models.functions import Cast
from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model"""
    
    list_display = ['username', 'email', 'role', 'password_display', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']
    actions = ['delete_users_with_cascade']
    readonly_fields = ['password_display']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'plaintext_password', 'password_display')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone')}),
    )
    
    def save_model(self, request, obj, form, change):
        """Override to capture plaintext password before saving"""
        # Check if a password field was in the form data
        if request.method == 'POST':
            plaintext = request.POST.get('plaintext_password', '').strip()
            if plaintext:
                obj.plaintext_password = plaintext
        
        super().save_model(request, obj, form, change)
    
    def password_display(self, obj):
        """Display plaintext password if available, otherwise show hash (read-only)"""
        if obj.pk:
            if hasattr(obj, 'plaintext_password') and obj.plaintext_password:
                return format_html(
                    '<code style="font-size: 12px; color: #28a745; font-weight: bold;">{}</code>',
                    obj.plaintext_password
                )
            else:
                return format_html(
                    '<code style="font-size: 10px; word-break: break-all; color: #666;">{}</code><br><small style="color: #999;">(No plaintext stored)</small>',
                    obj.password[:50] + '...' if len(obj.password) > 50 else obj.password
                )
        return '-'
    password_display.short_description = 'Password'
    
    def delete_users_with_cascade(self, request, queryset):
        """Delete users and cascade delete related data"""
        deleted_count = 0
        
        for user in queryset:
            # Delete related data based on role
            if user.role == 'CUSTOMER':
                # Cascade delete service requests (handled by CASCADE on_delete)
                pass
            elif user.role == 'TECHNICIAN':
                # Delete technician profile if exists
                # This will set assignments to NULL (SET_NULL on_delete)
                if hasattr(user, 'technician_profile'):
                    user.technician_profile.delete()
            
            # Delete the user
            user.delete()
            deleted_count += 1
        
        self.message_user(
            request,
            f'Successfully deleted {deleted_count} user(s) and their related data.',
            messages.SUCCESS
        )
    
    delete_users_with_cascade.short_description = 'Delete selected users and their related data'


