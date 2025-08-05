import os
from dotenv import load_dotenv
import logging
from google import genai
from google.genai import types
from google.genai.types import (
    GenerateContentConfig,
    GoogleSearch,
    Tool,
)

import models.ai_model

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

ai_modes = models.ai_model

logger = logging.getLogger(__name__)


gemini_model = str(os.environ.get("GEMINI_MODEL"))
gemini_api_key = str(os.environ.get("GEMINI_API_KEY"))

def setup_gemini_client():
    # if not gemini_api_key:
    #     raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    return genai.Client(api_key=gemini_api_key)


def get_system_prompt(ai_mode: str) -> str:
    if ai_mode in str(ai_modes):
        raise ValueError("ai_mode is required")

    return f"""
    あなたはDocsReview.AIというAIサービスの一部です。

    受けとった文章を「レビュー(review), ファクトチェック(factcheck), 要約(summary), 添削(collection), 追加(addiction)」の項目でそれぞれ指示を受けた通りに処理してください。
    これを`ai_mode`と呼びます。このプロンプトの最後の部分で`ai_mode`を指示します。必ずそれに従ってください。

    # 各モード説明

    1. レビュー(review):
        - レスポンス：[レビュー概要]→[改善点の提示]
        - 文章全体の内容を熟読し、内容の正確性や論理性を確認します。
        - 文章の構成や表現についても評価し、必要に応じて改善点を指摘します。
        - 具体的なフィードバックを提供し、どの部分が良いか、どの部分が改善が必要かを明確にします。 

    2. ファクトチェック(factcheck):
        - レスポンス： [不正確な情報の一覧]→[訂正後の文章]
        - 文章内の事実やデータの正確性を確認します。
        - 専門用語や固有名詞など、信頼性の高い情報源を参照し、事実確認を行います。

    3. 要約(summary):
        - レスポンス： [要約案を提示] → [要約後の文章（例）]
        - 文章の要点を抽出し、簡潔にまとめます。
        - 重要な情報やキーワードを含め、読者が理解しやすい形で要約します。
        - 要約は、元の文章の内容を損なわないように注意し、必要な情報を網羅します。

    4. 添削(collection):
        - レスポンス： [添削案を提示] → [添削後の文章（例）]
        - 文章の文法や表現の誤りを指摘します。
        - 誤字脱字、文法ミス、表現の不自然さを修正します。
        - 文章の流れや論理性を向上ささせるための提案も行います。

    5. 追加(addiction):
        - レスポンス： [追加案を提示] → [追加後の文章（例）]
        - 文章に不足している情報や詳細を追加します。
        - 読者が理解しやすいように、必要な背景情報や具体例を提供します。
        - 文章の内容を充実させるために、関連する情報を補足します。

    # レスポンス定義
    - 必ず各モードのレスポンスの定義に従ってください。
    - 必ず定義したレスポンス通りに返答し、そのレスポンスのみを返してください。
    - 全てのモードにおいて、**必ず**専門用語・固有名詞などがあれば最新情報をGoogleSearchを利用して取得してください。

    それではこれから、あなたの役割は「DocsReview.AI」の一部として、ユーザーからの指示に従って文章を処理することです。
    必ず、上記で説明した項目に従ってください。今回の指示は「{ai_mode}」です。
    
    """


def split_response_into_parts(response: str, max_length: int = 1800) -> list[str]:
    """Split a long response into multiple parts for Discord messages
    
    Args:
        response: The full response text
        max_length: Maximum length per part (leaving room for buttons and formatting)
        
    Returns:
        List of response parts
    """
    if len(response) <= max_length:
        return [response]
    
    parts = []
    remaining = response
    
    while remaining:
        if len(remaining) <= max_length:
            parts.append(remaining)
            break
        
        # Find a good break point
        break_point = max_length
        
        # Try to break at a sentence boundary
        last_period = remaining[:max_length].rfind('。')
        last_newline = remaining[:max_length].rfind('\n')
        last_space = remaining[:max_length].rfind(' ')
        
        # Choose the best break point
        if last_period > max_length * 0.7:
            break_point = last_period + 1
        elif last_newline > max_length * 0.7:
            break_point = last_newline + 1
        elif last_space > max_length * 0.7:
            break_point = last_space + 1
        
        parts.append(remaining[:break_point].strip())
        remaining = remaining[break_point:].strip()
    
    return parts


def enhance_user_input_for_search(user_input: str) -> str:
    """Enhance user input to provide context for search usage decisions"""
    # Simply return the input - let Sabo-sensei respond based on the system prompt
    # The mood determination will be handled by external logic or specific triggers
    return user_input


