"""
CLI Interface for Nimbus

Command-line interface for backup operations, configuration, and management.
"""

from pathlib import Path

import click
from loguru import logger
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

from app import __version__
from app.core.backup import BackupEngine, IncrementalBackup
from app.core.config import config

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="Nimbus")
@click.pass_context
def cli(ctx):
    """
    🌥️ Nimbus - Enterprise Backup & Cloud Sync Solution

    A professional-grade backup tool for Linux systems.
    """
    ctx.ensure_object(dict)


@cli.command()
@click.argument("source", type=click.Path(exists=True))
@click.option("--destination", "-d", required=True, help="Backup destination path")
@click.option("--incremental", "-i", is_flag=True, help="Perform incremental backup")
@click.option("--encrypt", "-e", is_flag=True, help="Encrypt backup")
@click.option("--compress", "-c", is_flag=True, default=True, help="Compress backup")
@click.option("--verify", "-v", is_flag=True, default=True, help="Verify backup integrity")
def backup(source, destination, incremental, encrypt, compress, verify):
    """Backup files to specified destination."""

    console.print("\n[bold cyan]🚀 Starting Backup[/bold cyan]")
    console.print(f"Source: [green]{source}[/green]")
    console.print(f"Destination: [green]{destination}[/green]")
    console.print(f"Mode: [yellow]{'Incremental' if incremental else 'Full'}[/yellow]\n")

    source_path = Path(source)
    dest_path = Path(destination)

    try:
        # Initialize backup engine
        if incremental:
            engine = IncrementalBackup(source_path, dest_path)
        else:
            engine = BackupEngine(source_path, dest_path)

        # Progress callback
        progress_data = {"current": 0}

        def progress_callback(data):
            progress_data["current"] = data.get("backed_up_files", 0)

        # Perform backup with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Backing up files...", total=100)

            stats = engine.backup(progress_callback)

            progress.update(task, completed=100)

        # Display results
        console.print("\n[bold green]✅ Backup Completed![/bold green]\n")

        table = Table(title="Backup Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Files", str(stats["total_files"]))
        table.add_row("Backed Up", str(stats["backed_up_files"]))
        table.add_row("Failed", str(stats["failed_files"]))
        table.add_row("Total Size", f"{stats['total_size'] / (1024**3):.2f} GB")
        table.add_row("Transferred", f"{stats['transferred_size'] / (1024**3):.2f} GB")

        if stats["start_time"] and stats["end_time"]:
            duration = (stats["end_time"] - stats["start_time"]).total_seconds()
            table.add_row("Duration", f"{duration:.2f} seconds")

        console.print(table)

    except Exception as e:
        console.print(f"\n[bold red]❌ Backup Failed:[/bold red] {e}\n")
        logger.error(f"Backup failed: {e}")
        raise click.Abort()


@cli.command()
@click.argument("backup_path", type=click.Path(exists=True))
@click.argument("restore_path", type=click.Path())
def restore(backup_path, restore_path):
    """Restore files from backup."""

    console.print("\n[bold cyan]🔄 Starting Restore[/bold cyan]")
    console.print(f"Backup: [green]{backup_path}[/green]")
    console.print(f"Restore to: [green]{restore_path}[/green]\n")

    backup_path = Path(backup_path)
    restore_path = Path(restore_path)

    try:
        # Initialize backup engine
        engine = BackupEngine(backup_path, restore_path)

        # Perform restore with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Restoring files...", total=100)

            stats = engine.restore(restore_path)

            progress.update(task, completed=100)

        console.print("\n[bold green]✅ Restore Completed![/bold green]")
        console.print(f"Files restored: {stats['restored_files']}/{stats['total_files']}\n")

    except Exception as e:
        console.print(f"\n[bold red]❌ Restore Failed:[/bold red] {e}\n")
        logger.error(f"Restore failed: {e}")
        raise click.Abort()


@cli.group(name="config")
def config_cmd():
    """Manage Nimbus configuration."""
    pass


@config_cmd.command("show")
def config_show():
    """Show current configuration."""

    console.print("\n[bold cyan]⚙️ Current Configuration[/bold cyan]\n")

    table = Table(title="Nimbus Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    # Display key configuration settings
    table.add_row("Default Destination", str(config.get("backup.default_destination", "Not set")))
    table.add_row("Compression", str(config.get("backup.compression", True)))
    table.add_row("Encryption", str(config.get("backup.encryption", False)))
    table.add_row("Incremental", str(config.get("backup.incremental", True)))
    table.add_row("Threads", str(config.get("performance.threads", 4)))
    table.add_row("Log Level", config.get("logging.level", "INFO"))

    console.print(table)
    console.print()


@config_cmd.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Set configuration value."""

    try:
        # Convert value to appropriate type
        if value.lower() in ["true", "false"]:
            value = value.lower() == "true"
        elif value.isdigit():
            value = int(value)

        config.set(key, value)
        config.save()

        console.print(f"\n[green]✅ Configuration updated:[/green] {key} = {value}\n")

    except Exception as e:
        console.print(f"\n[red]❌ Error:[/red] {e}\n")
        raise click.Abort()


@config_cmd.command("reset")
@click.confirmation_option(prompt="Are you sure you want to reset configuration to default?")
def config_reset():
    """Reset configuration to default values."""

    try:
        config.reset_to_default()
        console.print("\n[green]✅ Configuration reset to default values[/green]\n")

    except Exception as e:
        console.print(f"\n[red]❌ Error:[/red] {e}\n")
        raise click.Abort()


@cli.group(name="schedule")
def schedule_cmd():
    """Manage backup schedules."""
    pass


@schedule_cmd.command("add")
@click.option("--source", "-s", required=True, help="Source directory")
@click.option("--destination", "-d", required=True, help="Destination path")
@click.option("--time", "-t", default="23:00", help="Backup time (HH:MM)")
@click.option(
    "--frequency",
    "-f",
    default="daily",
    type=click.Choice(["daily", "weekly", "monthly"]),
)
def schedule_add(source, destination, time, frequency):
    """Add a scheduled backup."""

    console.print("\n[cyan]📅 Adding Schedule[/cyan]")
    console.print(f"Source: {source}")
    console.print(f"Destination: {destination}")
    console.print(f"Time: {time}")
    console.print(f"Frequency: {frequency}\n")

    # TODO: Implement scheduling functionality
    console.print("[yellow]⚠️ Scheduling functionality coming soon![/yellow]\n")


@cli.command()
def gui():
    """Launch Nimbus GUI application."""

    console.print("\n[cyan]🖥️ Launching Nimbus GUI...[/cyan]\n")

    try:
        from app.gui.main import main as gui_main

        gui_main()
    except ImportError:
        console.print("[red]❌ GUI dependencies not installed. Install with: pip install nimbus-backup[gui][/red]\n")
        raise click.Abort()


@cli.command()
def version():
    """Show version information."""

    from app import __author__, __copyright__, __email__

    console.print(f"\n[bold cyan]Nimbus v{__version__}[/bold cyan]")
    console.print(f"Author: {__author__}")
    console.print(f"Email: {__email__}")
    console.print(f"{__copyright__}\n")


if __name__ == "__main__":
    cli()
