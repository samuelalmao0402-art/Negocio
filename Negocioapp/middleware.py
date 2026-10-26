import zoneinfo
from django.utils import timezone

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lee la cookie enviada por el navegador con la zona horaria del dispositivo
        tzname = request.COOKIES.get('user_timezone')
        
        if tzname:
            try:
                tz = zoneinfo.ZoneInfo(tzname)
                timezone.activate(tz)
            except Exception:
                timezone.deactivate()
        else:
            timezone.deactivate()
            
        response = self.get_response(request)
        return response