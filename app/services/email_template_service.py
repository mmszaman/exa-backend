"""
Template Service - Handles email template rendering with Jinja2
"""

import os
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from app.core.logger import get_logger

logger = get_logger("template_service")


class TemplateService:
    """
    Service for rendering email templates using Jinja2.
    Templates are stored in app/templates/email/
    """
    
    # Template configuration with defaults
    TEMPLATE_CONFIG = {
        "welcome": {
            "subject": "Welcome to {company_name}!",
            "from_name": "{company_name} Team",
            "description": "Welcome email for new users"
        },
        "password_reset": {
            "subject": "Reset Your Password",
            "from_name": "{company_name} Security",
            "description": "Password reset email with reset link"
        },
        "email_verification": {
            "subject": "Verify Your Email Address",
            "from_name": "{company_name}",
            "description": "Email verification with confirmation link"
        },
        "notification": {
            "subject": "New Notification",
            "from_name": "{company_name}",
            "description": "General notification email"
        }
    }
    
    def __init__(self):
        """Initialize template environment."""
        # Get absolute path to templates directory
        template_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),  # app directory
            "templates",
            "email"
        )
        
        # Create Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True,  # Auto-escape HTML for security
            trim_blocks=True,  # Remove whitespace
            lstrip_blocks=True
        )
        
        logger.info(f"Template service initialized with directory: {template_dir}")
    
    def get_available_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Get list of available templates with their configuration.
        
        Returns:
            Dictionary of template names and their config
        """
        return self.TEMPLATE_CONFIG.copy()
    
    def get_template_config(self, template_name: str) -> Optional[Dict[str, str]]:
        """
        Get configuration for a specific template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template configuration or None if not found
        """
        return self.TEMPLATE_CONFIG.get(template_name)
    
    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        use_base: bool = True
    ) -> str:
        """
        Render an email template with the given context.
        
        Args:
            template_name: Name of template file (without .html extension)
            context: Dictionary of variables to pass to template
            use_base: Whether to wrap in base template (default: True)
            
        Returns:
            Rendered HTML string
            
        Raises:
            TemplateNotFound: If template file doesn't exist
            Exception: If rendering fails
        """
        logger.debug(f"Rendering template: {template_name}")
        
        try:
            # Add default context values
            default_context = {
                "company_name": context.get("company_name", "Exa"),
                "year": 2025,
                "support_email": "support@exateks.com"
            }
            
            # Merge with provided context (provided values take precedence)
            full_context = {**default_context, **context}
            
            # Load and render template
            if use_base:
                # Render content template first
                content_template = self.env.get_template(f"{template_name}.html")
                content_html = content_template.render(**full_context)
                
                # Wrap in base template
                base_template = self.env.get_template("base.html")
                full_context["content"] = content_html
                html = base_template.render(**full_context)
            else:
                # Render standalone template
                template = self.env.get_template(f"{template_name}.html")
                html = template.render(**full_context)
            
            logger.info(f"Successfully rendered template: {template_name}")
            return html
            
        except TemplateNotFound as e:
            logger.error(f"Template not found: {template_name}.html")
            raise ValueError(f"Template '{template_name}' not found") from e
            
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {type(e).__name__}: {e}")
            raise
    
    def render_text_from_html(self, html: str) -> str:
        """
        Convert HTML to plain text (simple version).
        Strips HTML tags for plain text email version.
        
        Args:
            html: HTML content
            
        Returns:
            Plain text version
        """
        import re
        
        # Remove HTML tags
        text = re.sub('<[^<]+?>', '', html)
        
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def get_subject(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Get subject line for a template, formatted with context.
        
        Args:
            template_name: Name of the template
            context: Context dictionary for formatting
            
        Returns:
            Formatted subject line
        """
        config = self.get_template_config(template_name)
        if not config:
            return "Notification"
        
        subject = config.get("subject", "Notification")
        
        # Format subject with context values
        try:
            return subject.format(**context)
        except KeyError:
            # If formatting fails, return as-is
            return subject
    
    def get_from_name(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Get from name for a template, formatted with context.
        
        Args:
            template_name: Name of the template
            context: Context dictionary for formatting
            
        Returns:
            Formatted from name
        """
        config = self.get_template_config(template_name)
        if not config:
            return context.get("company_name", "Exa")
        
        from_name = config.get("from_name", "{company_name}")
        
        # Format from name with context values
        try:
            return from_name.format(**context)
        except KeyError:
            return from_name


# Create singleton instance
template_service = TemplateService()
