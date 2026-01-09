"""CLI interface for the SysML v2 Expert Agent."""

import sys
from pathlib import Path

import click

from config.settings import get_settings
from src.agent import SysMLAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)


@click.group()
@click.version_option(version="2026.01.09")
def cli():
    """SysML v2 Expert Agent - CLI tool for SysML document management and Q&A."""
    pass


@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True))
@click.option('--no-progress', is_flag=True, help='Hide upload progress bar')
def upload(pdf_path, no_progress):
    """Upload a PDF file to Gemini File Search."""
    try:
        agent = SysMLAgent()
        show_progress = not no_progress
        
        click.echo(f"Uploading {pdf_path}...")
        result = agent.upload_file(pdf_path, show_progress=show_progress)
        
        if result:
            click.echo(click.style("✓ File uploaded successfully!", fg='green'))
            click.echo(f"  Name: {result.get('name', 'N/A')}")
            click.echo(f"  URI: {result.get('uri', 'N/A')}")
        else:
            click.echo(click.style("✗ Failed to upload file", fg='red'), err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        logger.exception("Error in upload command")
        sys.exit(1)


@cli.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--no-progress', is_flag=True, help='Hide upload progress bars')
def upload_dir(directory, no_progress):
    """Upload all PDF files from a directory."""
    try:
        agent = SysMLAgent()
        show_progress = not no_progress
        
        click.echo(f"Uploading PDFs from {directory}...")
        results = agent.upload_directory(directory, show_progress=show_progress)
        
        if results:
            click.echo(click.style(f"✓ Successfully uploaded {len(results)} file(s)", fg='green'))
            for result in results:
                click.echo(f"  - {result.get('name', 'N/A')}")
        else:
            click.echo(click.style("✗ No files were uploaded", fg='yellow'))
            
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        logger.exception("Error in upload-dir command")
        sys.exit(1)


@cli.command()
def list_files():
    """List all uploaded files."""
    try:
        agent = SysMLAgent()
        files = agent.list_files()
        
        if not files:
            click.echo("No files uploaded yet.")
            return
        
        click.echo(f"Found {len(files)} uploaded file(s):\n")
        for i, file_info in enumerate(files, 1):
            click.echo(f"{i}. {Path(file_info['original_path']).name}")
            click.echo(f"   Uploaded: {file_info.get('upload_date', 'Unknown')}")
            click.echo(f"   URI: {file_info.get('uri', 'Unknown')}")
            if i < len(files):
                click.echo()
                
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        logger.exception("Error in list-files command")
        sys.exit(1)


@cli.command()
@click.argument('question', required=True)
@click.option('--no-retry', is_flag=True, help='Disable retry logic')
def ask(question, no_retry):
    """Ask a SysML question."""
    try:
        agent = SysMLAgent()
        
        file_count = agent.get_file_count()
        if file_count == 0:
            click.echo(click.style(
                "Warning: No files uploaded. Answer may not be based on your documents.",
                fg='yellow'
            ))
            click.echo()
        
        click.echo("Thinking...")
        response = agent.ask_question(question, use_retry=not no_retry)
        
        click.echo("\n" + "=" * 70)
        click.echo(click.style("Answer:", fg='cyan', bold=True))
        click.echo("=" * 70)
        click.echo(response)
        click.echo("=" * 70)
        
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        logger.exception("Error in ask command")
        sys.exit(1)


@cli.command()
def interactive():
    """Enter interactive Q&A mode."""
    try:
        agent = SysMLAgent()
        
        file_count = agent.get_file_count()
        click.echo(click.style("SysML v2 Expert Agent - Interactive Mode", fg='cyan', bold=True))
        click.echo("=" * 70)
        
        if file_count == 0:
            click.echo(click.style(
                "Warning: No files uploaded. Answers may not be based on your documents.",
                fg='yellow'
            ))
            click.echo("Use 'upload' or 'upload-dir' commands to add PDF documents.")
        else:
            click.echo(f"Loaded {file_count} document(s) for context.")
        
        click.echo("\nType your questions (or 'quit'/'exit' to exit):\n")
        
        while True:
            try:
                question = click.prompt("Question", type=str, default="").strip()
                
                if not question or question.lower() in ['quit', 'exit', 'q']:
                    click.echo("Goodbye!")
                    break
                
                click.echo("\nThinking...")
                response = agent.ask_question(question)
                
                click.echo("\n" + "-" * 70)
                click.echo(click.style("Answer:", fg='cyan'))
                click.echo("-" * 70)
                click.echo(response)
                click.echo("-" * 70 + "\n")
                
            except KeyboardInterrupt:
                click.echo("\n\nGoodbye!")
                break
            except EOFError:
                click.echo("\n\nGoodbye!")
                break
            except Exception as e:
                click.echo(click.style(f"Error: {e}", fg='red'), err=True)
                logger.exception("Error in interactive mode")
                
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        logger.exception("Error starting interactive mode")
        sys.exit(1)


@cli.command()
@click.confirmation_option(prompt='Are you sure you want to clear the file tracking cache?')
def clear_cache():
    """Clear the file tracking cache."""
    try:
        agent = SysMLAgent()
        
        if agent.clear_cache():
            click.echo(click.style("✓ Cache cleared successfully", fg='green'))
        else:
            click.echo(click.style("✗ Failed to clear cache", fg='red'), err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        logger.exception("Error in clear-cache command")
        sys.exit(1)


if __name__ == '__main__':
    cli()

