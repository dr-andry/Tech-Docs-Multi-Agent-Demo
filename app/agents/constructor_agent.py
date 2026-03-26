"""Агент для формирования итогового отчёта по продукту.

Он запрашивает у Redis все документы, накопленные для заданного
product_id, и вызывает ``mcp_constructor.construct_report``.
Отчёт пока составляется по жёсткой демонстрационной схеме;
пользователь позже сможет передавать шаблоны.
"""

import asyncio

from mcp_servers.mcp_constructor import construct_report


async def run_constructor(product_id: str) -> None:
    report = await construct_report(product_id)
    print("[constructor] сформирован отчёт:")
    print(report)


async def main():
    product_id = "PROD-123"
    await run_constructor(product_id)


if __name__ == "__main__":
    asyncio.run(main())