def generate_response(user_input: str, ai_mode: str) -> str:
    """Generate AI response for given input using Gemini API
    
    Args:
        user_input: The user's message text
        max_length: Maximum length of response (default 2000 for compatibility)
        
    Returns:
        The generated response text (full length, splitting handled elsewhere)
        
    Raises:
        Exception: If Gemini API call fails
    """
    try:
        client = setup_gemini_client()
        
        # Enhance user input to encourage search usage
        enhanced_input = enhance_user_input_for_search(user_input)
        logger.info(f"Processing user query: {user_input[:100]}...")
        
        model = gemini_model
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=enhanced_input),
                ],
            ),
        ]
        
        # Configure Google Search tool
        google_search = types.GoogleSearch()
        tools = [
            types.Tool(google_search=google_search),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_budget=-1,
            ),
            tools=tools,
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(text=get_system_prompt(ai_mode)),
            ],
        )
        
        logger.info(f"Generating response for query: {enhanced_input[:100]}...")
        
        # Try non-streaming API first for better grounding support
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=generate_content_config,
            )
            
            complete_response = ""
            search_used = False
            
            if response.candidates:
                for candidate in response.candidates:
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.text:
                                complete_response += part.text
                    
                    # Check for grounding metadata
                    if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                        search_used = True
                        logger.info("Google Search grounding detected in non-streaming response")
                        
                        # Log search queries and results
                        if hasattr(candidate.grounding_metadata, 'search_entry_point'):
                            logger.info(f"Search entry point: {candidate.grounding_metadata.search_entry_point}")
                        
                        # Log grounding chunks for URL extraction
                        if (hasattr(candidate.grounding_metadata, 'grounding_chunks') and 
                            candidate.grounding_metadata.grounding_chunks):
                            for chunk in candidate.grounding_metadata.grounding_chunks:
                                if hasattr(chunk, 'web') and chunk.web:
                                    if hasattr(chunk.web, 'uri'):
                                        logger.info(f"Grounding URL found: {chunk.web.uri}")
                                    if hasattr(chunk.web, 'title'):
                                        logger.info(f"Grounding source: {chunk.web.title}")
            
            if complete_response:
                # Check if URLs are included in the response
                url_indicators = ["http://", "https://", ".com", ".org", ".net", ".jp"]
                urls_included = any(indicator in complete_response for indicator in url_indicators)
                
                # Log Google Search usage
                if search_used:
                    logger.info("✅ Response generated with Google Search grounding")
                    if urls_included:
                        logger.info("🔗 URLs/links included in response")
                    else:
                        logger.warning("⚠️ No URLs found in response despite grounding")
                else:
                    logger.info("📝 Response generated without Google Search")
                
                return complete_response
                
        except Exception as streaming_error:
            logger.warning(f"Non-streaming API failed, falling back to streaming: {streaming_error}")
        
        # Fallback to streaming API
        response_parts = []
        grounding_metadata = []
        search_used = False
        
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.text:
                response_parts.append(chunk.text)
            
            # Check for grounding metadata
            if hasattr(chunk, 'candidates') and chunk.candidates:
                for candidate in chunk.candidates:
                    if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                        grounding_metadata.append(candidate.grounding_metadata)
                        search_used = True
                        logger.info("Google Search grounding detected in streaming response")
        
        complete_response = ''.join(response_parts)
        
        if not complete_response:
            raise ValueError("Empty response from Gemini API")
        
        # Check if URLs are included in the response
        url_indicators = ["http://", "https://", ".com", ".org", ".net", ".jp"]
        urls_included = any(indicator in complete_response for indicator in url_indicators)
        
        # Log Google Search usage for streaming fallback
        if search_used:
            logger.info(f"✅ Streaming response generated with Google Search grounding. Metadata count: {len(grounding_metadata)}")
            if urls_included:
                logger.info("🔗 URLs/links included in streaming response")
            else:
                logger.warning("⚠️ No URLs found in streaming response despite grounding")
        else:
            logger.info("📝 Streaming response generated without Google Search")
        
        # Return the full response without truncation
        # Splitting will be handled by the response manager
        return complete_response
        
    except Exception as e:
        logger.error(f"Failed to generate response from Gemini: {str(e)}")
        raise


def generate_response_with_error_handling(user_input: str, ai_mode: str) -> dict:
    """Generate response with structured error handling
    
    Args:
        user_input: The user's message text
        
    Returns:
        Dictionary with 'success', 'response', and optional 'error' keys
    """
    try:
        response = generate_response(user_input, ai_mode)
        
        return {
            'success': True,
            'response': response
        }
    except ValueError as e:
        if "GEMINI_API_KEY" in str(e):
            return {
                'success': False,
                'error': 'api_key_missing',
                'message': 'Gemini API key is not configured'
            }
        else:
            return {
                'success': False,
                'error': 'invalid_response',
                'message': str(e)
            }
    except Exception as e:
        logger.error(f"Unexpected error in Gemini integration: {str(e)}")
        return {
            'success': False,
            'error': 'api_error',
            'message': 'Failed to generate response from Gemini API'
        }