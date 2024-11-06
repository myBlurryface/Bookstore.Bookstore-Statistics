from confluent_kafka import Consumer, KafkaException
import json
from statistics_operator.models import Customer, Purchase
from django.utils.dateparse import parse_datetime
from django.db import IntegrityError
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

config = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'statistics_consumer_group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True
}

consumer = Consumer(config)
consumer.subscribe(['customer_topic', 'order_topic','order_items_topic'])

logging.info("Kafka consumer started and subscribed to topics: customer_topic, order_topic, order_items_topic")

try:
    while True:
        msg = consumer.poll(timeout=1)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())
        else:
            try:
                message = msg.value().decode('utf-8')
                data = json.loads(message)
                logging.debug(f"Received message content: {data}")

                topic = msg.topic()

                if topic == 'customer_topic':
                    if 'user_action' in data and data['user_action'] in ['create', 'update']:
                        if data['user_action'] == 'create':
                            Customer.objects.create(
                                customer_id=data['customer_id'],
                                username=data['username'],
                                phone_number=data['phone_number'],
                                total_spent=data['spent_money'],
                                date_joined=data['date_joined']
                            )
                            logging.debug("Customer created successfully.")
                        elif data['user_action'] == 'update':
                            try:
                                customer = Customer.objects.get(customer_id=data['customer_id'])
                                customer.username = data['username']
                                customer.phone_number = data['phone_number']
                                customer.total_spent = data['spent_money']
                                customer.date_joined = data['date_joined']
                                customer.save()
                                logging.debug("Customer updated successfully.")
                            except Customer.DoesNotExist:
                                logging.debug(f"Customer with ID {['customer_id']} does not exist.")
                elif topic == 'order_topic':
                    if 'order_action' in data and data['order_action'] in ['create', 'update']:
                        customer_id = data.get('customer_id')
                        customer = Customer.objects.filter(customer_id=customer_id).first()

                        if not customer:
                            logging.warning(f"Customer with ID {customer_id} not found.")
                            continue

                        # Create new record    
                        if data['order_action'] == 'create':
                            purchase = Purchase.objects.create(
                                purchase_id=data.get('order_id'),
                                customer=data.get('customer_id'),
                                status=data.get('status', 'pending'),
                                purchase_date=parse_datetime(data.get('purchase_date')),
                                purchase_price=data.get('purchase_price')
                            )
                            logging.info(f"Purchase created: {purchase}")

                        # Update record
                        elif data['order_action'] == 'update':
                            purchase_id = data.get('order_id')
                            purchase = Purchase.objects.filter(purchase_id=purchase_id).first()

                            if purchase:
                                purchase.status = data.get('status', purchase.status)
                                purchase.purchase_date = parse_datetime(data.get('purchase_date')) or purchase.purchase_date
                                purchase.purchase_price = data.get('purchase_price', purchase.purchase_price)
                                purchase.save()
                                logging.info(f"Purchase updated: {purchase}")
                            else:
                                logging.warning(f"Purchase with ID {purchase_id} not found.")
                elif topic == 'order_items_topic':
                    if 'book_id' in data:
                        try:
                            purchase_date = parse_datetime(data.get('purchase_date'))
            
                            Purchase.objects.create(
                                book_id=data['book_id'],
                                book_title=data.get('book_title', 'Unknown'),
                                quantity=data.get('quantity', 1),
                                price=data.get('price'),
                                discount=data.get('discount', 0.00),
                                total_price=data.get('total_price'),
                                purchase_date=purchase_date
                            )
            
                            logging.info(f"Order item processed successfully for book ID {data['book_id']}.")
                        except IntegrityError as e:
                            logging.error(f"Failed to process order item: {e}")
                        except Exception as e:
                            logging.error(f"Unexpected error when processing order item: {e}")
            except json.JSONDecodeError as e:
                logging.error(f"Failed to decode message: {e}")

except KeyboardInterrupt:
    logging.info("Consumer stopped.")
finally:
    consumer.close()
    logging.info("Kafka consumer closed.")
