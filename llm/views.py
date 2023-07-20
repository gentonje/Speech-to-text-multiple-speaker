from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from audio.models import SessionTranscript

from .utils import get_llm_feedback



@method_decorator(login_required, name='dispatch')
class LlmView(APIView):
    def get(self, request):
        try:
            #get SessionTranscriptID from request
            session_transcript_id = request.GET.get('session_transcript_id')
            if session_transcript_id is None:
                return Response({"error": "session_transcript_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            prompt_for_llm = request.GET.get('prompt_for_llm')
            if prompt_for_llm is None or prompt_for_llm=="":
                return Response({"error": "prompt_for_llm is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            #get SessionTranscript object
            object_for_response = SessionTranscript.objects.get(user=request.user, id_token=session_transcript_id)

            # double check that session transcript is owned by user
            if object_for_response.user != request.user:
                return Response({"error": "session_transcript_id is invalid"}, status=status.HTTP_400_BAD_REQUEST)

            transcript_from_session_transcript = object_for_response.transcript

            prompt_for_llm = "Transcript: \n\n"+transcript_from_session_transcript+"\n--------------\n\nInstructions: "+prompt_for_llm
            response_from_llm = get_llm_feedback(prompt_for_llm)

            return Response({"prompt_for_llm":prompt_for_llm,"response_from_llm": response_from_llm})

        except SessionTranscript.DoesNotExist:
            # return error
            return Response({"error": "session_transcript_id is invalid"}, status=status.HTTP_400_BAD_REQUEST)