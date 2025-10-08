from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from .forms import CustomUserCreationForm, CustomUserChangeForm

User = get_user_model()

class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Verify that the current user is a superuser."""
    def test_func(self):
        return self.request.user.is_superuser

class UserListView(SuperuserRequiredMixin, ListView):
    """View for listing all users."""
    model = User
    template_name = 'sales_hub/users/list.html'
    context_object_name = 'users'
    paginate_by = 10
    
    def get_queryset(self):
        return User.objects.all().order_by('date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'user_management'
        return context

class UserCreateView(SuperuserRequiredMixin, SuccessMessageMixin, CreateView):
    """View for creating a new user."""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'sales_hub/users/list.html'  # Using the same template with modal
    success_url = reverse_lazy('users:user_list')
    success_message = 'User created successfully!'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all().order_by('date_joined')
        context['active_tab'] = 'user_management'
        context['show_add_user_modal'] = True
        return context
    
    def form_valid(self, form):
            # The form's save method already handles saving the user
        return super().form_valid(form)

class UserUpdateView(SuperuserRequiredMixin, SuccessMessageMixin, UpdateView):
    """View for updating a user."""
    model = User
    form_class = CustomUserChangeForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user_list')
    success_message = 'User updated successfully!'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'user_management'
        return context
