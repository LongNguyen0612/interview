import time
from collections import defaultdict
from threading import Lock
from django.conf import settings
from django.http import JsonResponse


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_history = defaultdict(list)
        self.lock = Lock()

        self.max_requests = getattr(settings, 'RATE_LIMIT_REQUESTS', 100)
        self.window_seconds = getattr(settings, 'RATE_LIMIT_WINDOW', 60)

    def __call__(self, request):
        ip_address = self.get_client_ip(request)

        if not self.is_allowed(ip_address):
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': f'Maximum {self.max_requests} requests per {self.window_seconds} seconds allowed'
            }, status=429)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip

    def is_allowed(self, ip_address):
        current_time = time.time()

        with self.lock:
            timestamps = self.request_history[ip_address]

            cutoff_time = current_time - self.window_seconds
            timestamps[:] = [ts for ts in timestamps if ts > cutoff_time]

            if len(timestamps) >= self.max_requests:
                return False

            timestamps.append(current_time)

            if len(self.request_history) > 10000:
                self.cleanup_old_entries(cutoff_time)

            return True

    def cleanup_old_entries(self, cutoff_time):
        ips_to_remove = [
            ip for ip, timestamps in self.request_history.items()
            if not timestamps or max(timestamps) < cutoff_time
        ]
        for ip in ips_to_remove:
            del self.request_history[ip]
