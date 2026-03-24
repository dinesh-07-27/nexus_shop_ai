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

import time
import random

@shared_task
def fake_stripe_payment(order_id):
    """
    Simulates a Stripe payment API call with an 80% success rate.
    """
    time.sleep(3)  # Simulate network latency
    
    try:
        order = Order.objects.get(id=order_id)
        
        # 80% chance to succeed
        if random.random() < 0.80:
            order.status = 'PAID'
            order.save()
            print(f" [$$$] Fake Stripe Payment SUCCESS for Order {order_id}")
            # Trigger Saga to deduct product stock
            publish_order_event.delay(order.id)
        else:
            order.status = 'FAILED'
            order.save()
            print(f" [XXX] Fake Stripe Payment FAILED for Order {order_id}")
            
    except Exception as e:
        print(f"Failed to process fake payment: {e}")
