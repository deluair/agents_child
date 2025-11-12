"""
Command-line interface for the Advanced AI Agent
"""

import typer
import json
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from pathlib import Path
import time

from .core.config import load_config, AgentConfig
from .core.agent import AdvancedAgent

app = typer.Typer(help="Advanced AI Agent with Continuous Learning and Memory")
console = Console()


@app.command()
def chat(
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file path"),
    memory_path: Optional[str] = typer.Option("./memory", "--memory", "-m", help="Memory storage path"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Agent name")
):
    """Start an interactive chat session with the agent"""
    
    console.print(Panel.fit("🤖 Advanced AI Agent Chat", style="bold blue"))
    
    # Load configuration
    config = load_config(config_file) if config_file else load_config()
    if name:
        config.name = name
        
    # Initialize agent
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Initializing agent...", total=None)
        
        try:
            agent = AdvancedAgent(config, memory_path)
            progress.update(task, description="Agent ready!")
            time.sleep(0.5)
        except Exception as e:
            console.print(f"[red]Error initializing agent: {e}[/red]")
            raise typer.Exit(1)
    
    console.print(f"[green]✓ Agent '{config.name}' is ready to chat![/green]")
    console.print("[dim]Type 'quit', 'exit', or press Ctrl+C to end the conversation.[/dim]")
    console.print("[dim]Type 'help' for available commands.[/dim]")
    console.print()
    
    # Main chat loop
    while True:
        try:
            user_input = Prompt.ask("[bold blue]You[/bold blue]")
            
            if user_input.lower() in ["quit", "exit", "q"]:
                console.print("[yellow]Goodbye! Shutting down agent...[/yellow]")
                agent.shutdown()
                break
                
            elif user_input.lower() == "help":
                _show_chat_help()
                continue
                
            elif user_input.lower() == "stats":
                _show_agent_stats(agent)
                continue
                
            elif user_input.lower() == "memory":
                _show_memory_info(agent)
                continue
                
            elif user_input.lower().startswith("feedback "):
                feedback_text = user_input[9:].strip()
                if feedback_text:
                    feedback = {"comment": feedback_text, "rating": 0.7}
                    agent.learn(feedback)
                    console.print("[green]✓ Feedback recorded. Thank you![/green]")
                continue
                
            elif user_input.lower().startswith("remember "):
                knowledge_text = user_input[9:].strip()
                if knowledge_text:
                    knowledge = {
                        "type": "fact",
                        "statement": knowledge_text,
                        "importance": 0.8
                    }
                    agent.add_knowledge(knowledge)
                    console.print("[green]✓ Knowledge added to memory.[/green]")
                continue
                
            # Process user input
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("Thinking...", total=None)
                response = agent.process(user_input)
                
            # Display response
            console.print(f"[bold green]{config.name}[/bold green]: {response['response']}")
            
            # Show confidence if low
            if response.get("confidence", 0) < 0.5:
                console.print(f"[dim]Confidence: {response['confidence']:.2f}[/dim]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupt received. Shutting down gracefully...[/yellow]")
            agent.shutdown()
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@app.command()
def query(
    query_text: str,
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file path"),
    memory_path: Optional[str] = typer.Option("./memory", "--memory", "-m", help="Memory storage path"),
    memory_type: Optional[str] = typer.Option(None, "--type", "-t", help="Memory type to query"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of results")
):
    """Query agent's memory"""
    
    config = load_config(config_file) if config_file else load_config()
    agent = AdvancedAgent(config, memory_path)
    
    try:
        results = agent.query_memory(query_text, memory_type, limit)
        
        if not results:
            console.print(f"[yellow]No memories found for query: '{query_text}'[/yellow]")
            return
            
        # Display results in a table
        table = Table(title=f"Memory Query Results: '{query_text}'")
        table.add_column("Type", style="cyan")
        table.add_column("Content", style="white")
        table.add_column("Relevance", style="yellow")
        table.add_column("Importance", style="green")
        
        for result in results:
            content = str(result.get("content", ""))[:100] + "..." if len(str(result.get("content", ""))) > 100 else str(result.get("content", ""))
            table.add_row(
                result.get("type", "unknown"),
                content,
                f"{result.get('relevance', 0):.2f}",
                f"{result.get('importance', 0):.2f}"
            )
            
        console.print(table)
        
    finally:
        agent.shutdown()


@app.command()
def stats(
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file path"),
    memory_path: Optional[str] = typer.Option("./memory", "--memory", "-m", help="Memory storage path"),
    export_file: Optional[str] = typer.Option(None, "--export", "-e", help="Export statistics to file")
):
    """Show agent statistics"""
    
    config = load_config(config_file) if config_file else load_config()
    agent = AdvancedAgent(config, memory_path)
    
    try:
        statistics = agent.get_statistics()
        
        # Display statistics
        _show_detailed_stats(statistics)
        
        # Export if requested
        if export_file:
            with open(export_file, 'w') as f:
                json.dump(statistics, f, indent=2, default=str)
            console.print(f"[green]Statistics exported to: {export_file}[/green]")
            
    finally:
        agent.shutdown()


@app.command()
def export(
    output_file: str,
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file path"),
    memory_path: Optional[str] = typer.Option("./memory", "--memory", "-m", help="Memory storage path")
):
    """Export agent memory to file"""
    
    config = load_config(config_file) if config_file else load_config()
    agent = AdvancedAgent(config, memory_path)
    
    try:
        agent.export_memory(output_file)
        console.print(f"[green]Memory exported to: {output_file}[/green]")
        
    finally:
        agent.shutdown()


@app.command()
def import_memory(
    input_file: str,
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file path"),
    memory_path: Optional[str] = typer.Option("./memory", "--memory", "-m", help="Memory storage path")
):
    """Import agent memory from file"""
    
    if not Path(input_file).exists():
        console.print(f"[red]File not found: {input_file}[/red]")
        raise typer.Exit(1)
        
    config = load_config(config_file) if config_file else load_config()
    agent = AdvancedAgent(config, memory_path)
    
    try:
        agent.import_memory(input_file)
        console.print(f"[green]Memory imported from: {input_file}[/green]")
        
    finally:
        agent.shutdown()


@app.command()
def reset(
    memory_path: str = typer.Option("./memory", "--memory", "-m", help="Memory storage path", 
                                   confirmation_prompt=True)
):
    """Reset agent memory (WARNING: This will delete all stored data!)"""
    
    if typer.confirm("Are you sure you want to reset all agent memory? This cannot be undone."):
        config = load_config()
        agent = AdvancedAgent(config, memory_path)
        
        try:
            agent.reset()
            console.print("[green]✓ Agent memory has been reset.[/green]")
            
        finally:
            agent.shutdown()


def _show_chat_help():
    """Show help for chat commands"""
    
    help_text = """
    [bold]Available Commands:[/bold]
    
    • [cyan]help[/cyan] - Show this help message
    • [cyan]stats[/cyan] - Show agent statistics
    • [cyan]memory[/cyan] - Show memory information
    • [cyan]feedback <message>[/cyan] - Provide feedback to the agent
    • [cyan]remember <fact>[/cyan] - Add a fact to agent's memory
    • [cyan]quit/exit/q[/cyan] - End the conversation
    
    [bold]Examples:[/bold]
    • feedback That was a helpful response
    • remember The capital of France is Paris
    """
    
    console.print(Panel(help_text, title="Chat Commands", border_style="blue"))


def _show_agent_stats(agent):
    """Show agent statistics"""
    
    stats = agent.get_statistics()
    _show_detailed_stats(stats)


def _show_memory_info(agent):
    """Show memory information"""
    
    memory_stats = agent.memory.get_memory_stats()
    
    table = Table(title="Memory Information")
    table.add_column("Memory Type", style="cyan")
    table.add_column("Count", style="white")
    table.add_column("Capacity", style="white")
    table.add_column("Utilization", style="yellow")
    
    for memory_type, stats in memory_stats.items():
        if memory_type != "total_consolidations":
            utilization = stats["utilization"] * 100
            table.add_row(
                memory_type.replace("_", " ").title(),
                str(stats["count"]),
                str(stats["capacity"]),
                f"{utilization:.1f}%"
            )
    
    console.print(table)


def _show_detailed_stats(statistics):
    """Show detailed statistics"""
    
    # Agent info
    agent_info = statistics["agent_info"]
    console.print(f"[bold]Agent:[/bold] {agent_info['name']} v{agent_info['version']}")
    console.print(f"[bold]Uptime:[/bold] {agent_info['uptime_hours']:.1f} hours")
    console.print(f"[bold]Total Interactions:[/bold] {agent_info['total_interactions']}")
    console.print()
    
    # State info
    state = statistics["state"]
    console.print(f"[bold]Current Mode:[/bold] {state['mode']}")
    console.print(f"[bold]Emotional State:[/bold] {state['emotional_state']}")
    console.print()
    
    # Memory stats
    memory_stats = statistics["memory"]
    console.print("[bold]Memory Usage:[/bold]")
    
    for memory_type, stats in memory_stats.items():
        if memory_type != "total_consolidations":
            utilization = stats["utilization"] * 100
            console.print(f"  • {memory_type.replace('_', ' ').title()}: {stats['count']}/{stats['capacity']} ({utilization:.1f}%)")
    
    console.print(f"  • Total Consolidations: {memory_stats['total_consolidations']}")
    console.print()
    
    # Learning stats
    learning_stats = statistics["learning"]
    console.print("[bold]Learning Statistics:[/bold]")
    console.print(f"  • Learning Episodes: {learning_stats['learning_episodes']}")
    console.print(f"  • Adaptation Count: {learning_stats['adaptation_count']}")
    console.print(f"  • Response Patterns: {learning_stats['response_patterns_count']}")
    console.print(f"  • Recent Performance: {learning_stats['recent_performance']:.2f}")
    console.print()
    
    # Knowledge stats
    knowledge_stats = statistics["knowledge"]
    console.print("[bold]Knowledge Graph:[/bold]")
    console.print(f"  • Total Entities: {knowledge_stats['total_entities']}")
    console.print(f"  • Total Relations: {knowledge_stats['total_relations']}")
    console.print(f"  • Entity Types: {knowledge_stats['entity_types']}")


def main():
    """Main entry point"""
    app()


if __name__ == "__main__":
    main()
