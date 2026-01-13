# Raw CLI Command

Execute a raw CLI command in a new terminal window.

## Instructions

1. Before executing an unfamiliar command, run `<command> --help` to understand its options
2. Pass the command directly to fork_terminal without modification
3. No model selection needed - this is for arbitrary CLI commands

## Use Cases

- Running development servers (`npm run dev`, `python manage.py runserver`)
- Build processes (`npm run build`, `cargo build`)
- Long-running processes (`tail -f logs.txt`)
- Any command that benefits from a separate terminal window

## Examples

```bash
# Development servers
npm run dev
python manage.py runserver
cargo run

# Build processes
npm run build
make all

# Long-running processes
tail -f /var/log/app.log

# Media processing
ffmpeg -i input.mp4 -c:v libx264 output.mp4
```
