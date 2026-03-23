import json
import pika
from celery import shared_task
from .models import Order

@shared_task
def publish_order_event(order_id):
    """
    Saga Pattern Trigger: Publishes a message to RabbitMQ when an order is placed.
    Other services (like Inventory) listen to this queue to adjust stock.
    """
    try:
        order = Order.objects.get(id=order_id)
        
        # Connect to RabbitMQ (host is 'rabbitmq' in docker-compose, 'localhost' otherwise)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='order_events', durable=True)

        message = {
            "order_id": order.id,
            "product_id": order.product_id,
            "quantity": order.quantity,
            "status": order.status,
            "event": "ORDER_CREATED"
        }

        channel.basic_publish(
            exchange='',
            routing_key='order_events',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        print(f" [x] Sent order event for Order {order_id}")
        connection.close()
    except Exception as e:
        print(f"Failed to publish order event: {e}")
