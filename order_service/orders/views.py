import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from .models import Order
from .tasks import publish_order_event
from .auth import require_jwt

logger = logging.getLogger(__name__)

@csrf_exempt
@require_jwt
def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            user_id = request.user_id or data.get('user_id')
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

@require_jwt
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

@csrf_exempt
@require_jwt
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            user_id = request.user_id or data.get('user_id')
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)

            from .models import Cart, CartItem
            cart, _ = Cart.objects.get_or_create(user_id=user_id)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, product_id=product_id,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return JsonResponse({'message': 'Added to cart'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@require_jwt
def get_cart(request, user_id):
    if request.method == 'GET':
        from .models import Cart
        try:
            cart = Cart.objects.get(user_id=user_id)
            items = cart.items.all()
            result = [
                {'product_id': item.product_id, 'quantity': item.quantity}
                for item in items
            ]
            return JsonResponse({'cart_items': result}, status=200)
        except Cart.DoesNotExist:
            return JsonResponse({'cart_items': []}, status=200)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@require_jwt
def checkout(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            user_id = request.user_id or data.get('user_id')
            
            if not user_id:
                return JsonResponse({'error': 'Missing user_id'}, status=400)
                
            from .models import Cart, Order
            try:
                cart = Cart.objects.get(user_id=user_id)
            except Cart.DoesNotExist:
                return JsonResponse({'error': 'Cart is empty'}, status=400)
                
            items = cart.items.all()
            if not items:
                return JsonResponse({'error': 'Cart is empty'}, status=400)
                
            order_ids = []
            from .tasks import fake_stripe_payment
            
            # Since Order model takes 1 product, we split the cart into separate shipments
            for item in items:
                # We assume total_price is 99.99 for mock purposes since we don't query product service synchronously
                order = Order.objects.create(
                    user_id=user_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    total_price=99.99 * item.quantity,
                    status='PENDING_PAYMENT'
                )
                order_ids.append(order.id)
                
                # Trigger Fake Stripe
                fake_stripe_payment.delay(order.id)
                
            # Empty cart
            cart.items.all().delete()
            
            return JsonResponse({'message': 'Checkout initiated', 'pending_orders': order_ids}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def health_check(request):
    return JsonResponse({"status": "Order Saga Service API v1 is fully healthy"}, status=200)
