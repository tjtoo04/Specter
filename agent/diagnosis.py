import os
import json
#import google.generativeai as genai
from agent.prompts import DIAGNOSIS_PROMPT

def diagnose(vision, state, friction_type):
    return {
        "issue_type": "UX Friction",
        "severity": "P2",
        "root_cause": f"Friction detected: {friction_type}",
        "suggested_team": "Frontend"
    }

