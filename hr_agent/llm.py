"""
LLM module for answer generation (vLLM backend)
"""
from typing import Optional
from pathlib import Path
import requests

from hr_agent.utils import get_device, get_logger

logger = get_logger(__name__)


class LLM:
    """
    vLLM-backed wrapper for answer generation.
    Expects vLLM OpenAI-compatible server running on http://127.0.0.1:8001
    """

    def __init__(
        self,
        model_path: Path,
        device: Optional[str] = None,
        max_new_tokens: int = 512,
        temperature: float = 0.3,
        use_4bit: bool = False,
        base_url: str = "http://127.0.0.1:8001",
    ):
        self.model_path = model_path
        self.device = device or get_device()
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.use_4bit = use_4bit

        # vLLM settings
        self.base_url = base_url.rstrip("/")
        self.vllm_model_name = str(self.model_path)

        # compatibility placeholders (not used with vLLM)
        self.model = None
        self.tokenizer = None

        self.available = False
        self._load_model()

    def _load_model(self):
        """
        Ping vLLM server and discover model id.
        """
        self.available = False

        try:
            logger.info(f"Checking vLLM server at {self.base_url} ...")
            r = requests.get(f"{self.base_url}/v1/models", timeout=5)
            r.raise_for_status()
            data = r.json()

            models = data.get("data", []) if isinstance(data, dict) else []
            if models and isinstance(models, list):
                self.vllm_model_name = models[0].get("id", str(self.model_path))
            else:
                self.vllm_model_name = str(self.model_path)
                logger.warning(
                    "vLLM server responded but returned no models. "
                    f"Falling back to model id = {self.vllm_model_name}"
                )

            self.available = True
            logger.info(f"✓ vLLM server reachable. Using model id: {self.vllm_model_name}")

        except Exception as e:
            logger.error(f"vLLM server not reachable on {self.base_url}: {e}")
            logger.error(
                "Start it with:\n"
                "  vllm serve /home/saad/hr_case/models1/Qwen__Qwen3-1.7B "
                "--host 127.0.0.1 --port 8001 --tensor-parallel-size 4 "
                "--dtype auto --max-model-len 2048"
            )
            logger.error("App will run in retrieval-only mode")
            self.available = False

    def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        if not self.available:
            return "[خطأ: نموذج اللغة غير متوفر. يرجى التحقق من إعدادات النموذج أو تشغيل vLLM.]"

        try:
            url = f"{self.base_url}/v1/completions"
            payload = {
                "model": self.vllm_model_name,
                "prompt": (
                    f"{system_prompt}\n\n"
                    f"{user_prompt}\n\n"
                    "- اكتب فقرة قصيرة بدون تعداد.\n\n"
                    "الإجابة:"
                ),
                "temperature": 0.0,
                "max_tokens": 180,
                "presence_penalty": 0.2,
                "frequency_penalty": 0.3,
                "stop": ["\n\nالمصادر:", "\n\nSources:"],
            }

            # (connect timeout, read timeout)
            r = requests.post(url, json=payload, timeout=(5, 180))
            r.raise_for_status()

            data = r.json()
            choices = data.get("choices", [])
            if not choices:
                return "[خطأ: لم يتم استلام مخرجات من vLLM.]"

            text = choices[0].get("text")
            if text is None:
                # fallback (rare)
                text = str(choices[0])

            return text.strip()

        except Exception as e:
            logger.error(f"Error generating answer via vLLM: {e}")
            return f"[خطأ في توليد الإجابة عبر vLLM: {str(e)}]"

def create_llm(
    model_path: Path,
    device: Optional[str] = None,
    max_new_tokens: int = 512,
    temperature: float = 0.3,
    use_4bit: bool = False,
) -> LLM:
    return LLM(model_path, device, max_new_tokens, temperature, use_4bit)
