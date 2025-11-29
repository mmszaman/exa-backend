"""
Template Service - Handles email template rendering with Jinja2.
Simple and straightforward, just like EmailService.
"""

import os
import re
from typing import Dict, Any, Tuple
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from app.core.logger import get_logger

logger = get_logger("template_service")


class TemplateService:
    """
    Service for rendering email templates using Jinja2.
    Templates are stored in app/templates/email/
    
    Simple workflow (just like EmailService):
    1. Render HTML body from template file
    2. Convert HTML to plain text
    3. Return both versions
    
    No template configuration - caller provides subject, from_name, etc.
    """
    
    def __init__(self):
        """Initialize Jinja2 template environment."""
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
    
    @staticmethod
    def _get_default_context(context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add default context values (company_name, year, support_email).
        User-provided values take precedence.
        
        Args:
            context: User-provided context
            
        Returns:
            Merged context with defaults
        """
        default_context = {
            "company_name": "Exa",
            "year": 2025,
            "support_email": "support@exateks.com"
        }
        
        # Merge with provided context (provided values override defaults)
        return {**default_context, **context}
    
    def render_html_body(
        self,
        template_name: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Render HTML body from template file.
        Template automatically extends base_template.html.
        
        Args:
            template_name: Template filename (without .html extension)
            context: Variables to pass to template
            
        Returns:
            Rendered HTML string
            
        Raises:
            ValueError: If template file not found
            Exception: If rendering fails
        """
        logger.debug(f"Rendering template: {template_name}")
        
        try:
            # Add default context values
            full_context = self._get_default_context(context)
            
            # Load and render template (template extends base_template.html)
            template = self.env.get_template(f"{template_name}.html")
            html = template.render(**full_context)
            
            logger.info(f"Template rendered: {template_name} ({len(html)} chars)")
            return html
            
        except TemplateNotFound as e:
            logger.error(f"Template not found: {template_name}.html")
            raise ValueError(f"Template '{template_name}' not found") from e
            
        except Exception as e:
            logger.error(f"Template rendering error: {type(e).__name__}: {e}")
            raise
    
    @staticmethod
    def render_text_body(html_body: str) -> str:
        """
        Convert HTML to plain text (strip HTML tags).
        
        Args:
            html_body: HTML content
            
        Returns:
            Plain text version
        """
        # Remove HTML tags
        text = re.sub('<[^<]+?>', '', html_body)
        
        # Replace multiple spaces/newlines with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        logger.debug(f"Converted HTML to text ({len(text)} chars)")
        return text
    
    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any]
    ) -> Tuple[str, str]:
        """
        Render template and return both HTML and text versions.
        
        This is the main method - simple and straightforward:
        1. Render HTML from template (template extends base_template.html)
        2. Convert to plain text
        3. Return both
        
        Args:
            template_name: Template filename (without .html)
            context: Template variables
            
        Returns:
            Tuple of (html_body, text_body)
            
        Raises:
            ValueError: If template not found
        """
        logger.info(f"Rendering template: {template_name}")
        logger.debug(f"Context: {list(context.keys())}")
        
        # Render HTML body (template extends base_template.html automatically)
        html_body = self.render_html_body(template_name, context)
        
        # Create plain text version
        text_body = self.render_text_body(html_body)
        
        logger.info(f"Template complete - HTML: {len(html_body)} chars, Text: {len(text_body)} chars")
        
        return html_body, text_body


# Create singleton instance
template_service = TemplateService()
