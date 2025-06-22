from config.settings import settings
from utils.cache import DevelopmentCache

from services.file_service import FileService


def pdf_to_markdown(
    pdf_path: str,
    max_polls: int = 300,
    poll_interval: int = 2,
) -> str:
    # Check cache first in development mode
    if settings.DEVELOPMENT_MODE:
        cached_result = DevelopmentCache.get_cached_response(pdf_path)
        if cached_result:
            print(f"[DEV] Using cached result for {pdf_path}")
            return cached_result

    # Read file using file service
    print(f"Reading file: {pdf_path}")
    file_bytes = FileService.read_file(pdf_path)
    file_name = FileService.get_file_name(pdf_path)
    return file_bytes

    # print(f"File loaded: {file_name} ({len(file_bytes)} bytes)")

    # url = "https://www.datalab.to/api/v1/marker"
    # headers = {"X-Api-Key": settings.DATALAB_API_KEY}

    # # Prepare form data using file bytes
    # form_data = {
    #     "file": (file_name, io.BytesIO(file_bytes), "application/pdf"),
    #     "output_format": (None, "markdown"),
    #     "use_llm": (None, True),
    # }

    # try:
    #     print("Submitting PDF to API...")
    #     # Submit the file for conversion
    #     response = requests.post(url, files=form_data, headers=headers)
    #     response.raise_for_status()
    #     data = response.json()

    #     if not data.get("success"):
    #         raise Exception(f"API request failed: {data.get('error', 'Unknown error')}")

    #     request_id = data["request_id"]
    #     check_url = data["request_check_url"]

    #     print(f"Request submitted. ID: {request_id}")
    #     print("Polling for completion...")

    #     # Poll for completion
    #     for i in range(max_polls):
    #         time.sleep(poll_interval)

    #         response = requests.get(check_url, headers=headers)
    #         response.raise_for_status()
    #         data = response.json()

    #         if data["status"] == "complete":
    #             if not data.get("success"):
    #                 raise Exception(
    #                     f"Conversion failed: {data.get('error', 'Unknown error')}"
    #                 )

    #             # Get the markdown content
    #             markdown = data.get("markdown", "")
    #             print(
    #                 f"Conversion completed successfully! ({len(markdown)} characters)"
    #             )

    #             # Cache the result in development mode
    #             if settings.DEVELOPMENT_MODE and markdown:
    #                 DevelopmentCache.cache_response(pdf_path, markdown)
    #                 print("[DEV] Cached result for future use")

    #             return markdown

    #         elif data["status"] == "failed":
    #             raise Exception(
    #                 f"Conversion failed: {data.get('error', 'Unknown error')}"
    #             )

    #         if i % 10 == 0:  # Print status every 20 seconds
    #             print(
    #                 f"Status: {data.get('status', 'unknown')} (polling {i + 1}/{max_polls})"
    #             )

    #     # If we get here, we've exceeded max_polls
    #     raise Exception(
    #         f"Conversion timed out after {max_polls * poll_interval} seconds"
    #     )

    # except requests.RequestException as e:
    #     raise requests.RequestException(f"API request failed: {str(e)}")
    # finally:
    #     # Ensure the BytesIO object is closed if it exists
    #     if "file" in form_data and hasattr(form_data["file"][1], "close"):
    #         form_data["file"][1].close()
