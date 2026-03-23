import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order
from .tasks import publish_order_event

@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)
            total_price = data.get('total_price')

            if not all([user_id, product_id, total_price]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            # 1. Create the Order in Database (PENDING status)
            order = Order.objects.create(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity,
                total_price=total_price,
                status='PENDING'
            )

            # 2. Trigger Async Celery Task to publish event to RabbitMQ
            publish_order_event.delay(order.id)

            return JsonResponse({'message': 'Order placed successfully', 'order_id': order.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_order(request, order_id):
    if request.method == 'GET':
        try:
            order = Order.objects.get(id=order_id)
            return JsonResponse({
                'id': order.id,
                'user_id': order.user_id,
                'product_id': order.product_id,
                'status': order.status,
                'total_price': float(order.total_price)
            })
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
