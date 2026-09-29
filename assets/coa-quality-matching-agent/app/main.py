from sap_cloud_sdk.aicore import set_aicore_config

set_aicore_config()

import logging
import os

import click
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from sap_cloud_sdk import bootstrap
from starlette.middleware.base import BaseHTTPMiddleware

from agent_executor import AgentExecutor
from mcp_providers.agw import set_user_token, reset_user_token

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "5000"))


@click.command()
@click.option("--host", default=HOST)
@click.option("--port", default=PORT)
def main(host: str, port: int):
    skill = AgentSkill(
        id="coa-quality-matching-agent",
        name="coa-quality-matching-agent",
        description="An AI agent that automates vendor Certificate of Analysis (COA) verification for Lubes and Solid Chemicals by ingesting COAs from multiple channels, extracting quality parameters via OCR, validating against S/4HANA QM inspection plan specifications, and posting usage decisions automatically.",
        tags=["coa", "quality", "certificate", "matching", "agent"],
        examples=[
            "Check if there are any new COA documents waiting to be processed",
            "Process the COA received from Shell Chemicals for material LUB-1042",
            "What is the validation status of the latest COA for material LUB-1042?",
            "Show me all COA parameters for the last rejected certificate",
            "Which COAs are currently on hold and waiting for manual review?",
            "Post the usage decision for inspection lot 0000123456 as accepted",
        ],
    )
    agent_card = AgentCard(
        name="coa-quality-matching-agent",
        description="An AI agent that automates vendor Certificate of Analysis (COA) verification for Lubes and Solid Chemicals by ingesting COAs from multiple channels, extracting quality parameters via OCR, validating against S/4HANA QM inspection plan specifications, and posting usage decisions automatically.",
        url=os.environ.get("AGENT_PUBLIC_URL", f"http://{host}:{port}/"),
        version="1.0.0",
        default_input_modes=["text", "text/plain"],
        default_output_modes=["text", "text/plain"],
        capabilities=AgentCapabilities(streaming=True, push_notifications=False),
        skills=[skill],
    )
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=DefaultRequestHandler(
            agent_executor=AgentExecutor(),
            task_store=InMemoryTaskStore(),
        ),
    )
    app = server.build()

    class JWTContextMiddleware(BaseHTTPMiddleware):
        """Extracts JWT token from Authorization header and sets it in context."""

        async def dispatch(self, request, call_next):
            auth_header = request.headers.get("authorization", "")
            token = auth_header[7:] if auth_header.lower().startswith("bearer ") else None
            token_ctx = set_user_token(token)
            try:
                return await call_next(request)
            finally:
                reset_user_token(token_ctx)

    app.add_middleware(JWTContextMiddleware)

    bootstrap(app)

    logger.info(f"Starting A2A server at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
