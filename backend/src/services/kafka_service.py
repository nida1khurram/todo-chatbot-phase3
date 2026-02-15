"""
Kafka Service for Todo Application
This module handles Kafka integration for event-driven architecture
"""

import logging
import json
from typing import Dict, Any, Optional
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
from ..settings import settings

logger = logging.getLogger(__name__)

class KafkaService:
    def __init__(self):
        self.producer = None
        self.bootstrap_servers = settings.kafka_bootstrap_servers
        self.security_protocol = settings.kafka_security_protocol
        self.sasl_mechanism = settings.kafka_sasl_mechanism if settings.kafka_sasl_mechanism else None
        self.sasl_plain_username = settings.kafka_sasl_plain_username if settings.kafka_sasl_plain_username else None
        self.sasl_plain_password = settings.kafka_sasl_plain_password if settings.kafka_sasl_plain_password else None
        
    async def create_producer(self):
        """Create and return a Kafka producer"""
        if self.producer is None:
            config = {
                'bootstrap_servers': self.bootstrap_servers,
                'value_serializer': lambda v: json.dumps(v).encode('utf-8')
            }
            
            # Add security configuration if provided
            if self.security_protocol:
                config['security_protocol'] = self.security_protocol
            if self.sasl_mechanism:
                config['sasl_mechanism'] = self.sasl_mechanism
            if self.sasl_plain_username:
                config['sasl_plain_username'] = self.sasl_plain_username
            if self.sasl_plain_password:
                config['sasl_plain_password'] = self.sasl_plain_password
                
            self.producer = AIOKafkaProducer(**config)
        
        if not self.producer.started:
            await self.producer.start()
        
        return self.producer
    
    async def send_task_event(self, event_type: str, task_data: Dict[str, Any], key: Optional[str] = None):
        """Send a task-related event to Kafka"""
        try:
            producer = await self.create_producer()
            
            event = {
                'event_type': event_type,
                'timestamp': asyncio.get_event_loop().time(),
                'task_data': task_data,
                'source': 'todo-backend'
            }
            
            topic = f"task-{event_type}"
            
            await producer.send_and_wait(topic, value=event, key=key.encode('utf-8') if key else None)
            
            logger.info(f"Sent {event_type} event to topic {topic}")
            
        except Exception as e:
            logger.error(f"Error sending {event_type} event to Kafka: {str(e)}")
            raise
    
    async def send_user_event(self, event_type: str, user_data: Dict[str, Any], key: Optional[str] = None):
        """Send a user-related event to Kafka"""
        try:
            producer = await self.create_producer()
            
            event = {
                'event_type': event_type,
                'timestamp': asyncio.get_event_loop().time(),
                'user_data': user_data,
                'source': 'todo-backend'
            }
            
            topic = f"user-{event_type}"
            
            await producer.send_and_wait(topic, value=event, key=key.encode('utf-8') if key else None)
            
            logger.info(f"Sent {event_type} event to topic {topic}")
            
        except Exception as e:
            logger.error(f"Error sending {event_type} event to Kafka: {str(e)}")
            raise
    
    async def close_producer(self):
        """Close the Kafka producer"""
        if self.producer:
            await self.producer.stop()
            self.producer = None

    async def create_consumer(self, topics: list, group_id: str):
        """Create and return a Kafka consumer"""
        config = {
            'bootstrap_servers': self.bootstrap_servers,
            'group_id': group_id,
            'value_deserializer': lambda m: json.loads(m.decode('utf-8'))
        }
        
        # Add security configuration if provided
        if self.security_protocol:
            config['security_protocol'] = self.security_protocol
        if self.sasl_mechanism:
            config['sasl_mechanism'] = self.sasl_mechanism
        if self.sasl_plain_username:
            config['sasl_plain_username'] = self.sasl_plain_username
        if self.sasl_plain_password:
            config['sasl_plain_password'] = self.sasl_plain_password
            
        consumer = AIOKafkaConsumer(*topics, **config)
        await consumer.start()
        
        return consumer