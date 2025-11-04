"""
Gemini LLM Integration
Uses Google's Gemini 2.5 Flash for impact analysis reasoning
"""
from typing import Dict, List
import json
from backend.config import config
from backend.utils.logger import get_logger

logger = get_logger(__name__)

class GeminiAnalyzer:
    """Analyzes code impacts using Gemini LLM"""
    
    def __init__(self):
        self.available = False
        try:
            import google.generativeai as genai
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.available = True
            logger.info("Gemini API initialized successfully")
        except Exception as e:
            logger.warning(f"Gemini API not available: {e}")
    
    def analyze_impact(self, changed_modules: List[str], affected_modules: List[str]) -> Dict:
        """
        Use Gemini to analyze why modules are affected.
        
        Args:
            changed_modules: Modules that were changed
            affected_modules: Modules affected by the change
            
        Returns:
            Dictionary with LLM analysis
        """

        # Check if Gemini is available
        if not self.available or not config.GEMINI_API_KEY:
            raise RuntimeError("Gemini API key missing or Gemini not available")

        prompt = self._build_prompt(changed_modules, affected_modules)
        response = self.model.generate_content(prompt)
        analysis = self._parse_response(response.text)
        return analysis

        
        # if not self.available or not config.GEMINI_API_KEY:
        #     logger.warning("Gemini not available, returning basic analysis")
        #     return self._fallback_analysis(changed_modules, affected_modules)
        
        # try:
        #     prompt = self._build_prompt(changed_modules, affected_modules)
        #     response = self.model.generate_content(prompt)
            
        #     # Parse response
        #     analysis = self._parse_response(response.text)
        #     logger.info("Gemini analysis completed successfully")
        #     return analysis
        
        # except Exception as e:
        #     logger.error(f"Gemini analysis failed: {e}")
        #     return self._fallback_analysis(changed_modules, affected_modules)
    
    def _build_prompt(self, changed_modules: List[str], affected_modules: List[str]) -> str:
        """Build the prompt for Gemini"""
        return f"""You are a code impact analysis expert.

Changed modules: {', '.join(changed_modules)}
Affected modules: {', '.join(affected_modules)}

For each affected module, provide:
1. Brief reason why it's affected (1-2 sentences)
2. Potential issue that might occur
3. Risk level: LOW, MEDIUM, or HIGH

Return ONLY valid JSON (no markdown, no extra text):
{{
  "module_name": {{
    "reason": "...",
    "potential_issue": "...",
    "risk": "HIGH|MEDIUM|LOW"
  }}
}}
"""
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse Gemini's response"""
        try:
            # Clean up response
            clean_text = response_text.strip()
            if clean_text.startswith('```'):
                clean_text = clean_text.split('```')
            if clean_text.startswith('json'):
                clean_text = clean_text[4:]
            
            return json.loads(clean_text)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Gemini response: {e}")
            return {}
    
    def _fallback_analysis(self, changed_modules: List[str], affected_modules: List[str]) -> Dict:
        """Fallback analysis when Gemini is unavailable"""
        logger.info("Using fallback analysis")
        return {
            m: {
                "reason": f"Module affected by changes to {', '.join(changed_modules)}",
                "potential_issue": "Dependency on changed functionality",
                "risk": "MEDIUM"
            }
            for m in affected_modules
        }
