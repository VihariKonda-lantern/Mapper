"""LLM client for Copilot Studio integration via Direct Line API."""
from typing import Any, Dict, List, Optional
import json
import os
import time
import requests
from core.exceptions import MappingError

try:
    from utils.structured_logging import StructuredLogger
    logger = StructuredLogger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class CopilotStudioLLMClient:
    """Client for calling Copilot Studio LLM agent via Direct Line API."""
    
    DIRECT_LINE_BASE_URL = "https://directline.botframework.com/v3/directline"
    
    def __init__(
        self,
        direct_line_secret: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        timeout: int = 30,
        enabled: bool = True,
        max_retries: int = 2
    ):
        """
        Initialize Copilot Studio LLM client.
        
        Args:
            direct_line_secret: Direct Line Secret for authentication
            endpoint_url: Custom endpoint URL (overrides default Direct Line URL)
            timeout: Request timeout in seconds
            enabled: Whether LLM is enabled
            max_retries: Maximum retry attempts
        """
        self.direct_line_secret = direct_line_secret or os.getenv("LLM_DIRECT_LINE_SECRET") or os.getenv("LLM_API_KEY")
        self.endpoint_url = endpoint_url or os.getenv("LLM_API_ENDPOINT")
        self.timeout = timeout
        self.max_retries = max_retries
        self.enabled = enabled and bool(self.direct_line_secret or self.endpoint_url)
        
        # If custom endpoint is provided, use it; otherwise use standard Direct Line
        if self.endpoint_url:
            # Extract base URL from the endpoint (remove /conversations and query params)
            if "/conversations" in self.endpoint_url:
                self.base_url = self.endpoint_url.split("/conversations")[0]
            else:
                self.base_url = self.endpoint_url.rstrip("/")
            self.use_custom_endpoint = True
        else:
            self.base_url = self.DIRECT_LINE_BASE_URL
            self.use_custom_endpoint = False
        
        if not self.direct_line_secret and not self.endpoint_url and enabled:
            logger.warning("Direct Line Secret or API endpoint not configured. LLM mapping will be disabled.")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        # Only add Authorization if we have a secret
        if self.direct_line_secret:
            headers["Authorization"] = f"Bearer {self.direct_line_secret}"
        return headers
    
    def _create_conversation(self) -> tuple[str, str]:
        """
        Create a Direct Line conversation.
        
        Returns:
            Tuple of (conversation_id, token)
        """
        if self.use_custom_endpoint:
            # Use the custom endpoint URL directly
            url = self.endpoint_url or f"{self.base_url}/conversations?api-version=2022-03-01-preview"
        else:
            url = f"{self.DIRECT_LINE_BASE_URL}/conversations"
        
        response = requests.post(
            url,
            headers=self._get_headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        
        data = response.json()
        conversation_id = data.get("conversationId")
        token = data.get("token")
        
        if not conversation_id or not token:
            raise MappingError("Failed to create conversation: missing conversationId or token")
        
        return conversation_id, token
    
    def _send_message(self, conversation_id: str, message_text: str) -> str:
        """
        Send a message to the conversation.
        
        Args:
            conversation_id: Conversation ID
            message_text: Message text to send
            
        Returns:
            Activity ID
        """
        if self.use_custom_endpoint:
            url = f"{self.base_url}/conversations/{conversation_id}/activities?api-version=2022-03-01-preview"
        else:
            url = f"{self.DIRECT_LINE_BASE_URL}/conversations/{conversation_id}/activities"
        
        payload = {
            "type": "message",
            "from": {"id": "user"},
            "text": message_text
        }
        
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        data = response.json()
        activity_id = data.get("id")
        
        if not activity_id:
            raise MappingError("Failed to send message: missing activity ID")
        
        return activity_id
    
    def _poll_for_response(self, conversation_id: str, watermark: Optional[str] = None, max_wait: int = 30) -> str:
        """
        Poll for bot response messages.
        
        Args:
            conversation_id: Conversation ID
            watermark: Watermark for incremental polling
            max_wait: Maximum time to wait in seconds
            
        Returns:
            Bot response text
        """
        if self.use_custom_endpoint:
            url = f"{self.base_url}/conversations/{conversation_id}/activities?api-version=2022-03-01-preview"
            if watermark:
                url += f"&watermark={watermark}"
        else:
            url = f"{self.DIRECT_LINE_BASE_URL}/conversations/{conversation_id}/activities"
            if watermark:
                url += f"?watermark={watermark}"
        
        start_time = time.time()
        poll_interval = 1.0
        
        while time.time() - start_time < max_wait:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            activities = data.get("activities", [])
            new_watermark = data.get("watermark")
            
            for activity in activities:
                if activity.get("from", {}).get("id") != "user" and activity.get("type") == "message":
                    text = activity.get("text", "").strip()
                    if text:
                        return text
            
            if new_watermark and new_watermark != watermark:
                watermark = new_watermark
                if self.use_custom_endpoint:
                    url = f"{self.base_url}/conversations/{conversation_id}/activities?api-version=2022-03-01-preview&watermark={watermark}"
                else:
                    url = f"{self.DIRECT_LINE_BASE_URL}/conversations/{conversation_id}/activities?watermark={watermark}"
            
            time.sleep(poll_interval)
        
        raise MappingError("Timeout waiting for bot response")
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from bot response text.
        
        Args:
            text: Response text that may contain JSON
            
        Returns:
            Parsed JSON dictionary
        """
        json_start = text.find("{")
        json_end = text.rfind("}") + 1
        
        if json_start < 0 or json_end <= json_start:
            raise MappingError("No valid JSON found in bot response")
        
        json_str = text[json_start:json_end]
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise MappingError(f"Invalid JSON in bot response: {e}")
    
    def call_copilot_mapper(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends payload JSON to Copilot Studio agent and returns parsed JSON response.
        
        Args:
            payload: Request payload dictionary
            
        Returns:
            Parsed JSON response from bot
            
        Raises:
            MappingError: If request fails or response is invalid
        """
        if not self.enabled:
            raise MappingError("LLM is not enabled or Direct Line Secret not configured")
        
        payload_json = json.dumps(payload, indent=2)
        
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                conversation_id, token = self._create_conversation()
                
                self._send_message(conversation_id, payload_json)
                
                response_text = self._poll_for_response(conversation_id)
                
                return self._extract_json_from_text(response_text)
                
            except requests.exceptions.Timeout as e:
                last_error = f"Request timeout: {e}"
                if attempt < self.max_retries:
                    logger.warning(f"LLM request timeout, retrying ({attempt + 1}/{self.max_retries})")
                    time.sleep(1)
                    continue
            except requests.exceptions.RequestException as e:
                last_error = f"Request failed: {e}"
                if attempt < self.max_retries:
                    logger.warning(f"LLM request failed, retrying ({attempt + 1}/{self.max_retries})")
                    time.sleep(1)
                    continue
            except MappingError as e:
                raise
            except Exception as e:
                last_error = f"Unexpected error: {e}"
                if attempt < self.max_retries:
                    logger.warning(f"LLM error, retrying ({attempt + 1}/{self.max_retries})")
                    time.sleep(1)
                    continue
        
        raise MappingError(f"LLM request failed after {self.max_retries + 1} attempts: {last_error}")
    
    def suggest_mappings(
        self,
        internal_field: Dict[str, Any],
        source_columns: List[Dict[str, Any]],
        domain_context: Dict[str, Any],
        existing_mappings: Dict[str, str],
        algorithmic_suggestions: List[Dict[str, Any]],
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call LLM to get mapping suggestions.
        
        Args:
            internal_field: Internal field metadata
            source_columns: Available source columns
            domain_context: Domain context information
            existing_mappings: Existing field mappings
            algorithmic_suggestions: Algorithmic suggestions (for context)
            user_preferences: User preferences
            
        Returns:
            LLM response with mapping suggestions
        """
        request_payload = {
            "internal_field": internal_field,
            "source_columns": source_columns,
            "domain_context": domain_context,
            "existing_mappings": existing_mappings,
            "algorithmic_suggestions": algorithmic_suggestions,
            "user_preferences": user_preferences
        }
        
        return self.call_copilot_mapper(request_payload)
