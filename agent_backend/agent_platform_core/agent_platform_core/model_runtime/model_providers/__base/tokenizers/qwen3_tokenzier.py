from os.path import abspath, dirname, join
from threading import Lock
from typing import Any

from transformers import AutoTokenizer as TransformerQwen3Tokenizer

_tokenizer = None
_lock = Lock()

class Qwen3Tokenizer:
    @staticmethod
    def _get_num_tokens_by_qwen3(text: str) -> int:
        """
            use qwen3 tokenizer to get num tokens
        """
        _tokenizer = Qwen3Tokenizer.get_encoder()
        tokens = _tokenizer.encode(text, verbose=False)
        return len(tokens)

    @staticmethod
    def get_num_tokens(text: str) -> int:
        return Qwen3Tokenizer._get_num_tokens_by_qwen3(text)

    @staticmethod
    def get_encoder() -> Any:
        global _tokenizer, _lock
        with _lock:
            if _tokenizer is None:
                base_path = abspath(__file__)
                qwen3_tokenizer_path = join(dirname(base_path), 'qwen3')
                _tokenizer = TransformerQwen3Tokenizer.from_pretrained(qwen3_tokenizer_path)

            return _tokenizer