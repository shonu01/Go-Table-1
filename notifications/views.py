from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Notification

# Create your views here.

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)
    paginator = Paginator(notifications, 10)
    page = request.GET.get('page')
    notifications = paginator.get_page(page)
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

@login_required
def notification_detail(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    if notification.booking:
        return redirect('bookings:detail', pk=notification.booking.pk)
    return redirect('notifications:list')

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    messages.success(request, 'Notification marked as read.')
    return redirect('notifications:list')

@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications:list')
