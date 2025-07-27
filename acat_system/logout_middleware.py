"""
ACAT Logout Middleware
Handles admin logout redirect issues
"""

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import logging
import re

logger = logging.getLogger(__name__)

class ACATLogoutMiddleware:
    """
    Middleware to handle logout redirects properly
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if this is an admin logout request BEFORE processing
        if (request.path.startswith('/admin/logout/') and 
            request.method in ['GET', 'POST']):
            
            logger.info("ACAT: Admin logout detected, intercepting and redirecting to login")
            
            # Force redirect to admin login immediately
            return HttpResponseRedirect('/admin/login/')
        
        response = self.get_response(request)
        
        # Inject JavaScript into admin pages to handle logout clicks
        if (request.path.startswith('/admin/') and 
            hasattr(response, 'content') and 
            hasattr(response, 'status_code') and 
            response.status_code == 200 and 
            b'text/html' in response.get('Content-Type', b'').encode()):
            
            logout_js = b'''
            <script>
            // ACAT Logout Fix - Injected by middleware
            (function() {
                function setupLogoutFix() {
                    document.addEventListener('click', function(e) {
                        const target = e.target;
                        const href = target.getAttribute('href') || '';
                        const text = target.textContent || target.value || '';
                        
                        if (href.includes('logout') || text.includes('Cerrar') || text.includes('Logout')) {
                            console.log('ACAT: Intercepting logout click');
                            e.preventDefault();
                            e.stopPropagation();
                            window.location.href = '/logout/';
                            return false;
                        }
                    });
                }
                
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', setupLogoutFix);
                } else {
                    setupLogoutFix();
                }
            })();
            </script>
            '''
            
            if b'</head>' in response.content:
                response.content = response.content.replace(b'</head>', logout_js + b'</head>')
                logger.info("ACAT: JavaScript injected into admin page")
        
        # Check if this is a redirect from admin that should go to login
        if (hasattr(response, 'status_code') and 
            response.status_code == 302 and 
            hasattr(response, 'url') and 
            response.url and 
            response.url.endswith('/admin/') and 
            request.path.startswith('/admin/logout/')):
            
            logger.info("ACAT: Intercepting admin redirect, sending to login instead")
            return HttpResponseRedirect('/admin/login/')
        
        # Check for blank responses from admin
        if (request.path.startswith('/admin/') and 
            hasattr(response, 'content') and 
            len(response.content) < 100):
            
            logger.warning("ACAT: Blank admin page detected, redirecting to login")
            return HttpResponseRedirect('/admin/login/')
        
        return response
