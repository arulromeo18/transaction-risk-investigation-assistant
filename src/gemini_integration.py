"""
Gemini API Integration for narrative generation.

This module handles integration with Google's Gemini API to generate
natural language investigation narratives from structured fraud detection results.

Validates: Requirements 3.1, 3.3, 3.4, 3.5, 6.1, 6.2
"""

import os
import asyncio
from typing import Optional
import google.generativeai as genai

from src.models.detection import DetectionResult
from src.models.customer import CustomerProfile


class GeminiIntegration:
    """
    Handles Gemini API integration for narrative generation.
    
    Features:
    - Async generation with configurable timeout
    - Automatic fallback to rule results only on failure
    - Structured prompts for consistent output
    - Error handling for network issues and API failures
    
    Validates: Requirements 3.1, 3.3, 3.4, 3.5, 6.1, 6.2
    """
    
    NARRATIVE_TIMEOUT_SECONDS = 45  # Leave 15s buffer for other processing
    MODEL_NAME = "gemini-3.6-flash"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini integration.
        
        Args:
            api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
        
        Raises:
            ValueError: If no API key is provided and GEMINI_API_KEY is not set
        """
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key not provided. Set GEMINI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.MODEL_NAME)
    
    def generate_narrative_sync(
        self,
        detection_result: DetectionResult,
        profile: CustomerProfile
    ) -> Optional[str]:
        """
        Generate investigation narrative synchronously (blocking).
        
        This is the main entry point for Flask applications that need
        synchronous execution. It wraps the async implementation.
        
        Args:
            detection_result: Fraud detection results to narrate
            profile: Customer profile with transaction context
        
        Returns:
            Investigation narrative string, or None if generation fails/times out
        """
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                narrative = loop.run_until_complete(
                    self.generate_narrative_async(detection_result, profile)
                )
                return narrative
            finally:
                loop.close()
                
        except Exception as e:
            print(f"Gemini narrative generation error: {e}")
            return None
    
    async def generate_narrative_async(
        self,
        detection_result: DetectionResult,
        profile: CustomerProfile
    ) -> Optional[str]:
        """
        Generate investigation narrative asynchronously with timeout.
        
        Args:
            detection_result: Fraud detection results to narrate
            profile: Customer profile with transaction context
        
        Returns:
            Investigation narrative string, or None if generation fails/times out
        """
        try:
            # Build structured prompt
            prompt = self._build_prompt(detection_result, profile)
            
            # Generate with timeout
            response = await asyncio.wait_for(
                self._generate_with_retry(prompt),
                timeout=self.NARRATIVE_TIMEOUT_SECONDS
            )
            
            return response.text if response else None
            
        except asyncio.TimeoutError:
            print(f"Gemini API timeout after {self.NARRATIVE_TIMEOUT_SECONDS}s")
            return None
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None
    
    async def _generate_with_retry(self, prompt: str, max_retries: int = 2):
        """
        Generate content with retry on transient failures.
        
        Args:
            prompt: The prompt to send to Gemini
            max_retries: Maximum number of retry attempts
        
        Returns:
            Generation response object
        
        Raises:
            Exception: If all retries fail
        """
        for attempt in range(max_retries):
            try:
                # Run synchronous API call in executor to avoid blocking
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    self.model.generate_content,
                    prompt
                )
                return response
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                # Brief delay before retry
                await asyncio.sleep(1)
    
    def _build_prompt(
        self,
        detection_result: DetectionResult,
        profile: CustomerProfile
    ) -> str:
        """
        Build structured prompt for narrative generation.
        
        The prompt provides:
        - Customer context and transaction overview
        - Detected fraud patterns with details
        - Request for structured investigation narrative
        - Guidelines on tone and content
        
        Args:
            detection_result: Fraud detection results
            profile: Customer profile
        
        Returns:
            Formatted prompt string for Gemini API
        """
        # Build patterns summary
        patterns_summary = []
        for pattern in detection_result.detected_patterns:
            details_str = "\n    ".join([f"{k}: {v}" for k, v in pattern.details.items()])
            patterns_summary.append(
                f"  {pattern.pattern_name} (Risk: {pattern.risk_score}/100)\n"
                f"  Type: {pattern.pattern_type}\n"
                f"  Description: {pattern.description}\n"
                f"  Triggered Transactions: {len(pattern.triggered_transactions)}\n"
                f"  Details:\n    {details_str}"
            )
        
        patterns_text = "\n\n".join(patterns_summary)
        
        # Calculate date range
        if profile.transactions:
            sorted_txns = sorted(profile.transactions, key=lambda t: t.timestamp)
            first_date = sorted_txns[0].timestamp.strftime("%Y-%m-%d")
            last_date = sorted_txns[-1].timestamp.strftime("%Y-%m-%d")
            date_range = f"{first_date} to {last_date}"
        else:
            date_range = "Unknown"
        
        prompt = f"""You are a fraud investigation specialist analyzing transaction data for a banking fraud desk. Review the following fraud detection results and provide a clear, professional investigation narrative.

**Customer Profile:**
- Customer ID: {profile.customer_id}
- Name: {profile.name}
- Transaction Count: {len(profile.transactions)}
- Date Range: {date_range}
- Overall Risk Score: {detection_result.overall_risk_score}/100

**Detected Fraud Patterns ({len(detection_result.detected_patterns)}):**

{patterns_text}

**Instructions:**
Please provide a structured investigation narrative with these sections:

### Executive Summary
A 2-3 sentence overview stating whether this account requires immediate attention, the primary risk level, and the main concerns.

### Pattern Analysis
For each detected pattern, create a subsection with:

#### [Pattern Name] (Risk Score: X/100)
* Indication: What the pattern indicates
* Deviation: How it deviates from normal behavior
* Evidence: The specific evidence found (with transaction counts/amounts)

Use one bullet point per line (start each with "* " on a new line).

---

### Risk Assessment
An overall evaluation of the risk severity and likelihood of fraudulent activity.

### Recommended Actions
Specific, actionable steps the fraud investigation team should take, prioritized by urgency. Use bullet points:
* Action 1
* Action 2
* Action 3

**Important Guidelines:**
- Use markdown formatting: ### for main sections, #### for subsections, * for bullets (one per line)
- Separate sections with --- (horizontal rule)
- NEVER claim fraud has definitively occurred - use "flagged for review," "suspicious activity," "requires investigation"
- Be factual and evidence-based - reference specific transaction counts and amounts
- Keep narrative concise but thorough (approximately 300-500 words)
- Put each bullet point on its own line starting with "* "

Generate the investigation narrative now:"""

        return prompt


def create_gemini_integration() -> Optional[GeminiIntegration]:
    """
    Factory function to create GeminiIntegration with error handling.
    
    Returns:
        GeminiIntegration instance if API key is available, None otherwise
    """
    try:
        return GeminiIntegration()
    except ValueError as e:
        print(f"Gemini integration disabled: {e}")
        return None

