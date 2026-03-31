"""CLI entry point for the Data Agent."""

import click
from dotenv import load_dotenv

from data_agent.graph import create_graph, get_postgres_saver
from data_agent.state import AgentState


@click.command()
@click.argument("request")
@click.option(
    "--thread-id",
    default="default",
    help="Thread ID for checkpointing (allows resuming conversations).",
)
@click.option(
    "--use-postgres-checkpointer",
    is_flag=True,
    help="Use PostgreSQL for checkpoint persistence instead of memory.",
)
def main(request: str, thread_id: str, use_postgres_checkpointer: bool) -> None:
    """Run the Data Agent with a user request.

    Example: python -m data_agent "Query last 7 days user activity and bounce rate"
    """
    # Load environment variables
    load_dotenv()

    # Prepare initial state
    state: AgentState = {
        "user_request": request,
        "plan": {},
        "pg_data": [],
        "ga_data": [],
        "report_path": None,
        "error": None,
    }

    # Run the graph
    config = {"configurable": {"thread_id": thread_id}}

    click.echo(f"Processing request: {request}")
    click.echo("=" * 50)

    if use_postgres_checkpointer:
        with get_postgres_saver() as checkpointer:
            checkpointer.setup()
            graph = create_graph(checkpointer=checkpointer)
            final_state = graph.invoke(state, config=config)
    else:
        graph = create_graph()
        final_state = graph.invoke(state, config=config)

    # Output results
    click.echo()
    if final_state.get("error"):
        click.echo(f"Error: {final_state['error']}", err=True)
        raise click.Exit(code=1)

    plan = final_state.get("plan", {})
    if plan.get("needs_pg"):
        click.echo(f"PostgreSQL: {len(final_state.get('pg_data', []))} rows returned")
    if plan.get("needs_ga"):
        click.echo(f"Google Analytics: {len(final_state.get('ga_data', []))} rows returned")

    report_path = final_state.get("report_path")
    if report_path:
        click.echo()
        click.echo(f"Report generated: {report_path}")
    else:
        click.echo("No report was generated.")


if __name__ == "__main__":
    main()
