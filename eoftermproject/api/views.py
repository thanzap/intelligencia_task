from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import DynamicFieldsEFOtermSerializer
from .pagination import CustomPageNumberPagination
from rest_framework import status
from eoftermapp.models import EFOterm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

@api_view(['POST'])
def signup(request):
    if request.method == 'POST':
        
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        print(username)
        print(password)
        print(email)
        if not username or not password or not email:
            return Response({'error': 'All fields are required!'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already in use!'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()
        
        return Response({'message': 'User created successfully!'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials!'}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_efo_terms(request):
    try:
        efo_term = EFOterm.objects.all()
        # Check for a 'fields' query parameter and split it into a list.
        fields = request.query_params.get('fields')
        if fields:
            fields = fields.split(',')

        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(efo_term, request)
        
        # Use the dynamic fields serializer and pass the 'fields' argument
        serializer = DynamicFieldsEFOtermSerializer(result_page, many=True, fields=fields)
        return paginator.get_paginated_response(serializer.data)
    except EFOterm.DoesNotExist:
        return Response({"error": "No EFO terms"}, status=404)
        
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def handle_efo_term(request, efo_term_id=None):
    # Create a new EFO term
    if request.method == 'POST':
        serializer = DynamicFieldsEFOtermSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # If efo_term_id is not provided for GET, PUT, or DELETE, return an error
    if not efo_term_id:
        return Response({"error": "efo_term_id is required for this request method."}, status=status.HTTP_400_BAD_REQUEST)

    # Try to fetch the EFO term with the given ID
    try:
        efo_term = EFOterm.objects.get(efo_term_id=efo_term_id)
    except EFOterm.DoesNotExist:
        return Response({"error": f"No EFO term with this ID: {efo_term_id}"}, status=status.HTTP_404_NOT_FOUND)

    # Retrieve details of an EFO term
    if request.method == 'GET':
        # Check for a 'fields' query parameter and split it into a list.
        fields = request.query_params.get('fields')
        if fields:
            fields = fields.split(',')
        serializer = DynamicFieldsEFOtermSerializer(efo_term, fields=fields)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Update details of an EFO term
    elif request.method == 'PUT':
        serializer = DynamicFieldsEFOtermSerializer(efo_term, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Delete an EFO term
    elif request.method == 'DELETE':
        efo_term.delete()
        return Response({"message": f"EFOTerm {efo_term_id} deleted successfully"}, status=status.HTTP_200_OK)

    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_parents_of_term(request, efo_term_id):
    try:
        efo_term = EFOterm.objects.get(efo_term_id=efo_term_id)
        parent_relationships = efo_term.parent_relations.all()
        parent_terms = [relation.parent for relation in parent_relationships]
        
        efo_serializer = DynamicFieldsEFOtermSerializer(efo_term)
        parents_serializer = DynamicFieldsEFOtermSerializer(parent_terms, many=True)
        
        return Response({
            'efo_term': efo_serializer.data,
            'parents': parents_serializer.data
        })
        
    except EFOterm.DoesNotExist:
        return Response({"error": "EFOterm not found"}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_children_of_term(request, efo_term_id):
    try:
        efo_term = EFOterm.objects.get(efo_term_id=efo_term_id)
        child_relationships = efo_term.child_relations.all()
        child_terms = [relation.term for relation in child_relationships]
        
        efo_serializer = DynamicFieldsEFOtermSerializer(efo_term)
        children_serializer = DynamicFieldsEFOtermSerializer(child_terms, many=True)
        
        return Response({
            'efo_term': efo_serializer.data,
            'children': children_serializer.data
        })
        
    except EFOterm.DoesNotExist:
        return Response({"error": "EFOterm not found"}, status=404)

