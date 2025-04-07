from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm, CustomUserChangeForm

# Create your views here.

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('restaurants:home')
    template_name = 'accounts/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(self.request, 'Account created successfully!')
        return response

@login_required
def profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    context = {
        'user': user,
        'bookings': user.bookings.all().order_by('-created_at')[:5],
        'notifications': user.notification_set.filter(is_read=False).order_by('-created_at')[:5],
    }
    return render(request, 'accounts/dashboard.html', context)
