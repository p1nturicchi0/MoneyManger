

from django.urls import path
from transactions import views
from .views import SendMonthlyReportView
urlpatterns = [
    path('create_transaction/', views.TransactionCreateView.as_view(), name='create_transaction'),
    path('transactions_list/', views.TransactionListView.as_view(), name='transactions_list'),
    path('update_transaction/<int:pk>/', views.TransactionUpdateView.as_view(), name='update_transaction'),
    path('delete_transaction/<int:pk>/', views.TransactionDeleteView.as_view(), name='delete_transaction'),
    path('transaction_details/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_details'),
    path('dashboard/', views.DashboardListView.as_view(), name='dashboard'),
    path('limit/',views.LimitCreateView.as_view(), name='limit' ),
    path('profile/', views.ProfileListView.as_view(), name='profile'),
    path('send-report/', SendMonthlyReportView.as_view(), name='send_monthly_report'),
]