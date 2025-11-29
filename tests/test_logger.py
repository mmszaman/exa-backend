"""Test the universal logger"""

from app.core.logger import get_logger

# Get loggers for different modules
email_logger = get_logger('email_service')

# Test different log levels
email_logger.debug('This is a debug message')
email_logger.info('Email service started')
email_logger.warning('Rate limit approaching')
email_logger.error('FFFFFailed to send email')

print("\n✅ Check the logs/ folder - you should see separate log files!")