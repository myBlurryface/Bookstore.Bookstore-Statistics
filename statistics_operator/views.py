from statistics_operator.models import *
from statistics_operator.serializers import *
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets, filters, permissions, generics
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Sum, Avg
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware


class CustomerPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'
    max_page_size = 100


class CustomerViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerSerializer
    pagination_class = CustomerPagination    

    def get_queryset(self):
        return Customer.objects.all()
    
    # Get sorted user list 
    def list(self, request):
        queryset = self.get_queryset()
        
        ordering = request.query_params.get('ordering')
        if ordering in ['date_joined', '-date_joined', 'total_spent', '-total_spent']:
            queryset = queryset.order_by(ordering)
        
        serializer = CustomerSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def total_users(self, request):
        total_users = Customer.objects.count()
        users_with_no_spent = Customer.objects.filter(total_spent=0).count()
        users_with_spent = Customer.objects.filter(total_spent__gt=0).count()

        statistics = {
            'total_users': total_users,
            'users_with_zero_spent': users_with_no_spent,
            'users_with_spent': users_with_spent,
        }

        return Response(statistics)	


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['purchase_date', 'status']

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if status:
            queryset = queryset.filter(status=status)

        if start_date:
            queryset = queryset.filter(purchase_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(purchase_date__lte=end_date)

        return queryset

    @action(detail=False, methods=['get'])
    def current_month(self, request):
        current_month = timezone.now().month
        current_year = timezone.now().year
        purchases = Purchase.objects.filter(purchase_date__month=current_month, purchase_date__year=current_year)
        serializer = self.get_serializer(purchases, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_month(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year', timezone.now().year)

        if month:
            purchases = Purchase.objects.filter(purchase_date__month=month, purchase_date__year=year)
            serializer = self.get_serializer(purchases, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Month parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def by_date(self, request):
        date_str = request.query_params.get('date')
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                purchases = Purchase.objects.filter(purchase_date__date=date)
                serializer = self.get_serializer(purchases, many=True)
                return Response(serializer.data)
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Date parameter is required."}, status=status.HTTP_400_BAD_REQUEST)


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['purchase_date', 'status']

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if status:
            queryset = queryset.filter(status=status)
        if start_date:
            start_date = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            queryset = queryset.filter(purchase_date__gte=start_date)
        if end_date:
            end_date = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
            queryset = queryset.filter(purchase_date__lte=end_date)

        return queryset

    @action(detail=False, methods=['get'])
    def current_month(self, request):
        current_month = timezone.now().month
        current_year = timezone.now().year
        purchases = Purchase.objects.filter(
            purchase_date__month=current_month,
            purchase_date__year=current_year
        )
        serializer = self.get_serializer(purchases, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_month(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year', timezone.now().year)

        try:
            month = int(month)
            year = int(year)
            purchases = Purchase.objects.filter(purchase_date__month=month, purchase_date__year=year)
            serializer = self.get_serializer(purchases, many=True)
            return Response(serializer.data)
        except (ValueError, TypeError):
            return Response({"error": "Invalid month or year. Ensure they are integers."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def by_date(self, request):
        date_str = request.query_params.get('date')
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                date = timezone.make_aware(datetime.combine(date, datetime.min.time()))
                purchases = Purchase.objects.filter(purchase_date__date=date)
                serializer = self.get_serializer(purchases, many=True)
                return Response(serializer.data)
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Date parameter is required."}, status=status.HTTP_400_BAD_REQUEST)


class PurchaseSummaryView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_previous_quarter_dates(self):
        now = timezone.now()
        current_month = now.month
        
        if current_month in [1, 2, 3]:
            start_date = make_aware(datetime(now.year - 1, 10, 1))   
            end_date = make_aware(datetime(now.year - 1, 12, 31))    
        elif current_month in [4, 5, 6]:
            start_date = make_aware(datetime(now.year, 1, 1))        
            end_date = make_aware(datetime(now.year, 3, 31))         
        elif current_month in [7, 8, 9]:
            start_date = make_aware(datetime(now.year, 4, 1))        
            end_date = make_aware(datetime(now.year, 6, 30))          
        else:
            start_date = make_aware(datetime(now.year, 7, 1))         
            end_date = make_aware(datetime(now.year, 9, 30))         

        return start_date, end_date

    # Top buy book
    def get_top_book(self, start_date, end_date):

        top_book = Purchase.objects.filter(
            purchase_date__range=(start_date, end_date),
            status='delivered'
        ).values('book_title').annotate(total=Count('purchase_id')).order_by('-total').first()
 
        return top_book

    # Total sales for current quate/last_quater/special date/this month/date range/today
    def get_total_sales(self, start_date, end_date):
        return Purchase.objects.filter(
            purchase_date__range=(start_date, end_date),
            status='delivered'
        ).aggregate(Sum('purchase_price'))['purchase_price__sum'] or 0

    # Average check for current quate/last_quater/special date/this month/today
    def get_avg_check(self, start_date, end_date):
        return Purchase.objects.filter(
            purchase_date__range=(start_date, end_date),
            status='delivered'
        ).aggregate(Avg('purchase_price'))['purchase_price__avg'] or 0

    def get_date_range(self, period, date=None):
        today = timezone.now()   

        if period == 'specific_date' and date:
            try:
                date = datetime.strptime(date, '%Y-%m-%d')  
                start_date = timezone.make_aware(date)  
                end_date = start_date + timedelta(days=1) - timedelta(seconds=1)   
            except ValueError:
                return None, None  
        elif period == 'this_month':
            start_date = today.replace(day=1)   
            end_date = today
        elif period == 'today':
            start_date = today  
            end_date = today
        elif period == 'this_quarter':
            quarter_start_month = (today.month - 1) // 3 * 3 + 1  
            start_date = today.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = today
        elif period == 'last_quarter':
            start_date, end_date = self.get_previous_quarter_dates()
        elif period == 'this_year':
            start_date = today.replace(month=1, day=1)  
            end_date = today
        else:
            return None, None  

        return start_date, end_date

    @action(detail=False, methods=['get'])
    def get_summary(self, request):
        period = request.query_params.get('period')
        date = request.query_params.get('date')

        start_date, end_date = self.get_date_range(period, date)

        if start_date is None or end_date is None:
            return Response({'error': 'Invalid period specified.'}, status=400)

        top_book = self.get_top_book(start_date, end_date)
        total_sales = self.get_total_sales(start_date, end_date)
        avg_check = self.get_avg_check(start_date, end_date)

        return Response({
            'top_book': top_book['book_title'] if top_book else None,
            'total_sales': total_sales,
            'avg_check': avg_check,
        })