from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import stripe
from dotenv import load_dotenv
import os

load_dotenv()

class PaymentAPI(APIView):

    def post(self, request):
        print("Received POST request")  
        token = request.data.get('token')
        response = {}
        if token:
            print("Token received") 

            stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
            if not stripe.api_key:
                return Response({
                    'error': 'Stripe API key not found',
                    'status': status.HTTP_500_INTERNAL_SERVER_ERROR
                })

            response = self.stripe_card_payment(token=token)
        else:
            print("Token not received")  
            response = {
                'errors': 'Token not provided',
                'status': status.HTTP_400_BAD_REQUEST
            }

        return Response(response)

    def stripe_card_payment(self, token):
        try:
            print("Starting stripe_card_payment")  

            payment_intent = stripe.PaymentIntent.create(
                amount=10000,
                currency='inr',
                payment_method_data={
                    'type': 'card',
                    'card': {
                        'token': token,
                    },
                },
                confirmation_method='manual',
                confirm=True,
                return_url='https://your-return-url.com'  
            )
            print("PaymentIntent created:", payment_intent)  

            if payment_intent['status'] == 'requires_action' and payment_intent['next_action']['type'] == 'use_stripe_sdk':
                response = {
                    'message': "Card requires additional authentication",
                    'status': status.HTTP_200_OK,
                    "payment_intent": payment_intent,
                    "payment_confirm": {'status': "Requires Action"}
                }
            elif payment_intent['status'] == 'succeeded':
                response = {
                    'message': "Card Payment Success",
                    'status': status.HTTP_200_OK,
                    "payment_intent": payment_intent,
                    "payment_confirm": {'status': "Succeeded"}
                }
            else:
                response = {
                    'message': "Card Payment Failed",
                    'status': status.HTTP_400_BAD_REQUEST,
                    "payment_intent": payment_intent,
                    "payment_confirm": {'status': "Failed"}
                }
        except Exception as e:
            print("Error in stripe_card_payment:", e)  
            response = {
                'error': str(e),  
                'status': status.HTTP_400_BAD_REQUEST,
                "payment_intent": {"id": "Null"},
                "payment_confirm": {'status': "Failed"}
            }
        return response