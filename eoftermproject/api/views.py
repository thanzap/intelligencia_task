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
    """
    Handles user registration.
    
    Args:
    - request (Request): Contains user registration data (username, password, email).
    
    Returns:
    - Response object with success or error message.
    """
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
    """
    Authenticates a user and provides JWT tokens upon successful authentication.
    
    Args:
    - request (Request): Contains user login data (username, password).
    
    Returns:
    - Response object with access and refresh tokens or error message.
    """
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
    """
    Fetches all EFO terms with optional dynamic fields filtering.
    
    Args:
    - request (Request): Optional query parameter 'fields' to select specific fields.
    
    Returns:
    - Paginated response containing EFO terms or error message.
    """
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
    """
    Create, retrieve, update, or delete an EFO term based on the HTTP method.
    
    Args:
    - request (Request): Contains data for creating/updating an EFO term.
    - efo_term_id (str, optional): EFO term ID to retrieve, update, or delete.
    
    Returns:
    - Response object with EFO term data, success or error message.
    """
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
    """
    Fetches parent terms of a given EFO term.
    
    Args:
    - request (Request): Not used directly but required by the decorator.
    - efo_term_id (str): EFO term ID whose children are to be retrieved.
    
    Returns:
    - Response object with the EFO term data and its parents or error message.
    """
    if request.method=='GET':
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
    """
    Fetches child terms of a given EFO term.
    
    Args:
    - request (Request): Not used directly but required by the decorator.
    - efo_term_id (str): EFO term ID whose children are to be retrieved.
    
    Returns:
    - Response object with the EFO term data and its children or error message.
    """
    if request.method=='GET':
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

