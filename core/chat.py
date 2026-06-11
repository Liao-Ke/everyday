import logging
import time
import uuid

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI, RateLimitError

from utils.metadata_utils import process_stream_chunks, save_chat_metadata

logger = logging.getLogger("每日故事")


def chat_ai(
    api_key: str,
    client_params: dict,
    chat_params: dict,
    session_id: str = str(uuid.uuid4()),
    model_name: str = "unknown",
    max_retries=3,
    initial_backoff=1,
    max_backoff=10,
):
    retries = 0
    start_time = time.time()
    is_stream = chat_params.get("stream", False)
    params_copy = chat_params.copy()
    is_retry = params_copy.pop("RETRY", True)

    while retries <= (max_retries if is_retry else 0):
        try:
            if retries > 0:
                logger.debug(f"[{model_name}] 第 {retries} 次等待结束，开始第 {retries + 1} 次重试")

            client = OpenAI(api_key=api_key, **client_params)

            if retries == 0:
                logger.debug(f"[{model_name}] 调用 API")

            response = client.chat.completions.create(**params_copy)
            response_time = time.time() - start_time
            if not is_stream:
                if not response.choices or response.choices[0] is None:
                    raise ValueError("API 返回空响应")
                response_content = response.choices[0].message.model_dump() or ""

                save_chat_metadata(
                    response_time=response_time,
                    session_id=session_id,
                    response_data=response.to_dict(),
                    client_params=client_params,
                    chat_params=chat_params,
                )

                if not response_content["content"]:
                    raise ValueError("响应内容为空")

                return response_content
            else:
                content_chunks = []
                reasoning_chunks = []
                full_response = []
                for chunk in response:
                    full_response.append(chunk)
                    if chunk.choices:
                        if chunk.choices[0].delta.content:
                            if not isinstance(content_chunks, list):
                                content_chunks = [content_chunks]
                            content_chunks.append(chunk.choices[0].delta.content)
                        if (
                            hasattr(chunk.choices[0].delta, "reasoning_content")
                            and chunk.choices[0].delta.reasoning_content
                        ):
                            reasoning_chunks.append(chunk.choices[0].delta.reasoning_content)
                response_content = {"content": "".join(content_chunks)}
                if reasoning_chunks:
                    response_content["reasoning_content"] = "".join(reasoning_chunks)
                save_chat_metadata(
                    response_time=response_time,
                    session_id=session_id,
                    response_data=process_stream_chunks(full_response),
                    client_params=client_params,
                    chat_params=chat_params,
                )

                if not response_content["content"]:
                    raise ValueError("响应内容为空")

                return response_content

        except RateLimitError as e:
            backoff_time = min(initial_backoff * (2**retries) * 2, max_backoff)
            logger.warning(f"[{model_name}] RateLimit: 第 {retries + 1} 次重试，等待 {backoff_time:.2f}s: {str(e)}")
            retry_after = getattr(e, "retry_after", None)
            if retry_after and retry_after > backoff_time:
                logger.info(f"[{model_name}] 使用API建议的重试时间: {retry_after}s")
                backoff_time = retry_after
        except APITimeoutError:
            backoff_time = min(initial_backoff * (2**retries), max_backoff)
            logger.error(f"[{model_name}] 请求超时，第 {retries + 1} 次重试，等待 {backoff_time:.2f}s")

        except (APIConnectionError, APIStatusError) as e:
            backoff_time = min(initial_backoff * (2**retries), max_backoff)
            logger.error(f"[{model_name}] API 错误，第 {retries + 1} 次重试，等待 {backoff_time:.2f}s: {e}")

        except ValueError as e:
            backoff_time = min(initial_backoff * (2**retries), max_backoff)
            logger.error(f"[{model_name}] 值错误，第 {retries + 1} 次重试，等待 {backoff_time:.2f}s: {e}")

        except Exception as e:
            backoff_time = min(initial_backoff * (2**retries), max_backoff)
            logger.critical(f"[{model_name}] 严重错误: {e}", exc_info=True)

        retries += 1
        if retries < max_retries:
            time.sleep(backoff_time)
    logger.error(f"[{model_name}] 所有 {max_retries} 次重试均失败")
    return None
