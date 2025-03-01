from django.urls import path
from .views import CreatePaymentView, ExecutePaymentView, CancelPaymentView

urlpatterns = [
    path('create/', CreatePaymentView.as_view(), name='create-payment'),
    path('execute/', ExecutePaymentView.as_view(), name='execute-payment'),
    path('cancel/', CancelPaymentView.as_view(), name='cancel-payment'),
]
