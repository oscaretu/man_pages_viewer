import click
import sys
from manls.parser import ManParser
from manls.tui import ManPageViewer


@click.command()
@click.argument("args", nargs=-1)
@click.option("-k", "--search", "search_query", help="Search man pages")
def main(args: tuple, search_query: str):
    parser = ManParser()

    if search_query:
        results = parser.search(search_query)
        if not results:
            click.echo(f"No results found for: {search_query}")
            return

        click.echo(f"Search results for: {search_query}\n")
        for name, desc in results:
            click.echo(f"  {name}")
            if desc:
                click.echo(f"    {desc}")
            click.echo()
        return

    if not args:
        click.echo("Usage: manls [section] <command> or manls -k <search>")
        click.echo("Examples:")
        click.echo("  manls ls")
        click.echo("  manls 2 open")
        click.echo("  manls passwd 5")
        click.echo("  manls -k ssh")
        return

    # Parse arguments: can be "command" or "section command"
    if len(args) == 1:
        command = args[0]
        section = None
    elif len(args) == 2:
        # Check if first arg is a section number
        if args[0].isdigit():
            section = int(args[0])
            command = args[1]
        else:
            command = args[0]
            section = None
    else:
        click.echo("Usage: manls [section] <command>")
        return

    if not parser.exists(command, section if section else None):
        click.echo(f"No manual entry for: {command}")
        if section:
            click.echo(f"  (section {section})")
        sys.exit(1)

    try:
        man_page = parser.parse(command, section if section else None)
        app = ManPageViewer(man_page)
        app.run()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
